from pydantic import BaseModel
from datetime import date

class Venta(BaseModel):
    fecha: date
    total: float
    estado: str
    id_vendedor: int
    productos : str