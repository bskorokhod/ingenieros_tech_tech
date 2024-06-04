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
    
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=PUERTO_API)


