from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..schemas.auth import LoginRequest, RegisterRequest
from ..schemas.user import UserOut
from ..services.auth_service import AuthService

router = APIRouter()


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    token, user = AuthService.login(db, data.username, data.password)
    user_out = jsonable_encoder(UserOut.model_validate(user))
    return JSONResponse({"token": token, "user": user_out})


@router.post("/register", status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    token, user = AuthService.register(db, data.username, data.password)
    user_out = jsonable_encoder(UserOut.model_validate(user))
    return JSONResponse({"token": token, "user": user_out}, status_code=201)
