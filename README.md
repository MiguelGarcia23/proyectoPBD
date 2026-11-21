# Tienda de ropa multi-NoSQL

Proyecto de la asignatura **Programación de Bases de Datos**: una tienda de ropa online que integra tres bases de datos NoSQL, cada una usada para lo que mejor hace.

| Base de datos | Qué guarda | Por qué |
|---|---|---|
| **MongoDB** | Prendas (con sus variantes de talla y color), usuarios y pedidos | Documentos flexibles; es la fuente de verdad |
| **Cassandra** | Métricas: visitas, ventas por día, ranking y tallas más vendidas | Muchas escrituras pequeñas y consultas conocidas de antemano |
| **Neo4j** | Relaciones usuario–prenda–categoría | Recomendaciones como "completa el look" o "para ti" |

Al comprar (`POST /pedidos`), la API escribe en las tres bases de datos: descuenta el stock y guarda el pedido en MongoDB, registra la venta en Cassandra y crea las relaciones `COMPRO` en Neo4j.

## Tecnologías

- **Backend:** Python + FastAPI
- **Frontend:** React + TypeScript + Vite + Tailwind (diseñado con Figma Make)
- **Bases de datos:** MongoDB 7, Cassandra 5 y Neo4j 5, en Docker Compose

## Estructura

```
├── docker-compose.yml     # MongoDB, Cassandra, Neo4j, contenedores de inicialización y API
├── mongo/init.js          # Colecciones, validación e índices
├── cassandra/init.cql     # Keyspace y tablas de métricas
├── neo4j/                 # Restricciones y consultas Cypher
├── backend/app/
│   ├── db/                # Conexión a cada base de datos
│   ├── routers/           # Endpoints agrupados por base de datos
│   ├── services/          # Operaciones combinadas (compra, visita, grafo)
│   └── data.py            # Carga de datos de ejemplo
└── frontend/              # Interfaz web
```

## Puesta en marcha

Requisitos: Docker y Node.js.

1. Crear un archivo `.env` en la raíz con las credenciales:
   ```env
   MONGO_USER=admin
   MONGO_PASSWORD=admin12345
   NEO4J_PASSWORD=neo4j12345
   ```
   En Neo4j Community el usuario es siempre `neo4j`.

2. Levantar las bases de datos y la API (Cassandra tarda 1–2 minutos en arrancar):
   ```bash
   docker compose up -d --build
   ```

3. Cargar los datos de ejemplo (24 prendas, 8 usuarios, 350 visitas y 70 compras):
   ```bash
   docker compose exec api python -m app.data          # --reset para borrar y volver a cargar
   ```

4. Arrancar el front:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

| Servicio | URL |
|---|---|
| Tienda | http://localhost:8443 |
| API (Swagger) | http://localhost:8000/docs |
| Estado de las bases de datos | http://localhost:8000/health |
| Neo4j Browser | http://localhost:7474 |

## Endpoints principales

| Endpoint | Bases de datos |
|---|---|
| `GET /productos` | MongoDB |
| `GET /productos/{id}?usuario_id=` | MongoDB, más la visita en Cassandra y Neo4j |
| `POST /pedidos` | MongoDB + Cassandra + Neo4j |
| `GET /metricas/...` | Cassandra |
| `GET /recomendaciones/...` | Neo4j, completado con MongoDB |

La lista completa y la opción de probarlos están en Swagger (`/docs`).

## Autores

- Carlos Martín Magariño
- Miguel Alejandro García Sevilla
