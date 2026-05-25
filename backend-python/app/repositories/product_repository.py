from typing import Optional
from sqlalchemy.orm import Session
from ..models.product import Producto


class ProductRepository:
    def get_all(self, db: Session, name_filter: Optional[str] = None) -> list[Producto]:
        query = db.query(Producto)
        if name_filter:
            query = query.filter(Producto.nombre.ilike(f"%{name_filter}%"))
        return query.all()

    def get_by_id(self, db: Session, product_id: int) -> Producto | None:
        return db.query(Producto).filter(Producto.id == product_id).first()

    def create(self, db: Session, **kwargs) -> Producto:
        product = Producto(**kwargs)
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    def update(self, db: Session, product: Producto, **kwargs) -> Producto:
        for key, value in kwargs.items():
            setattr(product, key, value)
        db.commit()
        db.refresh(product)
        return product

    def delete(self, db: Session, product: Producto) -> None:
        db.delete(product)
        db.commit()


product_repository = ProductRepository()
