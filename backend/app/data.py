"""
Uso (con los contenedores en marcha):
    docker compose exec api python -m app.seed           # solo si la tienda está vacía
    docker compose exec api python -m app.seed --reset   # borra todo y vuelve a cargar
"""
import argparse
import logging
import random
import sys
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException

from app.db import cassandra_db, mongo_db, neo4j_db
from app.models.pedido import LineaCompra, PedidoCrear
from app.models.producto import ProductoCrear
from app.models.usuario import UsuarioCrear
from app.routers.productos import crear_producto
from app.routers.usuarios import crear_usuario
from app.services.compra import realizar_compra
from app.services.visita import registrar_visita

logging.basicConfig(level=logging.WARNING)
random.seed(42)  # siempre se generan los mismos datos

DIAS = 30            # periodo simulado
NUM_COMPRAS = 70
VISITAS_POR_USUARIO = 25
VISITAS_ANONIMAS = 150


# ============================================================
#  Catálogo
#  El "estilo" se guarda en atributos y sirve para que los usuarios compren "looks" coherentes -> dar recomendaciones con sentido
# ============================================================
ROPA = ["XS", "S", "M", "L", "XL"]
PIE_MUJER = ["36", "37", "38", "39", "40"]
PIE_HOMBRE = ["40", "41", "42", "43", "44"]
PANT = ["36", "38", "40", "42", "44"]
UNICA = ["Única"]

CATALOGO = [
    # --- Urbano ---
    ("Camiseta básica algodón", "Camisetas", "unisex", 14.99, "urbano", ROPA, ["blanco", "negro", "gris"],
     {"material": "algodón orgánico", "manga": "corta", "cuello": "redondo"}),
    ("Camiseta oversize estampada", "Camisetas", "unisex", 19.99, "urbano", ROPA, ["negro", "beige"],
     {"material": "algodón", "manga": "corta", "corte": "oversize"}),
    ("Sudadera con capucha", "Sudaderas", "unisex", 34.95, "urbano", ROPA, ["gris", "negro", "verde"],
     {"material": "algodón perchado", "capucha": True, "bolsillo": "canguro"}),
    ("Vaqueros slim", "Pantalones", "mujer", 39.95, "urbano", PANT, ["azul", "negro"],
     {"material": "denim elástico", "tiro": "alto", "corte": "slim"}),
    ("Vaqueros rectos", "Pantalones", "hombre", 39.95, "urbano", PANT, ["azul", "gris"],
     {"material": "denim", "corte": "recto"}),
    ("Cazadora vaquera", "Chaquetas", "unisex", 49.95, "urbano", ROPA, ["azul"],
     {"material": "denim", "cierre": "botones"}),
    ("Zapatillas urbanas", "Calzado", "mujer", 59.95, "urbano", PIE_MUJER, ["blanco", "negro"],
     {"material": "piel sintética", "suela": "goma", "cierre": "cordones"}),
    ("Zapatillas lona", "Calzado", "hombre", 44.95, "urbano", PIE_HOMBRE, ["blanco", "azul"],
     {"material": "lona", "suela": "goma", "cierre": "cordones"}),
    ("Gorra de algodón", "Accesorios", "unisex", 12.99, "urbano", UNICA, ["negro", "beige"],
     {"material": "algodón", "ajuste": "regulable"}),
    # --- Clásico ---
    ("Camisa Oxford", "Camisas", "hombre", 29.95, "clasico", ROPA, ["blanco", "azul celeste"],
     {"material": "algodón Oxford", "cuello": "abotonado", "manga": "larga"}),
    ("Blusa de lino", "Camisas", "mujer", 32.95, "clasico", ROPA, ["blanco", "crudo"],
     {"material": "lino", "manga": "larga"}),
    ("Pantalón chino", "Pantalones", "hombre", 35.95, "clasico", PANT, ["beige", "azul marino"],
     {"material": "algodón", "corte": "slim"}),
    ("Pantalón palazzo", "Pantalones", "mujer", 37.95, "clasico", PANT, ["negro", "camel"],
     {"material": "viscosa", "corte": "ancho", "tiro": "alto"}),
    ("Vestido midi estampado", "Vestidos", "mujer", 45.95, "clasico", ROPA, ["azul", "verde"],
     {"material": "viscosa", "largo": "midi", "manga": "corta"}),
    ("Vestido camisero", "Vestidos", "mujer", 42.95, "clasico", ROPA, ["blanco", "rayas"],
     {"material": "algodón", "largo": "rodilla", "cinturón": True}),
    ("Blazer", "Chaquetas", "unisex", 69.95, "clasico", ROPA, ["negro", "azul marino"],
     {"material": "lana mezcla", "botones": 2, "forro": True}),
    ("Mocasines de piel", "Calzado", "hombre", 79.95, "clasico", PIE_HOMBRE, ["marrón", "negro"],
     {"material": "piel", "suela": "cuero"}),
    ("Cinturón de piel", "Accesorios", "unisex", 24.95, "clasico", ["85", "95", "105"], ["marrón", "negro"],
     {"material": "piel", "hebilla": "metálica"}),
    # --- Deportivo ---
    ("Camiseta técnica running", "Camisetas", "unisex", 17.95, "deportivo", ROPA, ["negro", "azul", "naranja"],
     {"material": "poliéster reciclado", "transpirable": True, "manga": "corta"}),
    ("Camiseta tirantes training", "Camisetas", "mujer", 15.95, "deportivo", ROPA, ["negro", "rosa"],
     {"material": "poliéster", "transpirable": True}),
    ("Sudadera técnica cremallera", "Sudaderas", "unisex", 39.95, "deportivo", ROPA, ["negro", "gris"],
     {"material": "poliéster", "cierre": "cremallera"}),
    ("Sudadera básica cuello redondo", "Sudaderas", "hombre", 27.95, "deportivo", ROPA, ["azul marino", "gris"],
     {"material": "algodón"}),
    ("Vestido deportivo", "Vestidos", "mujer", 34.95, "deportivo", ROPA, ["negro", "verde"],
     {"material": "punto técnico", "largo": "corto"}),
    ("Cortavientos ligero", "Chaquetas", "unisex", 54.95, "deportivo", ROPA, ["negro", "amarillo"],
     {"material": "nylon", "impermeable": True, "capucha": True}),
]

