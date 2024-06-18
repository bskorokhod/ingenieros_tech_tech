# ingenieros_tech_tech
Repositorio para el TP Integral de la materia Introducción al Desarrollo de Software de la Facultad de Ingeniería de la Universidad de Buenos Aires.

## Endpoint /reportes_reencuentro

### Descripción
El servicio `/reportes_reencuentro` ofrece operaciones para gestionar reportes de mascotas que han sido encontradas tras haber estado perdidas.

### GET
Obtiene una lista paginada de reportes de reencuentros de mascotas perdidas que no han sido procesados.
#### Parámetros de Query
• `pag_reportes`: Parámetro opcional que especifica el número de la página que se desea obtener.
    • *Tipo*: int
    • *Valor por defecto*: 1
    • *Descripción*: Define el número de la página actual para la paginación. La paginación se basa en un número entero que representa la página que el usuario quiere ver.

• `limite_reportes`: Parámetro opcional que especifica el número de reportes a mostrar por página.
    • *Tipo*: int
    • *Valor por defecto*: 5
    • *Descripción*: Define la cantidad máxima de reportes a mostrar por cada página. Este valor limita el número de resultados devueltos por la consulta.
#### Ejemplos de Uso
Obtener la primera página de reportes (valores por defecto):

    http://127.0.0.1:5001/reportes_reencuentro/

Obtener la segunda página de reportes con 5 reportes por página:

    http://127.0.0.1:5001/reportes_reencuentro/?pag_reportes=2&limite_reportes=5

#### Respuesta
Si la consulta fue exitosa, el servicio devuelve una tupla que contiene un JSON y el código de estado `200`. 
La respuesta JSON tiene dos componentes principales:

1. `hay_pag_siguiente`: Esta clave está asociada a un valor booleano que indica si hay más reportes disponibles para mostrar en la siguiente página.
2. `reportes_reencuentro`: Esta clave está asociada a un diccionario de diccionarios, las claves del cual corresponden al campo `id_reporte` de la tabla `reportes_reencuentro`; y los valores son diccionarios que contienen los datos de la mascota asociada, incluyendo `nombre_mascota`, `direccion`, `fecha_extravio`, `telefono_contacto`, y `nombre_contacto`. Si no hay ningún reporte de reencuentro, entonces `reportes_reencuentro` estará asociada a un diccionario vacío.
```py 
{
    "hay_pag_siguiente": true,
    "reportes_reencuentro": {
        "1": {
            "direccion": "Calle Defensa 1234",
            "fecha_extravio": "01/05/2024",
            "id_mascota": 1,
            "nombre_contacto": "María Gómez",
            "nombre_mascota": "Luna",
            "telefono_contacto": "01112345678"
        },
        "2": {
            "direccion": "Calle Bolívar 5678",
            "fecha_extravio": "02/05/2024",
            "id_mascota": 2,
            "nombre_contacto": "Juan Pérez",
            "nombre_mascota": "Max",
            "telefono_contacto": "01187654321"
        },
        "3": {
            "direccion": "Avenida Santa Fe 4321",
            "fecha_extravio": "03/05/2024",
            "id_mascota": 3,
            "nombre_contacto": "Carla Fernández",
            "nombre_mascota": "Rocky",
            "telefono_contacto": "01123456789"
        },
        "4": {
            "direccion": "Calle Alvear 876",
            "fecha_extravio": "04/05/2024",
            "id_mascota": 4,
            "nombre_contacto": "Luis Martínez",
            "nombre_mascota": "Mia",
            "telefono_contacto": "01198765432"
        },
        "5": {
            "direccion": "Calle Rivadavia 567",
            "fecha_extravio": "05/05/2024",
            "id_mascota": 5,
            "nombre_contacto": "Ana López",
            "nombre_mascota": "Toby",
            "telefono_contacto": "01111223344"
        }
    }
}
```
#### Manejo de Errores
* Si ocurre un error al ejecutar la consulta, el servicio devuelve una tupla que contiene un JSON con la causa del error y el código de estado `500`. 

### POST
Agrega un nuevo registro a la tabla reportes_reencuentro, verificando previamente que la mascota exista y se encuentre reportada como perdida.
#### BODY
En el `body` de la solicitud se debe incluir un objeto de tipo JSON que contenga los datos de la mascota reportada como encontrada y cumpla con el siguiente formato:
La solicitud debe incluir un JSON con el campo `id`:
    • *Tipo*: int
    • *Descripción*: ID de la mascota que se desea reportar como reencontrada. Este campo es obligatorio.
