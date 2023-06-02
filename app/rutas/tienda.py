from fastapi import APIRouter
from app.model.tienda import Tienda
import asyncpg

router = APIRouter(
    prefix= "/tienda",
    tags=["Tienda"]
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

# Bloque de funciones CRUD para tienda #

@router.post("/")
async def crear_tienda(tienda: Tienda):
    productos = tienda.productos.split(", ")
    query = "INSERT INTO tienda (nombre, direccion, id_vendedor, productos) VALUES ($1::text, $2::text, $3::integer, $4::text[]) RETURNING id, nombre, direccion, id_vendedor, productos"
    values = (tienda.nombre, tienda.direccion, tienda.id_vendedor, productos)
    row = await router.db_connection.fetchrow(query, *values)
    return {"id": row[0], "nombre": row[1], "direccion": row[2], "id_vendedor": row[3], "productos": row[4]}

@router.get("/{tienda_id}")
async def leer_tienda(tienda_id: int):
    query = "SELECT id, nombre, direccion, id_vendedor, productos FROM tienda WHERE id = $1"
    row = await router.db_connection.fetchrow(query, tienda_id)
    if row:
        return {"id": row[0], "nombre": row[1], "direccion": row[2], "id_vendedor": row[3], "productos": row[4]}
    else:
        return {"message": "Tienda no encontrada"}

@router.put("/{tienda_id}")
async def actualizar_tienda(tienda_id: int, tienda: Tienda):
    productos = tienda.productos.split(", ")
    query = "UPDATE tienda SET nombre = $1, direccion = $2, id_vendedor =$3, productos = $4 WHERE id = $5 RETURNING id, fecha_inicio, fecha_fin, precio, tipo, id_usuario"
    values = (tienda.nombre, tienda.direccion, tienda.id_vendedor, productos, tienda_id)
    row = await router.db_connection.fetchrow(query, *values)
    if row:
        return {"id": row[0], "nombre": row[1], "direccion": row[2], "id_vendedor": row[3], "productos": row[4]}
    else:
        return {"message": "Suscripción no encontrada"}

@router.delete("/{tienda_id}")
async def borrar_tienda(tienda_id: int):
    query = "DELETE FROM tienda WHERE id = $1 RETURNING id, fecha_inicio, fecha_fin, precio, tipo, id_usuario"
    row = await router.db_connection.fetchrow(query, tienda_id)
    if row:
        return {"id": row[0], "nombre": row[1], "direccion": row[2], "id_vendedor": row[3], "productos": row[4]}
    else:
        return {"message": "Suscripción no encontrada"}