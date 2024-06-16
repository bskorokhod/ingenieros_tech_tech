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
LISTA_RAZAS_ANIMAL = {
    "perro": ["Labrador Retriever", "Golden Retriever", "Ovejero Aleman", "Bulldog Ingles", "Beagle", "Caniche", "Boxer", "Salchicha", "Husky Siberiano", "Rottweiler", "Yorkshire Terrier", "Chihuahua", "Shih Tzu", "Dobermann", "Cocker Spaniel Ingles", "Pomeranian (Spitz Aleman)", "Bulldog Frances", "Border Collie", "Basset Hound", "Gran Danes", "Dogo Aleman", "Mestizo", "Otro / No se"],
    "gato": ["Persa", "Siames", "Maine Coon", "Bengala", "Esfinge", "Ragdoll", "British Shorthair", "Azul Ruso", "Abisinio", "Fold escoces (Scottish Fold)", "Exotico de Pelo Corto", "Himalayo", "Devon Rex", "Burmes", "Cornish Rex", "American Shorthair", "Birmano", "Angora Turco", "Bombay", "Tonquines", "Mestizo", "Otro / No se"]
}

LISTA_SEXOS = ["Macho", "Hembra"]

LISTA_COLORES_ANIMAL = {
    "perro": ["negro", "blanco", "gris", "marron", "dorado"],
    "gato": ["negro", "blanco", "gris", "marron", "naranja"]
}

LISTA_EDADES = ["Cachorro", "Joven", "Adulto"]

# Diccionario Endpoint master
TABLAS = {} # un Dict o Set con las tablas de la Base de Datos