from datetime import date, timedelta, timezone
from functools import lru_cache

from fastapi import APIRouter, Path, Query

from app.db.cassandra_db import get_session
from app.models.producto import Categoria
from app.utils.utils import completar_prendas

router = APIRouter(prefix="/metricas", tags=["Métricas"])

PATRON_MES = r"^\d{4}-(0[1-9]|1[0-2])$"

@lru_cache(maxsize=None)
def _preparada(cql: str):
    """Sentencias preparadas"""
    return get_session().prepare(cql)

@router.get("/visitas/{producto_id}")
def visitas_producto(producto_id: str, dias: int = Query(7, ge=1, le=90)):
    """Visitas de una prenda en los últimos X días"""
    fecha_inicio = date.today() - timedelta(days=dias - 1)
    filas = get_session().execute(
        _preparada("SELECT dia, visitas FROM visitas_producto_dia "
                   "WHERE producto_id = ? AND dia >= ?"),
        (producto_id, fecha_inicio),
    )
    resumen_por_dia = [{"dia": str(f.dia), "visitas": f.visitas} for f in filas]
    return {
        "producto_id": producto_id,
        "dias": dias,
        "total_visitas": sum(d["visitas"] for d in resumen_por_dia),
        "resumen_por_dia": resumen_por_dia,
    }

@router.get("/ventas/dia/{fecha}")
def ventas_del_dia(fecha: date):
    """Detalle de las ventas de un día, la más reciente primero."""
    filas = get_session().execute(
        _preparada("SELECT momento, pedido_id, producto_id, sku, talla, color, "
                   "usuario_id, cantidad, importe FROM ventas_por_dia WHERE dia = ?"),
        (fecha,),
    )
    ventas = [{
        "momento": f.momento.replace(tzinfo=timezone.utc), "pedido_id": f.pedido_id, "producto_id": f.producto_id,
        "sku": f.sku, "talla": f.talla, "color": f.color, "usuario_id": f.usuario_id,
        "cantidad": f.cantidad, "importe": float(f.importe or 0),
    } for f in filas]
    return {
        "dia": str(fecha),
        "unidades": sum(v["cantidad"] for v in ventas),
        "importe_total": round(sum(v["importe"] for v in ventas), 2),
        "ventas": ventas,
    }

@router.get("/ventas/mes/{mes}")
def ventas_del_mes(mes: str = Path(pattern=PATRON_MES, examples=["2026-11"])):
    """Resumen diario de pedidos y total en un mes"""
    filas = get_session().execute(
        _preparada("SELECT dia, num_pedidos, importe_centimos FROM resumen_ventas_dia WHERE mes = ?"),
        (mes,),
    )
    resumen_por_dia = [{
        "dia": str(f.dia),
        "pedidos": f.num_pedidos or 0,
        "importe": (f.importe_centimos or 0) / 100,  # se guarda en céntimos
    } for f in filas]
    return {
        "mes": mes,
        "total_pedidos": sum(d["pedidos"] for d in resumen_por_dia),
        "importe_total": round(sum(d["importe"] for d in resumen_por_dia), 2),
        "resumen_por_dia": resumen_por_dia,
    }

@router.get("/ranking/{mes}")
def prendas_mas_vendidas(
    mes: str = Path(pattern=PATRON_MES, examples=["2026-11"]),
    limite: int = Query(10, ge=1, le=50),
):
    """Prendas más vendidas del mes"""
    filas = get_session().execute(
        _preparada("SELECT producto_id, unidades, importe_centimos FROM ventas_producto_mes WHERE mes = ?"),
        (mes,),
    )
    ranking = sorted(
        ({"producto_id": f.producto_id, "unidades": f.unidades or 0,
          "importe": (f.importe_centimos or 0) / 100} for f in filas),
        key=lambda x: x["unidades"], reverse=True,
    )[:limite]

    datos = completar_prendas([r["producto_id"] for r in ranking])
    for posicion, r in enumerate(ranking, start=1):
        r["posicion"] = posicion
        r["nombre"] = datos.get(r["producto_id"], {}).get("nombre")
    return {"mes": mes, "ranking": ranking}

@router.get("/tallas/{mes}/{categoria}")
def tallas_mas_vendidas(
    categoria: Categoria,
    mes: str = Path(pattern=PATRON_MES, examples=["2026-11"]),
):
    """Unidades vendidas por talla de una categoría en un mes para reponer stock"""
    filas = get_session().execute(
        _preparada("SELECT talla, unidades FROM ventas_talla_mes WHERE mes = ? AND categoria = ?"),
        (mes, categoria),
    )
    tallas = sorted(({"talla": f.talla, "unidades": f.unidades or 0} for f in filas),
                    key=lambda x: x["unidades"], reverse=True)
    return {"mes": mes, "categoria": categoria, "tallas": tallas}