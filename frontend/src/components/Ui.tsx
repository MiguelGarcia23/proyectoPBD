import type { ReactNode } from "react";
import { AlertCircle, LoaderCircle } from "lucide-react";
export const eur = (n: number) => new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR" }).format(n);
export const fecha = (d: string) => new Intl.DateTimeFormat("es-ES", { dateStyle: "medium" }).format(new Date(d));
export function PageTitle({ eyebrow, title, text, action }: { eyebrow?: ReactNode; title: string; text?: string; action?: ReactNode }) {
  return <div className="mb-8 flex flex-wrap items-end justify-between gap-5"><div>{eyebrow && <div className="mb-3">{eyebrow}</div>}<h1 className="text-4xl font-black tracking-[-.04em] text-stone-900 md:text-5xl">{title}</h1>{text && <p className="mt-3 max-w-2xl text-stone-500">{text}</p>}</div>{action}</div>;
}
export function Loading({ text = "Cargando datos…" }: { text?: string }) { return <div className="flex min-h-52 items-center justify-center gap-3 rounded-2xl border border-stone-200 bg-white text-sm text-stone-500"><LoaderCircle className="animate-spin" size={18} />{text}</div>; }
export function ErrorBox({ message }: { message: string }) { return <div className="flex items-center gap-3 rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700"><AlertCircle size={19} />{message}</div>; }
export function Empty({ title, text }: { title: string; text: string }) { return <div className="rounded-3xl border border-dashed border-stone-300 bg-white px-6 py-16 text-center"><h2 className="text-xl font-bold">{title}</h2><p className="mt-2 text-sm text-stone-500">{text}</p></div>; }
