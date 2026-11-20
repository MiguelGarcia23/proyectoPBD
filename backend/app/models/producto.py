from typing import Literal

from pydantic import BaseModel, Field, model_validator

# Valores cerrados
Categoria = Literal["Camisetas", "Camisas", "Sudaderas", "Pantalones",
                    "Vestidos", "Chaquetas", "Calzado", "Accesorios"]
Genero = Literal["hombre", "mujer", "unisex"]

class Variante(BaseModel):
    """Una combinación concreta de talla y color, con su propio stock."""
    sku: str = Field(min_length=1, examples=["CAM-BAS-BLA-M"])
    talla: str = Field(min_length=1, examples=["M"])
    color: str = Field(min_length=1, examples=["blanco"])
    stock: int = Field(ge=0, examples=[40])

class ProductoCrear(BaseModel):
    """Datos que se envían para dar de alta una prenda."""
    nombre: str = Field(min_length=1)
    descripcion: str | None = None
    precio: float = Field(gt=0)
    categoria: Categoria
    genero: Genero
    imagen: str | None = None
    atributos: dict = Field(default_factory=dict, description="Características libres según el tipo de prenda")
    variantes: list[Variante] = Field(min_length=1)

    @model_validator(mode="after")
    def skus_sin_repetir(self):
        """El índice único de MongoDB impide repetir un SKU entre prendas
        distintas, pero no dentro de la misma prenda"""
        skus = [v.sku for v in self.variantes]
        if len(skus) != len(set(skus)):
            raise ValueError("Hay variantes con el SKU repetido")
        return self

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "nombre": "Camiseta básica algodón",
                "descripcion": "Camiseta de manga corta 100% algodón orgánico",
                "precio": 14.99,
                "categoria": "Camisetas",
                "genero": "unisex",
                "imagen": "camiseta-basica.jpg",
                "atributos": {"material": "algodón orgánico", "manga": "corta"},
                "variantes": [
                    {"sku": "CAM-BAS-BLA-S", "talla": "S", "color": "blanco", "stock": 25},
                    {"sku": "CAM-BAS-BLA-M", "talla": "M", "color": "blanco", "stock": 40},
                ],
            }]
        }
    }

class Producto(ProductoCrear):
    """Prenda tal y como la devuelve la API (con su id)."""
    id: str