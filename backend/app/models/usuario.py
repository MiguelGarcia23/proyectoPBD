from datetime import datetime

from pydantic import BaseModel, Field

class Direccion(BaseModel):
    calle: str
    ciudad: str
    cp: str

class UsuarioCrear(BaseModel):
    """Datos que se envían para registrar un usuario"""
    nombre: str = Field(min_length=1, examples=["Lucía Martín"])
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", examples=["lucia@example.com"])
    direccion: Direccion | None = None

class Usuario(UsuarioCrear):
    """Usuario tal y como lo devuelve la API"""
    id: str
    fecha_alta: datetime