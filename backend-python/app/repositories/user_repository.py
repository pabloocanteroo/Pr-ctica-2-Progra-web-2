from sqlalchemy.orm import Session
from ..models.user import User


class UserRepository:
    def get_by_id(self, db: Session, user_id: int) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, db: Session, username: str) -> User | None:
        return db.query(User).filter(User.username == username).first()

    def get_all(self, db: Session) -> list[User]:
        return db.query(User).all()

    def create(self, db: Session, username: str, password_hash: str, role: str = "user") -> User:
        user = User(username=username, password=password_hash, role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update(self, db: Session, user: User, **kwargs) -> User:
        for key, value in kwargs.items():
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return user

    def delete(self, db: Session, user: User) -> None:
        db.delete(user)
        db.commit()


user_repository = UserRepository()
