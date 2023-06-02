from fastapi import APIRouter
from app.model.suscripcion import Suscripcion
import asyncpg

router = APIRouter(
    prefix= "/suscripcion",
    tags=["Suscripcion"]
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

# Bloque de funciones CRUD para suscripcion #

@router.post("/")
async def crear_suscripcion(suscripcion: Suscripcion):
    query = "INSERT INTO suscripcion (fecha_inicio, fecha_fin, precio, tipo, id_usuario) VALUES ($1::date, $2::date, $3::numeric, $4::text, $5::integer) RETURNING id, fecha_inicio, fecha_fin, precio, tipo, id_usuario"
    values = (suscripcion.fecha_inicio, suscripcion.fecha_fin, suscripcion.precio, suscripcion.tipo, suscripcion.id_usuario)
    row = await router.db_connection.fetchrow(query, *values)
    return {"id": row[0], "fecha_inicio": row[1], "fecha_fin": row[2], "precio": row[3], "tipo": row[4], "id_usuario": row[5]}

@router.get("/{suscripcion_id}")
async def leer_suscripcion(suscripcion_id: int):
    query = "SELECT id, fecha_inicio, fecha_fin, precio, tipo, id_usuario FROM suscripcion WHERE id = $1"
    row = await router.db_connection.fetchrow(query, suscripcion_id)
    if row:
        return {"id": row[0], "fecha_inicio": row[1], "fecha_fin": row[2], "precio": row[3], "tipo": row[4], "id_usuario": row[5]}
    else:
        return {"message": "Suscripción no encontrada"}

@router.put("/{suscripcion_id}")
async def actualizar_suscripcion(suscripcion_id: int, suscripcion: Suscripcion):
    query = "UPDATE suscripcion SET nombre = $1, descripcion = $2, secciones =$3, diseño = $4, tipo = $5, url = $6 WHERE id = $7 RETURNING id, fecha_inicio, fecha_fin, precio, tipo, id_usuario"
    values = (suscripcion.fecha_inicio, suscripcion.fecha_fin, suscripcion.precio, suscripcion.tipo, suscripcion.id_usuario, suscripcion_id)
    row = await router.db_connection.fetchrow(query, *values)
    if row:
        return {"id": row[0], "fecha_inicio": row[1], "fecha_fin": row[2], "precio": row[3], "tipo": row[4], "id_usuario": row[5]}
    else:
        return {"message": "Suscripción no encontrada"}

@router.delete("/{suscripcion_id}")
async def borrar_suscripcion(suscripcion_id: int):
    query = "DELETE FROM suscripcion WHERE id = $1 RETURNING id, fecha_inicio, fecha_fin, precio, tipo, id_usuario"
    row = await router.db_connection.fetchrow(query, suscripcion_id)
    if row:
        return {"id": row[0], "fecha_inicio": row[1], "fecha_fin": row[2], "precio": row[3], "tipo": row[4], "id_usuario": row[5]}
    else:
        return {"message": "Suscripción no encontrada"}