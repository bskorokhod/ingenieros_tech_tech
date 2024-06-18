from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from queries import traer_info, realizar_cambios, realizar_query_validacion
from config_api import CONECTOR_SQL, PUERTO_API, TABLA_ADMIN, TABLA_ANIMALES_PERDIDOS, TABLA_CARACTERISTICAS_MASCOTAS, TABLA_REFUGIOS, TABLA_REPORTES_REENCUENTRO
from validaciones import es_id, es_fecha, es_float, es_telefono, es_varchar, es_admin, es_animal_perdido, es_caracteristica_mascota, es_refugio, TABLAS

engine = create_engine(CONECTOR_SQL)

app = Flask(__name__)

@app.route('/caracteristicas_mascotas', methods=['GET'])
def obtener_tabla_caracteristicas():
    query =  """SELECT * FROM caracteristicas_mascotas ORDER BY
    CASE
        WHEN valor = 'Otro / No se' THEN 1
        ELSE 0
    END,
valor;"""
    try:
        with engine.connect() as conn:
            response = conn.execute(text(query))
            data = {}
            for row in response:
                if row.animal not in data:
                    data[row.animal] = {}
                data[row.animal][row.caracteristica] = data[row.animal].get(row.caracteristica, []) + [row.valor]
            return jsonify(data), 200
    except SQLAlchemyError as err:
        return jsonify(str(err.__cause__)), 500
    
    
@app.route('/login_admin',  methods = ['GET'])
def login_admin():
    
    try:
        with engine.connect() as conn:
            
            user = request.args.get('user')
            password = request.args.get('password')

            response = conn.execute(text(f"SELECT * FROM admin WHERE usuario = '{user}' AND contrasena = '{password}'"))
            
            if response.rowcount > 0:
                return jsonify({'code': 1}), 200
            return jsonify({'code': 0}), 200
        
    except SQLAlchemyError as err:
        return jsonify(str(err.__cause__)), 500   
    

