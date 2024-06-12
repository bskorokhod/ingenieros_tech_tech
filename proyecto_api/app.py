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
            
            try: 
                data = request.get_json(force=True)
            except:
                return jsonify({'code': 0})
            
        
            user = data.get('user')
            password = data.get('password')

            response = conn.execute(text(f"SELECT * FROM admin WHERE usuario = '{user}' AND contrasena = '{password}'"))
            
            if response.rowcount > 0:
                return jsonify({'code': 1})
            return jsonify({'code': 0})
        
    except SQLAlchemyError as err:
        return jsonify(str(err.__cause__))    
    
    
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=PUERTO_API)


