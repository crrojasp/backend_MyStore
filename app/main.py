import uvicorn
from fastapi import FastAPI, Response, File, UploadFile, Request, status, HTTPException, Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import asyncpg
import secrets
from tkinter import *
import uuid
import aiofiles
import base64
import datetime
from PIL import Image
import io
import hashlib
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import jwt
import psycopg2
from psycopg2.extras import RealDictCursor
import traceback
from decimal import Decimal
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.model.carrito_compra import Carrito
from app.model.compra import Compra
from app.model.comprador import Comprador
from app.model.devolucion import Devolucion
from app.model.envio import Envio
from app.model.lista_deseos import ListaDeseos
from app.model.plantilla import Plantilla
from app.model.producto import Producto
from app.model.suscripcion import Suscripcion
from app.model.tienda import Tienda
from app.model.usuario import User, UserLogin
from app.model.vendedor import Vendedor
from app.model.venta import Venta
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from fastapi.exceptions import RequestValidationError
import asyncio



ALGORITHM = "HS256"
SECRET_KEY = secrets.token_hex(32)
origins= ["http://localhost:3000",
          "http://localhost:8000",
          "http://localhost:8888",
          "http://localhost:5432",
          "http://localhost"
          ]


app = FastAPI()
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
def init_app():
    class MyForm(FlaskForm):
        name = StringField('Name')
        submit = SubmitField('Submit')

    app = FastAPI(
        title= "MyStore",
        description= "Pagina  de ingreso",
        version= "0.9.12"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
        expose_headers=["Content-Type"]
    )

    async def perform_ping():
        conn = await connect_db()
        try:
            await conn.fetchval('SELECT 1;')
        finally:
            await conn.close()
    
    async def ping_task():
        while True:
            await perform_ping()
            await asyncio.sleep(300)  # Espera 5 minutos antes de enviar la próxima consulta de ping

    @app.on_event("startup")
    async def startup():
        app.db_connection = await connect_db()
        asyncio.create_task(ping_task())

    @app.on_event("shutdown")
    async def shutdown():
        await app.db_connection.close()

    async def connect_db():
        conn = await asyncpg.connect(user='Cristian', password='1234509876', database='test', host='databasetest.cucej1optovn.us-east-1.rds.amazonaws.com')
        return conn

    # Bloque de funciones de primer necesidad #

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": str(exc)}
        )

    @app.post("/register")
    async def register(user: User):
        # Verificar si el correo electrónico ya existe en la base de datos
        query = "SELECT email FROM usuario WHERE email = $1"
        row = await app.db_connection.fetchrow(query, user.email)
        if row:
            return {"message": "El correo electrónico ya está registrado"}

        # Almacenar el nuevo usuario en la base de datos
        password_bytes = user.password.encode('utf-8')
        salt = hashlib.sha256(password_bytes).hexdigest().encode('utf-8')
        hashed_bytes = hashlib.pbkdf2_hmac('sha256', password_bytes, salt, 100000)
        hashed_password = salt + hashed_bytes

        # Convertir el hash a base64
        hashed_password_b64 = base64.b64encode(hashed_password).decode('utf-8')

        query = "INSERT INTO usuario (name, email, cellphone, password, tipo) VALUES ($1::text, $2::text, $3::text, $4::text, $5::text) RETURNING id, name, email, cellphone, tipo"
        values = (user.name, user.email, user.cellphone, hashed_password_b64, user.tipo)
        row = await app.db_connection.fetchrow(query, *values)

        return {"id": row[0], "name": row[1], "email": row[2], "cellphone": row[3], "tipo": row[4]}



    @app.post("/login-utf8")
    async def login(user_credentials: UserLogin, response: Response):
        query = "SELECT id, name, email, password FROM usuario WHERE email = $1"
        row = await app.db_connection.fetchrow(query, user_credentials.email)
        if row:
            user_id, name, email, hashed_password_b64 = row
            password_bytes = user_credentials.password.encode('utf-8')
            salt = base64.b64decode(hashed_password_b64)[:64]
            hashed_bytes = hashlib.pbkdf2_hmac('sha256', password_bytes, salt, 100000)
            hashed_input_password = salt + hashed_bytes
            if hashed_password_b64.encode('utf-8') == base64.b64encode(hashed_input_password):
                # Generate JWT with user data
                user_data = {"id": user_id, "name": name, "email": email}
                jwt_token = jwt.encode(
                    {"user": user_data, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=300)},
                    SECRET_KEY,
                    algorithm="HS256"
                )

                # Update user last login and save name and email
                update_query = "UPDATE usuario SET last_login = $1, name = $2, email = $3 WHERE id = $4"
                await app.db_connection.execute(update_query, datetime.datetime.utcnow(), name, email, user_id)

                response.headers["Access-Control-Allow-Origin"] = "*"
                return {"jwt_token": jwt_token}
                
            else:
                response.headers["Access-Control-Allow-Origin"] = "*"
                return {"message": "Contraseña incorrecta"}
        else:
            response.headers["Access-Control-Allow-Origin"] = "*"
            return {"message": "Usuario no encontrado"}






    # Bloque de funciones CRUD para usuario #

    @app.get("/users/{user_id}")
    async def leer_usuario(user_id: int):
        query = "SELECT id, name, email, cellphone, password FROM usuario WHERE id = $1"
        row = await app.db_connection.fetchrow(query, user_id)
        if row:
            return {"id": row[0], "name": row[1], "email": row[2], "cellphone": row[3], "password": row[4]}
        else:
            return {"message": "Usuario no encontrado"}
        
    @app.put("/users/{user_id}")
    async def actualizar_usuario(user_id: int, user: User):
        query = "UPDATE usuario SET name = $1, email = $2, cellphone =$3, password = $4 WHERE id = $5 RETURNING id, name, email, cellphone, password"
        values = (user.name, user.email, user.cellphone, user.password, user_id)
        row = await app.db_connection.fetchrow(query, *values)
        if row:
            return {"id": row[0], "name": row[1], "email": row[2], "cellphone": row[3], "password": row[4]}
        else:
            return {"message": "Usuario no encontrado"}

    @app.delete("/users/{user_id}")
    async def eliminar_usuario(user_id: int):
        query = "DELETE FROM usuario WHERE id = $1 RETURNING id, name, email, cellphone, password"
        row = await app.db_connection.fetchrow(query, user_id)
        if row:
            return {"id": row[0], "name": row[1], "email": row[2], "cellphone": row[3], "password": row[4]}
        else:
            return {"message": "Usuario no encontrado"}

    # Bloque de funciones CRUD para usuario #

    # Bloque de funciones CRUD para vendedor #

    @app.post("/vendedor")
    async def crear_vendedor(vendedor: Vendedor):
        ventas = vendedor.historial_ventas.split(", ")
        query = "INSERT INTO vendedor (nombre_tienda, rues, historial_ventas, nombre) VALUES ($1::text, $2::integer, $3::text[], $4::text) RETURNING id, nombre_tienda, rues, historial_ventas, nombre"
        values = (vendedor.nombre_tienda, vendedor.rues, ventas, vendedor.nombre)
        row = await app.db_connection.fetchrow(query, *values)
        return {"id": row[0], "nombre_tienda": row[1], "rues": row[2], "historial_ventas": row[3], "nombre": row[4]}

    @app.get("/vendedor/{vendedor_id}")
    async def leer_vendedor(vendedor_id: int):
        query = "SELECT id, nombre_tienda, rues, historial_ventas, nombre FROM vendedor WHERE id = $1"
        row = await app.db_connection.fetchrow(query, vendedor_id)
        if row:
            return {"id": row[0], "nombre_tienda": row[1], "rues": row[2], "historial_ventas": row[3], "nombre": row[4]}
        else:
            return {"message": "Vendedor no encontrado"}
        
    @app.put("/vendedor/{vendedor_id}")
    async def actualizar_vendedor(vendedor_id: int, vendedor: Vendedor):
        ventas = vendedor.historial_ventas.split(", ")
        query = "UPDATE vendedor SET nombre_tienda = $1, rues = $2, historial_ventas =$3, nombre = $4 WHERE id = $5 RETURNING id, nombre_tienda, rues, historial_ventas, nombre"
        values = (vendedor.nombre_tienda, vendedor.rues, ventas, vendedor.nombre, vendedor_id)
        row = await app.db_connection.fetchrow(query, *values)
        if row:
            return {"id": row[0], "nombre_tienda": row[1], "rues": row[2], "historial_ventas": row[3], "nombre": row[4]}
        else:
            return {"message": "Vendedor no encontrado"}

    @app.delete("/vendedor/{vendedor_id}")
    async def eliminar_vendedor(vendedor_id: int):
        query = "DELETE FROM vendedor WHERE id = $1 RETURNING id, nombre_tienda, rues, historial_ventas, nombre"
        row = await app.db_connection.fetchrow(query, vendedor_id)
        if row:
            return {"id": row[0], "nombre_tienda": row[1], "rues": row[2], "historial_ventas": row[3], "nombre": row[4]}
        else:
            return {"message": "Vendedor no encontrado"}

    # Bloque de funciones CRUD para vendedor #

    # Bloque de funciones CRUD para comprador #

    @app.post("/comprador")
    async def crear_comprador(comprador: Comprador):
        compras = comprador.historial_compras.split(", ")
        query = "INSERT INTO comprador (direccion, telefono, historial_compras) VALUES ($1::text, $2::integer, $3::text[]) RETURNING id, direccion, telefono, historial_compras"
        values = (comprador.direccion, comprador.telefono, compras)
        row = await app.db_connection.fetchrow(query, *values)
        return {"id": row[0], "direccion": row[1], "telefono": row[2], "compras": row[3]}

    @app.get("/comprador/{comprador_id}")
    async def leer_comprador(comprador_id: int):
        query = "SELECT id, direccion, telefono, historial_compras FROM comprador WHERE id = $1"
        row = await app.db_connection.fetchrow(query, comprador_id)
        if row:
            return {"id": row[0], "direccion": row[1], "telefono": row[2], "compras": row[3]}
        else:
            return {"message": "Comprador no encontrado"}
        
    @app.put("/comprador/{comprador_id}")
    async def actualizar_comprador(comprador_id: int, comprador: Comprador):
        compras = comprador.historial_compras.split(", ")
        query = "UPDATE comprador SET direccion = $1, telefono = $2, historial_compras =$3 WHERE id = $4 RETURNING id, direccion, telefono, historial_compras"
        values = (comprador.direccion, comprador.telefono, compras, comprador_id)
        row = await app.db_connection.fetchrow(query, *values)
        if row:
            return {"id": row[0], "direccion": row[1], "telefono": row[2], "compras": row[3]}
        else:
            return {"message": "Comprador no encontrado"}

    @app.delete("/comprador/{comprador_id}")
    async def eliminar_comprador(comprador_id: int):
        query = "DELETE FROM comprador WHERE id = $1 RETURNING id, direccion, telefono, historial_compras"
        row = await app.db_connection.fetchrow(query, comprador_id)
        if row:
            return {"id": row[0], "direccion": row[1], "telefono": row[2], "compras": row[3]}
        else:
            return {"message": "Comprador no encontrado"}

    # Bloque de funciones CRUD para comprador #

    # Bloque de funciones CRUD para carrito de compras #

    @app.post("/carrito")
    async def crear_carrito(carrito: Carrito):
        productos = carrito.productos.split(", ")
        query = "INSERT INTO carrito_compra (productos, id_comprador) VALUES ($1::text[], $2::integer) RETURNING id, productos, id_comprador "
        values = (productos, int(carrito.id_comprador))
        row = await app.db_connection.fetchrow(query, *values)
        return {"id": row[0], "productos": row[1], "id_comprador": row[2]}

    @app.get("/carrito/{carrito_id}")
    async def leer_carrito(carrito_id: int):
        query = "SELECT id, productos, id_comprador FROM carrito_compra WHERE id = $1"
        row = await app.db_connection.fetchrow(query, carrito_id)
        if row:
            return {"id": row[0], "productos": row[1], "id_comprador": row[2]}
        else:
            return {"message": "Carrito no encontrado"}

    @app.put("/carrito/{carrito_id}")
    async def actualizar_carrito(carrito_id: int, carrito: Carrito):
        productos = carrito.productos.split(", ")
        query = "UPDATE carrito_compra SET productos = $1, id_comprador = $2 WHERE id = $3 RETURNING id, productos, id_comprador"
        values = (productos,carrito.id_comprador, carrito_id)
        row = await app.db_connection.fetchrow(query, *values)
        if row:
            return {"id": row[0], "productos": row[1], "id_comprador": row[2]}
        else:
            return {"message": "Carrito no encontrado"}

    @app.delete("/carrito/{carrito_id}")
    async def borrar_carrito(carrito_id: int):
        query = "DELETE FROM carrito_compra WHERE id = $1 RETURNING id, productos, id_comprador"
        row = await app.db_connection.fetchrow(query, carrito_id)
        if row:
            return {"id": row[0], "productos": row[1], "id_comprador": row[2]}
        else:
            return {"message": "Carrito no encontrado"}

    # Bloque de funciones CRUD para carrito de compras #

    # Bloque de funciones CRUD para compra #

    @app.post("/compra")
    async def crear_compra(compra: Compra):
        query = "INSERT INTO compra (fecha, total, estado, id_comprador) VALUES ($1::date, $2::numeric, $3::text, $4::integer) RETURNING id, fecha, total, estado, id_comprador"
        values = (compra.fecha, compra.total, compra.estado, compra.id_comprador)
        row = await app.db_connection.fetchrow(query, *values)
        return {"id": row[0], "fecha": row[1], "total": row[2], "estado": row[3], "id_comprador": row[4]}

    @app.get("/compra/{compra_id}")
    async def leer_compra(compra_id: int):
        query = "SELECT id, fecha, total, estado, id_comprador FROM compra WHERE id = $1"
        row = await app.db_connection.fetchrow(query, compra_id)
        if row:
            return {"id": row[0], "fecha": row[1], "total": row[2], "estado": row[3], "id_comprador": row[4]}
        else:
            return {"message": "Compra no encontrada"}

    @app.put("/compra/{compra_id}")
    async def actualizar_compra(compra_id: int, compra: Compra):
        query = "UPDATE compra SET fecha = $1, total = $2, estado =$3, id_comprador = $4 WHERE id = $5 RETURNING id, fecha, total, estado, id_comprador"
        values = (compra.fecha, compra.total, compra.estado, compra.id_comprador, compra_id)
        row = await app.db_connection.fetchrow(query, *values)
        if row:
            return {"id": row[0], "fecha": row[1], "total": row[2], "estado": row[3], "id_comprador": row[4]}
        else:
            return {"message": "Compra no encontrada"}

    @app.delete("/compra/{compra_id}")
    async def borrar_compra(compra_id: int):
        query = "DELETE FROM compra WHERE id = $1 RETURNING id, fecha, total, estado, id_comprador"
        row = await app.db_connection.fetchrow(query, compra_id)
        if row:
            return {"id": row[0], "fecha": row[1], "total": row[2], "estado": row[3], "id_comprador": row[4]}
        else:
            return {"message": "Compra no encontrada"}

    # Bloque de funciones CRUD para compra #

    # Bloque de funciones CRUD para devolucion #

    @app.post("/devolucion")
    async def crear_devolucion(devolucion: Devolucion):
        query = "INSERT INTO devolucion (fecha_solicitud, id_producto, id_vendedor, id_comprador, razon, id_envio) VALUES ($1::date, $2::integer, $3::integer, $4::integer, $5::text, $6::integer) RETURNING id, fecha_solicitud, id_producto, id_vendedor, id_comprador, razon, id_envio"
        values = (devolucion.fecha_solicitud, devolucion.id_producto, devolucion.id_vendedor, devolucion.id_comprador, devolucion.razon, devolucion.id_envio)
        row = await app.db_connection.fetchrow(query, *values)
        return {"id": row[0], "fecha_solicitud": row[1], "id_producto": row[2], "id_vendedor": row[3], "id_comprador": row[4], "razon" : row[5], "id_envio" : row[6]}

    @app.get("/devolucion/{devolucion_id}")
    async def leer_devolucion(devolucion_id: int):
        query = "SELECT id, fecha_solicitud, id_producto, id_vendedor, id_comprador, razon, id_envio FROM devolucion WHERE id = $1"
        row = await app.db_connection.fetchrow(query, devolucion_id)
        if row:
            return {"id": row[0], "fecha_solicitud": row[1], "id_producto": row[2], "id_vendedor": row[3], "id_comprador": row[4], "razon" : row[5], "id_envio" : row[6]}
        else:
            return {"message": "Devolución no encontrada"}

    @app.put("/devolucion/{devolucion_id}")
    async def actualizar_devolucion(devolucion_id: int, devolucion: Devolucion):
        query = "UPDATE devolucion SET fecha_solicitud = $1, id_producto = $2, id_vendedor =$3, id_comprador = $4,  razon = $5, id_envio = $6 WHERE id = $7 RETURNING id, fecha_solicitud, id_producto, id_vendedor, id_comprador, razon, id_envio"
        values = (devolucion.fecha_solicitud, devolucion.id_producto, devolucion.id_vendedor, devolucion.id_comprador, devolucion.razon, devolucion.id_envio)
        row = await app.db_connection.fetchrow(query, *values)
        if row:
            return {"id": row[0], "fecha_solicitud": row[1], "id_producto": row[2], "id_vendedor": row[3], "id_comprador": row[4], "razon" : row[5], "id_envio" : row[6]}
        else:
            return {"message": "Devolución no encontrada"}

    @app.delete("/devolucion/{devolucion_id}")
    async def borrar_devolucion(devolucion_id: int):
        query = "DELETE FROM devolucion WHERE id = $1 RETURNING id, fecha_solicitud, id_producto, id_vendedor, id_comprador, razon, id_envio"
        row = await app.db_connection.fetchrow(query, devolucion_id)
        if row:
            return {"id": row[0], "fecha_solicitud": row[1], "id_producto": row[2], "id_vendedor": row[3], "id_comprador": row[4], "razon" : row[5], "id_envio" : row[6]}
        else:
            return {"message": "Devolución no encontrada"}

    # Bloque de funciones CRUD para devolucion #

    # Bloque de funciones CRUD para envio #

    @app.post("/envio")
    async def crear_envio(envio: Envio):
        query = "INSERT INTO envio (direccion_entrega, direccion_origen, transportista, precio, id_producto) VALUES ($1::text, $2::text, $3::text, $4::numeric, $5::integer) RETURNING id, direccion_entrega, direccion_origen, transportista, precio, id_producto"
        values = (envio.direccion_entrega, envio.direccion_origen, envio.transportista, envio.precio, envio.id_producto)
        row = await app.db_connection.fetchrow(query, *values)
        return {"id": row[0], "direccion_entrega": row[1], "direccion_origen": row[2], "transportista": row[3], "precio": row[4], "id_producto" : row[5]}

    @app.get("/envio/{envio_id}")
    async def leer_envio(envio_id: int):
        query = "SELECT id, direccion_entrega, direccion_origen, transportista, precio, id_producto FROM envio WHERE id = $1"
        row = await app.db_connection.fetchrow(query, envio_id)
        if row:
            return {"id": row[0], "direccion_entrega": row[1], "direccion_origen": row[2], "transportista": row[3], "precio": row[4], "id_producto" : row[5]}
        else:
            return {"message": "Envio no encontrado"}

    @app.put("/envio/{envio_id}")
    async def actualizar_envio(envio_id: int, envio: Envio):
        query = "UPDATE envio SET direccion_entrega = $1, direccion_origen = $2, transportista =$3, precio = $4,  id_producto = $5 WHERE id = $6 RETURNING id, direccion_entrega, direccion_origen, transportista, precio, id_producto"
        values = (envio.direccion_entrega, envio.direccion_origen, envio.transportista, envio.precio, envio.id_producto, envio_id)
        row = await app.db_connection.fetchrow(query, *values)
        if row:
            return {"id": row[0], "direccion_entrega": row[1], "direccion_origen": row[2], "transportista": row[3], "precio": row[4], "id_producto" : row[5]}
        else:
            return {"message": "Envio no encontrado"}

    @app.delete("/envio/{envio_id}")
    async def borrar_envio(envio_id: int):
        query = "DELETE FROM envio WHERE id = $1 RETURNING id, direccion_entrega, direccion_origen, transportista, precio, id_producto"
        row = await app.db_connection.fetchrow(query, envio_id)
        if row:
            return {"id": row[0], "direccion_entrega": row[1], "direccion_origen": row[2], "transportista": row[3], "precio": row[4], "id_producto" : row[5]}
        else:
            return {"message": "Envio no encontrado"}

    # Bloque de funciones CRUD para devolucion #

    # Bloque de funciones CRUD para lista de deseos #

    @app.post("/lista-de-deseos")
    async def crear_lista_de_deseos(lista: ListaDeseos):
        productos = lista.productos.split(", ")
        query = "INSERT INTO lista_deseos (productos, id_comprador) VALUES ($1::text[], $2::integer) RETURNING id, productos, id_comprador"
        values = (productos,lista.id_comprador)
        row = await app.db_connection.fetchrow(query, *values)
        return {"id": row[0], "productos": row[1], "id_comprador": row[2]}

    @app.get("/lista-de-deseos/{lista_id}")
    async def leer_lista_de_deseos(lista_id: int):
        query = "SELECT id, productos, id_comprador FROM lista_deseos WHERE id = $1"
        row = await app.db_connection.fetchrow(query, lista_id)
        if row:
            return {"id": row[0], "productos": row[1], "id_comprador": row[2]}
        else:
            return {"message": "Lista de deseos no encontrada"}

    @app.put("/lista-de-deseos/{lista_id}")
    async def actualizar_lista_de_deseos(lista_id: int, lista: ListaDeseos):
        productos = lista.productos.split(", ")
        query = "UPDATE lista_deseos SET productos = $1, id_comprador = $2 WHERE id = $3 RETURNING id, productos, id_comprador"
        values = (productos,lista.id_comprador)
        row = await app.db_connection.fetchrow(query, *values)
        if row:
            return {"id": row[0], "productos": row[1], "id_comprador": row[2]}
        else:
            return {"message": "Lista de deseos no encontrada"}

    @app.delete("/lista-de-deseos/{lista_id}")
    async def borrar_lista_de_deseos(lista_id: int):
        query = "DELETE FROM lista_deseos WHERE id = $1 RETURNING id, productos, id_comprador"
        row = await app.db_connection.fetchrow(query, lista_id)
        if row:
            return {"id": row[0], "productos": row[1], "id_comprador": row[2]}
        else:
            return {"message": "Lista de deseos no encontrada"}

    # Bloque de funciones CRUD para lista de deseos #

    # Bloque de funciones CRUD para plantilla #

    @app.post("/plantila")
    async def crear_plantilla(plantilla: Plantilla):
        secciones = plantilla.secciones.split(", ")
        query = "INSERT INTO plantilla (nombre, descripcion, secciones, diseño, tipo, url) VALUES ($1::text, $2::text, $3::text[], $4::text, $5::text, $6::text) RETURNING id, nombre, descripcion, secciones, diseño, tipo, url"
        values = (plantilla.nombre,plantilla.descripcion, secciones, plantilla.diseño, plantilla.tipo, plantilla.url)
        row = await app.db_connection.fetchrow(query, *values)
        return {"id": row[0], "nombre": row[1], "descripcion": row[2], "secciones": row[3], "diseño": row[4], "tipo": row[5], "url": row[6]}

    @app.get("/plantilla/{plantilla_id}")
    async def leer_plantilla(plantilla_id: int):
        query = "SELECT id, nombre, descripcion, secciones, diseño, tipo, url FROM plantilla WHERE id = $1"
        row = await app.db_connection.fetchrow(query, plantilla_id)
        if row:
            return {"id": row[0], "nombre": row[1], "descripcion": row[2], "secciones": row[3], "diseño": row[4], "tipo": row[5], "url": row[6]}
        else:
            return {"message": "Plantilla no encontrada"}

    @app.put("/plantilla/{plantilla_id}")
    async def actualizar_plantilla(plantilla_id: int, plantilla: Plantilla):
        query = "UPDATE plantilla SET nombre = $1, descripcion = $2, secciones =$3, diseño = $4, tipo = $5, url = $6 WHERE id = $3 RETURNING id, nombre, descripcion, secciones, diseño, tipo, url"
        values = (plantilla.nombre,plantilla.descripcion, plantilla.secciones, plantilla.diseño, plantilla.tipo, plantilla.url)
        row = await app.db_connection.fetchrow(query, *values)
        if row:
            return {"id": row[0], "nombre": row[1], "descripcion": row[2], "secciones": row[3], "diseño": row[4], "tipo": row[5], "url": row[6]}
        else:
            return {"message": "Plantilla no encontrada"}

    @app.delete("/plantilla/{plantilla_id}")
    async def borrar_plantilla(plantilla_id: int):
        query = "DELETE FROM plantilla WHERE id = $1 RETURNING id, nombre, descripcion, secciones, diseño, tipo, url"
        row = await app.db_connection.fetchrow(query, plantilla_id)
        if row:
            return {"id": row[0], "nombre": row[1], "descripcion": row[2], "secciones": row[3], "diseño": row[4], "tipo": row[5], "url": row[6]}
        else:
            return {"message": "Plantilla no encontrada"}

    # Bloque de funciones CRUD para plantilla #

    # Bloque de funciones CRUD para producto #

    @app.post("/producto/")
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
            async with app.db_connection.transaction():
                query = "INSERT INTO producto (nombre, descripcion, precio, ilustracion) VALUES ($1::text, $2::text, $3::money, $4::bytea[])"
                await app.db_connection.execute(query, nombre, descripcion, str(precio), [contenido])
            return {"mensaje": "Producto creado exitosamente."}
        except Exception as e:
            print(e) # Imprimir el error en la consola
            return {"mensaje": "Error al crear el producto."}

    @app.get("/productos")
    async def obtener_productos():
        try:
            async with app.db_connection.transaction():
                query = "SELECT id, nombre, descripcion, precio, (SELECT ilustracion[1] FROM producto WHERE id = p.id) AS ilustracion FROM producto p "
                resultados = await app.db_connection.fetch(query)
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



    @app.get("/producto/{producto_id}")
    async def leer_producto(producto_id: int):
        query = "SELECT id, nombre, descripcion, precio FROM producto WHERE id = $1"
        row = await app.db_connection.fetchrow(query, producto_id)
        if row:
            return {"id": row[0], "nombre": row[1], "descripcion": row[2], "precio": row[3]}
        else:
            return {"message": "Producto no encontrado"}

    @app.put("/producto/{producto_id}")
    async def actualizar_producto(producto_id: int, producto: Producto):
        query = "UPDATE producto SET nombre = $1, descripcion = $2, secciones =$3, diseño = $4, tipo = $5, url = $6 WHERE id = $3 RETURNING id, nombre, descripcion, precio, ilustracion"
        values = (producto.nombre, producto.descripcion, producto.precio, producto.ilustracion, producto_id)
        row = await app.db_connection.fetchrow(query, *values)
        if row:
            return {"id": row[0], "nombre": row[1], "descripcion": row[2], "precio": row[3], "ilustracion": row[4]}
        else:
            return {"message": "Producto no encontrado"}

    @app.delete("/producto/{producto_id}")
    async def borrar_producto(producto_id: int):
        query = "DELETE FROM producto WHERE id = $1 RETURNING id, nombre, descripcion, precio, ilustracion"
        row = await app.db_connection.fetchrow(query, producto_id)
        if row:
            return {"id": row[0], "nombre": row[1], "descripcion": row[2], "precio": row[3], "ilustracion": row[4]}
        else:
            return {"message": "Producto no encontrado"}

    # Bloque de funciones CRUD para producto #

    # Bloque de funciones CRUD para suscripcion #

    @app.post("/suscripcion")
    async def crear_suscripcion(suscripcion: Suscripcion):
        query = "INSERT INTO suscripcion (fecha_inicio, fecha_fin, precio, tipo, id_usuario) VALUES ($1::date, $2::date, $3::numeric, $4::text, $5::integer) RETURNING id, fecha_inicio, fecha_fin, precio, tipo, id_usuario"
        values = (suscripcion.fecha_inicio, suscripcion.fecha_fin, suscripcion.precio, suscripcion.tipo, suscripcion.id_usuario)
        row = await app.db_connection.fetchrow(query, *values)
        return {"id": row[0], "fecha_inicio": row[1], "fecha_fin": row[2], "precio": row[3], "tipo": row[4], "id_usuario": row[5]}

    @app.get("/suscripcion/{suscripcion_id}")
    async def leer_suscripcion(suscripcion_id: int):
        query = "SELECT id, fecha_inicio, fecha_fin, precio, tipo, id_usuario FROM suscripcion WHERE id = $1"
        row = await app.db_connection.fetchrow(query, suscripcion_id)
        if row:
            return {"id": row[0], "fecha_inicio": row[1], "fecha_fin": row[2], "precio": row[3], "tipo": row[4], "id_usuario": row[5]}
        else:
            return {"message": "Suscripción no encontrada"}

    @app.put("/suscripcion/{suscripcion_id}")
    async def actualizar_suscripcion(suscripcion_id: int, suscripcion: Suscripcion):
        query = "UPDATE suscripcion SET nombre = $1, descripcion = $2, secciones =$3, diseño = $4, tipo = $5, url = $6 WHERE id = $7 RETURNING id, fecha_inicio, fecha_fin, precio, tipo, id_usuario"
        values = (suscripcion.fecha_inicio, suscripcion.fecha_fin, suscripcion.precio, suscripcion.tipo, suscripcion.id_usuario, suscripcion_id)
        row = await app.db_connection.fetchrow(query, *values)
        if row:
            return {"id": row[0], "fecha_inicio": row[1], "fecha_fin": row[2], "precio": row[3], "tipo": row[4], "id_usuario": row[5]}
        else:
            return {"message": "Suscripción no encontrada"}

    @app.delete("/suscripcion/{suscripcion_id}")
    async def borrar_suscripcion(suscripcion_id: int):
        query = "DELETE FROM suscripcion WHERE id = $1 RETURNING id, fecha_inicio, fecha_fin, precio, tipo, id_usuario"
        row = await app.db_connection.fetchrow(query, suscripcion_id)
        if row:
            return {"id": row[0], "fecha_inicio": row[1], "fecha_fin": row[2], "precio": row[3], "tipo": row[4], "id_usuario": row[5]}
        else:
            return {"message": "Suscripción no encontrada"}

    # Bloque de funciones CRUD para suscripcion #

    # Bloque de funciones CRUD para tienda #

    @app.post("/tienda")
    async def crear_tienda(tienda: Tienda):
        productos = tienda.productos.split(", ")
        query = "INSERT INTO tienda (nombre, direccion, id_vendedor, productos) VALUES ($1::text, $2::text, $3::integer, $4::text[]) RETURNING id, nombre, direccion, id_vendedor, productos"
        values = (tienda.nombre, tienda.direccion, tienda.id_vendedor, productos)
        row = await app.db_connection.fetchrow(query, *values)
        return {"id": row[0], "nombre": row[1], "direccion": row[2], "id_vendedor": row[3], "productos": row[4]}

    @app.get("/tienda/{tienda_id}")
    async def leer_tienda(tienda_id: int):
        query = "SELECT id, nombre, direccion, id_vendedor, productos FROM tienda WHERE id = $1"
        row = await app.db_connection.fetchrow(query, tienda_id)
        if row:
            return {"id": row[0], "nombre": row[1], "direccion": row[2], "id_vendedor": row[3], "productos": row[4]}
        else:
            return {"message": "Tienda no encontrada"}

    @app.put("/tienda/{tienda_id}")
    async def actualizar_tienda(tienda_id: int, tienda: Tienda):
        productos = tienda.productos.split(", ")
        query = "UPDATE tienda SET nombre = $1, direccion = $2, id_vendedor =$3, productos = $4 WHERE id = $5 RETURNING id, fecha_inicio, fecha_fin, precio, tipo, id_usuario"
        values = (tienda.nombre, tienda.direccion, tienda.id_vendedor, productos, tienda_id)
        row = await app.db_connection.fetchrow(query, *values)
        if row:
            return {"id": row[0], "nombre": row[1], "direccion": row[2], "id_vendedor": row[3], "productos": row[4]}
        else:
            return {"message": "Suscripción no encontrada"}

    @app.delete("/tienda/{tienda_id}")
    async def borrar_tienda(tienda_id: int):
        query = "DELETE FROM tienda WHERE id = $1 RETURNING id, fecha_inicio, fecha_fin, precio, tipo, id_usuario"
        row = await app.db_connection.fetchrow(query, tienda_id)
        if row:
            return {"id": row[0], "nombre": row[1], "direccion": row[2], "id_vendedor": row[3], "productos": row[4]}
        else:
            return {"message": "Suscripción no encontrada"}

    # Bloque de funciones CRUD para tienda #

    # Bloque de funciones CRUD para venta #

    @app.post("/venta")
    async def crear_venta(venta: Venta):
        productos = venta.productos.split(", ")
        query = "INSERT INTO venta (fecha, total, estado, id_vendedor, productos) VALUES ($1::date, $2::integer, $3::text, $4::integer,$5::text[]) RETURNING id, fecha, total, estado, id_vendedor, productos"
        values = (venta.fecha,venta.total,venta.estado,venta.id_vendedor, productos)
        row = await app.db_connection.fetchrow(query, *values)
        return {"id": row[0], "fecha": row[1], "total": row[2], "estado": row[3], "id_vendedor": row[4], "productos": row[5]}

    @app.get("/venta/{venta_id}")
    async def leer_venta(venta_id: int):
        query   = "SELECT id, fecha, estado, id_vendedor, productos FROM venta WHERE id = $1"
        row     = await app.db_connection.fetchrow(query, venta_id)
        if row:
            return {"id": row[0], "fecha": row[1], "total": row[2], "estado": row[3], "id_vendedor": row[4], "productos": row[5]}
        else:
            return {"message": "Venta no encontrada"}

    @app.put("/venta/{venta_id}")
    async def actualizar_venta(venta_id: int, venta: Venta):
        productos = venta.productos.split(", ")
        query = "UPDATE venta SET nombre = $1, direccion = $2, id_vendedor =$3, productos = $4 WHERE id = $5 RETURNING id, fecha, estado, id_vendedor, productos"
        values = (venta.fecha,venta.total,venta.estado,venta.id_vendedor, productos,venta_id)
        row = await app.db_connection.fetchrow(query, *values)
        if row:
            return {"id": row[0], "fecha": row[1], "total": row[2], "estado": row[3], "id_vendedor": row[4], "productos": row[5]}
        else:
            return {"message": "Venta no encontrada"}

    @app.delete("/venta/{venta_id}")
    async def borrar_venta(venta_id: int):
        query = "DELETE FROM venta WHERE id = $1 RETURNING id, fecha, estado, id_vendedor, productos"
        row = await app.db_connection.fetchrow(query, venta_id)
        if row:
            return {"id": row[0], "fecha": row[1], "total": row[2], "estado": row[3], "id_vendedor": row[4], "productos": row[5]}
        else:
            return {"message": "Venta no encontrada"}

    # Bloque de funciones CRUD para venta #

    @app.post("/registro_vendedor")
    async def registro_vendedor(data: dict):
        try:
            usuario_data = data.get("user")
            vendedor_data = data.get("vendedor")
            usuario = User(**usuario_data)
            vendedor = Vendedor(**vendedor_data)
            # Verificar si el correo electrónico ya existe en la base de datos
            query = "SELECT email FROM usuario WHERE email = $1"
            row = await app.db_connection.fetchrow(query, usuario.email)
            if row:
                return {"message": "El correo electrónico ya está registrado"}

            # Almacenar el nuevo usuario en la base de datos
            password_bytes = usuario.password.encode('utf-8')
            salt = hashlib.sha256(password_bytes).hexdigest().encode('utf-8')
            hashed_bytes = hashlib.pbkdf2_hmac('sha256', password_bytes, salt, 100000)
            hashed_password = salt + hashed_bytes

            # Convertir el hash a base64
            hashed_password_b64 = base64.b64encode(hashed_password).decode('utf-8')

            # Insertar el usuario en la tabla "usuario"
            query = "INSERT INTO usuario (name, email, cellphone, password, tipo) VALUES ($1::text, $2::text, $3::text, $4::text, $5::text) RETURNING id, name, email, cellphone, tipo"
            values = (usuario.name, usuario.email, usuario.cellphone, hashed_password_b64, usuario.tipo)
            usuario_row = await app.db_connection.fetchrow(query, *values)

            # Insertar el vendedor en la tabla "vendedor"
            ventas = vendedor.historial_ventas.split(", ")
            query = "INSERT INTO vendedor (nombre_tienda, rues, nombre) VALUES ($1::text, $2::integer, $3::text) RETURNING id, nombre_tienda, rues, historial_ventas, nombre"
            values = (vendedor.nombre_tienda, vendedor.rues, vendedor.nombre)
            vendedor_row = await app.db_connection.fetchrow(query, *values)

            print("usuario_row:", usuario_row)
            print("vendedor_row:", vendedor_row)

            return {
                "usuario": {"id": usuario_row[0], "name": usuario_row[1], "email": usuario_row[2], "cellphone": usuario_row[3],
                            "tipo": usuario_row[4]},
                "vendedor": {"id": vendedor_row[0], "nombre_tienda": vendedor_row[1], "rues": vendedor_row[2],
                            "historial_ventas": vendedor_row[3], "nombre": vendedor_row[4]}
            }
        except Exception as e:
            print(usuario)
            print(vendedor)
            return {"user" : usuario, "vendedor": vendedor, "error": str(e)}
        
    @app.post("/registro_comprador")
    async def registro_comprador(data: dict):
        usuario=None
        comprador = None
        try:
            usuario_data = data.get("user")
            comprador_data = data.get("comprador")
            usuario = User(**usuario_data)
            comprador = Comprador(**comprador_data)
            
            # Verificar si el correo electrónico ya existe en la base de datos
            query = "SELECT email FROM usuario WHERE email = $1"
            row = await app.db_connection.fetchrow(query, usuario.email)
            if row:
                return {"message": "El correo electrónico ya está registrado"}

            # Almacenar el nuevo usuario en la base de datos
            password_bytes = usuario.password.encode('utf-8')
            salt = hashlib.sha256(password_bytes).hexdigest().encode('utf-8')
            hashed_bytes = hashlib.pbkdf2_hmac('sha256', password_bytes, salt, 100000)
            hashed_password = salt + hashed_bytes

            # Convertir el hash a base64
            hashed_password_b64 = base64.b64encode(hashed_password).decode('utf-8')

            # Insertar el usuario en la tabla "usuario"
            query = "INSERT INTO usuario (name, email, cellphone, password, tipo) VALUES ($1::text, $2::text, $3::text, $4::text, $5::text) RETURNING id, name, email, cellphone, tipo"
            values = (usuario.name, usuario.email, usuario.cellphone, hashed_password_b64, usuario.tipo)
            usuario_row = await app.db_connection.fetchrow(query, *values)

            # Insertar el comprador en la tabla "comprador"
            compras = comprador.historial_compras.split(", ")
            query = "INSERT INTO comprador (name, direccion, telefono) VALUES ($1::text, $2::text, $3::bigint) RETURNING id, direccion, telefono, name"
            values = (comprador.name, comprador.direccion, comprador.telefono)
            comprador_row = await app.db_connection.fetchrow(query, *values)

            return {
                "usuario": {
                    "id": usuario_row[0],
                    "name": usuario_row[1],
                    "email": usuario_row[2],
                    "cellphone": usuario_row[3],
                    "tipo": usuario_row[4]
                },
                "comprador": {
                    "id": comprador_row[0],
                    "direccion": comprador_row[1],
                    "telefono": comprador_row[2],
                    "nombre": comprador_row[3]
                }
            }
        except Exception as e:
            return {"user": usuario, "comprador": comprador, "error": str(e)}

    return app

app = init_app()

def start():
    """Launched with 'poetry run start' at root level """
    uvicorn.run("app.main:app", host="localhost", port=8888, reload=True)