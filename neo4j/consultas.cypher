// ---------- ESCRITURA ----------

// Registrar una compra
MERGE (u:Usuario {id: $usuario_id})
  ON CREATE SET u.nombre = $usuario_nombre
MERGE (p:Producto {id: $producto_id})
  ON CREATE SET p.nombre = $producto_nombre
MERGE (u)-[r:COMPRO]->(p)
  ON CREATE SET r.veces = 0
SET r.veces = r.veces + $cantidad,
    r.ultima = datetime();

// Registrar una visita a un producto
MATCH (u:Usuario {id: $usuario_id}), (p:Producto {id: $producto_id})
MERGE (u)-[v:VIO]->(p)
  ON CREATE SET v.veces = 0
SET v.veces = v.veces + 1,
    v.ultima = datetime();

// Dar de alta un producto con su categoría
MERGE (p:Producto {id: $producto_id})
SET p.nombre = $nombre
MERGE (c:Categoria {nombre: $categoria})
MERGE (p)-[:PERTENECE_A]->(c);

// ---------- RECOMENDACIONES ----------

// 1. "Quien compró este producto también compró..."
MATCH (p:Producto {id: $producto_id})<-[:COMPRO]-(u:Usuario)-[:COMPRO]->(otro:Producto)
WHERE otro <> p
RETURN otro.id AS producto_id, otro.nombre AS nombre, count(DISTINCT u) AS compradores
ORDER BY compradores DESC
LIMIT 5;

// 2. "Recomendado para ti": lo que compran usuarios con gustos parecidos y que no has comprado
MATCH (yo:Usuario {id: $usuario_id})-[:COMPRO]->(:Producto)<-[:COMPRO]-(similar:Usuario)-[:COMPRO]->(rec:Producto)
WHERE similar <> yo AND NOT (yo)-[:COMPRO]->(rec)
RETURN rec.id AS producto_id, rec.nombre AS nombre, count(DISTINCT similar) AS puntuacion
ORDER BY puntuacion DESC
LIMIT 5;

// 3. "Productos de la misma categoría"
MATCH (p:Producto {id: $producto_id})-[:PERTENECE_A]->(c:Categoria)<-[:PERTENECE_A]-(otro:Producto)
WHERE otro <> p
RETURN otro.id AS producto_id, otro.nombre AS nombre, c.nombre AS categoria
LIMIT 5;

// 4. "Vistos pero no comprados"
MATCH (u:Usuario {id: $usuario_id})-[v:VIO]->(p:Producto)
WHERE NOT (u)-[:COMPRO]->(p)
RETURN p.id AS producto_id, p.nombre AS nombre, v.veces AS veces_visto
ORDER BY v.ultima DESC
LIMIT 5;

// 5. "Completa el look": prendas de OTRAS categorías que compraron quienes compraron esta
MATCH (p:Producto {id: $producto_id})-[:PERTENECE_A]->(cat:Categoria)
MATCH (p)<-[:COMPRO]-(u:Usuario)-[:COMPRO]->(otro:Producto)-[:PERTENECE_A]->(otraCat:Categoria)
WHERE otraCat <> cat
RETURN otro.id AS producto_id, otro.nombre AS nombre, otraCat.nombre AS categoria,
       count(DISTINCT u) AS compradores
ORDER BY compradores DESC
LIMIT 5;
