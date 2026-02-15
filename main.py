from fastapi import FastAPI, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from jwt_handler import create_access_token, create_refresh_token
import models
import schemas
import crud
from hasher import Hasher
from database import engine, SessionLocal
from enums import UserStatus
from datetime import datetime, timezone

models.Base.metadata.create_all(bind = engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@app.post("/auth/register", response_model=schemas.UserRegisterResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.register_user(db, user)
    return {
        "message": "User regiestered successfully :)",
        "role": db_user.role,
        "status": db_user.status,
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email
    }
    
@app.post("/auth/login", response_model=schemas.UserLoginResponse)
def login_user(user_data: schemas.UserLoginCreate, db: Session = Depends(get_db)):
    
    user = db.query(models.UserRegister).filter(
        models.UserRegister.username == user_data.username
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username or password"
        )
        
    if not Hasher.verify_password(user_data.password,user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username or password"
        )
        
    # create JWT Token
    access_token = create_access_token(
        data={"sub": user.username}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username}
    )
    crud.store_token(db, user, access_token, refresh_token)
        
    return {
        "access_token" : access_token,
        "refresh_token" : refresh_token,
        "token_type" : "bearer",
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "status": user.status,
        "message" : "User loggedin successfully :)"
    }
    
@app.post("/auth/logout", response_model=schemas.UserLogoutResponse)
def logout_user(token: str, db: Session = Depends(get_db)):
    
    # Check Bearer token format
    # if not authorization.startswith("Bearer "):
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Invalid authorization header format"
    #     )
        
    # Extract token
    # token = authorization.replace("Bearer ", "")
    
    result  = crud.suspend_token(db, token)

    # Token not found
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token!!"
        )
    
    # Already logged out    
    if result == "already_logged_out":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already logged out!!"
        )
        
    # Token expired
    if result == "expired":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
        
    # success response
    return {
        "message": "User logged out successfully :)",     
    }
    
@app.post("/auth/refresh", response_model=schemas.GetAccessTokenResponse)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    
    db_token = db.query(models.UserLogin).filter(
        models.UserLogin.refresh_token == refresh_token
        ).first()
    
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token!!"
        )
        
    db_expire = db_token.refresh_token_expiration_date

    # Convert DB time to UTC if naive
    if db_expire.tzinfo is None:
        db_expire = db_expire.replace(tzinfo=timezone.utc)

    current_time = datetime.now(timezone.utc)

    if db_expire < current_time:
        raise HTTPException(
            status_code=401,
            detail="Refresh token expired"
        )
        
    db_user = db.query(models.UserRegister).filter(
        models.UserRegister.id == db_token.user_id
        ).first()
        
    new_access_token = create_access_token(
        data={"sub": db_user.username}
    )
    
    db_token.access_token = new_access_token
    db.commit()
    
    return {
        "access_token": new_access_token
    }
        