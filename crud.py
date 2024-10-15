from sqlalchemy.orm import Session
import models
import schema
from fastapi import HTTPException

# Create Post
def create_post(db: Session, post: schema.PostCreate, owner_id: int):
    db_post = models.Post(**post.dict(), owner_id=owner_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

# Read All Posts
def get_posts(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Post).offset(skip).limit(limit).all()

# Read a Single Post
def get_post(db: Session, post_id: int):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

# Update Post
def update_post(db: Session, post_id: int, post_data: schema.PostCreate):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    for key, value in post_data.dict().items():
        setattr(db_post, key, value)
    db.commit()
    db.refresh(db_post)
    return db_post

# Delete Post
def delete_post(db: Session, post_id: int):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(db_post)
    db.commit()
    return {"message": "Post deleted successfully"}
