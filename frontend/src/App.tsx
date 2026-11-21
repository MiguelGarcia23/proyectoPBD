import { RouterProvider } from "react-router";
import { router } from "./app/routes";
import { CarritoProvider } from "./context/CarritoContext";
import { UsuarioProvider } from "./context/UsuarioContext";
export default function App() {
  return <UsuarioProvider><CarritoProvider><RouterProvider router={router} /></CarritoProvider></UsuarioProvider>;
}
