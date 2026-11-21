import { Check, Minus, Plus } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router";
import { obtenerProducto } from "../api/productos";
import { completaElLook, mismaCategoria, tambienCompraron } from "../api/recomendaciones";
import { CarruselRecomendaciones } from "../components/CarruselRecomendaciones";
import { EtiquetaMotor } from "../components/EtiquetaMotor";
import { ImagenPrenda } from "../components/ImagenPrenda";
import { ErrorBox, eur, Loading } from "../components/Ui";
import { useCarrito } from "../context/CarritoContext";
import { useUsuario } from "../context/UsuarioContext";
import type { Producto as TipoProducto, Recomendacion, Variante } from "../types/api";
export function Producto() {
  const { id = "" } = useParams(); const { usuario } = useUsuario(); const { agregar } = useCarrito();
  const [p, setP] = useState<TipoProducto>(); const [error, setError] = useState(""); const [color, setColor] = useState(""); const [talla, setTalla] = useState(""); const [cantidad, setCantidad] = useState(1); const [added, setAdded] = useState(false);
  const [recs, setRecs] = useState<Record<string, Recomendacion[]>>({});
  useEffect(() => { obtenerProducto(id, usuario?.id).then(x => { setP(x); setColor(x.variantes[0]?.color ?? ""); }).catch(e => setError(e.message)); Promise.allSettled([completaElLook(id), tambienCompraron(id), mismaCategoria(id)]).then(r => setRecs({ look: r[0].status === "fulfilled" ? r[0].value : [], tambien: r[1].status === "fulfilled" ? r[1].value : [], categoria: r[2].status === "fulfilled" ? r[2].value : [] })); }, [id, usuario?.id]);
  const colors = useMemo(() => [...new Set(p?.variantes.map(v => v.color))], [p]); const sizes = useMemo(() => [...new Set(p?.variantes.filter(v => v.color === color).map(v => v.talla))], [p, color]);
  const variant: Variante | undefined = p?.variantes.find(v => v.color === color && v.talla === talla);
  if (error) return <main className="page"><ErrorBox message={error} /></main>; if (!p) return <main className="page"><Loading text="Preparando la prenda…" /></main>;
  const add = () => { if (!variant) return; agregar({ producto_id: p.id, sku: variant.sku, nombre: p.nombre, talla: variant.talla, color: variant.color, precio_unitario: p.precio, cantidad, imagen: p.imagen, categoria: p.categoria }); setAdded(true); setTimeout(() => setAdded(false), 2000); };
  return <main className="page"><Link to="/" className="mb-7 inline-block text-sm font-bold text-stone-500 hover:text-stone-900">← Volver al catálogo</Link><div className="grid gap-10 lg:grid-cols-2 lg:gap-16">
    <div className="group overflow-hidden rounded-[2rem]"><ImagenPrenda producto={p} /></div><div className="py-3"><EtiquetaMotor motor="MongoDB" /><p className="mt-6 text-xs font-bold uppercase tracking-[.2em] text-[#727b61]">{p.categoria} · {p.genero}</p><h1 className="mt-3 text-4xl font-black tracking-[-.04em] md:text-5xl">{p.nombre}</h1><p className="mt-4 text-2xl font-black">{eur(p.precio)}</p><p className="mt-6 max-w-xl leading-7 text-stone-500">{p.descripcion}</p>
      <div className="mt-8"><p className="label">Color: <b className="text-stone-900">{color}</b></p><div className="flex gap-2">{colors.map(c => <button key={c} onClick={() => { setColor(c); setTalla(""); }} className={`rounded-full border px-4 py-2 text-sm font-bold ${color === c ? "border-stone-900 bg-stone-900 text-white" : "border-stone-200"}`}>{c}</button>)}</div></div>
      <div className="mt-6"><p className="label">Selecciona una talla</p><div className="flex gap-2">{sizes.map(s => { const v = p.variantes.find(x => x.color === color && x.talla === s)!; return <button key={s} disabled={!v.stock} onClick={() => setTalla(s)} className={`size-12 rounded-xl border text-sm font-bold ${talla === s ? "border-[#596348] bg-[#596348] text-white" : "border-stone-200"} disabled:bg-stone-100 disabled:text-stone-300 disabled:line-through`}>{s}</button>; })}</div>{variant && variant.stock < 5 && <p className="mt-2 text-xs font-bold text-[#b45f45]">Últimas unidades</p>}</div>
      <div className="mt-8 flex gap-3"><div className="flex items-center rounded-xl border border-stone-200"><button onClick={() => setCantidad(Math.max(1, cantidad - 1))} className="p-3"><Minus size={16} /></button><span className="w-8 text-center font-bold">{cantidad}</span><button onClick={() => setCantidad(Math.min(variant?.stock ?? 9, cantidad + 1))} className="p-3"><Plus size={16} /></button></div><button disabled={!variant || !variant.stock} onClick={add} className="btn-primary flex-1">{added ? <><Check size={18} />Añadido</> : "Añadir al carrito"}</button></div>
      <div className="mt-9 border-t border-stone-200 pt-7"><h2 className="font-black">Detalles</h2><dl className="mt-4 grid grid-cols-2 gap-x-8 gap-y-3 text-sm">{Object.entries(p.atributos).map(([k, v]) => <div key={k} className="flex justify-between border-b border-stone-100 pb-2"><dt className="capitalize text-stone-500">{k}</dt><dd className="font-semibold capitalize">{String(v)}</dd></div>)}</dl></div>
    </div></div>
    <CarruselRecomendaciones title="Completa el look" items={recs.look ?? []} /><CarruselRecomendaciones title="Quien compró esto también compró" items={recs.tambien ?? []} /><CarruselRecomendaciones title="De la misma categoría" items={recs.categoria ?? []} />
  </main>;
}
