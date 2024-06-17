#!/bin/bash


echo -e "Creando entorno virtual e instalando dependencias del 'proyecto_api'...\n\n"

 
cd ./proyecto_api
pip install pipenv
mkdir .venv
pipenv install flask
pipenv install flask-sqlalchemy
pipenv install requests
pipenv install mysql-connector-python


echo -e "\n\nCreando entorno virtual e instalando dependencias del 'proyecto_vistas'...\n\n"


cd ..
cd ./proyecto_vistas
pip install pipenv
mkdir .venv
pipenv install flask
pipenv install flask-sqlalchemy
pipenv install requests
pipenv install mysql-connector-python


echo -e "\n\nCreacion de entorno virtual e instalacion de dependencias completada!"