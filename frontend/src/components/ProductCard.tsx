import { ArrowUpRight } from "lucide-react";
import { Link } from "react-router";
import type { Producto, Recomendacion } from "../types/api";
import { ImagenPrenda } from "./ImagenPrenda";
import { eur } from "./Ui";
export function ProductCard({ producto }: { producto: Producto }) {
  const tallas = [...new Set(producto.variantes.filter(v => v.stock > 0).map(v => v.talla))];
  return <Link to={`/producto/${producto.id}`} className="group overflow-hidden rounded-3xl border border-stone-200 bg-white shadow-[0_10px_30px_rgba(40,35,25,.04)] transition hover:-translate-y-1 hover:shadow-xl">
    <ImagenPrenda producto={producto} /><div className="p-5"><div className="flex items-start justify-between gap-4"><div><p className="text-[11px] font-bold uppercase tracking-widest text-[#727b61]">{producto.genero}</p><h3 className="mt-1 text-lg font-bold">{producto.nombre}</h3></div><ArrowUpRight className="text-stone-400 transition group-hover:text-stone-900" size={19} /></div><p className="mt-3 text-lg font-black">{eur(producto.precio)}</p><div className="mt-4 flex gap-1.5">{tallas.map(t => <span key={t} className="rounded-md bg-stone-100 px-2 py-1 text-[10px] font-bold">{t}</span>)}</div></div>
  </Link>;
}
export function MiniProductCard({ producto }: { producto: Recomendacion }) {
  return <Link to={`/producto/${producto.producto_id}`} className="group min-w-[210px] overflow-hidden rounded-2xl border border-stone-200 bg-white transition hover:-translate-y-1"><ImagenPrenda compact producto={producto} /><div className="p-4"><h3 className="truncate font-bold">{producto.nombre}</h3><p className="mt-1 font-black">{eur(producto.precio)}</p></div></Link>;
}
