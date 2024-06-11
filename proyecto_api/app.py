from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Por ahora, hosteamos la BBDD locaclmente, con el nombre mascotas
CONECTOR_SQL = "mysql+mysqlconnector://root@localhost/mascotas"
QUERY_OBTENER_CARACTERISTICAS = "SELECT * FROM caracteristicas_mascotas" # Probar seleccionando sólo las columnas que no tienen id 

# TABLA_REFUGIOS = "refugios"

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


