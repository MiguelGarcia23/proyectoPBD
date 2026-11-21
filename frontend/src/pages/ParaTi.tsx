import { Sparkles } from "lucide-react";
import { useEffect, useState } from "react";
import { paraTi, vistosNoComprados } from "../api/recomendaciones";
import { EtiquetaMotor } from "../components/EtiquetaMotor";
import { MiniProductCard } from "../components/ProductCard";
import { Empty, Loading, PageTitle } from "../components/Ui";
import { useUsuario } from "../context/UsuarioContext";
import type { Recomendacion } from "../types/api";
function Row({ title, text, items }: { title: string; text: string; items: Recomendacion[] }) { if (!items.length) return null; return <section className="mt-12"><h2 className="text-2xl font-black">{title}</h2><p className="mb-5 mt-1 text-sm text-stone-500">{text}</p><div className="flex gap-4 overflow-x-auto pb-4">{items.map(x => <MiniProductCard key={x.producto_id} producto={x} />)}</div></section>; }
export function ParaTi() {
  const { usuario } = useUsuario(); const [data, setData] = useState<{ para: Recomendacion[]; vistos: Recomendacion[] }>(); 
  useEffect(() => { if (!usuario) { setData(undefined); return; } Promise.allSettled([paraTi(usuario.id), vistosNoComprados(usuario.id)]).then(([a, b]) => setData({ para: a.status === "fulfilled" ? a.value : [], vistos: b.status === "fulfilled" ? b.value : [] })); }, [usuario]);
  return <main className="page"><PageTitle eyebrow={<div className="flex items-center gap-2"><EtiquetaMotor motor="Neo4j" /><Sparkles size={18} className="text-[#596348]" /></div>} title={usuario ? `Elegido para ${usuario.nombre.split(" ")[0]}` : "Una selección para ti"} text="Recomendaciones creadas a partir de afinidades, visitas y compras." />{!usuario ? <Empty title="Selecciona un usuario" text="Elige un perfil en la cabecera para ver recomendaciones personalizadas." /> : !data ? <Loading text="Buscando prendas afines…" /> : <><Row title="Recomendado para ti" text="Personas con gustos parecidos también eligieron estas prendas." items={data.para} /><Row title="Lo viste y te puede interesar" text="Una segunda mirada a las piezas que llamaron tu atención." items={data.vistos} /></>}</main>;
}
