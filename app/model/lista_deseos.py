from pydantic import BaseModel

class ListaDeseos(BaseModel):
    productos : str
    id_comprador : int
