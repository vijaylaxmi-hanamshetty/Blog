from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Base model for Post
class PostBase(BaseModel):
    title: str
    content: str
    

# Model for creating a Post, with optional category and tags
class PostCreate(PostBase):
    category: Optional[str] = None
    tags: Optional[str] = None
    image_path:Optional[str]=None
    
# Response model for Post, including additional fields for retrieval
class Post(PostBase):
    id: int
    owner_id: int
    comments: List["Comment"] = []  
    likes_count: int = 0
    created_at: datetime

    class Config:
        orm_mode = True
class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    
    category: Optional[str] = None
    tags: Optional[str] = None
# Base model for User
class UserBase(BaseModel):
    username: str
    role: str

# Model for creating a User
class UserCreate(UserBase):
    password: str

# Response model for User, including posts list
class User(UserBase):
    id: int
    posts: List[Post] = [] 

    class Config:
        orm_mode = True

# Model for authentication token
class Token(BaseModel):
    access_token: str
    token_type: str

# Base model for Comment
class CommentBase(BaseModel):
    content: str

# Model for creating a Comment
class CommentCreate(CommentBase):
    pass

# Response model for Comment
class Comment(CommentBase):  
    id: int
    post_id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True
