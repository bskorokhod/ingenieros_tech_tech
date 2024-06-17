from validaciones import es_id, es_varchar, es_float, es_telefono, es_fecha, es_bool

# Constantes generales de la API
NOMBRE_BASE_DATOS = ""
# Por ahora, hosteamos la BBDD locaclmente
CONECTOR_SQL = f"mysql+mysqlconnector://root@localhost/{NOMBRE_BASE_DATOS}"
PUERTO_API = 5001

# Tablas de la base de datos
TABLA_ADMIN = "admin"
TABLA_ANIMALES_PERDIDOS = "animales_perdidos"
TABLA_CARACTERISTICAS_MASCOTAS = "caracteristicas_mascotas"
TABLA_REFUGIOS = "refugios"
TABLA_REPORTES_REENCUENTRO = "reportes_reencuentro"

# Opciones de valores para los campos correspondientes
LISTA_SEXOS = ["Macho", "Hembra"]

LISTA_EDADES = ["Cachorro", "Joven", "Adulto"]

# Diccionario Endpoint master
TABLAS = {TABLA_ADMIN: {"id": (es_id),
                        "usuario": (es_varchar, 10),
                        "contraseña": (es_varchar, 50)},
          TABLA_ANIMALES_PERDIDOS: {"id": (es_id),
                                    "nombre_mascota": (es_varchar, 20),
                                    "animal": (es_varchar, 5),
                                    "raza": (es_varchar, 30),
                                    "sexo": (es_varchar, 9),
                                    "color": (es_varchar, 8),
                                    "edad": (es_varchar, 9),
                                    "direccion": (es_varchar, 100),
                                    "coord_x": (es_float),
                                    "coord_y": (es_float),
                                    "fecha_extravio": (es_fecha),
                                    "telefono_contacto": (es_telefono),
                                    "nombre_contacto": (es_varchar, 64),
                                    "info adicional": (es_varchar, 280),
                                    "encontrado": (es_bool)},
          TABLA_CARACTERISTICAS_MASCOTAS: {"id": (es_id),
                                           "animal": (es_varchar, 5),
                                           "caracteristica": (es_varchar, 5),
                                           "valor": (es_varchar, 30)},
          TABLA_REFUGIOS: {"id": (es_id),
                           "nombre": (es_varchar, 64),
                           "direccion": (es_varchar, 100),
                           "coord_x": (es_float),
                           "coord_y": (es_float),
                           "telefono": (es_telefono),
                           "aceptado": (es_bool)},
          TABLA_REPORTES_REENCUENTRO: {"id reporte": (es_id),
                                       "id mascota": (es_id),
                                       "fue_procesado": (es_bool)}}