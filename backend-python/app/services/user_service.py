from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..repositories.user_repository import user_repository
from ..schemas.user import UserCreate, UserUpdate
from .auth_service import AuthService


class UserService:
    def get_all(self, db: Session):
        return user_repository.get_all(db)

    def create(self, db: Session, data: UserCreate):
        if user_repository.get_by_username(db, data.username):
            raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")
        hashed = AuthService.hash_password(data.password)
        return user_repository.create(db, data.username, hashed, data.role)

    def update(self, db: Session, user_id: int, data: UserUpdate):
        user = user_repository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        updates = {}
        if data.username is not None:
            updates["username"] = data.username
        if data.role is not None:
            updates["role"] = data.role
        if data.password is not None:
            updates["password"] = AuthService.hash_password(data.password)
        return user_repository.update(db, user, **updates)

    def delete(self, db: Session, user_id: int) -> None:
        user = user_repository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        user_repository.delete(db, user)


user_service = UserService()
