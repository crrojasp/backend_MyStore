import uvicorn
from fastapi import FastAPI, Response, File, UploadFile, Request, status, HTTPException, Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import asyncpg
import secrets
from tkinter import *
import io
import base64
import datetime
from PIL import Image
import hashlib
from fastapi.responses import JSONResponse
import jwt
import psycopg2
from psycopg2.extras import RealDictCursor
import traceback
from decimal import Decimal
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.model.usuario import User, UserLogin
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from fastapi.exceptions import RequestValidationError
from app.rutas import usuario, vendedor, comprador, carrito, compra, devolucion, lista_deseos, envio, plantilla, producto, suscripcion, tienda, venta


ALGORITHM = "HS256"
SECRET_KEY = secrets.token_hex(32)
origins= ["*"]
app = FastAPI()

def init_app():

    class MyForm(FlaskForm):
        name = StringField('Name')
        submit = SubmitField('Submit')

    #Instancia de la aplicacion FastApi
    app = FastAPI(
        title= "MyStore",
        description= "Pagina  de ingreso",
        version= "0.9.12"
    )

    #Configuracion del middleware CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Type"]
    )

    #Funcion que se ejecuta al iniciar la aplicacion, establece la conexion con la base de datos
    @app.on_event("startup")
    async def startup():
        app.db_connection = await connect_db()

    #Funcion que se ejecuta al cerrar la aplicacion, cierra la conexion con la base de datos    
    @app.on_event("shutdown")
    async def shutdown():
        await app.db_connection.close()

    #Conexion a la base de datos
    async def connect_db():
        conn = await asyncpg.connect(user='postgres', password='12345', database='My_Store', host='localhost')
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

        password_bytes = user.password.encode('utf-8')
        salt = hashlib.sha256(password_bytes).hexdigest().encode('utf-8')
        hashed_bytes = hashlib.pbkdf2_hmac('sha256', password_bytes, salt, 100000)
        hashed_password = salt + hashed_bytes

        # Convertir el hash a base64
        hashed_password_b64 = base64.b64encode(hashed_password).decode('utf-8')
        
        # Almacenar el nuevo usuario en la base de datos
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
                    {"user": user_data, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
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


    # Rutas para usuario #
    
    app.include_router(usuario.router)

    # Rutas para vendedor #

    app.include_router(vendedor.router)

    # Rutas para comprador #

    app.include_router(comprador.router)

    # Rutas para carrito de compras #

    app.include_router(carrito.router)

    # Rutas para compra

    app.include_router(compra.router)

    # Rutas para devolucion #

    app.include_router(devolucion.router)

    # Rutas para lista de deseos

    app.include_router(lista_deseos.router)

    # Rutas para envio

    app.include_router(envio.router)

    # Rutas para plantilla #

    app.include_router(plantilla.router)

    # Rutas para producto #

    app.include_router(producto.router)

    # Rutas para suscripcion #

    app.include_router(suscripcion.router)

    # Rutas para tienda #

    app.include_router(tienda.router)

    # Bloque de funciones CRUD para venta #

    app.include_router(venta.router)

    return app

app = init_app()

def start():
    """Launched with 'poetry run start' at root level """
    uvicorn.run("app.main:app", host="localhost", port=8888, reload=True)