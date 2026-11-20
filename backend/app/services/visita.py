"""
Operación combinada: VER UNA PRENDA.

  MongoDB   -> se lee la prenda (lo hace el endpoint)
  Cassandra -> +1 en visitas_producto_dia
  Neo4j     -> relación (Usuario)-[:VIO]->(Producto), si hay usuario
"""
import logging
from datetime import datetime, timezone

from bson import ObjectId

from app.db.cassandra_db import get_session, preparada
from app.db.mongo_db import get_db
from app.services import grafo

log = logging.getLogger("tienda")

def registrar_visita(producto: dict, usuario_id: str | None) -> None:
    producto_id = producto["id"]
    hoy = datetime.now(timezone.utc).date()

    # Cassandra: contador de visitas del día
    try:
        get_session().execute(
            preparada("UPDATE visitas_producto_dia SET visitas = visitas + 1 "
                      "WHERE producto_id = ? AND dia = ?"),
            (producto_id, hoy),
        )
    except Exception as e:
        log.warning("No se pudo registrar la visita en Cassandra: %s", e)

    # Neo4j: relación VIO (solo si sabemos quién es el usuario)
    if not usuario_id or not ObjectId.is_valid(usuario_id):
        return
    usuario = get_db().usuarios.find_one({"_id": ObjectId(usuario_id)}, {"nombre": 1})
    if usuario is None:
        return
    try:
        grafo.registrar_visita(usuario_id, usuario["nombre"], producto_id,
                               producto["nombre"], producto["categoria"])
    except Exception as e:
        log.warning("No se pudo registrar la visita en Neo4j: %s", e)