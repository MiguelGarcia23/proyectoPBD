import { USE_MOCK } from "../config";
import type { Pedido, PedidoCompra, PedidoCrear } from "../types/api";
import { apiGet, apiPost } from "./client";
import { id, pedidos, productos, wait } from "./mock/data";
export async function comprar(datos: PedidoCrear) {
  if (!USE_MOCK) return apiPost<PedidoCompra>("/pedidos", datos);
  const lineas = datos.lineas.map(l => {
    const p = productos.find(x => x.id === l.producto_id)!; const v = p.variantes.find(x => x.sku === l.sku)!;
    return { ...l, nombre: p.nombre, talla: v.talla, color: v.color, precio_unitario: p.precio };
  });
  return wait({ id: id(299), usuario_id: datos.usuario_id, fecha: new Date().toISOString(), estado: "Confirmado", lineas, total: lineas.reduce((s, l) => s + l.precio_unitario * l.cantidad, 0), sincronizacion: { mongodb: "ok", cassandra: "ok", neo4j: "ok" } } satisfies PedidoCompra, 650);
}
export const pedidosDeUsuario = (uid: string) => USE_MOCK ? wait(pedidos.filter(p => p.usuario_id === uid)) : apiGet<Pedido[]>(`/usuarios/${uid}/pedidos`);
export const obtenerPedido = (id: string) => USE_MOCK ? wait(pedidos.find(p => p.id === id)!) : apiGet<Pedido>(`/pedidos/${id}`);
