import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.db import mongo_db, cassandra_db, neo4j_db
from app.routers import metricas, pedidos, productos, recomendaciones, usuarios

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("tienda")

@asynccontextmanager
async def lifespan(app: FastAPI):
    "Se ejecuta al arrancar y al detener la app"

    log.info("Conectando a MongoDB")
    mongo_db.conectar()
    log.info("Conectando a Cassandra")
    cassandra_db.conectar()
    log.info("Conectando a Neo4j")
    neo4j_db.conectar()
    log.info("Se han conectado las tres bases de datos")

    yield   # Escuchar peticiones

    log.info("Cerrando conexiones")
    mongo_db.cerrar()
    cassandra_db.cerrar()
    neo4j_db.cerrar()

app = FastAPI(
    title="Tienda de ropa multi-NoSQL",
    description=(
        "API que integra tres motores NoSQL:\n\n"
        "- **MongoDB**: prendas, usuarios y pedidos\n"
        "- **Cassandra**: métricas de visitas y ventas\n"
        "- **Neo4j**: relaciones y recomendaciones"
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoints agrupados por base de datos
app.include_router(productos.router)        
app.include_router(usuarios.router)         
app.include_router(pedidos.router)          
app.include_router(metricas.router)
app.include_router(recomendaciones.router)

@app.get("/", tags=["Home"])
def raiz():
    """Comprobación rápida de que la API está en marcha."""
    return {"mensaje": "API de la tienda de ropa funcionando", "docs": "/docs"}

@app.get("/health", tags=["Home"])
def health():
    """Estado de la conexión con cada base de datos. Devuelve un error 503 si alguno falla."""

    estado = {
        "mongodb": "ok" if mongo_db.ping() else "error",
        "cassandra": "ok" if cassandra_db.ping() else "error",
        "neo4j": "ok" if neo4j_db.ping() else "error",
    }

    conexion_correcta = all(estadoDB == "ok" for estadoDB in estado.values())

    return JSONResponse(
        status_code=200 if conexion_correcta else 503,
        content={"estado": "ok" if conexion_correcta else "error_conexion", "motores": estado },
    )