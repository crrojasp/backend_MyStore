from pydantic import BaseModel

class Comprador(BaseModel):
    direccion: str
    telefono: int
    historial_compras : str
    name : str