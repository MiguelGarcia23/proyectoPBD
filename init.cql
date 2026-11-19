-- Inicialización de Cassandra para la tienda

CREATE KEYSPACE IF NOT EXISTS tienda
  WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};