#### Ejemplos de Uso
```py
    {
        "id": 1,
        "nombre_mascota": "Luna",
        "animal": "perro",
        "raza": "Labrador Retriever",
        "sexo": "Hembra",
        "color": "negro",
        "edad": "adulto",
        "coordx": -34.602676,
        "coordy": -58.383776,
        "fecha_extravio": "2024-05-01",
        "telefono_contacto": "01112345678",
        "nombre_contacto": "María Gómez",
        "direccion": "Calle Defensa 1234",
        "info_adicional": "Tiene una mancha blanca en la pata derecha",
        "encontrado": False
    }
```
#### Respuesta
Si la consulta fue exitosa, el servicio devuelve una tupla que contiene un JSON con un mensaje de éxito y el código de estado `201`. El JSON tiene el formato:
```py
{
    "Los cambios se realizaron correctamente"
}
```
#### Manejo de Errores
* Si el id de la mascota no es un entero positivo, o no hay ninguna mascota actualmente perdida asociada al mismo, el servicio devuelve una tupla que contiene un JSON con un mensaje de error y el código de estado `400`. Los objetos JSON tienen el formato:
```py
{
    "mensaje": "El id de la mascota es inválido"
}
```
```py
{
    "mensaje": "No existe ninguna mascota perdida asociada a ese id"
}
```
* Si ocurre un error al realizar la consulta, el servicio devuelve una tupla que contiene un JSON con la causa del error y el código de estado `500`. 

### PATCH
Modifica el estado de procesamiento de un reporte que haya sido descartado, verificando previamente la existencia del mismo.
#### BODY
En el `body` de la solicitud se debe incluir un objeto de tipo JSON que contenga el id del reporte de reencuentro rechazado y cumpla con el siguiente formato:
    • *Tipo*: int
    • *Descripción*: ID del reporte de reencuentro que se desea marcar como procesado. Este campo es obligatorio.
#### Ejemplos de Uso
```py
{
    "id_reporte": 1
}
```
#### Respuesta
Si la consulta fue exitosa, el servicio devuelve una tupla que contiene un JSON con un mensaje de éxito y el código de estado `200`. El JSON tiene el formato:
```py
{
    "Los cambios se realizaron correctamente"
}
```
#### Manejo de Errores
* Si el id del reporte no es un entero positivo, o no hay ningún reporte de reencuentro asociado al mismo, el servicio devuelve una tupla que contiene un JSON con un mensaje de error y el código de estado `400`. Los objetos JSON tienen el formato:
```py
{
    "mensaje": "El id del reporte es inválido"
}
```
```py
{
    "mensaje": "No existe ningun reporte de reencuentro asociado a ese id"
}
```
* Si hubo un error al hacer la consulta, el servicio devuelve una tupla que contiene un JSON con la causa del error y el código de estado `500`.

### PUT
Actualiza el estado en la tabla `animales_perdidos` de una mascota verificada como encontrada y marca todos los reportes de reencuentro asociados a la misma como procesados.
#### BODY
En el `body` de la solicitud se debe incluir un objeto de tipo JSON que contenga el id de la mascota que fue verificada como encontrada y cumpla con el siguiente formato:
    • *Tipo*: int
    • *Descripción*: ID de la mascota que se desea marcar como encontrada. Este campo es obligatorio.
#### Ejemplos de Uso
```py
{
    "id_mascota": 1
}
```
#### Respuesta
Si la consulta fue exitosa, el servicio devuelve una tupla que contiene un JSON con un mensaje de éxito y el código de estado `200`. El JSON tiene el formato:
```py
{
    "Los cambios se realizaron correctamente"
}
```
#### Manejo de Errores
* Si el id de la mascota no es un entero positivo; no hay ninguna mascota que se haya reportado como encontrada asociada al id enviado; o todos los reportes de reencuentro fueron previamente procesados, el servicio devuelve una tupla que contiene un JSON con un mensaje de error y el código de estado `400`. Los objetos JSON tienen el formato:
```py
{
    "mensaje": "El id de la mascota es inválido"
}
```
```py
{
    "mensaje": "Bad Request"
}
```
* Si hubo un error al hacer la consulta, el servicio devuelve una tupla que contiene un JSON con la causa del error y el código de estado `500`.