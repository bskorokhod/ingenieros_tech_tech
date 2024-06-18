# ingenieros_tech_tech - Patitas Perdidas
Repositorio para el TP Integral de la materia Introducción al Desarrollo de Software de la Facultad de Ingeniería de la Universidad de Buenos Aires.

## Descripción
Patitas Perdidas es un proyecto cuyo objetivo es desarrollar un sitio web para coordinar la búsqueda de mascotas extraviadas en la región del AMBA (Área Metropolitana de Buenos Aires) y reunirlas con sus familias. La plataforma ofrece funcionalidades para registrar mascotas perdidas, buscar animales encontrados y visualizar refugios de animales en tránsito.

## Características
* Registro de información sobre mascotas perdidas (tipo de animal, raza, color, zona de pérdida, etc.).
* Búsqueda de animales encontrados en la base de datos.
* Mapa interactivo para visualizar centros de animales en tránsito y añadir nuevos refugios.
* Vista de administrador para gestionar solicitudes de reportes de reencuentro y refugios.

## Instalación
### Requisitos
* Python 3.x
* pip (gestor de paquetes de Python)
* Tener acceso a una base de datos hosteada (el repositorio cuenta con un ejemplo de las sentencias SQL para configurar las tablas necesarias)

## Pasos
1. Clona el repositorio:
```bash
git clone https://github.com/bskorokhod/ingenieros_tech_tech.git
cd patitas-perdidas
```
2. Ejecutar archivo `init.sh` (crea los entornos virtuales de cada proyecto junto con las dependencias correspondientes)
```bash
bash init.sh
```
3. Inicializar en cada proyecto el ambiente virtual y ejecutar
```bash
cd proyecto_vistas
pipenv shell 
flask run --port=5000
```

```bash
cd proyecto_api
pipenv shell 
flask run --port=5001
```
## Uso
### Registro de Mascotas Perdidas
1. Accede a la vista `/perdido`.
2. Completa la información sobre la mascota perdida.
3. Envía el formulario.

### Búsqueda de Animales Encontrados
1. Accede a la vista `/encontrado`.
2. Introduce los filtros de búsqueda.
3. Revisa las tarjetas de las mascotas obtenidas y contactá al propietario si corresponde.

### Mapa de Refugios
1. Accede a la vista `/refugios`.
2. Visualiza los centros de animales en tránsito.

### Añadir un nuevo refugio
1. Accede a la vista `/agregar_refugio`
2. Completá el formulario con la información del nuevo refugios.

### Gestionar las solicitudes de reportes de reencuentro y refugios
1. Accede a la vista `/login_admin`
2. Inicia sesión como administrador.
3. Verifica o rechaza las solicitudes según corresponda.

## Documentación de los servicios de la API
Para acceder a la documentación de la API dirigirse al archivo `SERVICIOS.md` dentro de la carpeta `proyecto_api`