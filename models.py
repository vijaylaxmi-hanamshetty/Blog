from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# Many-to-many relationship table between users and posts for likes
user_like_post_table = Table(
    "user_like_post",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("post_id", Integer, ForeignKey("posts.id"))
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="reader")
    likes = relationship("Like", back_populates="user")
    posts = relationship("Post", back_populates="owner")
    comments = relationship("Comment", back_populates="user")
    liked_posts = relationship("Post", secondary=user_like_post_table, back_populates="liked_by")  

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text, nullable=False)
    category = Column(String, index=True)
    image_url = Column(String,nullable=True ) 
    tags = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
    liked_by = relationship("User", secondary=user_like_post_table, back_populates="liked_posts")  # Correct relationship with User
    likes = relationship("Like", back_populates="post")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
    

class Like(Base):
    __tablename__ = 'likes'

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('posts.id'),nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"),nullable=False)
    post = relationship("Post", back_populates="likes")
    user = relationship("User", back_populates="likes")