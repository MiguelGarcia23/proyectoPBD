from fastapi import APIRouter, HTTPException, Query

from app.db.mongo_db import get_db
from app.models.pedido import Pedido, PedidoCompra, PedidoCrear
from app.services.compra import realizar_compra
from app.utils.utils import a_object_id, doc_a_dict

router = APIRouter()
TAG_PEDIDOS = ["Pedidos"]

@router.post("/pedidos", response_model=PedidoCompra, status_code=201, tags=["Compra"])
def comprar(datos: PedidoCrear):
    """Operación combinada de las tres bases de datos.

    1. MongoDB: descuenta el stock de cada variante (solo si hay suficiente) y guarda el pedido.
    2. Cassandra: registra la venta y actualiza las métricas.
    3. Neo4j: crea o actualiza las relaciones COMPRO.
    """
    return realizar_compra(datos)

@router.get("/pedidos/{pedido_id}", response_model=Pedido, tags=TAG_PEDIDOS)
def obtener_pedido(pedido_id: str):
    doc = get_db().pedidos.find_one({"_id": a_object_id(pedido_id)})
    if doc is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return doc_a_dict(doc)

@router.get("/usuarios/{usuario_id}/pedidos", response_model=list[Pedido], tags=TAG_PEDIDOS)
def pedidos_de_usuario(usuario_id: str, limite: int = Query(20, ge=1, le=100)):
    """'Mis pedidos': los pedidos de un usuario, el más reciente primero.
    Usa el índice (usuario_id, fecha) creado en mongo/init.js."""
    a_object_id(usuario_id)  # valida el formato del id
    cursor = (get_db().pedidos.find({"usuario_id": usuario_id})
              .sort("fecha", -1).limit(limite))
    return [doc_a_dict(d) for d in cursor]