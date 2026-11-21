import { ChevronDown, Package } from "lucide-react";
import { useEffect, useState } from "react";
import { pedidosDeUsuario } from "../api/pedidos";
import { EtiquetaMotor } from "../components/EtiquetaMotor";
import { Empty, eur, fecha, Loading, PageTitle } from "../components/Ui";
import { useUsuario } from "../context/UsuarioContext";
import type { Pedido } from "../types/api";
export function MisPedidos() {
  const { usuario } = useUsuario(); const [items, setItems] = useState<Pedido[]>(); const [open, setOpen] = useState("");
  useEffect(() => { if (!usuario) return setItems(undefined); pedidosDeUsuario(usuario.id).then(setItems).catch(() => setItems([])); }, [usuario]);
  return <main className="page max-w-5xl"><PageTitle eyebrow={<EtiquetaMotor motor="MongoDB" />} title="Mis pedidos" text="Consulta el estado y el detalle de tus compras." />{!usuario ? <Empty title="Selecciona un usuario" text="Elige un perfil en la cabecera para consultar su historial." /> : !items ? <Loading /> : !items.length ? <Empty title="Aún no hay pedidos" text="Cuando hagas tu primera compra aparecerá aquí." /> : <div className="space-y-3">{items.map(p => <article key={p.id} className="overflow-hidden rounded-2xl border border-stone-200 bg-white"><button onClick={() => setOpen(open === p.id ? "" : p.id)} className="flex w-full items-center gap-5 p-5 text-left"><span className="grid size-11 place-items-center rounded-xl bg-[#e7e5dc] text-[#596348]"><Package size={20} /></span><span className="flex-1"><b className="block">Pedido #{p.id.slice(-8)}</b><small className="text-stone-500">{fecha(p.fecha)}</small></span><span className="hidden rounded-full bg-amber-50 px-3 py-1 text-xs font-bold text-amber-700 sm:block">{p.estado}</span><span className="hidden text-sm text-stone-500 sm:block">{p.lineas.reduce((s, l) => s + l.cantidad, 0)} prendas</span><b>{eur(p.total)}</b><ChevronDown className={`transition ${open === p.id ? "rotate-180" : ""}`} size={18} /></button>{open === p.id && <div className="border-t border-stone-100 bg-stone-50 px-5 py-4">{p.lineas.map(l => <div key={l.sku} className="flex justify-between border-b border-stone-200 py-3 text-sm last:border-0"><span><b>{l.nombre}</b><small className="ml-2 text-stone-500">{l.color} · {l.talla} · ×{l.cantidad}</small></span><b>{eur(l.precio_unitario * l.cantidad)}</b></div>)}</div>}</article>)}</div>}</main>;
}
