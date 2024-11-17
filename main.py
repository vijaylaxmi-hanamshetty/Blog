from fastapi import FastAPI, Depends, HTTPException,Path,UploadFile,File
from sqlalchemy.orm import Session
from typing import List,Optional
import schema 
import crud
from pathlib import Path
import models
from database import SessionLocal, engine
from auth import get_current_user, create_access_token, get_password_hash, authenticate_user
from fastapi.security import OAuth2PasswordRequestForm
from database import get_db
from datetime import datetime
from pathlib import Path
from fastapi import Form
# Create all the models (tables) in the database
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

UPLOAD_DIR = Path("static/images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Mount static files

# Register a new user
@app.post("/register", response_model=schema.User)
def register(user: schema.UserCreate, db: Session = Depends(get_db)):
    user_exists = crud.get_user_by_username(db, username=user.username)
    if user_exists:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)

    return crud.create_user(db, user, hashed_password)
# Login user and create token
@app.post("/token", response_model=schema.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/posts/")
async def create_post(
    title: str = Form(...),
    content: str = Form(...),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Debugging: log incoming form data
    print(f"Title: {title}, Content: {content}, Category: {category}, Tags: {tags}, Image: {image}")

    if current_user.role not in ["author", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    if not title.strip() or not content.strip():
        raise HTTPException(status_code=400, detail="Title and content cannot be empty")
    
    image_path = None
    if image:
        file_path = UPLOAD_DIR / image.filename
        with file_path.open("wb") as f:
            f.write(await image.read())
        image_path = str(file_path)
    
    post = schema.PostCreate(
        title=title,
        content=content,
        category=category,
        tags=tags,
        image_path=image_path
    )
    
    return crud.create_post(
        db=db,
        post=post,
        owner_id=current_user.id,
        image_path=image_path,
    )


# Get posts with search, filtering, and pagination
@app.get("/posts/")
def get_posts(search: str = None, category: str = None, tags: str = None, page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    total, posts = crud.get_posts(db, search, category, tags, page, limit)
    return {"total": total, "page": page, "posts": posts}

# Get a single post by ID (public access)
@app.get("/posts/{post_id}", response_model=schema.Post)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = crud.get_post(db=db, post_id=post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.put("/posts/{post_id}", response_model=schema.Post)
def update_post(post_id: int, post: schema.PostCreate,  db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_post = crud.get_post(db=db, post_id=post_id)
    if db_post.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return crud.update_post(db=db, post_id=post_id, post_data=post,)

# Delete a post
@app.delete("/posts/{post_id}/")
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: schema.User = Depends(get_current_user)):
    db_post = crud.get_post(db, post_id)
    if db_post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    if db_post.image_path:
        image_path = Path(db_post.image_path)
        if image_path.exists():
            image_path.unlink()
    return crud.delete_post(db, post_id)

# Create a comment
@app.post("/posts/{post_id}/comments/", response_model=schema.Comment)
def create_comment(post_id: int, comment: schema.CommentCreate, db: Session = Depends(get_db), current_user: schema.User = Depends(get_current_user)):
    return crud.create_comment(db, comment, post_id, user_id=current_user.id)

# Get comments for a post
@app.get("/posts/{post_id}/comments/", response_model=List[schema.Comment])
def read_comments(post_id: int, db: Session = Depends(get_db)):
    return crud.get_comments(db, post_id)

# Like a post
@app.post("/posts/{post_id}/like/")
def like_post(post_id: int, db: Session = Depends(get_db), current_user: schema.User = Depends(get_current_user)):
    return crud.like_post(db, post_id, current_user.id)

# Unlike a post
@app.delete("/posts/{post_id}/like/")
def unlike_post(post_id: int, db: Session = Depends(get_db), current_user: schema.User = Depends(get_current_user)):
    return crud.unlike_post(db, post_id, current_user.id)



