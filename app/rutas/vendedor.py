from fastapi import APIRouter
from app.model.vendedor import Vendedor
import asyncpg

router = APIRouter(
    prefix= "/vendedor",
    tags=["Vendedor"]
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

@router.post("/")
async def crear_vendedor(vendedor: Vendedor):
    ventas = vendedor.historial_ventas.split(", ")
    query = "INSERT INTO vendedor (nombre_tienda, rues, historial_ventas, nombre) VALUES ($1::text, $2::integer, $3::text[], $4::text) RETURNING id, nombre_tienda, rues, historial_ventas, nombre"
    values = (vendedor.nombre_tienda, vendedor.rues, ventas, vendedor.nombre)
    row = await router.db_connection.fetchrow(query, *values)
    return {"id": row[0], "nombre_tienda": row[1], "rues": row[2], "historial_ventas": row[3], "nombre": row[4]}

@router.get("/{vendedor_id}")
async def leer_vendedor(vendedor_id: int):
    query = "SELECT id, nombre_tienda, rues, historial_ventas, nombre FROM vendedor WHERE id = $1"
    row = await router.db_connection.fetchrow(query, vendedor_id)
    if row:
        return {"id": row[0], "nombre_tienda": row[1], "rues": row[2], "historial_ventas": row[3], "nombre": row[4]}
    else:
        return {"message": "Vendedor no encontrado"}
    
@router.put("/{vendedor_id}")
async def actualizar_vendedor(vendedor_id: int, vendedor: Vendedor):
    ventas = vendedor.historial_ventas.split(", ")
    query = "UPDATE vendedor SET nombre_tienda = $1, rues = $2, historial_ventas =$3, nombre = $4 WHERE id = $5 RETURNING id, nombre_tienda, rues, historial_ventas, nombre"
    values = (vendedor.nombre_tienda, vendedor.rues, ventas, vendedor.nombre, vendedor_id)
    row = await router.db_connection.fetchrow(query, *values)
    if row:
        return {"id": row[0], "nombre_tienda": row[1], "rues": row[2], "historial_ventas": row[3], "nombre": row[4]}
    else:
        return {"message": "Vendedor no encontrado"}

@router.delete("/{vendedor_id}")
async def eliminar_vendedor(vendedor_id: int):
    query = "DELETE FROM vendedor WHERE id = $1 RETURNING id, nombre_tienda, rues, historial_ventas, nombre"
    row = await router.db_connection.fetchrow(query, vendedor_id)
    if row:
        return {"id": row[0], "nombre_tienda": row[1], "rues": row[2], "historial_ventas": row[3], "nombre": row[4]}
    else:
        return {"message": "Vendedor no encontrado"}