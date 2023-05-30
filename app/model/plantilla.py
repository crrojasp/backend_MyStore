from pydantic import BaseModel

class Plantilla(BaseModel):
    nombre      : str
    descripcion : str
    secciones   : str
    diseño      : str
    tipo        : str
    url         : str