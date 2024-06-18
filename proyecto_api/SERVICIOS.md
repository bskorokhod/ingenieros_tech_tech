# Documentación de los servicios de la API

# ingenieros_tech_tech
Repositorio para el TP Integral de la materia Introducción al Desarrollo de Software de la Facultad de Ingeniería de la Universidad de Buenos Aires.

## Endpoint /mascotas_perdidas

### Descripción
El servicio `/mascotas_perdidas` permite registrar y obtener los datos de masctoas que se hayan extraviado.

### POST
Registra una mascota perdida en la tabla `animales_perdidos` de la Base de Datos.

#### BODY
El `body` debe contener todas las columnas junto a sus valores de una fila correspondiente a la tabla `animales_perdidos`, en formato JSON. Las columna `id` no se debe enviar, `encontrado` e `info_adicional` son opcionales.

#### Ejemplo de Uso
```json
    {
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
    }
```
#### Respuesta
Se devuelve un JSON con un `mensaje` que indica si la solicitud se envió correctamente, junto a un código de estado `201`.

#### Manejo de Errores
Si el `body` no cumple con lo necesario el código de estado será `400`, y en caso de que haya habido un error al ejecutar el registro en la Base de Datos será `500`.

### GET
Obtiene un JSON que contiene la página que se solicitó, confirmaciones de que exita una página anterior o una posterior y una lista paginada de las mascotas perdidas que cumplan con los filtros indicados en los parámetros.

#### Parámetros de Query
* `pagina`: Parámetro opcional que indica el número de la página que se solicitó.
    * *Tipo*: int
    * *Valor por defecto*: 1
    * *Descripción*: Define el número de la página actual para la paginación. La paginación se basa en un número entero que representa la página que el usuario quiere ver.

* `elementos`: Parámetro opcional que representa la cantidad de mascotas que se envian en `mascotas`.
    * *Tipo*: int
    * *Valor por defecto*: 20
    * *Descripción*: Define la cantidad máxima de mascotas que se van a devolver en el JSON.

* Cualquier columna que pertenezca a la tabla `animales_perdidos` de la Base de datos.
    * *Tipo*: El mismo que el de la columna
    * *Valor por defecto*: Ninguno
    * *Descripción*: Las mascotas que se devuelven, se filtran según las que coincidan con los valores para cada uno de este tipo de parámetros enviados.
#### Ejemplos de Uso
Obtener la primera página con un máximo de 20 mascotas sin ningún filtro:

    http://127.0.0.1:5001/mascotas_perdidas

Obtener la segunda página con un máximo de 5 mascotas con algunos filtros, en este caso, animal, color y encontrado:

    http://127.0.0.1:5001/masctoas_perdidas?pagina=2&elementos=5&animal=perro&color=blanco&encontrado=0

#### Respuesta
Si la respuesta fue correcta, se devuelve un JSON junto al código de estado de estado `200`.
El JSON contiene:
1. `mascotas`: Una lista de diccionarios que contiene los datos de las mascotas que cumplan con los filtros, página y elementos solicitados.
2. `pagina`: La página que se solicitó.
3. `hay_pagina_previa`: Un valor booleano que indica si se podría solicitar una página anterior a esta.
4. `hay_pagina_siguiente`: Un valor booleano que indica si se podría solicitar una página posterior a esta.

```json
{
    "mascotas": [
        {
            "id": 1,
            "nombre_mascota": "Tobi",
            "animal": "Perro",
            "raza": "Mestizo",
            "sexo": "Macho",
            "color": "Blanco",
            "edad": "Cachorro",
            "direccion": "Av la plata 1001, CABA",
            "coordx": -34.523232,
            "coordy": -53.234123,
            "fecha_extravio": "2024-06-18",
            "telefono_contacto": "01174652834",
            "nombre_contacto": "Juan Pérez",
            "info_adicional": "Se encariña mucho con extraños.",
            "encontrado": 0
        }, 
        ...
    ],
    "pagina": 2,
    "hay_pagina_previa": true,
    "hay_pagina_siguiente": false
}
```
#### Manejo de Errores
* Si ocurre un error al ejecutar la consulta, el servicio devuelve una tupla que contiene un JSON con la causa del error y el código de estado `500`. 

