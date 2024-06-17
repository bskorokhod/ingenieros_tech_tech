from flask import Flask, render_template, redirect, url_for, request
import requests
from config_app import PUERTO_APP, HOST_API, ENDPOINT_API_REFUGIO, ENDPOINT_API_REPORTES, ENDPOINT_API_LOGIN, ENDPOINT_API_CARACTERISTICAS, ENDPOINT_API_PERDIDAS


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login_admin', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST', 'PATCH', 'PUT', 'DELETE'])
def admin_config():
    """
    FLUJO GENERAL DEL ENDPOINT `/admin`

    Si la solicitud viene desde `/login_admin`...
    Se espera recibir un formulario que tenga datos dentro de las claves:
        1. `usuario`
        2. `contraseña`

    Si la solicitud viene desde esta misma página (`/admin`), es decir, se recarga la página...
    Se espera recibir un formulario que tenga datos dentro de las claves:
        1. `usuario`
        2. `contraseña`
        3. `tipo`
        4. `accion`
        5. `id` / `id_mascota` / `id_reporte` (basado en los valores de las anteriores 2 claves)
        6. `pag_actual_refugios`
        7. `pag_actual_reportes`

        Dependiendo de los valores de las claves 3 y 4 se envían requests:
            a. 'refugio' + 'aceptar'  ==> PATCH a `ENDPOINT_API_REFUGIO`
            b. 'refugio' + 'rechazar' ==> DELETE a `ENDPOINT_API_REFUGIO`
            c. 'reencuentro' + 'aceptar'  ==> PUT a `ENDPOINT_API_REPORTES`
            d. 'reencuentro' + 'rechazar' ==> PATCH a `ENDPOINT_API_REPORTES`

    En todos los casos se envían requests de método GET a:
        I.   `ENDPOINT_API_LOGIN` valida claves 1 y 2
        II.  `ENDPOINT_API_REFUGIO` obtiene solicitudes de refugios 
        III. `ENDPOINT_API_REPORTES` obtiene reportes de reencuentros

    Si la sesión es válida se renderiza la vista `/admin`, sino se redirige a `/login_admin`.
    """
    if request.method == "GET":
        return redirect(url_for('login'))

    # Antes de cargar la página se verifica la sesión
    usuario = request.form.get("usuario")
    contraseña = request.form.get("contraseña")

    if usuario is None or contraseña is None:
        return redirect(url_for('login'))

    # Se envía el usuario y contraseña ingresados a la API y se recibe la validación
    response_sesion = requests.get(HOST_API + ENDPOINT_API_LOGIN,
                                    params={"user": usuario,
                                            "password": contraseña})

    if response_sesion.status_code >= 500:
        return internal_server_error(e=response_sesion.status_code)

    sesion = response_sesion.json()

    if (not isinstance(sesion, dict) or
        "code" not in sesion or
        not isinstance(sesion.get("code"), int) or
        sesion.get("code", -1) < 0 or
        sesion.get("code", 2) > 1):
        return internal_server_error(e=500)

    if sesion.get("code") == 1:

        if request.method in ('PATCH', 'PUT', 'DELETE'):

            tipo = request.form.get("tipo", "").lower() # "refugio" / "reencuentro"
            accion = request.form.get("accion", "").lower() # "aceptar" / "rechazar"

            if tipo == "refugio":

                id = request.form.get("id", "").lower()

                if id == "": return internal_server_error(e=500)

                if accion == "aceptar":
                    requests.patch(HOST_API + ENDPOINT_API_REFUGIO,
                                    json={"id": id})

                elif accion == "rechazar":
                    requests.delete(HOST_API + ENDPOINT_API_REFUGIO,
                                    json={"id": id})
                
                else:
                    return internal_server_error(e=500)

            elif tipo == "reencuentro":
                
                if accion == "aceptar":
                    id_mascota = request.form.get("id_mascota", "").lower()

                    if id_mascota == "": return internal_server_error(e=500)

                    requests.put(HOST_API + ENDPOINT_API_REPORTES,
                                    json={"id mascota": id_mascota})

                elif accion == "rechazar":
                    id_reporte = request.form.get("id_reporte", "").lower()

                    if id_reporte == "": return internal_server_error(e=500)

                    requests.patch(HOST_API + ENDPOINT_API_REPORTES,
                                    json={"id reporte": id_reporte})
                
                else:
                    return internal_server_error(e=500)
            
            else:
                return internal_server_error(e=500)

        # Esto se ejecuta siempre que la sesión sea válida, independientemente del método

        # En caso de enviarse un form desde login se carga la primera página
        num_pagina_refugios = request.form.get("pag_actual_refugios", 1)
        num_pagina_reportes = request.form.get("pag_actual_reportes", 1)
        
        if not num_pagina_refugios.isdigit() or not num_pagina_reportes.isdigit():
            return internal_server_error(e=500)


        response_refugios = requests.get(HOST_API + ENDPOINT_API_REFUGIO,
                                            params={"pag_refugios": int(num_pagina_refugios),
                                                    "limite_refugios": LIMITE_REPORTES_REFUGIOS,
                                                    "aceptado": "false"})
        
        if response_refugios.status_code >= 500:
            return internal_server_error(e=response_refugios.status_code)


        response_reportes = requests.get(HOST_API + ENDPOINT_API_REPORTES,
                                            params={"pag_reportes": int(num_pagina_reportes),
                                                    "limite_reportes": LIMITE_REPORTES_REENCUENTRO,
                                                    "fue_procesado": False})

        if response_reportes.status_code >= 500:
            return internal_server_error(e=response_reportes.status_code)

        # PENDIENTE: CONSENSUAR CÓMO SE RECIBE SI HAY PÁGINA SIGUIENTE
        #            VERIFICAR QUE LOS JSON CUMPLAN CON EL FORMATO ESPERADO
        refugios = response_refugios.json()
        reportes = response_reportes.json()

        if (not refugios or
            "refugios" not in refugios or
            "hay_pag_siguiente" not in refugios or
            not reportes or
            "reportes_reencuentro" not in reportes or
            "hay_pag_siguiente" not in reportes):
            return internal_server_error(e=500)
        
        if num_pagina_refugios <= 1:
            hay_pag_ant_refugios = False
        elif num_pagina_refugios > 1:
            hay_pag_ant_refugios = True
        
        if num_pagina_reportes <= 1:
            hay_pag_ant_reportes = False
        elif num_pagina_reportes > 1:
            hay_pag_ant_reportes = True

        return render_template('admin.html',
                                usuario = usuario,
                                contraseña = contraseña,
                                refugios = refugios.get("refugios"),
                                reportes = reportes.get("reportes_reencuentro"),
                                hay_pag_sig_refugios = refugios.get("hay_pag_siguiente", False),
                                hay_pag_sig_reportes = reportes.get("hay_pag_siguiente", False),
                                hay_pag_ant_refugios = hay_pag_ant_refugios,
                                hay_pag_ant_reportes = hay_pag_ant_reportes,
                                pag_actual_refugios = num_pagina_refugios,
                                pag_actual_reportes = num_pagina_reportes)

    return redirect(url_for("login"))


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

@app.errorhandler(400)
def bad_request(e):
    return render_template('base_errores.html', numero_error=400), 400

@app.errorhandler(404)
def page_not_found(e):
    return render_template('base_errores.html', numero_error=404), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('base_errores.html', numero_error=500), 500

if __name__ == '__main__':
    app.run(port=PUERTO_APP)

