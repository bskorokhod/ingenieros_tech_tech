from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from queries import traer_info, realizar_cambios, realizar_query_validacion
from config_api import CONECTOR_SQL, PUERTO_API, TABLA_ADMIN, TABLA_ANIMALES_PERDIDOS, TABLA_CARACTERISTICAS_MASCOTAS, TABLA_REFUGIOS, TABLA_REPORTES_REENCUENTRO, TABLAS

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
    
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=PUERTO_API)
