from fastapi import APIRouter
from app.model.usuario import User, UserLogin
import asyncpg


router = APIRouter(
    prefix= "/users",
    tags=["Users"]
)

@router.on_event("startup")
async def startup():
    router.db_connection = await connect_db()

    #Funcion que se ejecuta al cerrar la aplicacion, cierra la conexion con la base de datos    
@router.on_event("shutdown")
async def shutdown():
    await router.db_connection.close()

    #Conexion a la base de datos
async def connect_db():
    conn = await asyncpg.connect(user='postgres', password='12345', database='My_Store', host='localhost')
    return conn

@router.get("/{user_id}")
async def leer_usuario(user_id: int):
    query = "SELECT id, name, email, cellphone, password FROM usuario WHERE id = $1"
    row = await router.db_connection.fetchrow(query, user_id)
    if row:
        return {"id": row[0], "name": row[1], "email": row[2], "cellphone": row[3], "password": row[4]}
    else:
        return {"message": "Usuario no encontrado"}
        
@router.put("/{user_id}")
async def actualizar_usuario(user_id: int, user: User):
    query = "UPDATE usuario SET name = $1, email = $2, cellphone =$3, password = $4 WHERE id = $5 RETURNING id, name, email, cellphone, password"
    values = (user.name, user.email, user.cellphone, user.password, user_id)
    row = await router.db_connection.fetchrow(query, *values)
    if row:
        return {"id": row[0], "name": row[1], "email": row[2], "cellphone": row[3], "password": row[4]}
    else:
        return {"message": "Usuario no encontrado"}

@router.delete("/{user_id}")
async def eliminar_usuario(user_id: int):
    query = "DELETE FROM usuario WHERE id = $1 RETURNING id, name, email, cellphone, password"
    row = await router.db_connection.fetchrow(query, user_id)
    if row:
        return {"id": row[0], "name": row[1], "email": row[2], "cellphone": row[3], "password": row[4]}
    else:
        return {"message": "Usuario no encontrado"}