## API Endpoint '/login_admin'

Recibe solo requests del método `GET`.

### GET

#### Parametros de Query
* `user` : Parametro 
* `password` : 

Estos parametros los almacena en dos variables llamadas como los parametros.

Manda a la BBDD una consulta 
```sql
SELECT * FROM admin WHERE usuario = '{user}' AND contrasena = '{password}'
```
para buscar coincidencias.

Si la consulta encuentra al menos una fila, devuelve un JSON con el siguiente formato y el código de estado 200:
```json
{
    "code": 1
}
```

Si no encuentra coincidencias, devuelve un JSON con el siguiente formato y el código de estado 200:
```json
{
    "code": 0
}
```


#### Errores en el Endpoint
En caso de que ocurra un error en la conexion con la BBDD se retorna un json con la causa o causas del error y el codigo de estado 500


## Endpoint /reportes_reencuentro

### Descripción
El servicio `/reportes_reencuentro` ofrece operaciones para gestionar reportes de mascotas que han sido encontradas tras haber estado perdidas.

### GET
Obtiene una lista paginada de reportes de reencuentros de mascotas perdidas que no han sido procesados.
#### Parámetros de Query
* `pag_reportes`: Parámetro opcional que especifica el número de la página que se desea obtener.
    * *Tipo*: int
    * *Valor por defecto*: 1
    * *Descripción*: Define el número de la página actual para la paginación. La paginación se basa en un número entero que representa la página que el usuario quiere ver.

* `limite_reportes`: Parámetro opcional que especifica el número de reportes a mostrar por página.
    * *Tipo*: int
    * *Valor por defecto*: 5
    * *Descripción*: Define la cantidad máxima de reportes a mostrar por cada página. Este valor limita el número de resultados devueltos por la consulta.
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
```json 
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
```json
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
```json
{
    "Los cambios se realizaron correctamente"
}
```
#### Manejo de Errores
* Si el id de la mascota no es un entero positivo, o no hay ninguna mascota actualmente perdida asociada al mismo, el servicio devuelve una tupla que contiene un JSON con un mensaje de error y el código de estado `400`. Los objetos JSON tienen el formato:
```json
{
    "mensaje": "El id de la mascota es inválido"
}
```
```json
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
```json
{
    "id_reporte": 1
}
```
#### Respuesta
Si la consulta fue exitosa, el servicio devuelve una tupla que contiene un JSON con un mensaje de éxito y el código de estado `200`. El JSON tiene el formato:
```json
{
    "Los cambios se realizaron correctamente"
}
```
#### Manejo de Errores
* Si el id del reporte no es un entero positivo, o no hay ningún reporte de reencuentro asociado al mismo, el servicio devuelve una tupla que contiene un JSON con un mensaje de error y el código de estado `400`. Los objetos JSON tienen el formato:
```json
{
    "mensaje": "El id del reporte es inválido"
}
```
```json
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
```json
{
    "id_mascota": 1
}
```
#### Respuesta
Si la consulta fue exitosa, el servicio devuelve una tupla que contiene un JSON con un mensaje de éxito y el código de estado `200`. El JSON tiene el formato:
```json
{
    "Los cambios se realizaron correctamente"
}
```
#### Manejo de Errores
* Si el id de la mascota no es un entero positivo; no hay ninguna mascota que se haya reportado como encontrada asociada al id enviado; o todos los reportes de reencuentro fueron previamente procesados, el servicio devuelve una tupla que contiene un JSON con un mensaje de error y el código de estado `400`. Los objetos JSON tienen el formato:
```json
{
    "mensaje": "El id de la mascota es inválido"
}
```
```json
{
    "mensaje": "Bad Request"
}
```
* Si hubo un error al hacer la consulta, el servicio devuelve una tupla que contiene un JSON con la causa del error y el código de estado `500`.


