db = db.getSiblingDB("tienda");

// COLLECTION productos
db.createCollection("productos", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["nombre", "precio", "categoria", "genero", "variantes"],
      properties: {
        nombre:    { bsonType: "string" },
        precio:    { bsonType: ["double", "int", "decimal"], minimum: 0 },
        categoria: { enum: ["Camisetas", "Camisas", "Sudaderas", "Pantalones", "Vestidos", "Chaquetas", "Calzado", "Accesorios"] },
        genero:    { enum: ["hombre", "mujer", "unisex"] },
        atributos: { bsonType: "object" },
        variantes: {
          bsonType: "array",
          minItems: 1,
          items: {
            bsonType: "object",
            required: ["sku", "talla", "color", "stock"],
            properties: {
              sku:   { bsonType: "string" },
              talla: { bsonType: "string" },
              color: { bsonType: "string" },
              stock: { bsonType: "int", minimum: 0 }
            }
          }
        }
      }
    }
  }
});
db.productos.createIndex({ categoria: 1, genero: 1 });              // Índice para los filtros del catálogo
db.productos.createIndex({ "variantes.sku": 1 }, { unique: true }); // Índice para que cada SKU sea único
db.productos.createIndex({ nombre: "text", descripcion: "text" });  // Índice para el buscador

// ---------- usuarios ----------
db.createCollection("usuarios", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["nombre", "email"],
      properties: {
        nombre: { bsonType: "string" },
        email:  { bsonType: "string" }
      }
    }
  }
});
db.usuarios.createIndex({ email: 1 }, { unique: true });            // Índice para que cada correo sea único

// ---------- pedidos ----------
db.createCollection("pedidos", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["usuario_id", "lineas", "total", "fecha", "estado"],
      properties: {
        usuario_id: { bsonType: "string" },
        lineas: {
          bsonType: "array",
          minItems: 1,
          items: {
            bsonType: "object",
            required: ["producto_id", "sku", "talla", "color", "precio_unitario", "cantidad"]
          }
        },
        total:  { bsonType: ["double", "int", "decimal"], minimum: 0 },
        fecha:  { bsonType: "date" },
        estado: { enum: ["pendiente", "pagado", "enviado", "entregado", "devuelto", "cancelado"] }
      }
    }
  }
});
db.pedidos.createIndex({ usuario_id: 1, fecha: -1 }); // Índice para que los pedidos más recientes del usuario aparezcan primero