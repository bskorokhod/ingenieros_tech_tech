from flask import Flask, render_template, redirect, url_for, request
import requests
from config_app import PUERTO_APP, HOST_API, ENDPOINT_API_REFUGIO, ENDPOINT_API_REPORTES, ENDPOINT_API_LOGIN, ENDPOINT_API_CARACTERISTICAS, ENDPOINT_API_PERDIDAS


app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')

@app.route("/admin", methods=['POST', 'PATCH', 'PUT', 'DELETE'])
def admin_config():
    return "vista admin"

@app.route("/login_admin", methods=['GET'])
def login():
    return "vista login admin"

@app.route('/agregar_refugio', methods=['GET', 'POST'])
def agregar_refugio():
    return "vista agregar_refugio"

@app.route('/refugios', methods=['GET', 'POST'])
def refugios():
    return "vista refugios"

@app.route("/aceptado/", defaults={"formulario": None})
@app.route("/aceptado/<formulario>", methods=["GET", "POST"])
def aceptado(formulario):
    # si el formulario es de reencuentro, se envía un POST a la API con el id de la mascota
    if request.method == "POST":
        id_mascota = request.form.get("id_mascota")
        data = {"id": id_mascota}

        response = requests.post(HOST_API + "/reportes_reencuentro", json=data)

        # si falla la petición, se redirige a la página de error 500
        if response.status_code != 201:
            return internal_server_error(e=response.status_code)

    return render_template("aceptado.html", form=formulario)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('base_errores.html', numero_error=404), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('base_errores.html', numero_error=500), 500

@app.route('/perdido', methods=['GET', 'POST'])
def perdido():
    if request.method == 'POST':
        datos_mascota_perdida = {}
        datos_mascota_perdida['nombre_mascota'] = request.form.get('nombre_mascota')
        datos_mascota_perdida['animal'] = request.form.get('animal')
        datos_mascota_perdida['raza'] = request.form.get('raza')
        datos_mascota_perdida['sexo'] = request.form.get('sexo')
        datos_mascota_perdida['color'] = request.form.get('color')
        datos_mascota_perdida['edad'] = request.form.get('edad')
        datos_mascota_perdida['coordx'] = request.form.get('coordx')
        datos_mascota_perdida['coordy'] = request.form.get('coordy')
        datos_mascota_perdida['fecha_extravio'] = request.form.get('fecha_extravio')
        datos_mascota_perdida['telefono_contacto'] = request.form.get('telefono_contacto') 
        datos_mascota_perdida['nombre_contacto'] = request.form.get('nombre_contacto')
        datos_mascota_perdida['info_adicional'] = request.form.get('info_adicional')
        datos_mascota_perdida['direccion'] = request.form.get('direccion')

        # Pegarle a la API para insertar el nuevo registro en la BBDD
        # Los campos sin completar se envían como cadenas vacías
        response = requests.post(HOST_API + '/mascotas_perdidas', json=datos_mascota_perdida) # HOST_API es una variable global
        if response.status_code == 201:
            return redirect(url_for("aceptado", formulario="mascota"))
        else:
            return internal_server_error(e=response.status_code) # Función que renderiza un template de error 500

    elif request.method == 'GET':
        response = requests.get(HOST_API + '/caracteristicas_mascotas')
        if response.status_code == 200:
            caracteristicas_animales = response.json()
            return render_template('form_mascotas.html', caracteristicas_animales=caracteristicas_animales)
        else:
            return internal_server_error(e=response.status_code)

@app.route('/encontrado', methods=["GET", "POST"])
def encontrado():

    datos_caracteristicas = requests.get(HOST_API + '/caracteristicas_mascotas')
    if datos_caracteristicas.status_code == 200:
        caracteristicas_animales = datos_caracteristicas.json()
    else:
        return internal_server_error(e=datos_caracteristicas.status_code)
    
    filtros_busqueda = ""

    # al recibir un POST se agregan los filtros a filtros_busqueda, si se recibe GET, los filtros quedan vacíos.
    if request.method == "POST":

        for clave, valor in request.form.items():
            filtros_busqueda += f"{clave}={valor}&"

    datos_mascotas = requests.get(HOST_API + '/mascotas_perdidas?' + filtros_busqueda)

    if datos_mascotas.status_code == 200:
        mascotas_perdidas = datos_mascotas.json()
    else:
        return internal_server_error(e=datos_mascotas.status_code)

    return render_template('mascotas_perdidas.html', caracteristicas = caracteristicas_animales, mascotas = mascotas_perdidas)

if __name__ == '__main__':
    app.run(port=PUERTO_APP)