## Endpoint '/refugios'
Recibe métodos `GET`, `POST`, `PATCH`, `DELETE`  
### GET 
Devuelve un JSON (lista de diccionarios) con formato:
```py
{
    "refugios":[   
        {
            'id': '1',
            'nombre': 'Red Patitas',
            "coordx":'123.456',
            "coordy":'123.456',
            'telefono': '11 1234-5678',
            'direccion': 'Paseo Colón 2345'
        },
        {
            'id': '2',
            'nombre': 'Patitas felices',
            "coordx":'123.456',
            "coordy":'123.456',
            'telefono': '11 4321-8765',
            'direccion': 'Paseo Colón 2345'
        }
    ],
    "hay_pag_siguiente":bool
}
```

Donde cada diccionario tiene la información correspondiente a un refugio, almacenado en la Base de datos.

#### Parámetros
Recibe como parámetros/argumentos 3 claves: 

* Recibe el parámetro `aceptado` que es o `"TRUE"` o `"FALSE"`.

Dependiendo de este parámetro, devolverá o los refugios que hayan sido o no aceptados.  
En caso no se trate de un parámetro esperado, se considera una `Bad Request`.

* Recibe el parámetro `pagina` como un `int` número de página actual.

* Recibe el parámetro `elementos` como un `int` cantidad de elementos máximos a entregar por página. 

#### Retorno
* En base a los parámetros `elemntos` y `pagina`, se realiza la paginación una solicitud SQL de forma:

```sql
SELECT * FROM 'refugios' WHERE aceptado = TRUE LIMIT 8 OFFSET 0;
```

En este caso `elementos` es 8 y `pagina` 1. De manera que si ingresa `pagina:3` y `elemntos:8`. La query que se realizará es la siguiente: 

```sql
SELECT * FROM 'refugios' WHERE aceptado = TRUE LIMIT 8 OFFSET 16;
```
De esta manera, se devolverán únicamente los refugios correspondientes a la página 3, (iniciando desde el refugio `pagina * elementos - 1`, que es 16 en este caso) siendo el límite por página de 8 (es decir, esta query traerá los refugios 16 a 24).

* Devuelve con la clave `"hay_pag_siguiente"` un valor booleano. que indica si existe por lo menos 1 refugio maás en la Base de datos.


* Devuelve además, el código de estado `200` en caso de no ocurrir errores.

### POST
Recibe la información de un json de formato:
```py
{
    "nombre":"nombre_refugio",
    "coordx":'123.456',
    "coordy":'123.456',
    "telefono":'1115642564',
    "direccion":"Paseo Colón 2345",
}
```

Esta es la información correspondiente a un nuevo refugio a agregar a la BBDD.

* Devuelve el código de estado `201` en caso de no ocurrir errores.

### PATCH

Recibe la `id` de un refugio en un JSON de formato `{'id':6}`.  
Verifica si existe el `id` (tomándolo como una `Bad request`, si este no existe).  
Y en caso afirmativo, cambia el valor de la columna `aceptado` a `true` para el `id` recibido.

* Devuelve el código de estado `200` en caso de no ocurrir errores.

### DELETE
Recibe la `id` de un refugio en un JSON de formato `{'id':9}`.  
Verifica si existe el `id` (tomándolo como una `Bad request`, si este no existe).  
Y en caso afirmativo, elmina de la BBDD, toda la información correspondiente a este `id`.

* Devuelve el código de estado `200` en caso de no ocurrir errores.

### Manejo de errores en el Endpoint
En caso de no cumplirse con el contrato de uso establecido:   
* Se devolverá un JSON con el mensaje `Bad request` y el código de estado `400`.
*  En caso de ocurrir un error conectando con la Base de datos (Un error interno del servidor), devolverá la causa del error en un JSON de formato `{"mensaje":casua_error}`, además del código `500`.


## Endpoint /master

### Descripción
Permite realizar request de tipo GET, POST, PATCH y DELETE sobre cualquier tabla de la Base de Datos al conocer su identificador único de la tabla.

### GET
Devuelve una fila de la `tabla` pedida al conocer su `id` (`id_reporte` en el caso de la tabla `reportes_reencuentro`).

#### Parámetros de Query
* `tabla`: El nombre de la tabla a la cuál se quiere acceder.
    * *Tipo*: string
    * *Valor por defecto*: Ninguno
    * *Descripción*: El nombre de la tabla tiene que encontrarse en la Base de Datos.

