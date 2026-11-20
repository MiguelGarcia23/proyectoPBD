from fastapi import APIRouter, Query

from app.db.neo4j_db import get_driver
from app.utils.utils import completar_prendas

router = APIRouter(prefix="/recomendaciones", tags=["Recomendaciones"])

LIMITE = Query(5, ge=1, le=20)

def _recomendar(cypher: str, **parametros) -> list[dict]:
    """Ejecuta la consulta en Neo4j y completa cada prenda con sus datos de MongoDB"""
    registros, _, _ = get_driver().execute_query(
        cypher, parameters_=parametros, database_="neo4j"
    )
    recomendaciones = [r.data() for r in registros]
    datos = completar_prendas([r["producto_id"] for r in recomendaciones])
    # Se descartan prendas que ya no existan en MongoDB
    return [{**r, **datos[r["producto_id"]]} for r in recomendaciones
            if r["producto_id"] in datos]

@router.get("/tambien-compraron/{producto_id}")
def tambien_compraron(producto_id: str, limite: int = LIMITE):
    """'Quien compró esta prenda también compró...'"""
    return _recomendar("""
        MATCH (p:Producto {id: $producto_id})<-[:COMPRO]-(u:Usuario)-[:COMPRO]->(otro:Producto)
        WHERE otro <> p
        RETURN otro.id AS producto_id, count(DISTINCT u) AS compradores
        ORDER BY compradores DESC
        LIMIT $limite
    """, producto_id=producto_id, limite=limite)

@router.get("/completa-el-look/{producto_id}")
def completa_el_look(producto_id: str, limite: int = LIMITE):
    """Prendas de OTRAS categorías que compraron quienes compraron esta"""
    return _recomendar("""
        MATCH (p:Producto {id: $producto_id})-[:PERTENECE_A]->(cat:Categoria)
        MATCH (p)<-[:COMPRO]-(u:Usuario)-[:COMPRO]->(otro:Producto)-[:PERTENECE_A]->(otraCat:Categoria)
        WHERE otraCat <> cat
        RETURN otro.id AS producto_id, count(DISTINCT u) AS compradores
        ORDER BY compradores DESC
        LIMIT $limite
    """, producto_id=producto_id, limite=limite)

@router.get("/misma-categoria/{producto_id}")
def misma_categoria(producto_id: str, limite: int = LIMITE):
    """Otras prendas de la misma categoría"""
    return _recomendar("""
        MATCH (p:Producto {id: $producto_id})-[:PERTENECE_A]->(c:Categoria)<-[:PERTENECE_A]-(otro:Producto)
        WHERE otro <> p
        RETURN otro.id AS producto_id
        LIMIT $limite
    """, producto_id=producto_id, limite=limite)

@router.get("/para-ti/{usuario_id}")
def para_ti(usuario_id: str, limite: int = LIMITE):
    """Lo que compran usuarios con gustos parecidos y el usuario todavía no ha comprado."""
    return _recomendar("""
        MATCH (yo:Usuario {id: $usuario_id})-[:COMPRO]->(:Producto)<-[:COMPRO]-(similar:Usuario)-[:COMPRO]->(rec:Producto)
        WHERE similar <> yo AND NOT (yo)-[:COMPRO]->(rec)
        RETURN rec.id AS producto_id, count(DISTINCT similar) AS puntuacion
        ORDER BY puntuacion DESC
        LIMIT $limite
    """, usuario_id=usuario_id, limite=limite)

@router.get("/vistos-no-comprados/{usuario_id}")
def vistos_no_comprados(usuario_id: str, limite: int = LIMITE):
    """Prendas que el usuario ha visto pero no ha comprado, la más reciente primero."""
    return _recomendar("""
        MATCH (u:Usuario {id: $usuario_id})-[v:VIO]->(p:Producto)
        WHERE NOT (u)-[:COMPRO]->(p)
        RETURN p.id AS producto_id, v.veces AS veces_visto
        ORDER BY v.ultima DESC
        LIMIT $limite
    """, usuario_id=usuario_id, limite=limite)