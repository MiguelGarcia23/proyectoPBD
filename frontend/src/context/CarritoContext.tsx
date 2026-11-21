import { createContext, useContext, useMemo, useState, type ReactNode } from "react";
import type { Categoria, LineaPedido } from "../types/api";
export interface LineaCarrito extends LineaPedido { imagen?: string | null; categoria?: Categoria; }
interface CarritoState {
  lineas: LineaCarrito[]; unidades: number; total: number;
  agregar: (l: LineaCarrito) => void; cambiarCantidad: (sku: string, n: number) => void; quitar: (sku: string) => void; vaciar: () => void;
}
const Context = createContext<CarritoState | null>(null);
export function CarritoProvider({ children }: { children: ReactNode }) {
  const [lineas, setLineas] = useState<LineaCarrito[]>(() => JSON.parse(localStorage.getItem("nosql-carrito") || "[]"));
  const save = (next: LineaCarrito[]) => { setLineas(next); localStorage.setItem("nosql-carrito", JSON.stringify(next)); };
  const agregar = (l: LineaCarrito) => { const found = lineas.find(x => x.sku === l.sku); save(found ? lineas.map(x => x.sku === l.sku ? { ...x, cantidad: x.cantidad + l.cantidad } : x) : [...lineas, l]); };
  const value = useMemo(() => ({
    lineas, unidades: lineas.reduce((s, l) => s + l.cantidad, 0), total: lineas.reduce((s, l) => s + l.precio_unitario * l.cantidad, 0),
    agregar, cambiarCantidad: (sku: string, n: number) => save(lineas.map(l => l.sku === sku ? { ...l, cantidad: Math.max(1, n) } : l)),
    quitar: (sku: string) => save(lineas.filter(l => l.sku !== sku)), vaciar: () => save([]),
  }), [lineas]);
  return <Context.Provider value={value}>{children}</Context.Provider>;
}
export function useCarrito() { const v = useContext(Context); if (!v) throw new Error("CarritoContext no disponible"); return v; }
