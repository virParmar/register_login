from typing import Optional
from pydantic import BaseModel, EmailStr
from enums import UserRole, UserStatus

# User Register
class UserBase(BaseModel):
    username: str
    email: EmailStr
    
class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    username: Optional[str] = None

class UserRegisterResponse(BaseModel):
    id: int
    username: str
    message: str
    email: EmailStr
    role: UserRole
    status: UserStatus
    
    class Config:
        # orm_mode = True
        from_attributes = True
   
# User Login 
class UserLoginBase(BaseModel):
    username: str
    password: str
    
class UserLoginCreate(UserLoginBase):
    pass

class UserLoginUpdate(UserLoginBase):
    pass

class UserLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    id: int
    username: str
    email: EmailStr
    role: UserRole
    status: UserStatus
    message: str
    
    class Config:
        # orm_mode = True
        from_attributes = True
        
# Get access token using refresh token
class GetAccessTokenResponse(BaseModel):
    access_token: str
    
    class Config:
        from_attributes = True

# User logout
class UserLogoutResponse(BaseModel):
    message: str
    
    class Config:
        from_attributes = True