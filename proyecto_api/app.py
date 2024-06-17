from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Por ahora, hosteamos la BBDD locaclmente, con el nombre mascotas
CONECTOR_SQL = "mysql+mysqlconnector://root@localhost/mascotas"


engine = create_engine(CONECTOR_SQL)

app = Flask(__name__)
PUERTO_API = 5001

@app.route('/caracteristicas_mascotas', methods=['GET'])
def obtener_tabla_caracteristicas():
    query =  "SELECT * FROM caracteristicas_mascotas" # Probar seleccionando sólo las columnas que no tienen id
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
        return jsonify(str(err.__cause__))
    
    
@app.route('/login_admin',  methods = ['GET'])
def login_admin():
    
    try:
        with engine.connect() as conn:
            
            user = request.args.get('user')
            password = request.args.get('password')

            response = conn.execute(text(f"SELECT * FROM admin WHERE usuario = '{user}' AND contrasena = '{password}'"))
            
            if response.rowcount > 0:
                return jsonify({'code': 1})
            return jsonify({'code': 0})
        
    except SQLAlchemyError as err:
        return jsonify(str(err.__cause__))    
    

@app.route('/reportes_reencuentro', methods=['GET', 'POST', 'PATCH', 'PUT'])
def reportes_reencuentro():
    if request.method == 'GET':
        try:
            with engine.connect() as conexion:
                # Trae de la BBDD los datos de las mascotas que corresponden a los reportes de reencuentro sin procesar
                query = """SELECT * FROM reportes_reencuentro WHERE fue_procesado = FALSE;"""
                
                response_reportes_reencuentro = conexion.execute(text(query))

                mascotas_encontradas = {}
                for reporte in response_reportes_reencuentro:
                    with engine.connect() as conexion:
                        query = f"""SELECT nombre_mascota, direccion, fecha_extravio, telefono_contacto, nombre_contacto
                                FROM animales_perdidos
                                WHERE id = {reporte.id_mascota};"""
                        datos_mascotas = conexion.execute(text(query))
                        for datos_mascota in datos_mascotas:        
                            mascotas_encontradas[reporte.id_reporte] = {
                                'id_mascota': reporte.id_mascota,
                                'nombre_mascota': datos_mascota.nombre_mascota,
                                'direccion': datos_mascota.direccion,
                                'fecha_extravio': datos_mascota.fecha_extravio,
                                'telefono_contacto': datos_mascota.telefono_contacto,
                                'nombre_contacto': datos_mascota.nombre_contacto
                            }

                return jsonify(mascotas_encontradas), 200

        except SQLAlchemyError as err:
            return jsonify(str(err.__cause__)), 500 

    elif request.method == 'POST':
        datos_mascota = request.get_json()
        id_mascota = datos_mascota.get('id')

        if not id_mascota:
            return jsonify({"mensaje": "No se envio ningun id de mascota"}), 400

        # Agrega un nuevo registro a la tabla reportes_reencuentro
        query = f"""INSERT INTO reportes_reencuentro (id_mascota) 
                    VALUES ('{id_mascota}');"""

        # Valida que la mascota asociada al id_mascota exista y se encuentre perdida
        validacion_mascota = f"""SELECT * 
                                FROM animales_perdidos
                                WHERE id = {id_mascota} AND encontrado = FALSE;"""

        try:
            with engine.begin() as conexion:
                resultado_validacion = conexion.execute(text(validacion_mascota))
                if resultado_validacion.rowcount != 0:
                    conexion.execute(text(query))
                    # Al usar engine.begin() se realiza engine.commit() implícitamente
                else:
                    return jsonify({'mensaje': "No existe ninguna mascota perdida asociada a ese id"}), 400

            return jsonify({'mensaje': "Los datos se agregaron correctamente"}), 201

        except SQLAlchemyError as err:
            return jsonify(str(err.__cause__)), 500
        
    elif request.method == 'PATCH':
        reporte_rechazado = request.get_json()
        id_reporte_rechazado = reporte_rechazado.get('id_reporte')

        if not id_reporte_rechazado:
            return jsonify({"mensaje": "No se envio ningun id de reporte"}), 400

        # Modifica el estado de procesamiento de un reporte que haya sido descartado
        query = f"""UPDATE reportes_reencuentro 
                    SET fue_procesado = TRUE 
                    WHERE id_reporte = {id_reporte_rechazado};"""

        # Valida la existencia de un reporte de reencuentro asociado a ese id       
        validacion_reporte = f"""SELECT * 
                                FROM reportes_reencuentro
                                WHERE id_reporte = {id_reporte_rechazado};"""

        try:
            with engine.begin() as conexion:
                resultado_validacion = conexion.execute(text(validacion_reporte))
                if resultado_validacion.rowcount != 0:
                    conexion.execute(text(query))
                else:
                    return jsonify({'mensaje': "No existe ningun reporte de reencuentro asociado a ese id"}), 400
            
            return jsonify({'mensaje': "El registro se ha modificado correctamente"}), 200
        
        except SQLAlchemyError as err:
            return jsonify(str(err.__cause__)), 500
    
    elif request.method == 'PUT':
        mascota_encontrada = request.get_json()
        id_mascota_encontrada = mascota_encontrada.get('id_mascota')

        if not id_mascota_encontrada:
            return jsonify({"mensaje": "No se envio ningun id de mascota"}), 400

        # Modifica el estado de procesamiento de un reporte que haya sido aprobado 
        reportes_query = f"""UPDATE reportes_reencuentro 
                            SET fue_procesado = TRUE 
                            WHERE id_mascota = {id_mascota_encontrada};"""

        # Modifica el valor del campo encontrado en la tabla animales_perdidos asociado a la mascota encontrada
        animales_query = f"""UPDATE animales_perdidos
                            SET encontrado = TRUE 
                            WHERE id = {id_mascota_encontrada};"""

        # Valida que la mascota asociada al id_mascota_encontrada exista y esté perdida
        validacion_animales_query = f"""SELECT * 
                                        FROM animales_perdidos
                                        WHERE id = {id_mascota_encontrada} AND encontrado = FALSE;"""

        # Valida que la mascota asociada al id_mascota_encontrada haya sido reportada como encontrada
        validacion_reportes_query = f"""SELECT * 
                                        FROM reportes_reencuentro
                                        WHERE id_mascota = {id_mascota_encontrada} AND fue_procesado = FALSE;"""

        try:
            with engine.begin() as conexion:

                resultado_validacion_animales = conexion.execute(text(validacion_animales_query))
                if resultado_validacion_animales.rowcount == 0:
                    return jsonify({'mensaje': "No existe ninguna mascota perdida asociada a ese id"}), 400                
                
                resultado_validacion_reportes = conexion.execute(text(validacion_reportes_query))
                if resultado_validacion_reportes.rowcount == 0:
                    return jsonify({'mensaje': "No existe ningun reporte de reencuentro vigente asociado a esa mascota"}), 400
                
                conexion.execute(text(reportes_query))
                conexion.execute(text(animales_query))

            return jsonify({'mensaje': "El registro se ha modificado correctamente"}), 200

        except SQLAlchemyError as err:
            return jsonify(str(err.__cause__)), 500


