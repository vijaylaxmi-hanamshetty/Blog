from pydantic import BaseModel
from typing import List, Optional

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    owner_id: int
    
    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str
    role:str
class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    posts: List[Post] = []

    class Config:
        orm_mode = True
        
class Token(BaseModel):
    access_token: str
    token_type: str

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    post_id: int
    user_id: int

    class Config:
        orm_mode = True