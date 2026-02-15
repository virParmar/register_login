from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from jwt_handler import ALGORITHM, SECRET_KEY
import schemas
import models
from hasher import Hasher
from enums import UserRole, UserStatus
from datetime import datetime, timedelta, timezone
from jose import jwt


def register_user(db: Session, user: schemas.UserCreate):
    
    existing_user = (
        db.query(models.UserRegister)
        .filter(models.UserRegister.username == user.username)
        .first()
    )
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered!"
        )
        
    existing_user = db.query(models.UserRegister).filter(
        models.UserRegister.email == user.email
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered!"
        )
    # Hash password
    hashed_password = Hasher.get_password_hash(user.password)

    # Create user object
    db_user = models.UserRegister(
        username=user.username,
        email=user.email,
        password=hashed_password,
        role=UserRole.user,
        status=UserStatus.active
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

def store_token(db: Session, user: models.UserRegister, new_access_token: str, new_refresh_token: str):
    
    # decode token to get payload
    access_token_payload = jwt.decode(
        new_access_token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
        options={"verify_exp": False} # Don't fail if expired
    )
    refresh_token_payload = jwt.decode(
        new_refresh_token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
        options={"verify_exp": False} # Don't fail if expired
    )
    
    access_token_exp_timestamp = access_token_payload.get("exp")
    refresh_token_exp_timestamp = refresh_token_payload.get("exp")
    
    access_token_expire_time = datetime.fromtimestamp(
        access_token_exp_timestamp,
        tz=timezone.utc
    )
    refresh_token_expire_time = datetime.fromtimestamp(
        refresh_token_exp_timestamp,
        tz=timezone.utc
    )
    
    db_token = models.UserLogin(
        user_id = user.id,
        access_token = new_access_token,
        refresh_token = new_refresh_token,
        status = UserStatus.active,
        created_at = datetime.now(timezone.utc),
        access_token_expiration_date = access_token_expire_time,
        refresh_token_expiration_date = refresh_token_expire_time
    )
    
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    
def suspend_token(db: Session, token: str):
    
    db_user_login = (
        db.query(models.UserLogin)
        .filter(models.UserLogin.token == token)
        .first()
    )
    
    # token not found
    if not db_user_login:
        return None
    
    # already logged out
    if db_user_login.status == UserStatus.suspended :
        return "already_logged_out"
    
    # logout (suspend token)
    db_user_login.status = UserStatus.suspended
    db.commit()
    
    # get user
    db_user = (
        db.query(models.UserRegister)
        .filter(models.UserRegister.id == db_user_login.user_id)
        .first()
    )
    
    return db_user