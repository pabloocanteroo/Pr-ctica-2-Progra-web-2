from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from ..dependencies import get_db, require_admin
from ..models.user import User
from ..schemas.user import UserCreate, UserOut, UserUpdate
from ..services.user_service import user_service

router = APIRouter()


@router.get("/users")
def get_users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    users = user_service.get_all(db)
    return JSONResponse([jsonable_encoder(UserOut.model_validate(u)) for u in users])


@router.post("/users", status_code=201)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    user = user_service.create(db, data)
    user_out = jsonable_encoder(UserOut.model_validate(user))
    return JSONResponse({"message": "Usuario creado con éxito", "user": user_out}, status_code=201)


@router.put("/users/{user_id}")
def update_user(
    user_id: str,
    data: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    user = user_service.update(db, int(user_id), data)
    return JSONResponse(jsonable_encoder(UserOut.model_validate(user)))


@router.delete("/users/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    user_service.delete(db, int(user_id))
    return JSONResponse({"message": "Usuario eliminado"})
