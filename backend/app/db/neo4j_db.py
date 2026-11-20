from neo4j import Driver, GraphDatabase

from app.config import settings

_driver: Driver | None = None

def conectar() -> None:
    global _driver
    _driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    )
    _driver.verify_connectivity() 

def cerrar() -> None:
    if _driver is not None:
        _driver.close()

def get_driver() -> Driver:
    if _driver is None:
        raise RuntimeError("Neo4j no está conectado")
    return _driver

def ping() -> bool:
    try:
        get_driver().execute_query("RETURN 1")
        return True
    except Exception:
        return False