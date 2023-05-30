from sqlalchemy import Enum
from app.model.mixins import TimeMixin
from pydantic import BaseModel

class Vendedor(BaseModel):
    nombre_tienda   : str
    rues            : int
    historial_ventas: str
    nombre          : str