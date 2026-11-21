import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { listarUsuarios } from "../api/usuarios";
import type { Usuario } from "../types/api";

// Perfiles de la demo (no hay login):
// - Invitado: usuario = null, empleado = false
// - Cliente:  usuario = el elegido, empleado = false
// - Empleado: usuario = null, empleado = true  -> único perfil que ve el panel de métricas
interface UsuarioState {
  usuario: Usuario | null; usuarios: Usuario[]; empleado: boolean;
  seleccionar: (u: Usuario | null) => void; entrarComoEmpleado: () => void;
}
const Context = createContext<UsuarioState | null>(null);
export function UsuarioProvider({ children }: { children: ReactNode }) {
  const [usuarios, setUsuarios] = useState<Usuario[]>([]);
  const [usuario, setUsuario] = useState<Usuario | null>(() => JSON.parse(localStorage.getItem("nosql-usuario") || "null"));
  useEffect(() => {
    listarUsuarios().then(lista => {
      setUsuarios(lista);
      // Tras recargar los datos de ejemplo los ids cambian: si el guardado ya no existe, pasa a Invitado
      setUsuario(actual => (actual && !lista.some(u => u.id === actual.id) ? null : actual));
    }).catch(() => setUsuarios([]));
  }, []);
  const [empleado, setEmpleado] = useState<boolean>(() => localStorage.getItem("nosql-empleado") === "true");
  const seleccionar = (u: Usuario | null) => {
    setUsuario(u); setEmpleado(false);
    localStorage.setItem("nosql-usuario", JSON.stringify(u)); localStorage.setItem("nosql-empleado", "false");
  };
  const entrarComoEmpleado = () => {
    setUsuario(null); setEmpleado(true);
    localStorage.setItem("nosql-usuario", "null"); localStorage.setItem("nosql-empleado", "true");
  };
  return <Context.Provider value={{ usuario, usuarios, empleado, seleccionar, entrarComoEmpleado }}>{children}</Context.Provider>;
}
export function useUsuario() { const v = useContext(Context); if (!v) throw new Error("UsuarioContext no disponible"); return v; }
