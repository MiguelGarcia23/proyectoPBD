import { BarChart3, Menu, ShoppingBag, X } from "lucide-react";
import { useState } from "react";
import { Link, NavLink } from "react-router";
import { useCarrito } from "../context/CarritoContext";
import { useUsuario } from "../context/UsuarioContext";
import { EstadoMotores } from "./EstadoMotores";
const links = [["/", "Catálogo"], ["/para-ti", "Para ti"], ["/pedidos", "Mis pedidos"], ["/metricas", "Métricas"]];
export function Header() {
  const { usuario, usuarios, empleado, seleccionar, entrarComoEmpleado } = useUsuario(); const { unidades } = useCarrito(); const [open, setOpen] = useState(false);
  // Clientes: Invitado o cualquier usuario de GET /usuarios (para comparar sus recomendaciones).
  // Empleado: perfil aparte, el único que ve "Métricas".
  const visibleLinks = empleado ? links : links.filter(([to]) => to !== "/metricas");
  const valor = empleado ? "__empleado" : usuario?.id ?? "";
  const cambiarPerfil = (v: string) => v === "__empleado" ? entrarComoEmpleado() : seleccionar(usuarios.find(u => u.id === v) ?? null);
  return <header className="sticky top-0 z-40 border-b border-stone-200/80 bg-[#faf9f6]/95 backdrop-blur-xl">
    <div className="mx-auto flex h-20 max-w-[1440px] items-center gap-5 px-5 lg:px-10">
      <Link to="/" className="mr-auto flex items-center gap-2 text-xl font-black tracking-tight text-stone-900"><span className="grid size-9 place-items-center rounded-xl bg-[#596348] text-sm text-white">PBD</span>Tienda</Link>
      <nav className="hidden items-center gap-1 md:flex">{visibleLinks.map(([to, label]) => <NavLink key={to} to={to} className={({ isActive }) => `rounded-full px-4 py-2 text-sm font-semibold ${isActive ? "bg-stone-900 text-white" : "text-stone-600 hover:bg-stone-100"}`}>{label}</NavLink>)}</nav>
      <EstadoMotores />
      <select aria-label="Perfil seleccionado" value={valor} onChange={e => cambiarPerfil(e.target.value)} className="max-w-48 rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-sm font-semibold outline-none focus:border-[#596348]">
        <option value="">Invitado</option>
        <optgroup label="Clientes">
          {usuarios.map(u => <option key={u.id} value={u.id}>{u.nombre}</option>)}
        </optgroup>
        <optgroup label="Personal de la tienda">
          <option value="__empleado">Empleado (panel interno)</option>
        </optgroup>
      </select>
      <Link to="/carrito" className="relative grid size-11 place-items-center rounded-xl bg-stone-900 text-white" aria-label={`Carrito, ${unidades} unidades`}><ShoppingBag size={19} /><span className="absolute -right-1.5 -top-1.5 grid min-w-5 place-items-center rounded-full bg-[#b45f45] px-1 text-[10px] font-bold">{unidades}</span></Link>
      <button className="md:hidden" onClick={() => setOpen(!open)} aria-label="Abrir menú">{open ? <X /> : <Menu />}</button>
    </div>
    {open && <nav className="grid gap-1 border-t border-stone-200 p-4 md:hidden">{visibleLinks.map(([to, label]) => <NavLink onClick={() => setOpen(false)} key={to} to={to} className="flex items-center gap-2 rounded-xl px-4 py-3 font-semibold hover:bg-stone-100">{label === "Métricas" && <BarChart3 size={17} />}{label}</NavLink>)}</nav>}
  </header>;
}
