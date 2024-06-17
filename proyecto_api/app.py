from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from queries import traer_info, realizar_cambios, realizar_query_validacion
from config_api import CONECTOR_SQL, PUERTO_API, TABLA_ADMIN, TABLA_ANIMALES_PERDIDOS, TABLA_CARACTERISTICAS_MASCOTAS, TABLA_REFUGIOS, TABLA_REPORTES_REENCUENTRO, TABLAS
from validaciones import es_id, es_fecha, es_float, es_telefono, es_varchar, es_admin, es_animal_perdido, es_caracteristica_mascota, es_refugio

engine = create_engine(CONECTOR_SQL)

app = Flask(__name__)

@app.route('/master', methods = ['GET','POST','PATCH', 'DELETE'])
def master():
    
    # acá se verifica el caso del metodo get
    
    # Si llega acá, método != GET
    body = request.get_json()
    tabla = body.get("tabla")

    if tabla not in TABLAS:
        return jsonify({"mensaje":"Bad request"}), 400
    
    if request.method == "DELETE":
        if tabla == "reportes_reencuentro":
            nombre_id = "id_reporte"
        else:
            nombre_id="id"
        if nombre_id not in body:
                return jsonify({"mensaje":"Bad request"}), 400
        id_a_eliminar = body[nombre_id]
        query_validacion = f"SELECT * FROM {tabla} WHERE '{nombre_id}' = {id_a_eliminar};"
        validacion = realizar_query_validacion(query_validacion, engine)

        if validacion == -1 : 
            return jsonify({"mensaje":"Ocurrió un error"}), 500
        if validacion == 0:
            return jsonify({"mensaje":"Bad request"}), 400
        
        query = f"DELETE FROM {tabla} WHERE '{nombre_id}' = {id_a_eliminar};" 

        resultado, codigo = realizar_cambios(query, 200, engine)
        return jsonify({"mensaje":resultado}), codigo
    
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


        query_modificacion = f"UPDATE {tabla} SET "


        for clave, valor in body.items():

            if clave in columnas_tabla and clave != clave_unica_tabla:

                funcion_auxiliar = columnas_tabla.get(clave)[0]

                if funcion_auxiliar is es_varchar:

                    argumento_funcion = columnas_tabla.get(clave)[1]

                    if funcion_auxiliar(valor, argumento_funcion):

                        query_modificacion += f"{clave} = {valor}, "

                    else:

                        return jsonify({"error": f"{clave}'value ({valor}) does not fit the requierements"}), 400
                else:

                    if funcion_auxiliar(valor):

                        query_modificacion += f"{clave} = {valor}, "

                    else:

                        return jsonify({"error": f"{clave}'value ({valor}) does not fit the requierements"}), 400
                    
        
        query_modificacion = query_modificacion[:-2] + f" WHERE {clave_unica_tabla} = {valor_clave_unica};"


        return realizar_cambios(query_modificacion, 200, engine)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=PUERTO_API)
