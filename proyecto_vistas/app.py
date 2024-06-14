from flask import Flask, render_template, redirect, url_for, request
import requests

app = Flask(__name__)
PUERTO_APP = 5000
#HOST_API=""


@app.route('/refugios')
def refugios():
    
    try:
        response = requests.get(HOST_API + ENDPOINT_API_REFUGIO, json={}) # Mando un json vacio xq asi me lo solicitan para poder diferencia dos metodos GET
        
        refugios = response.json()
        
        if response.status_code == 200:
            return render_template('refugios.html', refugios={'refugios': refugios})
        
        return internal_server_error(response.status_code)

    except requests.exceptions.HTTPError as e:
        return internal_server_error(e)
    except requests.exceptions.RequestException as e:
        return internal_server_error(e)


@app.route('/agregar_refugio', methods=['GET', 'POST'])
def agregar_refugio():
    if request.method == "POST":
        # Obtengo todos los elementos del formulario y los envío
        body = {}
        body["nombre"] = request.form.get("nombre_refugio")
        body["coord_x"] = request.form.get("coordx")
        body["coord_y"] = request.form.get("coordy")
        body["telefono"] = request.form.get("telefono_refugio")
        body["direccion"] = request.form.get("direccion")
        response = requests.post(HOST_API + "/refugios", json = body) 
        if response.status_code == 201: # verifico que no ocurrió un error
            return render_template("formulario_valido.html")
        # Si ocurrió un error, redirijo al error_handler
        return redirect(url_for('internal_server_error', e=response.status_code))
    return render_template("form_refugios.html")

if __name__ == '__main__':
    app.run(port=PUERTO_APP)