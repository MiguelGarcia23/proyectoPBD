import { createBrowserRouter, Outlet } from "react-router";
import { Header } from "../components/Header";
import { Carrito } from "../pages/Carrito";
import { Catalogo } from "../pages/Catalogo";
import { Metricas } from "../pages/Metricas";
import { MisPedidos } from "../pages/MisPedidos";
import { ParaTi } from "../pages/ParaTi";
import { Producto } from "../pages/Producto";
function Root() { return <><Header /><Outlet /><footer className="border-t border-stone-200 px-5 py-10 text-center text-xs font-semibold text-stone-400">NoSQL Wear · MongoDB + Cassandra + Neo4j</footer></>; }
export const router = createBrowserRouter([{ path: "/", Component: Root, children: [{ index: true, Component: Catalogo }, { path: "producto/:id", Component: Producto }, { path: "carrito", Component: Carrito }, { path: "para-ti", Component: ParaTi }, { path: "pedidos", Component: MisPedidos }, { path: "metricas", Component: Metricas }, { path: "*", Component: Catalogo }] }]);
