from pydantic import BaseModel

class Tipo(str):
    VENDEDOR    = "vendedor"
    COMPRADOR   = "comprador"

class User(BaseModel):
    name: str
    email: str
    cellphone : str
    password: str
    tipo        : Tipo 

class UserLogin(BaseModel):
    email    : str
    password: str