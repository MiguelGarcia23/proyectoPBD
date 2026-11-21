import { USE_MOCK } from "../config";
import type { Usuario } from "../types/api";
import { apiGet } from "./client";
import { usuarios, wait } from "./mock/data";
export const listarUsuarios = () => USE_MOCK ? wait(usuarios) : apiGet<Usuario[]>("/usuarios");
export const obtenerUsuario = (id: string) => USE_MOCK ? wait(usuarios.find(u => u.id === id)!) : apiGet<Usuario>(`/usuarios/${id}`);
