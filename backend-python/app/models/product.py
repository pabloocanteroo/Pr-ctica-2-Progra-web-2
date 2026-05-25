from sqlalchemy import Column, DateTime, Float, Integer, String
from ..database import Base


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    precio = Column(Float, nullable=False)
    vendedor = Column(String, default="Admin Oficial")
    comprador = Column(String, nullable=True)
    descripcion = Column(String, default="")
    estado_venta = Column(String, default="disponible")
    fecha_venta = Column(DateTime, nullable=True)
    imagen = Column(String, nullable=True)