@app.route('/reportes_reencuentro', methods=['GET', 'POST', 'PATCH', 'PUT'])
def reportes_reencuentro():
    """
    Servicio para gestionar reportes de reencuentros de mascotas perdidas.

    Métodos HTTP soportados:

    1. GET:
        Obtiene una lista paginada de reportes de reencuentros de mascotas perdidas que no han sido procesados.

        - PARÁMETROS DE QUERY: 
            - pag_reportes (int, opcional): Número de la página que se desea obtener (por defecto: 1).
            - limite_reportes (int, opcional): Número de reportes a mostrar por página (por defecto: 5).

        - POSTCONDICIONES: 
            - Si la consulta fue exitosa, el servicio devuelve una tupla que contiene un JSON con los los
            reportes de reencuentro junto con una indicación de si hay más páginas disponibles; y el código de estado 200
            - Ejemplo de respuesta exitosa:
                ```
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
                        }
                }
                ```
            - Si ocurre un error al ejecutar la consulta, el servicio devuelve una tupla que contiene un JSON con la causa del error 
            y el código de estado 500

    2. POST:
        Agrega un nuevo registro a la tabla reportes_reencuentro.

        - PRECONDICIONES: 
            - En el body de la solicitud debe enviarse un JSON con el id(int) de la mascota reportada

        - POSTCONDICIONES: 
            - Inserta un nuevo registro en la tabla reportes_reencuentro si la mascota existe y está perdida.
            - Si la consulta fue exitosa, el servicio devuelve una tupla que contiene un JSON con un mensaje de éxito y el código de 
            estado 201.
            - Si los datos enviados no son válidos, el servicio devuelve una tupla que contiene un JSON con un mensaje de error y el código 
            de estado 400.
            - Si ocurre un error al realizar la consulta, el servicio devuelve una tupla que contiene un JSON con la causa del error y el código 
            de estado 500.

    3. PATCH:
        Modifica el estado de procesamiento de un reporte de reencuentro descartado.

        - PRECONDICIONES: 
            - En el body de la solicitud debe enviarse un JSON con el id(int) del reporte de reencuentro descartado.
        
        - POSTCONDICIONES: 
            - Actualiza el campo fue_procesado a TRUE para el reporte especificado.
            - Si los datos enviados no son válidos, el servicio devuelve una tupla que contiene un JSON con un mensaje de error y el código 
            de estado 400.
            - Si ocurre un error al realizar la consulta, el servicio devuelve una tupla que contiene un JSON con la causa del error y el código 
            de estado 500.

    4. PUT:
        Actualiza el estado de una mascota encontrada y marca los reportes de reencuentro correspondientes como procesados.

        - PRECONDICIONES: 
            - En el body de la solicitud debe enviarse un JSON con el id(int) de la mascota encontrada.
        
        - POSTCONDICIONES: 
            - Actualiza el campo encontrado a TRUE en la tabla animales_perdidos para la mascota especificada.
            - Actualiza el campo fue_procesado a TRUE en la tabla reportes_reencuentro para los reportes correspondientes.
            - Si los datos enviados no son válidos, el servicio devuelve una tupla que contiene un JSON con un mensaje de error y el código 
            de estado 400.
            - Si ocurre un error al realizar la consulta, el servicio devuelve una tupla que contiene un JSON con la causa del error y el código 
            de estado 500.
    """

    if request.method == 'GET':
        # Obtenengo el limite y la página actual de los parámetros de consulta
        pagina = request.args.get('pag_reportes', default=1, type=int)
        elementos = request.args.get('limite_reportes', default=5, type=int)
        
        reportes_query = f"""
                        SELECT * FROM {TABLA_REPORTES_REENCUENTRO} 
                        WHERE fue_procesado = FALSE
                        ORDER BY id_reporte
                        LIMIT {elementos} OFFSET {(pagina - 1) * elementos};
                        """
        validacion_pagina = f"""
                            SELECT * FROM {TABLA_REPORTES_REENCUENTRO} 
                            WHERE fue_procesado = FALSE
                            ORDER BY id_reporte
                            LIMIT 1 OFFSET {pagina * elementos};
                            """

        resultado_reportes_reencuentro, reportes_codigo = traer_info(reportes_query, 200, engine)

        if reportes_codigo == 500:
            return jsonify(resultado_reportes_reencuentro), reportes_codigo
        
        mascotas_encontradas = {}
        for reporte in resultado_reportes_reencuentro:
            mascotas_query = f"""
                            SELECT nombre_mascota, direccion, fecha_extravio, telefono_contacto, nombre_contacto
                            FROM {TABLA_ANIMALES_PERDIDOS}
                            WHERE id = {reporte.id_mascota};
                            """
            datos_mascotas, mascotas_codigo = traer_info(mascotas_query, 200, engine)

            if mascotas_codigo == 500:
                return jsonify(datos_mascotas), mascotas_codigo
            
            for datos_mascota in datos_mascotas:

                # Construyo el diccionario con los datos de la mascota asociadas al reporte
                mascotas_encontradas[reporte.id_reporte] = {
                    'id_mascota': reporte.id_mascota,
                    'nombre_mascota': datos_mascota.nombre_mascota,
                    'direccion': datos_mascota.direccion,
                    'fecha_extravio': datos_mascota.fecha_extravio.strftime("%d/%m/%Y"),
                    'telefono_contacto': datos_mascota.telefono_contacto,
                    'nombre_contacto': datos_mascota.nombre_contacto
                }

        resultado_validacion_pagina = realizar_query_validacion(validacion_pagina, engine)
        if resultado_validacion_pagina == -1:
            return jsonify({'mensaje': "Error al validar"}), 500
        elif resultado_validacion_pagina == 0:
            return jsonify({'reportes_reencuentro': mascotas_encontradas, 'hay_pag_siguiente': False}), 200
        else:
            return jsonify({'reportes_reencuentro': mascotas_encontradas, 'hay_pag_siguiente': True}), 200

    # Si llega a este punto, es porque el método HTTP es POST, PATCH o PUT por lo que necesariamente recibe un JSON
    datos = request.get_json()

    if request.method == 'POST':
        id_mascota = datos.get('id')
        
        if not es_id(id_mascota):
            return jsonify({"mensaje": "El id de la mascota es inválido"}), 400

        id_mascota = int(id_mascota)

        # Agrega un nuevo registro a la tabla reportes_reencuentro
        query = f"""INSERT INTO {TABLA_REPORTES_REENCUENTRO} (id_mascota) 
                    VALUES ('{id_mascota}');"""

        # Valida que la mascota asociada al id_mascota exista y se encuentre perdida
        validacion_mascota = f"""SELECT * 
                                FROM {TABLA_ANIMALES_PERDIDOS}
                                WHERE id = {id_mascota} AND encontrado = FALSE;"""

        resultado_validacion = realizar_query_validacion(validacion_mascota, engine)
        if resultado_validacion == -1:
            return jsonify({'mensaje': "Error al validar"}), 500
        elif resultado_validacion == 0:
            return jsonify({'mensaje': "No existe ninguna mascota perdida asociada a ese id"}), 400
        else:
            resultado, codigo = realizar_cambios(query, 201, engine)
            return jsonify(resultado), codigo
        
    elif request.method == 'PATCH':
        id_reporte_rechazado = datos.get('id_reporte')

        if not es_id(id_reporte_rechazado):
            return jsonify({"mensaje": "El id del reporte es inválido"}), 400

        id_reporte_rechazado = int(id_reporte_rechazado)

        # Modifica el estado de procesamiento de un reporte que haya sido descartado
        query = f"""UPDATE {TABLA_REPORTES_REENCUENTRO} 
                    SET fue_procesado = TRUE 
                    WHERE id_reporte = {id_reporte_rechazado};"""

        # Valida la existencia de un reporte de reencuentro asociado a ese id       
        validacion_reporte = f"""SELECT * 
                                FROM {TABLA_REPORTES_REENCUENTRO}
                                WHERE id_reporte = {id_reporte_rechazado};"""

        resultado_validacion = realizar_query_validacion(validacion_reporte, engine)
        if resultado_validacion == -1:
            return jsonify({'mensaje': "Error al validar"}), 500
        elif resultado_validacion == 0:
            return jsonify({'mensaje': "No existe ningun reporte de reencuentro asociado a ese id"}), 400
        else:
            resultado, codigo = realizar_cambios(query, 200, engine)
            return jsonify(resultado), codigo
    
    elif request.method == 'PUT':
        id_mascota_encontrada = datos.get('id_mascota')

        if not es_id(id_mascota_encontrada):
            return jsonify({"mensaje": "El id de la mascota es inválido"}), 400

        id_mascota_encontrada = int(id_mascota_encontrada)

        # Modifica el valor del campo encontrado en la tabla animales_perdidos asociado a la mascota encontrada
        animales_query = f"""UPDATE {TABLA_ANIMALES_PERDIDOS}
                            SET encontrado = TRUE 
                            WHERE id = {id_mascota_encontrada};"""

        # Modifica el estado de procesamiento de un reporte que haya sido aprobado 
        reportes_query = f"""UPDATE {TABLA_REPORTES_REENCUENTRO} 
                            SET fue_procesado = TRUE 
                            WHERE id_mascota = {id_mascota_encontrada};"""

        # Valida que la mascota asociada al id_mascota_encontrada exista y esté perdida
        validacion_animales = f"""SELECT * 
                                FROM {TABLA_ANIMALES_PERDIDOS}
                                WHERE id = {id_mascota_encontrada} AND encontrado = FALSE;"""

        # Valida que la mascota asociada al id_mascota_encontrada haya sido reportada como encontrada
        validacion_reportes = f"""SELECT * 
                                FROM {TABLA_REPORTES_REENCUENTRO}
                                WHERE id_mascota = {id_mascota_encontrada} AND fue_procesado = FALSE;"""

        resultado_validacion_animales = realizar_query_validacion(validacion_animales, engine)
        resultado_validacion_reportes = realizar_query_validacion(validacion_reportes, engine)

        if resultado_validacion_animales == -1 or resultado_validacion_reportes == -1:
            return jsonify({'mensaje': "Error al validar"}), 500
        elif resultado_validacion_animales == 0 or resultado_validacion_reportes == 0:
            return jsonify({'mensaje': "Bad Request"}), 400       
        else:
            resultado_animales, codigo_animales = realizar_cambios(animales_query, 200, engine)
            if codigo_animales == 500:
                return jsonify(resultado_animales), codigo_animales

            resultado_reportes, codigo_reportes = realizar_cambios(reportes_query, 200, engine)
            return jsonify(resultado_reportes), codigo_reportes


