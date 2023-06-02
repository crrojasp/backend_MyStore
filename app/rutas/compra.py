from fastapi import APIRouter
from app.model.compra import Compra
import asyncpg

router = APIRouter(
    prefix= "/compra",
    tags=["Compras"]
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

# Bloque de funciones CRUD para compra #

@router.post("/")
async def crear_compra(compra: Compra):
    query = "INSERT INTO compra (fecha, total, estado, id_comprador) VALUES ($1::date, $2::numeric, $3::text, $4::integer) RETURNING id, fecha, total, estado, id_comprador"
    values = (compra.fecha, compra.total, compra.estado, compra.id_comprador)
    row = await router.db_connection.fetchrow(query, *values)
    return {"id": row[0], "fecha": row[1], "total": row[2], "estado": row[3], "id_comprador": row[4]}

@router.get("/{compra_id}")
async def leer_compra(compra_id: int):
    query = "SELECT id, fecha, total, estado, id_comprador FROM compra WHERE id = $1"
    row = await router.db_connection.fetchrow(query, compra_id)
    if row:
        return {"id": row[0], "fecha": row[1], "total": row[2], "estado": row[3], "id_comprador": row[4]}
    else:
        return {"message": "Compra no encontrada"}

@router.put("/{compra_id}")
async def actualizar_compra(compra_id: int, compra: Compra):
    query = "UPDATE compra SET fecha = $1, total = $2, estado =$3, id_comprador = $4 WHERE id = $5 RETURNING id, fecha, total, estado, id_comprador"
    values = (compra.fecha, compra.total, compra.estado, compra.id_comprador, compra_id)
    row = await router.db_connection.fetchrow(query, *values)
    if row:
        return {"id": row[0], "fecha": row[1], "total": row[2], "estado": row[3], "id_comprador": row[4]}
    else:
        return {"message": "Compra no encontrada"}

@router.delete("/{compra_id}")
async def borrar_compra(compra_id: int):
    query = "DELETE FROM compra WHERE id = $1 RETURNING id, fecha, total, estado, id_comprador"
    row = await router.db_connection.fetchrow(query, compra_id)
    if row:
        return {"id": row[0], "fecha": row[1], "total": row[2], "estado": row[3], "id_comprador": row[4]}
    else:
        return {"message": "Compra no encontrada"}