from pydantic import BaseModel

class Envio(BaseModel):
    direccion_entrega : str
    direccion_origen: str
    transportista : str
    precio :float
    id_producto : int