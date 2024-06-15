from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def traer_info(query: str, codigo_satisfactorio: int, engine) -> tuple[2]:
    """
    Envía una solicitud a la base de datos y devuelve el resultado y el código de estado HTTP.
    Atrapando los errores posibles, devolviendo (en caso de ocurrir) la causa de error y el código correspondiente.
    
    PRECONDICIONES:
        - 'query' es una solicitud válida de tipo 'SELECT'.
        - 'codigo_satisfactorio' y es el código de estado HTTP correspondiente al exito de la request.
        - 'engine' es el "motor" resultado de 'create_engine' (que conecta con la Base de datos).
    """
    try:
        with engine.connect() as conexion:
            resultado = conexion.execute(text(query))
            return resultado, codigo_satisfactorio
    except SQLAlchemyError as err:
        return str(err.__cause__), 500

def realizar_cambios(query: str, codigo_satisfactorio: int, engine) -> tuple[str, int]:
    """
    Envía una solicitud a la base de datos, guarda los cambios que causa y devuelve una tupla, 
    cuyo primer elemento es una cadena y el segundo, es el código de estado HTTP.
    Atrapando los errores posibles, devolviendo (en caso de ocurrir) la causa de error y el código correspondiente.

    PRECONDICIONES:
        - 'query' es una solicitud válida.
        - 'codigo_satisfactorio' y es el código de estado HTTP correspondiente al exito de la request.
        - 'engine' es el "motor" resultado de 'create_engine' (que conecta con la Base de datos).
    """
    try:
        with engine.begin() as conexion:
            conexion.execute(text(query))
            # al realizar engine.begin() al finalizar el bloque se agrega automáticamente el engine.commit() tras realizar los cambios
            return "Los cambios se realizaron correctamente", codigo_satisfactorio
    except SQLAlchemyError as err:
        return str(err.__cause__), 500

def realizar_query_validacion(query: str, engine) -> int:
    """
    Recibe una 'query' y un 'engine', y ejecuta traer_info con ese 'engine'.
    Luego verifica si esa query trajo al menos una coincidencia desde la Base de datos con la cual conecta 'engine'.
    
    PRECONDICIONES:
        - 'query' es una solicitud válida de tipo "SELECT"
    POSTCONDICIONES:
        - Devuelve un entero:    
            1 -> Hubo coincidencia
            0 -> No hubo coincidencia
           -1 -> Error al validar
    """
    resultado, codigo = traer_info(query, 200, engine)
    if codigo != 200:
        return -1 # ocurrió un error validando
    if resultado.rowcount != 0:
        return 1 # Se encontró al menos una fila
    return 0