from datetime import datetime, timezone
import bcrypt
from jose import JWTError, jwt
from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..config import settings
from ..repositories.user_repository import user_repository


class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode(), hashed.encode())

    @staticmethod
    def create_token(user) -> str:
        payload = {
            "userId": str(user.id),
            "username": user.username,
            "role": user.role,
            "exp": int(
                (
                    datetime.now(timezone.utc).timestamp()
                    + settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
                )
            ),
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> dict | None:
        try:
            return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except JWTError:
            return None

    @staticmethod
    def register(db: Session, username: str, password: str):
        if user_repository.get_by_username(db, username):
            raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")
        hashed = AuthService.hash_password(password)
        user = user_repository.create(db, username, hashed, "user")
        token = AuthService.create_token(user)
        return token, user

    @staticmethod
    def login(db: Session, username: str, password: str):
        user = user_repository.get_by_username(db, username)
        if not user or not AuthService.verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        token = AuthService.create_token(user)
        return token, user
