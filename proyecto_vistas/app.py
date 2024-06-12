from flask import Flask, render_template, redirect, url_for, request
import requests

app = Flask(__name__)
PUERTO_APP = 5000

@app.route('/')
def home():
    return render_template('home.html')

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
            return redirect("internal_server_error", e=response.status_code)

    return render_template("aceptado.html", form=formulario)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('base_errores.html', numero_error=404), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('base_errores.html', numero_error=500), 500

if __name__ == '__main__':
    app.run(port=PUERTO_APP)