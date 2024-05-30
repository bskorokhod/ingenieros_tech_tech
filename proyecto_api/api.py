from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# uri para acceder a la Base de datos
URI_BBDD = "" 

app = Flask(__name__)
engine = create_engine(URI_BBDD) 

def traer_info(query: str, codigo_satisfactorio: int, codigo_error: int) -> tuple:
    """
    Envía una solicitud a la base de datos y devuelve el resultado y el código de estado HTTP.
    Atrapando los errores posibles, devolviendo la causa de error en un json y el código correspondiente.
    
    PRECONDICIONES:
        - 'query' es una solicitud válida.
        - 'codigo_satisfactorio' y 'codigo_error' son los códigos de estado HTTP correspondientes.
    """
    try:
        with engine.connect() as conexion:
            resultado = conexion.execute(text(query))
            return resultado, codigo_satisfactorio
    except SQLAlchemyError as err:
        return jsonify(str(err.__cause__)), codigo_error 


def realizar_cambios(query, codigo_satisfactorio: int, codigo_error: int) -> tuple:
    """
    Envía una solicitud a la base de datos, guarda los cambios que causa y devuelve una tupla, cuyo segundo elemnto es el código de estado HTTP.
    Atrapando los errores posibles, devolviendo la causa de error en un json y el código correspondiente.

    PRECONDICIONES:
        - 'query' es una solicitud válida.
        - 'codigo_satisfactorio' y 'codigo_error' son los códigos de estado HTTP correspondientes.
    """
    try:
        with engine.connect() as conexion:
            conexion.execute(text(query))
            conexion.commit() # creo q es así el commit para guardar cambios
            return None, codigo_satisfactorio
    except SQLAlchemyError as err:
        return jsonify(str(err.__cause__)), codigo_error