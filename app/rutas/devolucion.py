from fastapi import APIRouter
from app.model.devolucion import Devolucion
import asyncpg

router = APIRouter(
    prefix= "/devolucion",
    tags=["Devolucion"]
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

# Bloque de funciones CRUD para devolucion #

@router.post("/")
async def crear_devolucion(devolucion: Devolucion):
    query = "INSERT INTO devolucion (fecha_solicitud, id_producto, id_vendedor, id_comprador, razon, id_envio) VALUES ($1::date, $2::integer, $3::integer, $4::integer, $5::text, $6::integer) RETURNING id, fecha_solicitud, id_producto, id_vendedor, id_comprador, razon, id_envio"
    values = (devolucion.fecha_solicitud, devolucion.id_producto, devolucion.id_vendedor, devolucion.id_comprador, devolucion.razon, devolucion.id_envio)
    row = await router.db_connection.fetchrow(query, *values)
    return {"id": row[0], "fecha_solicitud": row[1], "id_producto": row[2], "id_vendedor": row[3], "id_comprador": row[4], "razon" : row[5], "id_envio" : row[6]}

@router.get("/{devolucion_id}")
async def leer_devolucion(devolucion_id: int):
    query = "SELECT id, fecha_solicitud, id_producto, id_vendedor, id_comprador, razon, id_envio FROM devolucion WHERE id = $1"
    row = await router.db_connection.fetchrow(query, devolucion_id)
    if row:
        return {"id": row[0], "fecha_solicitud": row[1], "id_producto": row[2], "id_vendedor": row[3], "id_comprador": row[4], "razon" : row[5], "id_envio" : row[6]}
    else:
        return {"message": "Devolución no encontrada"}

@router.put("/{devolucion_id}")
async def actualizar_devolucion(devolucion_id: int, devolucion: Devolucion):
    query = "UPDATE devolucion SET fecha_solicitud = $1, id_producto = $2, id_vendedor =$3, id_comprador = $4,  razon = $5, id_envio = $6 WHERE id = $7 RETURNING id, fecha_solicitud, id_producto, id_vendedor, id_comprador, razon, id_envio"
    values = (devolucion.fecha_solicitud, devolucion.id_producto, devolucion.id_vendedor, devolucion.id_comprador, devolucion.razon, devolucion.id_envio)
    row = await router.db_connection.fetchrow(query, *values)
    if row:
        return {"id": row[0], "fecha_solicitud": row[1], "id_producto": row[2], "id_vendedor": row[3], "id_comprador": row[4], "razon" : row[5], "id_envio" : row[6]}
    else:
        return {"message": "Devolución no encontrada"}

@router.delete("/{devolucion_id}")
async def borrar_devolucion(devolucion_id: int):
    query = "DELETE FROM devolucion WHERE id = $1 RETURNING id, fecha_solicitud, id_producto, id_vendedor, id_comprador, razon, id_envio"
    row = await router.db_connection.fetchrow(query, devolucion_id)
    if row:
        return {"id": row[0], "fecha_solicitud": row[1], "id_producto": row[2], "id_vendedor": row[3], "id_comprador": row[4], "razon" : row[5], "id_envio" : row[6]}
    else:
        return {"message": "Devolución no encontrada"}