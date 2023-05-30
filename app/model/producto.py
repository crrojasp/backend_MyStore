from pydantic import BaseModel

class Producto(BaseModel):
    nombre: str
    descripcion: str
    precio: float
    ilustracion: bytes