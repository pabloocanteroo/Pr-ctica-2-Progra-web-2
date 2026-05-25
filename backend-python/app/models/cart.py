from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from ..database import Base


class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("productos.id"), nullable=False)

    user = relationship("User", back_populates="cart_items")
    product = relationship("Producto")