* `id`/`id_reporte`: El id de la fila que se quiere pedir.
    * *Tipo*: int
    * *Valor por defecto*: Ninguno
    * *Descripción*: El id de la fila que se quiere solicitar. Tiene que corresponder a una fila que exista.

#### Ejemplos de Uso
Obtener el refugio de id: 2 de la tabla `refugios`:

    http://127.0.0.1:5001/master?tabla=refugios&id=2

Obtener el reporte de id_reporte: 5 de la tabla `reportes_reencuentro`:

    http://127.0.0.1:5001/master?tabla=reportes_reencuentro&id_reporte=5

#### Respuesta
Se devuelve un JSON con los datos de esa tabla y los valores de la fila:
```json
{
    "id": 2,
    "nombre": "Refugio San Francisco de Asís",
    "direccion": "Avenida Rivadavia 4567",
    "coordx": -34.607162,
    "coordy": -58.384264,
    "teléfono": "01148975634",
    "aceptado": 1
}
```
#### Manejo de Errores
* Si ocurre un error al ejecutar la consulta, el servicio devuelve una tupla que contiene un JSON con la causa del error y el código de estado `500`. Si no se envía una tabla o un id, el código de estado es `400`.

### DELETE
Elimina una fila de la tabla pedida al conocer su id (id_reporte en el caso de la tabla reportes_reencuentro).

#### Parámetros de Query
Recibe como parámetros:
* `tabla` es el nombre (`str`) de la tabla en la cuál se quiere eliminar una fila. El nombre de la tabla tiene que encontrarse en la Base de Datos.

* id/id_reporte: El id (`int`) de la fila que se quiere pedir. El id de la fila que se quiere solicitar. Tiene que corresponder a una fila que exista, de lo contrario, se considera.

#### Ejemplo de Uso

Eliminar la mascota de id: 22 de la tabla animales_perdidos:
Y tras realizar un GET a la siguiente URI:

    http://127.0.0.1:5001/master?tabla=animales_perdidos&id=22

Realizará internamente la query SQL:

```sql
DELETE FROM `animales_perdidos` WHERE `id` = 22;
```
#### Manejo de Errores
Si ocurre un error al ejecutar la consulta, el servicio devuelve una tupla que contiene un JSON con la causa del error y el código de estado `500`.
Si no cumple con los parámetros esperados (tabla o un id inválidos), el código de estado es `400`.

### POST

#### BODY
Recibe un JSON con el siguiente formato:
```json
{
    "tabla": "nombre_de_la_tabla",
    "campo1": "valor1",
    "campo2": "valor2",
    "..."
}
```
Donde tabla es el nombre de la tabla en la base de datos y los demás campos son los datos a insertar en la tabla especificada.

#### Proceso

1. Extrae el valor de `tabla` del JSON recibido y lo almacena en la variable `tabla`.
2. Verifica si `tabla` está en la lista de tablas permitidas (`TABLAS`):
    * Si no está, devuelve un JSON con el mensaje "Bad request" y el código de estado `400`.
3. Si la tabla es válida, verifica que el JSON recibido tiene la estructura correcta para la tabla especificada:
    * Si `tabla` es `animales_perdidos`, verifica que el JSON cumple con la estructura esperada para `animales_perdidos`.
    * Si `tabla` es `refugios`, verifica que el JSON cumple con la estructura esperada para `refugios`.
    * Si `tabla` es `admin`, verifica que el JSON cumple con la estructura esperada para `admin`.
    * Si `tabla` es `caracteristicas_mascotas`, verifica que el JSON cumple con la estructura esperada para `caracteristicas_mascotas`.
    * Si la estructura no es correcta, devuelve un JSON con el mensaje "Bad request" y el código de estado `400`.
4. Extrae las claves y valores del JSON recibido que coinciden con las columnas de la tabla especificada.
5. Construye una consulta SQL `INSERT INTO` con las claves y valores extraídos.
6. Ejecuta la consulta SQL para insertar los datos en la base de datos.
7. Devuelve un JSON con el mensaje resultante de la operación y el código de estado correspondiente (`200` si fue exitoso).

#### Errores en el Endpoint

En caso de que ocurra un error en la conexión con la BBDD, se retorna un JSON con la causa o causas del error y el código de estado `500`.