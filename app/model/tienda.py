from pydantic import BaseModel
from datetime import date

class Tienda(BaseModel):
    nombre : str
    direccion : str
    id_vendedor : int
    productos : str