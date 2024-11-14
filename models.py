from sqlalchemy import Column, Integer, String, ForeignKey,Table,DateTime
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.sql import func

# many to many Relationship 
like_table = Table(
    'likes', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('post_id', Integer, ForeignKey('posts.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="reader")  
    posts = relationship("Post", back_populates="owner")
    comments = relationship("Comment", back_populates="user")
    liked_posts = relationship("Post", secondary=like_table, back_populates="likes")
    
class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("User", secondary=like_table, back_populates="liked_posts")  # Many-to-many for likes

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    post_id = Column(Integer, ForeignKey("posts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    post = relationship("Post", back_populates="comments")
    user = relationship("User", back_populates="comments")
