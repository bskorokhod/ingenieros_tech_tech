from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Por ahora, hosteamos la BBDD locaclmente, con el nombre mascotas
CONECTOR_SQL = "mysql+mysqlconnector://root@localhost/mascotas"
QUERY_OBTENER_CARACTERISTICAS = "SELECT * FROM caracteristicas_mascotas" # Probar seleccionando sólo las columnas que no tienen id 

engine = create_engine(CONECTOR_SQL)

app = Flask(__name__)
PUERTO_API = 5001

@app.route('/caracteristicas_mascotas', methods=['GET'])
def obtener_tabla_caracteristicas():
    try:
        with engine.connect() as conn:
            response = conn.execute(text(QUERY_OBTENER_CARACTERISTICAS))
            data = {}
            for row in response:
                if row.animal not in data:
                    data[row.animal] = {}
                data[row.animal][row.caracteristica] = data[row.animal].get(row.caracteristica, []) + [row.valor]
            return jsonify(data)
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

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=PUERTO_API)