@app.route('/mascotas_perdidas', methods=["GET", "POST"])
def mascotas_perdidas():
    """
    Método POST:
    Se reciben los datos de una mascota perdida para agregarlos a la Base de Datos.

    PRECONDICIONES:
        - Los datos de la mascota se reciben en un JSON, que contiene las columnas y sus respectivos
        valores.
    
    POSTCONDICIONES:
        - Si los datos son válidos, se agrega la mascota a `TABLA_ANIMALES_PERDIDOS`, y se devuelve un mensaje
        que indica que todo salió bien, junto a un código de estado 201. Si los datos que se enviaron en
        el JSON, no son válidos para la tabla `TABLA_ANIMALES_PERDIDOS`, devuelve un `Bad request` y código de
        estado 400. Si ocurrió un error mientras se insertaban los datos en la tabla, se devuelve un 
        mensaje que lo indica y un código de estado 500.

    Método GET:
    Se devuelve una página de la tabla `TABLA_ANIMALES_PERDIDOS` según los filtros que se envíen.

    PRECONDICIONES:
        - Los filtros se envían como parámetros en el argumento de la request, y deben especificar
        las columnas y valores según los que se quiera filtrar. También pueden aclarar la `pagina`
        que se desea obtener y `elementos` para la cantidad que se quiera ver en ellas.

    POSTCONDICIONES: 
        - Se devuelve un JSON que contiene:
            - `mascotas`: Una lista con los datos de las mascotas que cumplen con los filtros según
            la `pagina` y `elementos` pedidos.
            - `pagina`: La página que se solicitó
            - `hay_pagina_previa`: Un valor booleano que indica si es posible solicitar una página 
            anterior a la actual.
            - `hay_pagina_siguiente`: Un valor booleano que indica si es posible solicitar una página 
            posterior a la actual.
        - Si surge un error al ejecutar una consulta, se devuelve un JSON con su mensaje de error y
        código de estado 500.
    """
    if request.method == "POST":
        
        datos_mascota = request.get_json()

        # Validamos que el JSON recibido corresponda a una posible mascota perdida
        if not es_animal_perdido(datos_mascota):
            return jsonify({"mensaje": "Bad request"}), 400

        columnas = []
        valores = []

        # Se agregan solo columnas y datos los cuales no tienen un valor nulo
        for columna, dato in datos_mascota.items():
            if dato:
                columnas.append(columna)
                valores.append(f"""'{dato}'""")

        query = f"""
        INSERT INTO {TABLA_ANIMALES_PERDIDOS} ({', '.join(columnas)}) 
        VALUES ({', '.join(valores)});"""

        mensaje, codigo_estado = realizar_cambios(query, 201, engine)

        return jsonify({'mensaje': mensaje}), codigo_estado
        
    elif request.method == "GET":
        
        filtros = []
        clausula_where = ""

        # si no se pide ninguna página especifica se muestra la primera
        pagina = request.args.get('pagina', 1, type=int)
        # si no se pide ninguna cantidad especifica devuelve los 20 primeros elementos
        elementos = request.args.get('elementos', 20, type=int)

        # recibimos las columnas y valores con los que vamos a filtrar en los parámetros enviados
        for columna, valor in request.args.items():
            if valor and columna not in {'pagina', 'elementos'}:
                filtros.append(f"""{columna} = '{valor}'""")
        
        # Verificamos que haya algún filtro para agregar la línea a la clausula_where
        if filtros:
            clausula_where = f"WHERE {' AND '.join(filtros)}"

        # Pedimos los datos de las mascotas que coinciden con lo pedido
        query_recibir_mascotas = f"""
        SELECT * 
        FROM {TABLA_ANIMALES_PERDIDOS} 
        {clausula_where} 
        LIMIT {elementos} OFFSET {(pagina - 1) * elementos};"""

        res_mascotas, codigo_estado_mascotas = traer_info(query_recibir_mascotas, 200, engine)
        if codigo_estado_mascotas != 200:
            return jsonify({"mensaje": res_mascotas}), codigo_estado_mascotas

        # Si esta query devuelve un 1, significa que hay al menos una mascota más, si no devuelve nada, estamos en la última página
        query_verificar_pagina = f"""
        SELECT 1 
        FROM {TABLA_ANIMALES_PERDIDOS} 
        {clausula_where} 
        LIMIT 1 OFFSET {pagina * elementos};"""

        res_verificacion_pagina = realizar_query_validacion(query_verificar_pagina, engine)
        if res_verificacion_pagina == -1:
            return jsonify({"mensaje": "Hubo un problema al realizar la consulta."}), 500
            
        mascotas_perdidas = []

        for mascota in res_mascotas.mappings():
            dict_mascota = dict(mascota)
            dict_mascota['fecha_extravio'] = dict_mascota['fecha_extravio'].strftime("%d/%m/%Y")

            mascotas_perdidas.append(dict_mascota)

        resultados = {
            'mascotas': mascotas_perdidas,
            'pagina': pagina,
            'hay_pagina_previa': pagina - 1 > 0,
            'hay_pagina_siguiente': res_verificacion_pagina == 1
        }

        return jsonify(resultados), 200

