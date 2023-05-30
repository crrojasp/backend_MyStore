from pydantic import BaseModel
from datetime import date


class Compra(BaseModel):
    fecha : date
    total : float
    estado : str
    id_comprador : int
