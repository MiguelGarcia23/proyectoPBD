import { Shirt } from "lucide-react";
import { useEffect, useState } from "react";
import type { Categoria } from "../types/api";

type ProductoConImagen = {
  nombre: string;
  imagen?: string | null;
  categoria?: Categoria;
};

const imagenesCategoria: Partial<Record<Categoria, string>> = {
  Camisetas: "categoria-camisetas.jpg",
  Camisas: "categoria-camisas.jpg",
  Sudaderas: "categoria-sudaderas.jpg",
  Pantalones: "categoria-pantalones.jpg",
  Vestidos: "categoria-vestidos.jpg",
  Chaquetas: "categoria-chaquetas.jpg",
  Calzado: "categoria-calzado.jpg",
  Accesorios: "categoria-accesorios.jpg",
};

export function ImagenPrenda({
  producto,
  compact = false,
  className = "",
}: {
  producto: ProductoConImagen;
  compact?: boolean;
  className?: string;
}) {
  const [intento, setIntento] = useState(0);
  const principal = producto.imagen ? `/img/${producto.imagen}` : null;
  const fallback = producto.categoria ? imagenesCategoria[producto.categoria] : null;
  const fuentes = [principal, fallback ? `/img/${fallback}` : null].filter(Boolean) as string[];

  useEffect(() => setIntento(0), [producto.imagen, producto.categoria]);

  const base = `relative grid place-items-center overflow-hidden bg-[#e7e5dc] ${compact ? "h-36" : "aspect-[4/4.8]"} ${className}`;
  if (intento < fuentes.length) {
    return (
      <div className={base}>
        <img
          src={fuentes[intento]}
          alt={producto.nombre}
          className="size-full object-cover transition duration-500 group-hover:scale-[1.025]"
          loading={compact ? "lazy" : "eager"}
          onError={() => setIntento((actual) => actual + 1)}
        />
        {producto.categoria && <span className="absolute bottom-4 left-4 rounded-full bg-white/85 px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-stone-700 shadow-sm backdrop-blur">{producto.categoria}</span>}
      </div>
    );
  }

  return (
    <div className={base}>
      <div className="absolute -right-10 -top-10 size-36 rounded-full bg-[#cbd2bd]" />
      <div className="absolute -bottom-12 -left-8 size-40 rounded-full bg-[#efe1d7]" />
      <Shirt className="relative text-[#596348]" size={compact ? 42 : 60} strokeWidth={1.2} />
      {producto.categoria && <span className="absolute bottom-4 left-4 rounded-full bg-white/80 px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-stone-600 backdrop-blur">{producto.categoria}</span>}
    </div>
  );
}
