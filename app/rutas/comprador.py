from fastapi import APIRouter
from app.model.comprador import Comprador
import asyncpg

router = APIRouter(
    prefix= "/comprador",
    tags=["Comprador"]
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

# Bloque de funciones CRUD para comprador #

@router.post("/")
async def crear_comprador(comprador: Comprador):
    compras = comprador.historial_compras.split(", ")
    query = "INSERT INTO comprador (direccion, telefono, historial_compras) VALUES ($1::text, $2::integer, $3::text[]) RETURNING id, direccion, telefono, historial_compras"
    values = (comprador.direccion, comprador.telefono, compras)
    row = await router.db_connection.fetchrow(query, *values)
    return {"id": row[0], "direccion": row[1], "telefono": row[2], "compras": row[3]}

@router.get("/{comprador_id}")
async def leer_comprador(comprador_id: int):
    query = "SELECT id, direccion, telefono, historial_compras FROM comprador WHERE id = $1"
    row = await router.db_connection.fetchrow(query, comprador_id)
    if row:
        return {"id": row[0], "direccion": row[1], "telefono": row[2], "compras": row[3]}
    else:
        return {"message": "Comprador no encontrado"}
    
@router.put("/{comprador_id}")
async def actualizar_comprador(comprador_id: int, comprador: Comprador):
    compras = comprador.historial_compras.split(", ")
    query = "UPDATE comprador SET direccion = $1, telefono = $2, historial_compras =$3 WHERE id = $4 RETURNING id, direccion, telefono, historial_compras"
    values = (comprador.direccion, comprador.telefono, compras, comprador_id)
    row = await router.db_connection.fetchrow(query, *values)
    if row:
        return {"id": row[0], "direccion": row[1], "telefono": row[2], "compras": row[3]}
    else:
        return {"message": "Comprador no encontrado"}

@router.delete("/{comprador_id}")
async def eliminar_comprador(comprador_id: int):
    query = "DELETE FROM comprador WHERE id = $1 RETURNING id, direccion, telefono, historial_compras"
    row = await router.db_connection.fetchrow(query, comprador_id)
    if row:
        return {"id": row[0], "direccion": row[1], "telefono": row[2], "compras": row[3]}
    else:
        return {"message": "Comprador no encontrado"}
