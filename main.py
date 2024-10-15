from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import schema, crud, models
from database import SessionLocal, engine

# Create all the models (tables) in the database
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create a new post
@app.post("/posts/", response_model=schema.Post)
def create_post(post: schema.PostCreate, db: Session = Depends(get_db)):
    return crud.create_post(db=db, post=post, owner_id=1)  # Static user_id for now

# Get a list of posts
@app.get("/posts/", response_model=List[schema.Post])
def read_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_posts(db=db, skip=skip, limit=limit)

# Get a single post by ID
@app.get("/posts/{post_id}", response_model=schema.Post)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = crud.get_post(db=db, post_id=post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

# Update a post by ID
@app.put("/posts/{post_id}", response_model=schema.Post)
def update_post(post_id: int, post: schema.PostCreate, db: Session = Depends(get_db)):
    return crud.update_post(db=db, post_id=post_id, post_data=post)

# Delete a post by ID
@app.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    return crud.delete_post(db=db, post_id=post_id)
