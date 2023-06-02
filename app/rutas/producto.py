from fastapi import APIRouter, File, Form, UploadFile
from app.model.producto import Producto
import os
import uuid
import aiofiles
import base64
import asyncpg

router = APIRouter(
    prefix= "/producto",
    tags=["Producto"]
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

# Bloque de funciones CRUD para producto #

@router.post("/")
async def crear_producto(nombre: str = Form(...), descripcion: str = Form(...), precio: float = Form(...), ilustracion: UploadFile = File(...)):
    try:
        # Guardar la imagen del producto en el directorio de uploads
        extension = os.path.splitext(ilustracion.filename)[1]
        nombre_archivo = str(uuid.uuid4()) + extension
        ruta_archivo = os.path.join("uploads", nombre_archivo)
        async with aiofiles.open(ruta_archivo, "wb") as archivo:
            contenido = await ilustracion.read()
            await archivo.write(contenido)

        # Guardar los datos del producto en la base de datos
        async with router.db_connection.transaction():
            query = "INSERT INTO producto (nombre, descripcion, precio, ilustracion) VALUES ($1::text, $2::text, $3::money, $4::bytea[])"
            await router.db_connection.execute(query, nombre, descripcion, str(precio), [contenido])
        return {"mensaje": "Producto creado exitosamente."}
    except Exception as e:
        print(e) # Imprimir el error en la consola
        return {"mensaje": "Error al crear el producto."}


@router.get("s")
async def obtener_productos():
    try:
        async with router.db_connection.transaction():
            query = "SELECT id, nombre, descripcion, precio, (SELECT ilustracion[1] FROM producto WHERE id = p.id) AS ilustracion FROM producto p "
            resultados = await router.db_connection.fetch(query)
            productos = []
            for resultado in resultados:
                imagen = base64.b64encode(resultado['ilustracion']).decode('utf-8')
                producto = {
                    "id": resultado["id"],
                    "nombre": resultado["nombre"],
                    "descripcion": resultado["descripcion"],
                    "precio": resultado["precio"],
                    "ilustracion": imagen
                }
                productos.append(producto)
            return {"productos": productos}
    except Exception as e:
        print(e) # Imprimir el error en la consola
        return {"mensaje": "Error al obtener los productos."}


@router.get("/{producto_id}")
async def leer_producto(producto_id: int):
    query = "SELECT id, nombre, descripcion, precio FROM producto WHERE id = $1"
    row = await router.db_connection.fetchrow(query, producto_id)
    if row:
        return {"id": row[0], "nombre": row[1], "descripcion": row[2], "precio": row[3]}
    else:
        return {"message": "Producto no encontrado"}

@router.put("/{producto_id}")
async def actualizar_producto(producto_id: int, producto: Producto):
    query = "UPDATE producto SET nombre = $1, descripcion = $2, secciones =$3, diseño = $4, tipo = $5, url = $6 WHERE id = $3 RETURNING id, nombre, descripcion, precio, ilustracion"
    values = (producto.nombre, producto.descripcion, producto.precio, producto.ilustracion, producto_id)
    row = await router.db_connection.fetchrow(query, *values)
    if row:
        return {"id": row[0], "nombre": row[1], "descripcion": row[2], "precio": row[3], "ilustracion": row[4]}
    else:
        return {"message": "Producto no encontrado"}

@router.delete("/{producto_id}")
async def borrar_producto(producto_id: int):
    query = "DELETE FROM producto WHERE id = $1 RETURNING id, nombre, descripcion, precio, ilustracion"
    row = await router.db_connection.fetchrow(query, producto_id)
    if row:
        return {"id": row[0], "nombre": row[1], "descripcion": row[2], "precio": row[3], "ilustracion": row[4]}
    else:
        return {"message": "Producto no encontrado"}