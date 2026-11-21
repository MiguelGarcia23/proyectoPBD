export type Motor = "MongoDB" | "Cassandra" | "Neo4j";
const colors: Record<Motor, string> = {
  MongoDB: "bg-emerald-50 text-emerald-700 border-emerald-200",
  Cassandra: "bg-sky-50 text-sky-700 border-sky-200",
  Neo4j: "bg-violet-50 text-violet-700 border-violet-200",
};
export function EtiquetaMotor({ motor }: { motor: Motor }) {
  return <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-[10px] font-bold uppercase tracking-[.12em] ${colors[motor]}`}>{motor}</span>;
}
