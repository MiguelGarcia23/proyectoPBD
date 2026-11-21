export type Categoria = "Camisetas" | "Camisas" | "Sudaderas" | "Pantalones" | "Vestidos" | "Chaquetas" | "Calzado" | "Accesorios";
export type Genero = "hombre" | "mujer" | "unisex";
export interface Variante { sku: string; talla: string; color: string; stock: number; }
export interface Producto {
  id: string; nombre: string; descripcion?: string | null; precio: number;
  categoria: Categoria; genero: Genero; imagen?: string | null;
  atributos: Record<string, string | number | boolean>; variantes: Variante[];
}
export interface FiltrosProductos {
  categoria?: Categoria; genero?: Genero; q?: string; talla?: string;
  precio_max?: number; solo_disponibles?: boolean; limite?: number; saltar?: number;
}
export interface Usuario {
  id: string; nombre: string; email: string; fecha_alta: string;
  direccion?: { calle: string; ciudad: string; cp: string } | null;
}
export interface LineaPedido {
  producto_id: string; sku: string; nombre: string; talla: string; color: string;
  precio_unitario: number; cantidad: number;
}
export interface Pedido { id: string; usuario_id: string; fecha: string; estado: string; lineas: LineaPedido[]; total: number; }
export interface PedidoCrear { usuario_id: string; lineas: { producto_id: string; sku: string; cantidad: number }[]; }
export interface PedidoCompra extends Pedido {
  sincronizacion: { mongodb: "ok" | "error"; cassandra: "ok" | "error"; neo4j: "ok" | "error" };
}
export interface Recomendacion {
  producto_id: string; nombre: string; precio: number; imagen?: string | null; categoria: Categoria;
  tallas_disponibles: string[]; compradores?: number; puntuacion?: number; veces_visto?: number;
}
export interface VentasMes { mes: string; total_pedidos: number; importe_total: number; por_dia: { dia: string; pedidos: number; importe: number }[]; }
export interface VentasDia {
  dia: string; unidades: number; importe_total: number;
  ventas: { momento: string; pedido_id: string; producto_id: string; sku: string; talla: string; color: string; usuario_id: string; cantidad: number; importe: number }[];
}
export interface Ranking { mes: string; ranking: { posicion: number; producto_id: string; nombre: string | null; unidades: number; importe: number }[]; }
export interface TallasMes { mes: string; categoria: Categoria; tallas: { talla: string; unidades: number }[]; }
export interface VisitasProducto { producto_id: string; dias: number; total_visitas: number; por_dia: { dia: string; visitas: number }[]; }
export interface Salud { estado: "ok" | "degradado"; motores: { mongodb: "ok" | "error"; cassandra: "ok" | "error"; neo4j: "ok" | "error" }; }
