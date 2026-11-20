from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # MongoDB
    mongo_uri: str = "mongodb://admin:admin12345@localhost:27017/?authSource=admin"
    mongo_db: str = "tienda"

    # Cassandra
    cassandra_hosts: str = "localhost"
    cassandra_keyspace: str = "tienda"

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "neo4j12345"

    # Orígenes permitidos para CORS (el front-end), separados por comas
    cors_origins: str = "*"

# Objeto único que importa el resto de la aplicación
settings = Settings()