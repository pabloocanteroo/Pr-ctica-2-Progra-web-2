from datetime import datetime, timezone
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..models.cart import Cart
from ..repositories.product_repository import product_repository
from ..schemas.product import ProductOut


class ProductService:
    def get_all(self, db: Session, name_filter: Optional[str] = None):
        return product_repository.get_all(db, name_filter)

    def create(self, db: Session, data: dict):
        return product_repository.create(db, **data)

    def update(self, db: Session, product_id: int, data: dict):
        product = product_repository.get_by_id(db, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return product_repository.update(db, product, **data)

    def delete(self, db: Session, product_id: int) -> None:
        product = product_repository.get_by_id(db, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        db.query(Cart).filter(Cart.product_id == product_id).delete()
        db.commit()
        product_repository.delete(db, product)

    def get_cart(self, db: Session, user_id: int) -> dict:
        items = db.query(Cart).filter(Cart.user_id == user_id).all()
        return {"items": [ProductOut.model_validate(item.product) for item in items]}

    def add_to_cart(self, db: Session, user_id: int, product_id: int) -> dict:
        if not product_repository.get_by_id(db, product_id):
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        exists = (
            db.query(Cart)
            .filter(Cart.user_id == user_id, Cart.product_id == product_id)
            .first()
        )
        if exists:
            raise HTTPException(status_code=400, detail="El producto ya está en el carrito")
        db.add(Cart(user_id=user_id, product_id=product_id))
        db.commit()
        return self.get_cart(db, user_id)

    def remove_from_cart(self, db: Session, user_id: int, product_id: int) -> dict:
        item = (
            db.query(Cart)
            .filter(Cart.user_id == user_id, Cart.product_id == product_id)
            .first()
        )
        if item:
            db.delete(item)
            db.commit()
        return self.get_cart(db, user_id)

    def checkout(self, db: Session, user_id: int, username: str) -> dict:
        items = db.query(Cart).filter(Cart.user_id == user_id).all()
        if not items:
            raise HTTPException(status_code=400, detail="El carrito está vacío")
        now = datetime.now(timezone.utc)
        for item in items:
            product = item.product
            if product.estado_venta == "vendido":
                raise HTTPException(
                    status_code=400,
                    detail=f"El producto '{product.nombre}' ya ha sido vendido",
                )
            product.estado_venta = "vendido"
            product.comprador = username
            product.fecha_venta = now
            db.add(product)
        db.query(Cart).filter(Cart.user_id == user_id).delete()
        db.commit()
        return {"message": "Compra realizada con éxito"}


product_service = ProductService()
