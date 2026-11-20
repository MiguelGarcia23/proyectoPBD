from fastapi import APIRouter, HTTPException, Query
from pymongo.errors import DuplicateKeyError

from app.db.mongo_db import get_db
from app.models.producto import Categoria, Genero, Producto, ProductoCrear
from app.utils.utils import a_object_id, doc_a_dict

router = APIRouter(prefix="/productos", tags=["Prendas"])

@router.get("", response_model=list[Producto])
def listar_productos(
    categoria: Categoria | None = None,
    genero: Genero | None = Query(None, description="'mujer' u 'hombre' incluyen también las prendas unisex"),
    q: str | None = Query(None, description="Texto a buscar en nombre y descripción"),
    talla: str | None = None,
    precio_max: float | None = Query(None, gt=0),
    solo_disponibles: bool = Query(False, description="Solo prendas (o tallas) con stock"),
    limite: int = Query(20, ge=1, le=100),
    saltar: int = Query(0, ge=0, description="Para paginar: número de prendas a saltar"),
):
    """Catálogo con filtros"""
    filtro: dict = {}
    if categoria:
        filtro["categoria"] = categoria
    if genero:
        filtro["genero"] = genero if genero == "unisex" else {"$in": [genero, "unisex"]}
    if precio_max is not None:
        filtro["precio"] = {"$lte": precio_max}
    if talla and solo_disponibles:
        # $elemMatch: la MISMA variante debe tener esa talla y stock > 0
        filtro["variantes"] = {"$elemMatch": {"talla": talla, "stock": {"$gt": 0}}}
    elif talla:
        filtro["variantes.talla"] = talla
    elif solo_disponibles:
        filtro["variantes.stock"] = {"$gt": 0}

    productos = get_db().productos
    if q:
        # Búsqueda con el índice de texto, ordenada por relevancia
        filtro["$text"] = {"$search": q}
        cursor = (productos.find(filtro, {"score": {"$meta": "textScore"}})
                  .sort([("score", {"$meta": "textScore"})]))
    else:
        cursor = productos.find(filtro).sort("nombre", 1)

    return [doc_a_dict(d) for d in cursor.skip(saltar).limit(limite)]

@router.get("/{producto_id}", response_model=Producto)
def obtener_producto(producto_id: str):
    """Ficha completa de una prenda con todas sus variantes."""
    doc = get_db().productos.find_one({"_id": a_object_id(producto_id)})
    if doc is None:
        raise HTTPException(status_code=404, detail="Prenda no encontrada")
    return doc_a_dict(doc)

@router.post("", response_model=Producto, status_code=201)
def crear_producto(producto: ProductoCrear):
    """Da de alta una prenda nueva"""
    doc = producto.model_dump()
    try:
        resultado = get_db().productos.insert_one(doc)
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Ya existe una variante con alguno de esos SKU")
    doc["_id"] = resultado.inserted_id
    return doc_a_dict(doc)