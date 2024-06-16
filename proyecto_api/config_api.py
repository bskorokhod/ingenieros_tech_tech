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

# Diccionario Endpoint master
TABLAS = {} # un Dict o Set con las tablas de la Base de Datos