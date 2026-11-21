from pymongo import MongoClient
from pymongo.database import Database

from app.config import settings

_client: MongoClient | None = None

def conectar() -> None:
    global _client
    _client = MongoClient(settings.mongo_uri, serverSelectionTimeoutMS=5000, tz_aware=True)
    _client.admin.command("ping")

def cerrar() -> None:
    if _client is not None:
        _client.close()

def get_db() -> Database:
    if _client is None:
        raise RuntimeError("MongoDB no está conectado")
    return _client[settings.mongo_db]

def ping() -> bool:
    try:
        get_db().command("ping")
        return True
    except Exception:
        return False