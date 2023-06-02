from fastapi import APIRouter
from app.model.carrito_compra import Carrito
import asyncpg

router = APIRouter(
    prefix= "/carrito",
    tags=["Carrito Compras"]
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

# Bloque de funciones CRUD para carrito de compras #

@router.post("/")
async def crear_carrito(carrito: Carrito):
    productos = carrito.productos.split(", ")
    query = "INSERT INTO carrito_compra (productos, id_comprador) VALUES ($1::text[], $2::integer) RETURNING id, productos, id_comprador "
    values = (productos, int(carrito.id_comprador))
    row = await router.db_connection.fetchrow(query, *values)
    return {"id": row[0], "productos": row[1], "id_comprador": row[2]}

@router.get("/{carrito_id}")
async def leer_carrito(carrito_id: int):
    query = "SELECT id, productos, id_comprador FROM carrito_compra WHERE id = $1"
    row = await router.db_connection.fetchrow(query, carrito_id)
    if row:
        return {"id": row[0], "productos": row[1], "id_comprador": row[2]}
    else:
        return {"message": "Carrito no encontrado"}

@router.put("/{carrito_id}")
async def actualizar_carrito(carrito_id: int, carrito: Carrito):
    productos = carrito.productos.split(", ")
    query = "UPDATE carrito_compra SET productos = $1, id_comprador = $2 WHERE id = $3 RETURNING id, productos, id_comprador"
    values = (productos,carrito.id_comprador, carrito_id)
    row = await router.db_connection.fetchrow(query, *values)
    if row:
        return {"id": row[0], "productos": row[1], "id_comprador": row[2]}
    else:
        return {"message": "Carrito no encontrado"}

@router.delete("/{carrito_id}")
async def borrar_carrito(carrito_id: int):
    query = "DELETE FROM carrito_compra WHERE id = $1 RETURNING id, productos, id_comprador"
    row = await router.db_connection.fetchrow(query, carrito_id)
    if row:
        return {"id": row[0], "productos": row[1], "id_comprador": row[2]}
    else:
        return {"message": "Carrito no encontrado"}