from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto"
)

class Hasher:
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        password = password[:72]
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        plain_password = plain_password[:72]
        return pwd_context.verify(plain_password, hashed_password)
    
    
        