@app.route('/mascotas_perdidas', methods=["GET", "POST"])
def mascotas_perdidas():
    
    if request.method == "POST":
        
        datos_mascota = request.get_json()

        columnas = []
        valores = []

        # Se agregan solo columnas y datos los cuales no tienen un valor nulo
        for columna, dato in datos_mascota.items():
            if dato:
                columnas.append(columna)
                valores.append(f"'{dato}'")

        # Gracias a los bucles, me aseguro que se van a añadir los datos a las columnas correspondientes
        clausula_insert = "INSERT INTO animales_perdidos (" + ", ".join(columnas) + ") "
        clausula_values = "VALUES (" + ", ".join(valores) + ");"

        # Junto ambas partes para formar la query
        query = clausula_insert + clausula_values

        try:
            with engine.begin() as conexion:
                conexion.execute(text(query))
        except SQLAlchemyError as err:
            return jsonify(str(err.__cause__)), 500
        
        return jsonify({'mensaje': "Los datos se agregaron correctamente"}), 201
        
    elif request.method == "GET":
        
        filtros = []
        clausula_where = ""

        # request.args.items() recibe las columnas solicitadas y sus respectivos valores en un tupla a partir de la URL
        for columna, valor in request.args.items():
            if valor:
                filtros.append(f"{columna} = '{valor}'")
                
        if filtros:
            clausula_where = "WHERE " + " AND ".join(filtros)
        clausula_where += ";"

        # Escribo la query y le agrego la clausula_where
        query = """
        SELECT id, nombre_mascota, animal, raza, sexo, color, edad, coordx, coordy, fecha_extravio, telefono_contacto, nombre_contacto, IF(info_adicional IS NOT NULL, info_adicional, "No se ingresó ninguna información adicional.") as info_adicional 
        FROM animales_perdidos 
        """ + clausula_where 
        
        mascotas_perdidas = []
        try:
            with engine.connect() as conexion:
                filas_mascotas = conexion.execute(text(query))
        except SQLAlchemyError as err:
            return jsonify(str(err.__cause__)), 500

        # .mappings() me permite generar diccionarios con las columnas y los valores de la fila correspondiente
        for mascota in filas_mascotas.mappings():
            dict_mascota = dict(mascota)
            dict_mascota['fecha_extravio'] = dict_mascota['fecha_extravio'].strftime("%d/%m/%Y")

            mascotas_perdidas.append(dict_mascota)

        return jsonify(mascotas_perdidas), 200

    
