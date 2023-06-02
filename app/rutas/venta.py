from fastapi import APIRouter
from app.model.venta import Venta
import asyncpg

router = APIRouter(
    prefix= "/venta",
    tags=["Venta"]
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

# Bloque de funciones CRUD para venta #

@router.post("/")
async def crear_venta(venta: Venta):
    productos = venta.productos.split(", ")
    query = "INSERT INTO venta (fecha, total, estado, id_vendedor, productos) VALUES ($1::date, $2::integer, $3::text, $4::integer,$5::text[]) RETURNING id, fecha, total, estado, id_vendedor, productos"
    values = (venta.fecha,venta.total,venta.estado,venta.id_vendedor, productos)
    row = await router.db_connection.fetchrow(query, *values)
    return {"id": row[0], "fecha": row[1], "total": row[2], "estado": row[3], "id_vendedor": row[4], "productos": row[5]}

@router.get("/{venta_id}")
async def leer_venta(venta_id: int):
    query   = "SELECT id, fecha, estado, id_vendedor, productos FROM venta WHERE id = $1"
    row     = await router.db_connection.fetchrow(query, venta_id)
    if row:
        return {"id": row[0], "fecha": row[1], "total": row[2], "estado": row[3], "id_vendedor": row[4], "productos": row[5]}
    else:
        return {"message": "Venta no encontrada"}

@router.put("/{venta_id}")
async def actualizar_venta(venta_id: int, venta: Venta):
    productos = venta.productos.split(", ")
    query = "UPDATE venta SET nombre = $1, direccion = $2, id_vendedor =$3, productos = $4 WHERE id = $5 RETURNING id, fecha, estado, id_vendedor, productos"
    values = (venta.fecha,venta.total,venta.estado,venta.id_vendedor, productos,venta_id)
    row = await router.db_connection.fetchrow(query, *values)
    if row:
        return {"id": row[0], "fecha": row[1], "total": row[2], "estado": row[3], "id_vendedor": row[4], "productos": row[5]}
    else:
        return {"message": "Venta no encontrada"}

@router.delete("/{venta_id}")
async def borrar_venta(venta_id: int):
    query = "DELETE FROM venta WHERE id = $1 RETURNING id, fecha, estado, id_vendedor, productos"
    row = await router.db_connection.fetchrow(query, venta_id)
    if row:
        return {"id": row[0], "fecha": row[1], "total": row[2], "estado": row[3], "id_vendedor": row[4], "productos": row[5]}
    else:
        return {"message": "Venta no encontrada"}