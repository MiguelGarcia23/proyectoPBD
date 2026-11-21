import type { Categoria, Pedido, Producto, Recomendacion, Usuario } from "../../types/api";

const id = (n: number) => `6740a1b2c3d4e5f6a7b8${n.toString(16).padStart(4, "0")}`;
const variantes = (n: number) => [
  { sku: `NSW-${n}-S-OL`, talla: "S", color: "Oliva", stock: n % 3 ? 8 : 0 },
  { sku: `NSW-${n}-M-OL`, talla: "M", color: "Oliva", stock: 3 },
  { sku: `NSW-${n}-L-AR`, talla: "L", color: "Arena", stock: 7 },
];
const base: [string, string, Categoria, number, "hombre" | "mujer" | "unisex", string][] = [
  ["Camiseta básica de algodón", "camiseta-basica-algodon.jpg", "Camisetas", 24.99, "unisex", "Algodón orgánico suave y corte regular"],
  ["Camiseta oversize estampada", "camiseta-oversize-estampada.jpg", "Camisetas", 32.99, "unisex", "Silueta amplia con estampado de edición limitada"],
  ["Sudadera con capucha", "sudadera-con-capucha.jpg", "Sudaderas", 59.99, "unisex", "Felpa gruesa con capucha ajustable"],
  ["Vaqueros slim", "vaqueros-slim.jpg", "Pantalones", 64.9, "hombre", "Denim elástico de corte estrecho"],
  ["Vaqueros rectos", "vaqueros-rectos.jpg", "Pantalones", 69.9, "mujer", "Denim responsable de pierna recta"],
  ["Cazadora vaquera", "cazadora-vaquera.jpg", "Chaquetas", 89.99, "unisex", "Cazadora denim con lavado medio"],
  ["Zapatillas urbanas", "zapatillas-urbanas.jpg", "Calzado", 84.99, "unisex", "Zapatilla ligera de perfil minimalista"],
  ["Zapatillas de lona", "zapatillas-lona.jpg", "Calzado", 54.95, "unisex", "Lona resistente y suela flexible"],
  ["Gorra de algodón", "gorra-de-algodon.jpg", "Accesorios", 22, "unisex", "Algodón lavado y cierre metálico"],
  ["Camisa Oxford", "camisa-oxford.jpg", "Camisas", 49.9, "hombre", "Oxford de algodón con cuello abotonado"],
  ["Blusa de lino", "blusa-de-lino.jpg", "Camisas", 52.99, "mujer", "Lino transpirable de corte relajado"],
  ["Pantalón chino", "pantalon-chino.jpg", "Pantalones", 59.9, "hombre", "Sarga suave de corte contemporáneo"],
  ["Pantalón palazzo", "pantalon-palazzo.jpg", "Pantalones", 64.99, "mujer", "Cintura alta y caída fluida"],
  ["Vestido midi estampado", "vestido-midi-estampado.jpg", "Vestidos", 79.99, "mujer", "Vestido midi fluido con estampado sutil"],
  ["Vestido camisero", "vestido-camisero.jpg", "Vestidos", 74.9, "mujer", "Silueta camisera con cinturón"],
  ["Blazer", "blazer.jpg", "Chaquetas", 119, "unisex", "Sastrería relajada con acabado estructurado"],
  ["Mocasines de piel", "mocasines-de-piel.jpg", "Calzado", 99.99, "unisex", "Mocasín clásico de piel flexible"],
  ["Cinturón de piel", "cinturon-de-piel.jpg", "Accesorios", 34.95, "unisex", "Piel curtida y hebilla mate"],
  ["Camiseta técnica running", "camiseta-tecnica-running.jpg", "Camisetas", 39.99, "unisex", "Tejido técnico transpirable y ultraligero"],
  ["Camiseta de tirantes training", "camiseta-tirantes-training.jpg", "Camisetas", 29.99, "mujer", "Tirantes deportivos y secado rápido"],
  ["Sudadera técnica con cremallera", "sudadera-tecnica-cremallera.jpg", "Sudaderas", 69.99, "unisex", "Capa técnica elástica con cremallera"],
  ["Sudadera básica cuello redondo", "sudadera-basica-cuello-redondo.jpg", "Sudaderas", 54.99, "unisex", "Cuello redondo y felpa de algodón"],
  ["Vestido deportivo", "vestido-deportivo.jpg", "Vestidos", 62.5, "mujer", "Vestido elástico para un estilo activo"],
  ["Cortavientos ligero", "cortavientos-ligero.jpg", "Chaquetas", 79.9, "unisex", "Protección ligera contra viento y lluvia"],
];
export const productos: Producto[] = base.map(([nombre, imagen, categoria, precio, genero, descripcion], i) => ({
  id: id(i + 1), nombre, categoria, precio, genero, descripcion, variantes: variantes(i + 1), imagen,
  atributos: (categoria === "Calzado" ? { material: "Serraje vegano", suela: "Goma", estilo: "urbano" } : { material: "Tejido responsable", corte: "Regular", estilo: i % 2 ? "clasico" : "urbano" }) as Record<string, string>,
}));
export const usuarios: Usuario[] = ["Lucía Martín", "Álvaro Ruiz", "Sara Vega", "Diego León"].map((nombre, i) => ({
  id: id(101 + i), nombre, email: `${nombre.toLowerCase().replace(" ", ".").normalize("NFD").replace(/[\u0300-\u036f]/g, "")}@ejemplo.es`,
  fecha_alta: new Date(2024, i + 1, 4).toISOString(), direccion: { calle: `Calle Mayor ${i + 2}`, ciudad: "Madrid", cp: "28001" },
}));
const linea = (p: Producto, cantidad = 1) => ({ producto_id: p.id, sku: p.variantes[1].sku, nombre: p.nombre, talla: "M", color: "Oliva", precio_unitario: p.precio, cantidad });
export const pedidos: Pedido[] = [
  { id: id(201), usuario_id: usuarios[0].id, fecha: new Date().toISOString(), estado: "Entregado", lineas: [linea(productos[0], 2), linea(productos[7])], total: 89.93 },
  { id: id(202), usuario_id: usuarios[0].id, fecha: new Date(Date.now() - 864e5 * 12).toISOString(), estado: "Enviado", lineas: [linea(productos[4])], total: 79.99 },
  { id: id(203), usuario_id: usuarios[1].id, fecha: new Date(Date.now() - 864e5 * 4).toISOString(), estado: "Preparando", lineas: [linea(productos[1])], total: 49.9 },
];
export const recomendaciones: Recomendacion[] = productos.slice(0, 8).map(p => ({
  producto_id: p.id, nombre: p.nombre, precio: p.precio, categoria: p.categoria, imagen: p.imagen,
  tallas_disponibles: [...new Set(p.variantes.filter(v => v.stock > 0).map(v => v.talla))], puntuacion: 0.9,
}));
export const wait = <T>(value: T, ms = 320) => new Promise<T>(resolve => setTimeout(() => resolve(structuredClone(value)), ms));
export { id };
