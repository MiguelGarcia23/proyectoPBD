import { SlidersHorizontal, X } from "lucide-react";
import { useEffect, useState } from "react";
import { listarProductos } from "../api/productos";
import { EtiquetaMotor } from "../components/EtiquetaMotor";
import { ProductCard } from "../components/ProductCard";
import { Empty, ErrorBox, Loading, PageTitle } from "../components/Ui";
import type { Categoria, FiltrosProductos, Genero, Producto } from "../types/api";
const categorias: Categoria[] = ["Camisetas", "Camisas", "Sudaderas", "Pantalones", "Vestidos", "Chaquetas", "Calzado", "Accesorios"];
export function Catalogo() {
  const [f, setF] = useState<FiltrosProductos>({ limite: 8, saltar: 0, solo_disponibles: true });
  const [items, setItems] = useState<Producto[]>([]); const [loading, setLoading] = useState(true); const [error, setError] = useState(""); const [filters, setFilters] = useState(false); const [more, setMore] = useState(true);
  useEffect(() => { setLoading(true); setError(""); const t = setTimeout(() => listarProductos(f).then(x => { setItems(f.saltar ? old => [...old, ...x] : x); setMore(x.length === f.limite); }).catch(e => setError(e.message)).finally(() => setLoading(false)), 180); return () => clearTimeout(t); }, [f]);
  const update = (key: keyof FiltrosProductos, value: unknown) => setF(p => ({ ...p, [key]: value || undefined, saltar: 0 }));
  const form = <div className="space-y-6">
    <label className="block"><span className="label">Buscar</span><input value={f.q ?? ""} onChange={e => update("q", e.target.value)} placeholder="Nombre o descripción" className="input" /></label>
    <label className="block"><span className="label">Categoría</span><select value={f.categoria ?? ""} onChange={e => update("categoria", e.target.value as Categoria)} className="input"><option value="">Todas</option>{categorias.map(x => <option key={x}>{x}</option>)}</select></label>
    <div><span className="label">Género</span><div className="grid grid-cols-3 gap-2">{(["mujer", "hombre", "unisex"] as Genero[]).map(x => <button key={x} onClick={() => update("genero", f.genero === x ? "" : x)} className={`rounded-xl border px-2 py-2 text-xs font-bold capitalize ${f.genero === x ? "border-[#596348] bg-[#596348] text-white" : "border-stone-200"}`}>{x}</button>)}</div></div>
    <div><span className="label">Talla</span><div className="flex gap-2">{["XS", "S", "M", "L", "XL"].map(x => <button key={x} onClick={() => update("talla", f.talla === x ? "" : x)} className={`size-9 rounded-lg text-xs font-bold ${f.talla === x ? "bg-stone-900 text-white" : "bg-stone-100"}`}>{x}</button>)}</div></div>
    <label className="block"><span className="label flex justify-between"><span>Precio máximo</span><b>{f.precio_max ?? 150} €</b></span><input type="range" min="20" max="150" value={f.precio_max ?? 150} onChange={e => update("precio_max", +e.target.value)} className="w-full accent-[#596348]" /></label>
    <label className="flex items-center gap-3 text-sm font-semibold"><input type="checkbox" checked={f.solo_disponibles ?? false} onChange={e => update("solo_disponibles", e.target.checked)} className="size-4 accent-[#596348]" />Solo con stock</label>
  </div>;
  return <main className="page"><PageTitle eyebrow={<EtiquetaMotor motor="MongoDB" />} title="Piezas para cada día." text="Una colección serena, funcional y creada para durar. Encuentra tu próxima prenda esencial." action={<button onClick={() => setFilters(true)} className="btn-secondary lg:hidden"><SlidersHorizontal size={17} />Filtros</button>} />
    <div className="grid gap-8 lg:grid-cols-[250px_1fr]"><aside className="hidden self-start rounded-3xl border border-stone-200 bg-white p-6 lg:block"><div className="mb-6 flex items-center gap-2 font-black"><SlidersHorizontal size={18} />Filtrar colección</div>{form}</aside>
      <section>{error ? <ErrorBox message={error} /> : loading && !items.length ? <Loading /> : !items.length ? <Empty title="Sin resultados" text="Prueba a ajustar los filtros de búsqueda." /> : <><div className="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">{items.map(p => <ProductCard key={p.id} producto={p} />)}</div>{more && <div className="mt-10 text-center"><button disabled={loading} onClick={() => setF(p => ({ ...p, saltar: items.length }))} className="btn-secondary">{loading ? "Cargando…" : "Cargar más"}</button></div>}</>}</section>
    </div>
    {filters && <div className="fixed inset-0 z-50 bg-stone-900/30 backdrop-blur-sm lg:hidden"><div className="absolute inset-y-0 right-0 w-[88%] max-w-sm overflow-auto bg-white p-6"><div className="mb-8 flex items-center justify-between text-xl font-black">Filtros<button onClick={() => setFilters(false)}><X /></button></div>{form}<button className="btn-primary mt-8 w-full" onClick={() => setFilters(false)}>Ver resultados</button></div></div>}
  </main>;
}
