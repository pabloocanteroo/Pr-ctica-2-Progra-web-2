import time
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from ..config import settings
from ..dependencies import get_current_user, get_db
from ..models.user import User
from ..schemas.product import ProductOut, ProductUpdate
from ..services.product_service import product_service

router = APIRouter()


@router.get("/productos")
def get_products(name: Optional[str] = None, db: Session = Depends(get_db)):
    products = product_service.get_all(db, name)
    return JSONResponse([jsonable_encoder(ProductOut.model_validate(p)) for p in products])


@router.post("/productos", status_code=201)
def create_product(
    nombre: str = Form(...),
    precio: float = Form(...),
    descripcion: str = Form(""),
    imagen: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}
    filename = None
    if imagen and imagen.filename:
        suffix = imagen.filename.rsplit(".", 1)[-1].lower() if "." in imagen.filename else ""
        if suffix not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Extensión no permitida. Usa: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            )
        filename = f"{int(time.time() * 1000)}.{suffix}"
        dest = settings.UPLOADS_DIR / filename
        with open(dest, "wb") as f:
            f.write(imagen.file.read())

    data = {
        "nombre": nombre,
        "precio": precio,
        "descripcion": descripcion,
        "vendedor": current_user.username,
        "imagen": filename,
    }
    product = product_service.create(db, data)
    return JSONResponse(jsonable_encoder(ProductOut.model_validate(product)), status_code=201)


@router.put("/productos/{product_id}")
def update_product(
    product_id: str,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        pid = int(product_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de producto inválido")
    update_data = data.model_dump(exclude_none=True)
    product = product_service.update(db, pid, update_data)
    return JSONResponse(jsonable_encoder(ProductOut.model_validate(product)))


@router.delete("/productos/{product_id}")
def delete_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        pid = int(product_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de producto inválido")
    product_service.delete(db, pid)
    return JSONResponse({"message": "Producto eliminado"})
