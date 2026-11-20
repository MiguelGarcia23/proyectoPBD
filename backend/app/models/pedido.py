from datetime import datetime

from pydantic import BaseModel

class LineaPedido(BaseModel):
    producto_id: str
    sku: str
    nombre: str
    talla: str
    color: str
    precio_unitario: float
    cantidad: int

class Pedido(BaseModel):
    id: str
    usuario_id: str
    fecha: datetime
    estado: str
    lineas: list[LineaPedido]
    total: float