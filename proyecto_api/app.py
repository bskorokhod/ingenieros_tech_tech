from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Por ahora, hosteamos la BBDD locaclmente, con nombre el nombre mascotas
CONECTOR_SQL = "mysql+mysqlconnector://root@localhost/mascotas"

engine = create_engine(CONECTOR_SQL)

app = Flask(__name__)
PUERTO_API = 5001


    
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=PUERTO_API)
