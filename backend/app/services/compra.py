"""
Operación combinada: REALIZAR UNA COMPRA.

  1. MongoDB   -> comprobar y descontar stock de cada variante + guardar el pedido
  2. Cassandra -> registrar la venta y actualizar los contadores de métricas
  3. Neo4j     -> relaciones (Usuario)-[:COMPRO]->(Producto)
"""
import logging
from collections import OrderedDict
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException

from app.db.cassandra_db import get_session, preparada
from app.db.mongo_db import get_db
from app.models.pedido import PedidoCrear
from app.services import grafo
from app.utils.utils import a_object_id, doc_a_dict

log = logging.getLogger("tienda")

def realizar_compra(datos: PedidoCrear, fecha: datetime | None = None) -> dict:
    """Realiza la compra. `fecha` para los datos iniciales"""
    db = get_db()

    # ---------- Validaciones previas ----------
    usuario = db.usuarios.find_one({"_id": a_object_id(datos.usuario_id)})
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Si el mismo SKU viene en varias líneas, se juntan en una
    pedidas: OrderedDict[tuple, int] = OrderedDict()
    for l in datos.lineas:
        clave = (l.producto_id, l.sku)
        pedidas[clave] = pedidas.get(clave, 0) + l.cantidad

    # ---------- 1. MongoDB: descontar stock y guardar el pedido ----------
    descontadas = []   # para poder deshacer si algo falla a mitad
    lineas = []
    try:
        for (producto_id, sku), cantidad in pedidas.items():
            oid = a_object_id(producto_id)
            producto = db.productos.find_one({"_id": oid, "variantes.sku": sku})
            if producto is None:
                raise HTTPException(status_code=404,
                                    detail=f"No existe la variante {sku} de la prenda {producto_id}")
            variante = next(v for v in producto["variantes"] if v["sku"] == sku)

            resultado = db.productos.update_one(
                {"_id": oid, "variantes": {"$elemMatch": {"sku": sku, "stock": {"$gte": cantidad}}}},
                {"$inc": {"variantes.$.stock": -cantidad}},
            )
            if resultado.modified_count == 0:
                raise HTTPException(
                    status_code=409,
                    detail=(f"No hay stock suficiente de '{producto['nombre']}' "
                            f"talla {variante['talla']} color {variante['color']}"),
                )
            descontadas.append((oid, sku, cantidad))
            lineas.append({
                "producto_id": producto_id,
                "sku": sku,
                "nombre": producto["nombre"],
                "categoria": producto["categoria"],
                "talla": variante["talla"],
                "color": variante["color"],
                "precio_unitario": producto["precio"],  # precio de MongoDB, no del cliente
                "cantidad": cantidad,
            })

        pedido = {
            "usuario_id": datos.usuario_id,
            "fecha": fecha or datetime.now(timezone.utc),
            "estado": "pagado",
            "lineas": lineas,
            "total": round(sum(l["precio_unitario"] * l["cantidad"] for l in lineas), 2),
        }
        pedido["_id"] = db.pedidos.insert_one(pedido).inserted_id

    except Exception:
        # COMPENSACIÓN: devolver el stock ya descontado antes del fallo
        for oid, sku, cantidad in descontadas:
            db.productos.update_one({"_id": oid, "variantes.sku": sku},
                                    {"$inc": {"variantes.$.stock": cantidad}})
        raise

    resultado = doc_a_dict(pedido)
    resultado["sincronizacion"] = {"mongodb": "ok"}

    # ---------- 2. Cassandra: métricas ----------
    try:
        _registrar_en_cassandra(resultado)
        resultado["sincronizacion"]["cassandra"] = "ok"
    except Exception as e:
        log.warning("Compra %s: fallo al escribir en Cassandra: %s", resultado["id"], e)
        resultado["sincronizacion"]["cassandra"] = "error"

    # ---------- 3. Neo4j: relaciones de compra ----------
    try:
        grafo.registrar_compra(datos.usuario_id, usuario["nombre"], lineas)
        resultado["sincronizacion"]["neo4j"] = "ok"
    except Exception as e:
        log.warning("Compra %s: fallo al escribir en Neo4j: %s", resultado["id"], e)
        resultado["sincronizacion"]["neo4j"] = "error"

    return resultado

def _registrar_en_cassandra(pedido: dict) -> None:
    """Escribe la venta en las 4 tablas de métricas (una por consulta)"""
    s = get_session()
    momento = pedido["fecha"]
    dia = momento.date()
    mes = momento.strftime("%Y-%m")
    total_centimos = round(pedido["total"] * 100)

    # Resumen del día: 1 pedido más y su importe (una vez por pedido)
    s.execute(preparada(
        "UPDATE resumen_ventas_dia SET num_pedidos = num_pedidos + 1, "
        "importe_centimos = importe_centimos + ? WHERE mes = ? AND dia = ?"),
        (total_centimos, mes, dia))

    for l in pedido["lineas"]:
        importe = l["precio_unitario"] * l["cantidad"]
        centimos = round(importe * 100)

        # Detalle de la venta
        s.execute(preparada(
            "INSERT INTO ventas_por_dia (dia, momento, pedido_id, producto_id, sku, talla, "
            "color, usuario_id, cantidad, importe) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"),
            (dia, momento, pedido["id"], l["producto_id"], l["sku"], l["talla"], l["color"],
             pedido["usuario_id"], l["cantidad"], Decimal(str(round(importe, 2)))))

        # Ranking de prendas del mes
        s.execute(preparada(
            "UPDATE ventas_producto_mes SET unidades = unidades + ?, "
            "importe_centimos = importe_centimos + ? WHERE mes = ? AND producto_id = ?"),
            (l["cantidad"], centimos, mes, l["producto_id"]))

        # Tallas más vendidas por categoría
        s.execute(preparada(
            "UPDATE ventas_talla_mes SET unidades = unidades + ? "
            "WHERE mes = ? AND categoria = ? AND talla = ?"),
            (l["cantidad"], mes, l["categoria"], l["talla"]))