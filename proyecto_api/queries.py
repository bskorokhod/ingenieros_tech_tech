from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def traer_info(query: str, codigo_satisfactorio: int, codigo_error: int, engine) -> tuple[str, int]:
    """
    Envía una solicitud a la base de datos y devuelve el resultado y el código de estado HTTP.
    Atrapando los errores posibles, devolviendo (en caso de ocurrir) la causa de error y el código correspondiente.
    
    PRECONDICIONES:
        - 'query' es una solicitud válida.
        - 'codigo_satisfactorio' y 'codigo_error' son los códigos de estado HTTP correspondientes.
        - 'engine' es el "motor" resultado de 'create_engine' (conectando con la Base de datos).
    """
    try:
        with engine.connect() as conexion:
            resultado = conexion.execute(text(query))
            return resultado, codigo_satisfactorio
    except SQLAlchemyError as err:
        return str(err.__cause__), codigo_error

def realizar_cambios(query, codigo_satisfactorio: int, codigo_error: int, engine) -> tuple[str, int]:
    """
    Envía una solicitud a la base de datos, guarda los cambios que causa y devuelve una tupla, 
    cuyo primer elemento es una cadena y el segundo, es el código de estado HTTP.
    Atrapando los errores posibles, devolviendo (en caso de ocurrir) la causa de error y el código correspondiente.

    PRECONDICIONES:
        - 'query' es una solicitud válida.
        - 'codigo_satisfactorio' y 'codigo_error' son los códigos de estado HTTP correspondientes.
        - 'engine' es el "motor" resultado de 'create_engine' (conectando con la Base de datos).
    """
    try:
        with engine.begin() as conexion:
            conexion.execute(text(query))
            # al realizar engine.begin() al finalizar el bloque se agrega automáticamente el engine.commit() tras realizar los cambios
            return "Los cambios se realizaron correctamente", codigo_satisfactorio
    except SQLAlchemyError as err:
        return str(err.__cause__), codigo_error