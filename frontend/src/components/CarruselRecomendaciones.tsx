import type { Recomendacion } from "../types/api";
import { EtiquetaMotor } from "./EtiquetaMotor";
import { MiniProductCard } from "./ProductCard";
export function CarruselRecomendaciones({ title, items }: { title: string; items: Recomendacion[] }) {
  if (!items.length) return null;
  return <section className="mt-12"><div className="mb-5 flex items-center gap-3"><h2 className="text-2xl font-black tracking-tight">{title}</h2><EtiquetaMotor motor="Neo4j" /></div><div className="flex gap-4 overflow-x-auto pb-4">{items.map(p => <MiniProductCard key={p.producto_id} producto={p} />)}</div></section>;
}
