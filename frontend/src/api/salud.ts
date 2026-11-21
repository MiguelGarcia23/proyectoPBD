import { API_URL, USE_MOCK } from "../config";
import type { Salud } from "../types/api";
import { wait } from "./mock/data";

// /health devuelve 200 si todo va bien y 503 si algún motor falla.
// En los dos casos el cuerpo trae el estado de cada motor, así que se lee
// igualmente (apiGet lanzaría un error con el 503 y se perdería esa información).
export async function health(): Promise<Salud> {
  if (USE_MOCK) return wait<Salud>({ estado: "ok", motores: { mongodb: "ok", cassandra: "ok", neo4j: "ok" } }, 120);
  const response = await fetch(`${API_URL}/health`);
  if (response.status !== 200 && response.status !== 503) throw new Error(`Error ${response.status}`);
  return response.json();
}