@app.route('/master', methods = ['GET','POST','PATCH', 'DELETE'])
def master():
    
    if request.method == "GET":
        
        """
        Método GET:
        Recibe la `tabla` y un `id`, como parámetros en el argumento del endpoint, de la fila 
        que se quiera recibir.

        POSTCONDICIONES:
            - Si el `id` es válido, se devuelve un JSON con las columnas de la `tabla` y los 
            valores correspondientes a la fila del `id`. En caso de que no exista la `tabla` en la Base
            de datos o `id` no corresponda a ninguna fila, se devuelve un error 400: Bad Request.
        """

        # Recibo la tabla desde los argumentos
        tabla = request.args.get("tabla")
        if tabla not in TABLAS:
            return jsonify({"mensaje": "Bad request"}), 400
    
        # Como el id en TABLA_REPORTES_REENCUENTRO es id_reporte, verifico esto
        if tabla == TABLA_REPORTES_REENCUENTRO:
            nombre_id = "id_reporte"
        else:
            nombre_id = "id"

        # Selecciono la información de la tabla pedida en la que nombre_id sea el pasado por argumentos
        query = f"""
        SELECT * 
        FROM {tabla} 
        WHERE {nombre_id} = '{request.args.get(nombre_id)}';"""

        response, codigo_estado = traer_info(query, 200, engine)
        if codigo_estado != 200:
            return jsonify({"mensaje": response}), codigo_estado
        
        # fetchone() obtiene los valores del primer resultado que encuentre en response (aunque hay uno solo)
        fila = response.fetchone()

        # Si fila está vacía, entonces el id no correspondía a ninguna fila de la tabla
        if not fila:
            return jsonify({"mensaje": "Bad request"}), 400
        
        # Creo el diccionario que voy a JSONificar con las columnas y los valores de la fila pedida
        columnas = response.keys()
        info_fila = {}
        i = 0
        for columna in columnas:
            info_fila[columna] = fila[i]
            i += 1
        
        return jsonify(info_fila), codigo_estado
    
    if request.method == "DELETE":
        
        tabla = request.args.get("tabla")
        id_a_eliminar = request.args.get("id", -1)

        
        if tabla not in TABLAS or id_a_eliminar == -1:
            return jsonify({"mensaje":"Bad request"}), 400
        
        
        if tabla == "reportes_reencuentro":
            nombre_id = "id_reporte"    
        else:
            nombre_id="id"
        
        query_validacion = f"SELECT * FROM `{tabla}` WHERE `{nombre_id}` = {id_a_eliminar};"
        
        validacion = realizar_query_validacion(query_validacion, engine)

        if validacion == -1 : 
            return jsonify({"mensaje":"Ocurrió un error"}), 500
        if validacion == 0:
            return jsonify({"mensaje":"Bad request"}), 400
        
        query = f"DELETE FROM `{tabla}` WHERE `{nombre_id}` = {id_a_eliminar};" 

        resultado, codigo = realizar_cambios(query, 200, engine)
        
        return jsonify({"mensaje":resultado}), codigo
    
    
    # Si llega acá, método != GET y  metodo != DELETE
    body = request.get_json()
    tabla = body.get("tabla")

    if tabla not in TABLAS:
        return jsonify({"mensaje":"Bad request"}), 400
    
    
    if request.method == "POST":

        
        if tabla == TABLA_ANIMALES_PERDIDOS:
            columnas = list(TABLAS.get(TABLA_ANIMALES_PERDIDOS).keys())
            if not es_animal_perdido(body):
                return jsonify({"mensaje" : "Bad request"}), 400
        elif tabla == TABLA_REFUGIOS:
            columnas = list(TABLAS.get(TABLA_REFUGIOS).keys())
            if not es_refugio(body):
                return jsonify({"mensaje" : "Bad request"}), 400
        elif tabla == TABLA_ADMIN:
            columnas = list(TABLAS.get(TABLA_ADMIN).keys())
            if not es_admin(body):
                return jsonify({"mensaje" : "Bad request"}), 400
        else:
            columnas = list(TABLAS.get(TABLA_CARACTERISTICAS_MASCOTAS).keys())
            if not es_caracteristica_mascota(body):
                return jsonify({"mensaje" : "Bad request"}), 400

        claves = []
        valores = []
        
        for clave, valor in body.items():
            if clave not in columnas:
                continue
            claves.append(clave)
            valores.append(f"'{valor}'")
        
        claves = ",".join(claves)
        valores = ",".join(valores)
        
        query = f"INSERT INTO {tabla} ({claves}) VALUES ({valores});"
        
        resultado, codigo = realizar_cambios(query, 200, engine)
        
        return jsonify({"mensaje" : resultado}), codigo
    
    
    
    if request.method == "PATCH":

        columnas_tabla = TABLAS.get(tabla)
        clave_unica_tabla = list(columnas_tabla.keys())[0]

        if clave_unica_tabla not in body:
            return jsonify({"mensaje": f"falta la clave única: {clave_unica_tabla}"})

        valor_clave_unica = body.get(clave_unica_tabla)

        if not es_id(valor_clave_unica):
            return jsonify({"mensaje": "el valor de la clave única no es un id"})

        id_en_tabla = realizar_query_validacion(f"SELECT {clave_unica_tabla} FROM {tabla} WHERE id = {valor_clave_unica};", engine)

        if id_en_tabla == -1 : 
            return jsonify({"mensaje": "ocurrió un error"}), 500
        
        if id_en_tabla == 0:
            return jsonify({"mensaje": "Bad request"}), 400


        query_modificacion = f"UPDATE `{tabla}` SET "

        hay_cambios = False

        for clave, valor in body.items():
            if clave in columnas_tabla and clave != clave_unica_tabla:

                funcion_auxiliar = columnas_tabla.get(clave)[0]

                if funcion_auxiliar is es_varchar:

                    argumento_funcion = columnas_tabla.get(clave)[1]

                    if funcion_auxiliar(valor, argumento_funcion):

                        query_modificacion += f"`{clave}` = '{valor}', "

                        hay_cambios = True

                    else:

                        return jsonify({"mensaje": f"el valor de la clave {clave} ({valor}) no es válido"}), 400
                else:

                    if funcion_auxiliar(valor):

                        query_modificacion += f"`{clave}` = '{valor}', "

                        hay_cambios = True

                    else:

                        return jsonify({"mensaje": f"el valor de la clave {clave} ({valor}) no es válido"}), 400

        if not hay_cambios:
            return jsonify({"mensaje": "Bad request"}), 400

        query_modificacion = query_modificacion[:-2] + f" WHERE `{tabla}`.`{clave_unica_tabla}` = {valor_clave_unica};"
        
        resultado, codigo = realizar_cambios(query_modificacion, 200, engine)

        return jsonify({"mensaje": resultado}), codigo


