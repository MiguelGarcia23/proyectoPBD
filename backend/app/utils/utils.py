from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException

from app.db.mongo_db import get_db

def a_object_id(id: str) -> ObjectId:
    """Convierte el id de texto que llega en la URL al ObjectId de MongoDB. Si no tiene el formato correcto devuelve un error 400"""
    try:
        return ObjectId(id)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=400, detail=f"Id no válido: {id}")

def doc_a_dict(doc: dict | None) -> dict | None:
    """Cambia '_id' (ObjectId) por 'id' (texto)"""
    if doc is None:
        return None
    d = dict(doc)
    d["id"] = str(d.pop("_id"))
    return d

def completar_prendas(ids: list[str]) -> dict[str, dict]:
    """Busca en MongoDB, en UNA sola consulta, los datos de varias prendas para Cassandra y Neo4j"""
    oids = [ObjectId(i) for i in ids if ObjectId.is_valid(i)]
    if not oids:
        return {}
    cursor = get_db().productos.find(
        {"_id": {"$in": oids}},
        {"nombre": 1, "precio": 1, "imagen": 1, "categoria": 1, "variantes": 1},
    )
    resultado = {}
    for d in cursor:
        # tallas con stock, sin repetir y en el orden en que están guardadas
        tallas = list(dict.fromkeys(
            v["talla"] for v in d.get("variantes", []) if v.get("stock", 0) > 0
        ))
        resultado[str(d["_id"])] = {
            "nombre": d.get("nombre"),
            "precio": d.get("precio"),
            "imagen": d.get("imagen"),
            "categoria": d.get("categoria"),
            "tallas_disponibles": tallas,
        }
    return resultado