USUARIOS = [
    ("Lucía Martín", "lucia@example.com", "Madrid", "mujer", "urbano"),
    ("Pablo García", "pablo@example.com", "Valencia", "hombre", "urbano"),
    ("Marta López", "marta@example.com", "Sevilla", "mujer", "urbano"),
    ("Carlos Ruiz", "carlos@example.com", "Madrid", "hombre", "clasico"),
    ("Elena Sánchez", "elena@example.com", "Barcelona", "mujer", "clasico"),
    ("Ana Torres", "ana@example.com", "Bilbao", "mujer", "clasico"),
    ("Javier Moreno", "javier@example.com", "Zaragoza", "hombre", "deportivo"),
    ("Sara Navarro", "sara@example.com", "Málaga", "mujer", "deportivo"),
]

def _sku(nombre: str, color: str, talla: str) -> str:
    """'Camiseta básica algodón', 'blanco', 'M' -> 'CAM-BAS-ALG-BLA-M'."""
    trozos = [p[:3].upper() for p in nombre.split() if len(p) > 2][:3]
    limpio = lambda t: (t.upper().replace("Á", "A").replace("É", "E").replace("Í", "I")
                        .replace("Ó", "O").replace("Ú", "U").replace("Ñ", "N").replace(" ", ""))
    return "-".join(limpio(t) for t in trozos + [color[:3], talla])

def _slug(texto: str) -> str:
    """'Camiseta básica algodón' -> 'camiseta-basica-algodon'."""
    tabla = str.maketrans("áéíóúñü", "aeiounu")
    return "-".join(texto.lower().translate(tabla).split())

def _momento_aleatorio() -> datetime:
    """Un instante aleatorio de los últimos X días (más actividad en los recientes)"""
    dias_atras = int(random.triangular(0, DIAS, 0))
    hora = random.randint(9, 22)
    return (datetime.now(timezone.utc).replace(hour=hora, minute=random.randint(0, 59), second=0, microsecond=0)
            - timedelta(days=dias_atras))

def borrar_todo() -> None:
    print("Borrando datos anteriores")
    db = mongo_db.get_db()
    for coleccion in ("productos", "usuarios", "pedidos"):
        db[coleccion].delete_many({})  # se conservan índices y validación
    s = cassandra_db.get_session()
    for tabla in ("visitas_producto_dia", "ventas_por_dia", "resumen_ventas_dia",
                  "ventas_producto_mes", "ventas_talla_mes"):
        s.execute(f"TRUNCATE {tabla}")
    neo4j_db.get_driver().execute_query("MATCH (n) DETACH DELETE n", database_="neo4j")

