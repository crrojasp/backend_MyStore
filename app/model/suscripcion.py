from pydantic import BaseModel
from datetime import date

class Suscripcion(BaseModel):
    fecha_inicio: date
    fecha_fin   : date
    precio      : float
    tipo        : str
    id_usuario  : int