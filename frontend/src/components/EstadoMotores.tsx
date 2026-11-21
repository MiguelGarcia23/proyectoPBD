import { useEffect, useState } from "react";
import { health } from "../api/salud";
import type { Salud } from "../types/api";
export function EstadoMotores() {
  const [estado, setEstado] = useState<Salud["motores"] | null>(null);
  useEffect(() => { const load = () => health().then(x => setEstado(x.motores)).catch(() => setEstado({ mongodb: "error", cassandra: "error", neo4j: "error" })); load(); const t = setInterval(load, 30000); return () => clearInterval(t); }, []);
  return <div className="hidden items-center gap-3 rounded-full border border-stone-200 bg-white px-3 py-2 lg:flex" aria-label="Estado de los motores">
    {(["mongodb", "cassandra", "neo4j"] as const).map(x => <div key={x} className="flex items-center gap-1.5 text-[10px] font-semibold capitalize text-stone-500"><i className={`size-2 rounded-full ${estado?.[x] === "ok" ? "bg-emerald-500" : "bg-red-400"} ${!estado ? "animate-pulse" : ""}`} />{x}</div>)}
  </div>;
}
