import { USE_MOCK } from "../config";
import type { FiltrosProductos, Producto } from "../types/api";
import { apiGet } from "./client";
import { productos, wait } from "./mock/data";

export async function listarProductos(f: FiltrosProductos = {}) {
  if (!USE_MOCK) {
    const q = new URLSearchParams();
    Object.entries(f).forEach(([k, v]) => v !== undefined && v !== "" && q.set(k, String(v)));
    return apiGet<Producto[]>(`/productos?${q}`);
  }
  let list = productos.filter(p =>
    (!f.categoria || p.categoria === f.categoria) && (!f.genero || p.genero === f.genero) &&
    (!f.q || `${p.nombre} ${p.descripcion}`.toLowerCase().includes(f.q.toLowerCase())) &&
    (!f.talla || p.variantes.some(v => v.talla === f.talla && v.stock > 0)) &&
    (!f.precio_max || p.precio <= f.precio_max) &&
    (!f.solo_disponibles || p.variantes.some(v => v.stock > 0)));
  return wait(list.slice(f.saltar ?? 0, (f.saltar ?? 0) + (f.limite ?? 8)));
}
export const obtenerProducto = (id: string, usuarioId?: string) =>
  USE_MOCK ? wait(productos.find(p => p.id === id)!) : apiGet<Producto>(`/productos/${id}${usuarioId ? `?usuario_id=${usuarioId}` : ""}`);