@app.route('/refugios', methods = ['GET','POST','PATCH', 'DELETE'])
def refugios():
    if request.method == "POST": # se busca añadir un refugio y se recibe un body json con la data del formulario
        informacion = request.get_json()
        # Queda pendiente validar si las claves se encuentran en el json
        nombre_refugio = informacion.get("nombre")
        coord_x = informacion.get("coord_x")
        coord_y = informacion.get("coord_y")
        telefono = informacion.get("telefono")
        direccion = informacion.get("direccion")
        query = f"INSERT INTO {TABLA_REFUGIOS} (nombre, coord_x, coord_y, telefono, direccion) VALUES '{nombre_refugio}', '{coord_x}', '{coord_y}', '{telefono}', '{direccion}';" 
        try:
            with engine.begin() as conexion:
                resultado = conexion.execute(text(query))
                # al realizar engine.begin() al finalizar el bloque se agrega automáticamente el engine.commit() tras realizar los cambios guardándolos
                return jsonify({"mensaje":"exito"}), 201 
        except SQLAlchemyError as err:
            return jsonify(str(err.__cause__)), 500

    if request.method == "GET":
        informacion = request.get_json()
        if informacion == {}: # o  'if not informacion'
            filtro="TRUE"
        elif informacion.get("aceptado") == "false":
            filtro="FALSE"
        else: # Body inválido
            return jsonify({"mensaje":"Body inválido"}), 400 # Bad request
        query = f"SELECT * FROM {TABLA_REFUGIOS} WHERE aceptado = {filtro};"
        try:
            with engine.connect() as conexion:
                resultado = conexion.execute(text(query))
        except SQLAlchemyError as err:
            return jsonify(str(err.__cause__)), 500
        datos = []
        for fila in resultado:
            dato = {}
            dato["nombre"] = fila.nombre
            dato["telefono"] = fila.telefono
            dato["direccion"] = fila.direccion
            dato["coordx"] = fila.coordx
            dato["coordy"] = fila.coordy
            datos.append(dato)
        return jsonify(datos), 200

    # si llegó a este punto, el metodo o es PATCH, o es DELETE
    informacion = request.get_json()
    id_del_refugio = informacion.get("id", -1)
    if id_del_refugio == -1: # nunca va a existir un id '-1'
        return jsonify({"mensaje":"Body inválido"}), 400 # Bad request

    query_validacion = f"SELECT * FROM {TABLA_REFUGIOS} WHERE 'id' = {id_del_refugio};"
    try:
        with engine.connect() as conexion:
            resultado = conexion.execute(text(query_validacion))
    except SQLAlchemyError as err:
        return jsonify(str(err.__cause__)), 500

    if resultado.rowcount == 0: # No hay ningún refugio con ese id
        return jsonify({"mensaje":"Body inválido"}), 400 
    
    if request.method == "PATCH":
        query = f"UPDATE {TABLA_REFUGIOS} SET aceptado = TRUE WHERE id = {id_del_refugio};"
    else: # metodo == "DELETE"
        query = f"DELETE FROM {TABLA_REFUGIOS} WHERE id = {id_del_refugio};"
    try:
        with engine.begin() as conexion:
            resultado = conexion.execute(text(query))
            # al realizar engine.begin() al finalizar el bloque se agrega automáticamente el engine.commit() tras realizar los cambios guardándolos
            return jsonify({"mensaje":"exito"}), 201 
    except SQLAlchemyError as err:
        return jsonify(str(err.__cause__)), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=PUERTO_API)


