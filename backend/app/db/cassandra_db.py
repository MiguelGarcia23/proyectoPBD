from functools import lru_cache
from cassandra.cluster import Cluster, Session
from cassandra.query import PreparedStatement

from app.config import settings

_cluster: Cluster | None = None
_session: Session | None = None

def conectar() -> None:
    global _cluster, _session
    hosts = [h.strip() for h in settings.cassandra_hosts.split(",")]
    _cluster = Cluster(hosts, port=9042)
    _session = _cluster.connect(settings.cassandra_keyspace)

def cerrar() -> None:
    if _cluster is not None:
        _cluster.shutdown()

def get_session() -> Session:
    if _session is None:
        raise RuntimeError("Cassandra no está conectado")
    return _session

def ping() -> bool:
    try:
        get_session().execute("SELECT release_version FROM system.local")
        return True
    except Exception:
        return False

@lru_cache(maxsize=None)
def preparada(cql: str) -> PreparedStatement:
    """Devuelve la sentencia preparada (se prepara una sola vez y se reutiliza)."""
    return get_session().prepare(cql)