@app.route('/refugios', methods = ['GET','POST','PATCH', 'DELETE'])
def refugios():
    if request.method == "POST": # se busca añadir un refugio y se recibe un body json con la data del formulario
        query = f"INSERT INTO {TABLA_REFUGIOS} (nombre, coordx, coordy, telefono, direccion) " 
        informacion = request.get_json()

        if not es_refugio(informacion):
           return jsonify({"mensaje":"Body inválido"}), 400 # Bad request

        nombre_refugio = informacion["nombre"]
        coord_x = informacion["coordx"]
        coord_y = informacion["coordy"]
        telefono = informacion["telefono"]
        direccion = informacion["direccion"]


        query += f"VALUES ('{nombre_refugio}', '{coord_x}', '{coord_y}', '{telefono}', '{direccion}');"


        resultado, codigo = realizar_cambios(query, 201, engine)
        return jsonify({"mensaje":resultado}), codigo

    if request.method == "GET":
        pagina = request.args.get('pagina', 1, type=int)
        elementos = request.args.get('elementos', 16, type=int)
        filtro = request.args.get('aceptado', "/")
        if filtro not in ("TRUE","FALSE"):
            return jsonify({"mensaje":"Body inválido"}), 400 # Bad request

        query = f"SELECT * FROM {TABLA_REFUGIOS} WHERE aceptado = {filtro} "

        query += f"LIMIT {elementos} OFFSET {(pagina - 1) * elementos};"


        resultado, codigo = traer_info(query, 200, engine)
        if codigo != 200:
            return jsonify({"mensaje": resultado}), codigo
        datos = []
        for fila in resultado:
            dato = {}
            dato["id"]=fila.id
            dato["nombre"] = fila.nombre
            dato["telefono"] = fila.telefono
            dato["direccion"] = fila.direccion
            dato["coordx"] = fila.coordx
            dato["coordy"] = fila.coordy
            datos.append(dato)

        # ahora verifico si hay siguiente pagina
        query_pagina_siguiente = f"SELECT 1 FROM {TABLA_REFUGIOS} WHERE aceptado = {filtro} LIMIT 1 OFFSET {pagina * elementos};"

        # es otro traer info, contar rowcount y listo
        validacion = realizar_query_validacion(query_pagina_siguiente, engine)

        if validacion != -1:
            return jsonify({"refugios":datos, "hay_pag_siguiente":bool(validacion)}), 200
        return jsonify({"mensaje":"Error"}), 500

    # si llegó a este punto, el metodo o es PATCH, o es DELETE
    informacion = request.get_json()
    id_del_refugio = informacion.get("id", -1)
    if id_del_refugio == -1: # nunca va a existir un id '-1'
        return jsonify({"mensaje":"Body inválido"}), 400 # Bad request

    query_validacion = f"SELECT * FROM {TABLA_REFUGIOS} WHERE id = {id_del_refugio};"


    validacion = realizar_query_validacion(query_validacion, engine)
    if validacion == -1:
      return jsonify({"mensaje":"Ocurrió un error"}), 500
    if validacion == 0:
      return jsonify({"mensaje":"Bad request"}), 400 # No existe el id en la BBDD
    
    # si llegó aca, la validacion dio positiva
    if request.method == "PATCH":
        query = f"UPDATE {TABLA_REFUGIOS} SET aceptado = TRUE WHERE id = {id_del_refugio};"
    else: # metodo == "DELETE"
        query = f"DELETE FROM {TABLA_REFUGIOS} WHERE id = {id_del_refugio};"

    resultado, codigo = realizar_cambios(query, 200, engine)
    return jsonify({"mensaje":resultado}), codigo

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=PUERTO_API)


