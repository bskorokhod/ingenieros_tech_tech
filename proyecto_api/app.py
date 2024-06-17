from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from queries import traer_info, realizar_cambios, realizar_query_validacion
from config_api import CONECTOR_SQL, PUERTO_API, TABLA_ADMIN, TABLA_ANIMALES_PERDIDOS, TABLA_CARACTERISTICAS_MASCOTAS, TABLA_REFUGIOS, TABLA_REPORTES_REENCUENTRO
from validaciones import es_id, es_fecha, es_float, es_telefono, es_varchar, es_admin, es_animal_perdido, es_caracteristica_mascota, es_refugio, TABLAS

engine = create_engine(CONECTOR_SQL)

app = Flask(__name__)

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
            return jsonify({"error": f"missing unique key: {clave_unica_tabla}"})

        valor_clave_unica = body.get(clave_unica_tabla)

        if not es_id(valor_clave_unica):
            return jsonify({"error": "value is not id"})

        id_en_tabla = realizar_query_validacion(f"SELECT {clave_unica_tabla} FROM {tabla} WHERE id = {valor_clave_unica};", engine)

        if id_en_tabla == -1 : 
            return jsonify({"mensaje": "Ocurrió un error"}), 500
        
        if id_en_tabla == 0:
            return jsonify({"mensaje": "Bad request"}), 400


        query_modificacion = f"UPDATE `{tabla}` SET "

        for clave, valor in body.items():
            if clave in columnas_tabla and clave != clave_unica_tabla:

                funcion_auxiliar = columnas_tabla.get(clave)[0]

                if funcion_auxiliar is es_varchar:
                    argumento_funcion = columnas_tabla.get(clave)[1]
                    if funcion_auxiliar(valor, argumento_funcion):
                        query_modificacion += f"`{clave}` = '{valor}', "

                    else:

                        return jsonify({"error": f"{clave}'value ({valor}) does not fit the requierements"}), 400
                else:

                    if funcion_auxiliar(valor):

                        query_modificacion += f"{clave} = {valor}, "

                    else:

                        return jsonify({"error": f"{clave}'value ({valor}) does not fit the requierements"}), 400
                    
        query_modificacion = query_modificacion[:-2] + f" WHERE `{tabla}`.`{clave_unica_tabla}` = {valor_clave_unica};"

        #query_modificacion = "UPDATE `animales_perdidos` SET `nombre_mascota` = 'Marco' WHERE `animales_perdidos`.`id` = 72;"
        
        resultado, codigo  = realizar_cambios(query_modificacion, 200, engine)
        return jsonify({"mensaje": resultado}), codigo

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=PUERTO_API)
