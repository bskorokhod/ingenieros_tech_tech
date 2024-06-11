from flask import Flask, render_template, redirect, url_for, request
import requests

app = Flask(__name__)
PUERTO_APP = 5000

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

        # Pegarle a la API para insertar el nuevo registro en la BBDD
        # Los campos sin completar se envían como cadenas vacías
        response = requests.post(HOST_API + '/mascotas_perdidas', json=datos_mascota_perdida) # HOST_API es una variable global
        if response.status_code == 201:
            return redirect(url_for("aceptado", formulario="mascota"))
        else:
            return redirect(url_for('internal_server_error', e=response.status_code)) # Función que renderiza un template de error 500

    elif request.method == 'GET':
        response = requests.get(HOST_API + '/caracteristicas_mascotas')
        if response.status_code == 200:
            caracteristicas_animales = response.json()
            return render_template('form_mascotas.html', caracteristicas_animales=caracteristicas_animales)
        else:
            return redirect(url_for('internal_server_error', e=response.status_code))

if __name__ == '__main__':
    app.run(port=PUERTO_APP)