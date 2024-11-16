from sqlalchemy.orm import Session
import models
import schema
from typing import List, Optional
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy import or_, and_
from sqlalchemy.orm.exc import NoResultFound
# Create User
def create_user(db: Session, user: schema.UserCreate, hashed_password: str):
    db_user = models.User(username=user.username, hashed_password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()
# Create a Post
def create_post(db: Session, post: schema.PostCreate, owner_id: int, image_url: Optional[str] = None):
    db_post = models.Post(
        title=post.title,
        content=post.content,
        category=post.category,
        tags=post.tags,
        owner_id=owner_id,
        image_url=image_url
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

# Get Posts with Optional Filtering and Pagination
def get_posts(db: Session, search: Optional[str] = None, category: Optional[str] = None, 
              tags: Optional[str] = None, page: int = 1, limit: int = 10):
    query = db.query(models.Post)
    if search:
        query = query.filter(
            (models.Post.title.ilike(f"%{search}%")) |
            (models.Post.content.ilike(f"%{search}%"))
        )
    if category:
        query = query.filter(models.Post.category == category)
    if tags:
        query = query.filter(models.Post.tags.contains(tags))
    total = query.count()
    posts = query.offset((page - 1) * limit).limit(limit).all()
    return total, posts

# Read a Single Post
def get_post(db: Session, post_id: int):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

# Update a Post
def update_post(db: Session, post_id: int, post_data: schema.PostUpdate, image_url: Optional[str] = None):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    for key, value in post_data.dict().items():
        setattr(db_post, key, value)
    db_post.image_url = image_url if image_url else db_post.image_url
    db.commit()
    db.refresh(db_post)
    return db_post

# Delete a Post
def delete_post(db: Session, post_id: int):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(db_post)
    db.commit()
    return {"message": "Post deleted successfully"}

# Create a Comment
def create_comment(db: Session, comment: schema.CommentCreate, post_id: int, user_id: int):
    db_comment = models.Comment(
        content=comment.content,
        post_id=post_id,
        user_id=user_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

# Get Comments for a Post
def get_comments(db: Session, post_id: int):
    return db.query(models.Comment).filter(models.Comment.post_id == post_id).all()

# Like a Post
def like_post(db: Session, post_id: int, user_id: int):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_post and db_user:
        db_user.liked_posts.append(db_post)  
        db.commit()
        return {"message": "Post liked"}
    raise HTTPException(status_code=404, detail="Post or User not found")

def unlike_post(db: Session, post_id: int, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_user or not db_post:
        raise HTTPException(status_code=404, detail="Post or User not found")
    if db_post in db_user.liked_posts:
        db_user.liked_posts.remove(db_post) 
        return {"message": "Like removed"}
    return {"message": "Like not found"}


