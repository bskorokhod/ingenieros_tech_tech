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

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=PUERTO_API)


