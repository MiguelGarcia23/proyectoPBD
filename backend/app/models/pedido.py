from datetime import datetime

from pydantic import BaseModel, Field

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

class LineaCompra(BaseModel):
    """Lo que el cliente pide"""
    producto_id: str
    sku: str
    cantidad: int = Field(ge=1, le=20)

class PedidoCrear(BaseModel):
    """Datos que envía el front para realizar una compra"""
    usuario_id: str
    lineas: list[LineaCompra] = Field(min_length=1)

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "usuario_id": "ID_DE_UN_USUARIO",
                "lineas": [
                    {"producto_id": "ID_DE_UNA_PRENDA", "sku": "CAM-BAS-BLA-M", "cantidad": 2}
                ],
            }]
        }
    }

class PedidoCompra(Pedido):
    """Respuesta de la compra: el pedido más el resultado en cada base de datos"""
    sincronizacion: dict[str, str]