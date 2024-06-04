from flask import Flask, request, render_template, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


CONECTOR_SQL = "mysql+mysqlconnector://root@localhost/test001" # test001 tiene que cambiarse por el nombre de la BBDD que usemos
QUERY_OBTENER_CARACTERISTICAS = "SELECT * FROM caracteristicas_mascotas" # Probar seleccionando sólo las columnas que no tienen id 

app = Flask(__name__)
engine = create_engine(CONECTOR_SQL)

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
    
if __name__ == "__main__":
    app.run("127.0.0.1", port="5001", debug=True)
