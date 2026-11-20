-- Inicialización de Cassandra para la tienda

CREATE KEYSPACE IF NOT EXISTS tienda
  WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE tienda;

-- Consulta 1: "¿Cuántas visitas ha tenido el producto X cada día?"
-- Partición = producto, filas ordenadas por día (más reciente primero).
CREATE TABLE IF NOT EXISTS visitas_producto_dia (
    producto_id text,
    dia         date,
    visitas     counter,
    PRIMARY KEY ((producto_id), dia)
) WITH CLUSTERING ORDER BY (dia DESC);

-- Consulta 2: "¿Qué ventas ha habido el día X?" (detalle, en orden temporal)
-- Partición = día, filas ordenadas por momento de la venta.
CREATE TABLE IF NOT EXISTS ventas_por_dia (
    dia         date,
    momento     timestamp,
    pedido_id   text,
    producto_id text,
    sku         text,
    talla       text,
    color       text,
    usuario_id  text,
    cantidad    int,
    importe     decimal,
    PRIMARY KEY ((dia), momento, pedido_id, sku)
) WITH CLUSTERING ORDER BY (momento DESC, pedido_id ASC, sku ASC);

-- Consulta 3: "¿Cuánto se ha vendido cada día del mes x?"
-- Partición = mes ('2026-11'), una fila por día. 
-- IMPORTANTE: importe en céntimos porque los contadores de Cassandra solo admiten enteros.
CREATE TABLE IF NOT EXISTS resumen_ventas_dia (
    mes              text,
    dia              date,
    num_pedidos      counter,
    importe_centimos counter,
    PRIMARY KEY ((mes), dia)
) WITH CLUSTERING ORDER BY (dia DESC);

-- Consulta 4: "¿Cuáles son los productos más vendidos del mes X?"
-- Cassandra no puede ordenar por un contador, así que la API lee la partición del mes y ordena el ranking en Python.
CREATE TABLE IF NOT EXISTS ventas_producto_mes (
    mes              text,
    producto_id      text,
    unidades         counter,
    importe_centimos counter,
    PRIMARY KEY ((mes), producto_id)
);

-- Consulta 5: "¿Qué tallas se venden más de cada categoría este mes?"
-- Útil para reponer stock. Partición = (mes, categoría), una fila por talla.
CREATE TABLE IF NOT EXISTS ventas_talla_mes (
    mes       text,
    categoria text,
    talla     text,
    unidades  counter,
    PRIMARY KEY ((mes, categoria), talla)
);