import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.database import Base, SessionLocal, engine
from app.models import user, product, cart  # noqa: F401 — register models
from app.models.user import User
from app.services.auth_service import AuthService

Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    if not db.query(User).filter(User.username == "admin").first():
        db.add(User(
            username="admin",
            password=AuthService.hash_password("admin123"),
            role="admin",
        ))
        print("[OK] Usuario admin creado (admin / admin123)")
    else:
        print("[--] Usuario admin ya existe")

    if not db.query(User).filter(User.username == "user").first():
        db.add(User(
            username="user",
            password=AuthService.hash_password("user123"),
            role="user",
        ))
        print("[OK] Usuario user creado (user / user123)")
    else:
        print("[--] Usuario user ya existe")

    db.commit()
    print("[OK] Seed completado")
finally:
    db.close()
