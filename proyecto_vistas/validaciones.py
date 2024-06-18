import re
from datetime import datetime

# Validaciones de tipo de dato básicas
def es_id(id) -> bool:
    """ 
    Verifica si `id` es un número entero positivo.
    """
    # Se convierte a string para evitar excepciones al usar el método isdecimal()
    id = str(id)
    if id.isdecimal(): return int(id) > 0
    return False
    
def es_float(valor) -> bool:
    """ 
    Verifica si `valor` se puede convertir a número flotante.
    """
    # Se convierte a string para evitar excepciones al usar el método match()
    valor = str(valor)
    # Expresión regular para un número float
    regex_float = r'^[-+]?\d+\.\d+$'
    return bool(re.match(regex_float, valor))

def es_telefono(telefono) -> bool:
    """ 
    Verifica si un dato es un teléfono válido.
    """
    # Se convierte a string para evitar excepciones al usar el método isdecimal() y la función len()
    telefono = str(telefono)
    return telefono.isdecimal() and 8 <= len(telefono) <= 20

def es_fecha(fecha) -> bool:
    """
    Verifica que un dato sea una fecha existente con el formato AAAA-MM-DD 
    y ademas sea posterior al 2000-01-01 y anterior a la fecha actual.
    """
    # Se convierte a string para evitar excepciones al usar el método match()
    fecha = str(fecha)

    # Expresión regular para una fecha con el formato AAAA-MM-DD
    regex_fecha = r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$'
    
    if not re.match(regex_fecha, fecha):
        return False
    
    anio, mes, dia = map(int, fecha.split('-'))
    
    # Días máximos por mes
    dias_por_mes = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    # Ajuste para años bisiestos
    if anio % 4 == 0 and (anio % 100 != 0 or anio % 400 == 0):
        dias_por_mes[1] = 29

    # Verificar que el día no exceda el máximo para el mes dado
    if 1 <= dia <= dias_por_mes[mes - 1]:
        return datetime(2000, 1, 1) < datetime(anio, mes, dia) <= datetime.now()

    return False

def es_varchar(palabra, largo: int) -> bool:
    """
    Verifica si `palabra` tiene una longitud menor o igual a la especificada.
    """
    # Se convierte a string para evitar excepciones al usar la función len()
    palabra = str(palabra)
    return len(palabra) <= largo

def es_bool(valor) -> bool:
    """
    Verifica si `valor` es un booleano.
    """
    return isinstance(valor, bool)
    
# Validaciones de tipos en base de datos
def es_animal_perdido(datos :dict) -> bool:
    """
    Evalua si los datos enviados corresponden a un registro válido de la tabla animales_perdidos.

    PRE:
        - `datos` es un diccionario.

    POS:
        - Devuelve True si las claves del diccionario `datos` corresponden a las columnas de la tabla animales_perdidos y
        los valores asociados son campos válidos para la misma. Caso contrario, devuelve False.
    """
    try:
    # Se tiene en cuenta que el campo info_adicional es opcional    
        return (
            es_varchar(datos['nombre_mascota'], 20) and 
            es_varchar(datos['animal'], 5) and 
            es_varchar(datos['raza'], 30) and 
            es_varchar(datos['sexo'], 9) and
            es_varchar(datos['color'], 8) and 
            es_varchar(datos['edad'], 9) and
            es_varchar(datos['direccion'], 100) and 
            es_float(datos['coordx']) and 
            es_float(datos['coordy']) and 
            es_fecha(datos['fecha_extravio']) and 
            es_telefono(datos['telefono_contacto']) and 
            es_varchar(datos['nombre_contacto'], 64) and 
            es_varchar(datos.get('info_adicional', ""), 280)
            )
    except KeyError:
        return False

def es_refugio(datos :dict) -> bool:
    """
    Evalua si los datos enviados corresponden a un registro válido de la tabla refugios.

    PRE:
        - `datos` es un diccionario.

    POS:
        - Devuelve True si las claves del diccionario `datos` corresponden a las columnas de la tabla refugios y
        los valores asociados son campos válidos para la misma. Caso contrario, devuelve False.
    """
    try:
        return (
            es_varchar(datos['nombre'], 64) and 
            es_varchar(datos['direccion'], 100) and 
            es_float(datos['coordx']) and 
            es_float(datos['coordy']) and 
            es_telefono(datos['telefono'])
            )
    except KeyError:
        return False

def es_admin(datos :dict) -> bool:
    """
    Evalua si los datos enviados corresponden a un registro válido de la tabla admin.

    PRE:
        - `datos` es un diccionario.

    POS:
        - Devuelve True si las claves del diccionario `datos` corresponden a las columnas de la tabla admin y 
        los valores asociados son campos válidos para la misma. Caso contrario, devuelve False.
    """
    try:
        return es_varchar(datos['usuario'], 10) and es_varchar(datos['contrasena'], 50)
    except KeyError:
        return False

def es_caracteristica_mascota(datos :dict) -> bool:
    """
    Evalua si los datos enviados corresponden a un registro válido de la tabla caracteristicas_mascotas.

    PRE:
        - `datos` es un diccionario.

    POS:
        - Devuelve True si las claves del diccionario `datos` corresponden a las columnas de la tabla caracteristicas_mascotas y
        los valores asociados son campos válidos para la misma. Caso contrario, devuelve False.
    """
    try:
        return es_varchar(datos['animal'], 5) and es_varchar(datos['caracteristica'], 5) and es_varchar(datos['valor'], 30)
    except KeyError:
        return False