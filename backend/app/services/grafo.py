"""
Escrituras en Neo4j: mantener el grafo sincronizado con MongoDB.
"""

from app.db.neo4j_db import get_driver

def _ejecutar(cypher: str, **parametros) -> None:
    get_driver().execute_query(cypher, parameters_=parametros, database_="neo4j")

def guardar_producto(producto_id: str, nombre: str, categoria: str) -> None:
    """Nodo Producto + su relación con la Categoria (alta de prenda)"""
    _ejecutar("""
        MERGE (p:Producto {id: $producto_id})
        SET p.nombre = $nombre
        MERGE (c:Categoria {nombre: $categoria})
        MERGE (p)-[:PERTENECE_A]->(c)
    """, producto_id=producto_id, nombre=nombre, categoria=categoria)

def guardar_usuario(usuario_id: str, nombre: str) -> None:
    """Nodo Usuario (registro de usuario)"""
    _ejecutar("""
        MERGE (u:Usuario {id: $usuario_id})
        SET u.nombre = $nombre
    """, usuario_id=usuario_id, nombre=nombre)

def registrar_visita(usuario_id: str, usuario_nombre: str,
                     producto_id: str, producto_nombre: str, categoria: str) -> None:
    """Relación (Usuario)-[:VIO]->(Producto), sumando una visita"""
    _ejecutar("""
        MERGE (u:Usuario {id: $usuario_id})
          ON CREATE SET u.nombre = $usuario_nombre
        MERGE (p:Producto {id: $producto_id})
          ON CREATE SET p.nombre = $producto_nombre
        MERGE (c:Categoria {nombre: $categoria})
        MERGE (p)-[:PERTENECE_A]->(c)
        MERGE (u)-[v:VIO]->(p)
          ON CREATE SET v.veces = 0
        SET v.veces = v.veces + 1, v.ultima = datetime()
    """, usuario_id=usuario_id, usuario_nombre=usuario_nombre,
        producto_id=producto_id, producto_nombre=producto_nombre, categoria=categoria)

def registrar_compra(usuario_id: str, usuario_nombre: str, lineas: list[dict]) -> None:
    """Relaciones (Usuario)-[:COMPRO]->(Producto) de un pedido, en UNA consulta"""
    _ejecutar("""
        MERGE (u:Usuario {id: $usuario_id})
          ON CREATE SET u.nombre = $usuario_nombre
        WITH u
        UNWIND $lineas AS l
        MERGE (p:Producto {id: l.producto_id})
          ON CREATE SET p.nombre = l.nombre
        MERGE (c:Categoria {nombre: l.categoria})
        MERGE (p)-[:PERTENECE_A]->(c)
        MERGE (u)-[r:COMPRO]->(p)
          ON CREATE SET r.veces = 0
        SET r.veces = r.veces + l.cantidad, r.ultima = datetime()
    """, usuario_id=usuario_id, usuario_nombre=usuario_nombre, lineas=lineas)