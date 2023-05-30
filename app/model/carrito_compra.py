from pydantic import BaseModel

class Carrito(BaseModel):
    productos : str
    id_comprador : str