def cargar_prendas() -> list[dict]:
    prendas = []
    for nombre, cat, genero, precio, estilo, tallas, colores, atributos in CATALOGO:
        variantes = [{"sku": _sku(nombre, c, t), "talla": t, "color": c, "stock": random.randint(15, 40)}
                     for c in colores for t in tallas]
        p = crear_producto(ProductoCrear(
            nombre=nombre, categoria=cat, genero=genero, precio=precio,
            descripcion=f"{nombre} de estilo {estilo}.",
            imagen=_slug(nombre) + ".jpg",
            atributos={**atributos, "estilo": estilo}, variantes=variantes,
        ))
        prendas.append(p)
    return prendas

def cargar_usuarios() -> list[dict]:
    usuarios = []
    for nombre, email, ciudad, genero, estilo in USUARIOS:
        u = crear_usuario(UsuarioCrear(
            nombre=nombre, email=email,
            direccion={"calle": "Calle Mayor 1", "ciudad": ciudad, "cp": "00000"},
        ))
        usuarios.append({**u, "genero_pref": genero, "estilo_pref": estilo})
    return usuarios

def _prendas_para(usuario: dict, prendas: list[dict], afinidad: float) -> list[dict]:
    """Prendas compatibles con el género del usuario"""
    compatibles = [p for p in prendas if p["genero"] in (usuario["genero_pref"], "unisex")]
    if random.random() < afinidad:
        compatibles = [p for p in compatibles if p["atributos"]["estilo"] == usuario["estilo_pref"]]
    return compatibles

def cargar_visitas(usuarios: list[dict], prendas: list[dict]) -> int:
    total = 0
    for u in usuarios:
        for _ in range(VISITAS_POR_USUARIO):
            registrar_visita(random.choice(_prendas_para(u, prendas, 0.7)), u["id"], _momento_aleatorio())
            total += 1
    for _ in range(VISITAS_ANONIMAS):  # visitantes sin cuenta: solo cuentan en Cassandra
        registrar_visita(random.choice(prendas), None, _momento_aleatorio())
        total += 1
    return total

def cargar_compras(usuarios: list[dict], prendas: list[dict]) -> int:
    """Cada compra es un 'look': 1-3 prendas de categorías distintas"""
    hechas = 0
    for _ in range(NUM_COMPRAS):
        u = random.choice(usuarios)
        candidatas = _prendas_para(u, prendas, 0.85)
        random.shuffle(candidatas)
        look, categorias = [], set()
        for p in candidatas:
            if p["categoria"] not in categorias:
                look.append(p)
                categorias.add(p["categoria"])
            if len(look) == random.choice([1, 2, 2, 3, 3]):
                break
        lineas = [LineaCompra(producto_id=p["id"], sku=random.choice(p["variantes"])["sku"],
                              cantidad=random.choice([1, 1, 1, 2])) for p in look]
        try:
            realizar_compra(PedidoCrear(usuario_id=u["id"], lineas=lineas), fecha=_momento_aleatorio())
            hechas += 1
        except HTTPException as e:  # p. ej. sin stock: se salta esa compra
            print(f"  compra omitida: {e.detail}")
    return hechas

def main() -> None:
    parser = argparse.ArgumentParser(description="Carga datos de ejemplo en la tienda")
    parser.add_argument("--reset", action="store_true", help="borra los datos actuales antes de cargar")
    args = parser.parse_args()

    mongo_db.conectar()
    cassandra_db.conectar()
    neo4j_db.conectar()
    try:
        if args.reset:
            borrar_todo()
        elif mongo_db.get_db().productos.count_documents({}) > 0:
            print("La tienda ya tiene datos. Usa --reset para borrarlos y volver a cargar.")
            sys.exit(1)

        print("Creando prendas...")
        prendas = cargar_prendas()
        print("Creando usuarios...")
        usuarios = cargar_usuarios()
        print("Registrando visitas...")
        n_visitas = cargar_visitas(usuarios, prendas)
        print("Realizando compras...")
        n_compras = cargar_compras(usuarios, prendas)

        print("\n=== Datos de ejemplo cargados ===")
        print(f"  Prendas:  {len(prendas)} ({sum(len(p['variantes']) for p in prendas)} variantes)")
        print(f"  Usuarios: {len(usuarios)}")
        print(f"  Visitas:  {n_visitas}")
        print(f"  Compras:  {n_compras}")
        print("\nIds útiles para probar en /docs:")
        print(f"  usuario_id (Lucía, urbano):  {usuarios[0]['id']}")
        print(f"  usuario_id (Carlos, clásico): {usuarios[3]['id']}")
        print(f"  producto_id (Camiseta básica): {prendas[0]['id']}")
        print(f"  producto_id (Camisa Oxford):   {prendas[9]['id']}")
    finally:
        mongo_db.cerrar()
        cassandra_db.cerrar()
        neo4j_db.cerrar()

if __name__ == "__main__":
    main()