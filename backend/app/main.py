from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

app = FastAPI(
    title="Tienda de ropa multi-NoSQL",
    description=(
        "API que integra tres motores NoSQL:\n\n"
        "- **MongoDB**: prendas, usuarios y pedidos\n"
        "- **Cassandra**: métricas de visitas y ventas\n"
        "- **Neo4j**: relaciones y recomendaciones"
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Home"])
def raiz():
    """Comprobación rápida de que la API está en marcha."""
    return {"mensaje": "API de la tienda de ropa funcionando", "docs": "/docs"}