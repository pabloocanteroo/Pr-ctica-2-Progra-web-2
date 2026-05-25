from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..dependencies import get_current_user, get_db
from ..models.user import User
from ..schemas.product import ProductOut
from ..services.product_service import product_service

router = APIRouter()


class AddToCartBody(BaseModel):
    productoId: str


def _cart_response(cart: dict) -> dict:
    return {"items": [jsonable_encoder(ProductOut.model_validate(p)) for p in cart["items"]]}


@router.get("/cart")
def get_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart = product_service.get_cart(db, current_user.id)
    return JSONResponse(_cart_response(cart))


@router.post("/cart/add")
def add_to_cart(
    body: AddToCartBody,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cart = product_service.add_to_cart(db, current_user.id, int(body.productoId))
    return JSONResponse(_cart_response(cart))


@router.post("/cart/checkout")
def checkout(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return product_service.checkout(db, current_user.id, current_user.username)


@router.delete("/cart/{product_id}")
def remove_from_cart(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cart = product_service.remove_from_cart(db, current_user.id, int(product_id))
    return JSONResponse(_cart_response(cart))
