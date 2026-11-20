import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query
from pymongo.errors import DuplicateKeyError

from app.db.mongo_db import get_db
from app.models.usuario import Usuario, UsuarioCrear
from app.services import grafo
from app.utils.utils import a_object_id, doc_a_dict

log = logging.getLogger("tienda")

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.get("", response_model=list[Usuario])
def listar_usuarios(limite: int = Query(20, ge=1, le=100)):
    cursor = get_db().usuarios.find().sort("nombre", 1).limit(limite)
    return [doc_a_dict(d) for d in cursor]

@router.get("/{usuario_id}", response_model=Usuario)
def obtener_usuario(usuario_id: str):
    doc = get_db().usuarios.find_one({"_id": a_object_id(usuario_id)})
    if doc is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return doc_a_dict(doc)

@router.post("", response_model=Usuario, status_code=201)
def crear_usuario(usuario: UsuarioCrear):
    """Registra un usuario en MongoDB y crea su nodo en Neo4j"""
    doc = usuario.model_dump()
    doc["fecha_alta"] = datetime.now(timezone.utc)
    try:
        resultado = get_db().usuarios.insert_one(doc)
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Ya existe un usuario con ese email")
    doc["_id"] = resultado.inserted_id
    nuevo = doc_a_dict(doc)

    try:
        grafo.guardar_usuario(nuevo["id"], nuevo["nombre"])
    except Exception as e:
        log.warning("Usuario %s creado pero no se pudo crear el nodo en Neo4j: %s", nuevo["id"], e)
    return nuevo