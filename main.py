from fastapi import FastAPI, Depends, HTTPException,Query,Path
from sqlalchemy.orm import Session
from typing import List,Optional
import schema 
import crud
import models
from database import SessionLocal, engine
from auth import get_current_user, create_access_token, get_password_hash, authenticate_user
from fastapi.security import OAuth2PasswordRequestForm
from database import get_db
from datetime import datetime
# Create all the models (tables) in the database
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


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

# Create a new post (only accessible to authors)
@app.post("/posts/", response_model=schema.Post)
def create_post(post: schema.PostCreate, db: Session = Depends(get_db),current_user:models.User=Depends(get_current_user)):
    if current_user.role not in ["author", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return crud.create_post(db=db, post=post, owner_id=current_user.id)  

# Get a list of posts (public access)
@app.get("/posts/", response_model=List[models.Post])
def get_all_posts(search: Optional[str] = None, category_id: Optional[int] = None,
                  tag_id: Optional[int] = None, skip: int = 0, limit: int = 10,
                  db: Session = Depends(get_db)):
    posts = crud.get_posts(db=db, search=search, category_id=category_id, tag_id=tag_id, skip=skip, limit=limit)
    return posts
# Get a single post by ID (public access)
@app.get("/posts/{post_id}", response_model=schema.Post)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = crud.get_post(db=db, post_id=post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

# Update a post by ID (only accessible to the author of the post)
@app.put("/posts/{post_id}", response_model=schema.Post)
def update_post(post_id: int, post: schema.PostCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_post = crud.get_post(db=db, post_id=post_id)
    if db_post.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return crud.update_post(db=db, post_id=post_id, post_data=post)

# Delete a post by ID(only accessible to admin)
@app.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return crud.delete_post(db=db, post_id=post_id)
# Create a new comment for a post
@app.post("/posts/{post_id}/comments/", response_model=schema.Comment)
def create_comment(post_id: int, comment: schema.CommentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_comment(db=db, comment=comment, post_id=post_id, user_id=current_user.id)

# Get all comments for a post
@app.get("/posts/{post_id}/comments/", response_model=List[schema.Comment])
def read_comments(post_id: int, db: Session = Depends(get_db)):
    return crud.get_comments(db=db, post_id=post_id)

# Like a post
@app.post("/posts/{post_id}/like/")
def like_post(post_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.like_post(db=db, post_id=post_id, user_id=current_user.id)

# Unlike a post
@app.delete("/posts/{post_id}/like/")
def unlike_post(post_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.unlike_post(db=db, post_id=post_id, user_id=current_user.id)

# Get number of likes on a post
@app.get("/posts/{post_id}/likes/")
def get_likes(post_id: int, db: Session = Depends(get_db)):
    return {"likes_count": crud.get_likes(db=db, post_id=post_id)}


@app.get("/posts/search", response_model=schema.Post)
def search_posts(q: str = Query(None), page: int = 1, size: int = 10, db: Session = Depends(get_db)):
    skip = (page - 1) * size
    posts = crud.get_posts(db, search=q, skip=skip, limit=size)
    total = crud.count_posts(db, search=q)
    return {"total": total, "page": page, "page_size": size, "data": posts}

@app.get("/posts/filter/category/{category_id}", response_model=schema.Post)
def filter_posts_by_category(category_id: int = Path(...), page: int = 1, size: int = 10, db: Session = Depends(get_db)):
    skip = (page - 1) * size
    posts =crud. get_posts(db, category_id=category_id, skip=skip, limit=size)
    total = crud.count_posts(db, category_id=category_id)
    return {"total": total, "page": page, "page_size": size, "data": posts}

@app.get("/posts/filter/tag/{tag_id}", response_model=schema.Post)
def filter_posts_by_tag(tag_id: int = Path(...), page: int = 1, size: int = 10, db: Session = Depends(get_db)):
    skip = (page - 1) * size
    posts = crud.get_posts(db, tag_id=tag_id, skip=skip, limit=size)
    total = crud.count_posts(db, tag_id=tag_id)
    return {"total": total, "page": page, "page_size": size, "data": posts}

@app.get("/posts/filter/date", response_model=schema.Post)
def filter_posts_by_date(start_date: datetime, end_date: datetime, page: int = 1, size: int = 10, db: Session = Depends(get_db)):
    skip = (page - 1) * size
    posts = crud.get_posts(db, start_date=start_date, end_date=end_date, skip=skip, limit=size)
    total = crud.count_posts(db, start_date=start_date, end_date=end_date)
    return {"total": total, "page": page, "page_size": size, "data": posts}

@app.get("/posts", response_model=schema.Post)
def combined_search_filter(
    q: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    tag_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    page: int = 1,
    size: int = 10,
    db: Session = Depends(get_db)
):
    skip = (page - 1) * size
    posts = crud.get_posts(db, search=q, category_id=category_id, tag_id=tag_id, start_date=start_date, end_date=end_date, skip=skip, limit=size)
    total = crud.count_posts(db, search=q, category_id=category_id, tag_id=tag_id, start_date=start_date, end_date=end_date)
    return {"total": total, "page": page, "page_size": size, "data": posts}
