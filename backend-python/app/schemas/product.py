from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, model_serializer


class ProductCreate(BaseModel):
    nombre: str
    precio: float = Field(gt=0)
    descripcion: str = ""
    imagen: Optional[str] = None


class ProductUpdate(BaseModel):
    nombre: Optional[str] = None
    precio: Optional[float] = Field(default=None, gt=0)
    descripcion: Optional[str] = None
    comprador: Optional[str] = None
    estado_venta: Optional[str] = None
    fecha_venta: Optional[datetime] = None


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    precio: float
    vendedor: str
    comprador: Optional[str] = None
    descripcion: str
    estado_venta: str
    fecha_venta: Optional[datetime] = None
    imagen: Optional[str] = None

    @model_serializer
    def serialize(self) -> dict:
        return {
            "_id": str(self.id),
            "nombre": self.nombre,
            "precio": self.precio,
            "vendedor": self.vendedor,
            "comprador": self.comprador,
            "descripcion": self.descripcion,
            "estado_venta": self.estado_venta,
            "fecha_venta": self.fecha_venta.isoformat() if self.fecha_venta else None,
            "imagen": self.imagen,
        }
