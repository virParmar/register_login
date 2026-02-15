from sqlalchemy import Column, ForeignKey, Integer, String, Enum, TIMESTAMP, func
from database import Base
from enums import UserRole, UserStatus
from sqlalchemy.orm import relationship

class UserRegister(Base) :
    __tablename__ = "users"
    
    id = Column(Integer, primary_key = True, index = True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(
        Enum(UserRole, name="user_role_enum"),
        default=UserRole.user,
        nullable=False
    )
    status = Column(
        Enum(UserStatus, name="user_status_enum"),
        default=UserStatus.active,
        nullable=False
    )
    created_at = Column(
        TIMESTAMP, 
        server_default=func.now()
    )
    updated_at = Column(
        TIMESTAMP, 
        server_default=func.now(),
        onupdate=func.now()
    )
    user_logins = relationship(
        "UserLogin", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    
class UserLogin(Base):
    __tablename__ = "user_login"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    access_token = Column(String(255), unique=True, nullable=False)
    status = Column(
        Enum(UserStatus, name="user_status_enum"),
        default=UserStatus.active,
        nullable=False
    )
    created_at = Column(
        TIMESTAMP, 
        server_default=func.now()
    )
    expiration_date = Column(
        TIMESTAMP,
        nullable=False
    )
    user = relationship(
        "UserRegister", 
        back_populates="user_logins"
    )
    
    