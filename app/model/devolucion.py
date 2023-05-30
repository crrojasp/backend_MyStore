from pydantic import BaseModel
from datetime import date

class Devolucion(BaseModel):
    fecha_solicitud : date
    id_producto: int
    id_vendedor : int
    id_comprador :int
    razon : str
    id_envio : int