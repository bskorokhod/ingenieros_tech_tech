from flask import Flask, render_template, redirect, url_for, request
import requests
from config_app import PUERTO_APP, HOST_API, ENDPOINT_API_REFUGIO, ENDPOINT_API_REPORTES, ENDPOINT_API_LOGIN, ENDPOINT_API_CARACTERISTICAS, ENDPOINT_API_PERDIDAS, LIMITE_MASCOTAS, LIMITE_REFUGIOS, LIMITE_REPORTES_REENCUENTRO, LIMITE_REPORTES_REFUGIOS
from validaciones import es_refugio

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login_admin', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
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

        if "tipo" in request.form:

            tipo = request.form.get("tipo", "").lower() # "refugio" / "reencuentro"
            accion = request.form.get("accion", "").lower() # "aceptar" / "rechazar"

            if tipo == "refugio":

                id = request.form.get("id", "").lower()
                
                if id == "": return bad_request(e=400)

                if accion == "aceptar":
                    response = requests.patch(HOST_API + ENDPOINT_API_REFUGIO,
                                    json={"id": id})

                elif accion == "rechazar":
                    response = requests.delete(HOST_API + ENDPOINT_API_REFUGIO,
                                    json={"id": id})
                
                else:
                    return bad_request(e=400)

            elif tipo == "reencuentro":
                
                if accion == "aceptar":
                    id_mascota = request.form.get("id_mascota", "").lower()


                    if id_mascota == "": return bad_request(e=400)

                    response = requests.put(HOST_API + ENDPOINT_API_REPORTES,
                                    json={"id_mascota": id_mascota})

                elif accion == "rechazar":
                    id_reporte = request.form.get("id_reporte", "").lower()

                    if id_reporte == "": return bad_request(e=400)

                    response = requests.patch(HOST_API + ENDPOINT_API_REPORTES,
                                    json={"id_reporte": id_reporte})
                
                else:
                    return bad_request(e=400)
            
            else:
                return bad_request(e=400)
            
            if response.status_code == 500:
                return internal_server_error(e=response.status_code)
            elif response.status_code == 400:
                return bad_request(e=response.status_code)

        # En caso de enviarse un form desde login se carga la primera página
        num_pagina_refugios = request.form.get("pag_actual_refugios", "1")
        num_pagina_reportes = request.form.get("pag_actual_reportes", "1")
        
        if not num_pagina_refugios.isdigit() or not num_pagina_reportes.isdigit():
            return bad_request(e=400)

        num_pagina_refugios = int(num_pagina_refugios)
        num_pagina_reportes = int(num_pagina_reportes)

        response_refugios = requests.get(HOST_API + ENDPOINT_API_REFUGIO,
                                            params={"pagina": num_pagina_refugios,
                                                    "elementos": LIMITE_REPORTES_REFUGIOS,
                                                    "aceptado": "FALSE"})
        
        if response_refugios.status_code >= 500:
            return internal_server_error(e=response_refugios.status_code)
        elif response_refugios.status_code == 400:
            return bad_request(e=response.status_code)

        response_reportes = requests.get(HOST_API + ENDPOINT_API_REPORTES,
                                            params={"pag_reportes": num_pagina_reportes,
                                                    "limite_reportes": LIMITE_REPORTES_REENCUENTRO})

        if response_reportes.status_code >= 500:
            return internal_server_error(e=response_reportes.status_code)
        elif response_refugios.status_code == 400:
            return bad_request(e=response.status_code)

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

    return redirect(url_for('login'))


@app.route('/refugios', methods=["GET",'POST'])
def refugios():
    
    try:          
        pagina = request.form.get('pagina', 1, type=int)
        response = requests.get(HOST_API + ENDPOINT_API_REFUGIO, params={'pagina': pagina, 'elementos': LIMITE_REFUGIOS, 'aceptado': 'TRUE'})
        response = response.json()
        
        hay_siguiente_pagina = response.get("hay_pag_siguiente", False)
        
        refugios = response.get("refugios", [])
        
        hay_pagina_anterior = int(pagina) > 1
        
        return render_template('refugios.html', refugios=refugios, hay_pagina_siguiente=hay_siguiente_pagina, hay_pagina_anterior=hay_pagina_anterior, pagina=pagina)

    except requests.exceptions.HTTPError as e:
        return internal_server_error(e=500)
    except requests.exceptions.RequestException as e:
        return internal_server_error(e=500)


@app.route('/agregar_refugio', methods=['GET', 'POST'])
def agregar_refugio():
    if request.method == "POST":
        # Obtengo todos los elementos del formulario y los envío
        nuevo_refugio = {}
        nuevo_refugio["nombre"] = request.form.get("nombre_refugio")
        nuevo_refugio["coordx"] = request.form.get("coordx")
        nuevo_refugio["coordy"] = request.form.get("coordy")
        nuevo_refugio["telefono"] = request.form.get("telefono_refugio")
        nuevo_refugio["direccion"] = request.form.get("direccion")

        if not es_refugio(nuevo_refugio):
            return bad_request(e=400)
        
        response = requests.post(HOST_API + ENDPOINT_API_REFUGIO, json = nuevo_refugio) 
        if response.status_code == 201: # verifico que no ocurrió un error
            return redirect(url_for("aceptado", formulario="refugio"))
        # Si ocurrió un error, redirijo al error_handler
        return internal_server_error(e=response.status_code)
    
    return render_template("form_refugios.html")

@app.route("/aceptado/", defaults={"formulario": None})
@app.route("/aceptado/<formulario>", methods=["GET", "POST"])
def aceptado(formulario):
    # si el formulario es de reencuentro, se envía un POST a la API con el id de la mascota
    if request.method == "POST":
        id_mascota = request.form.get("id")
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
        elif response.status_code == 400:
            return bad_request(e=response.status_code) # Función que renderiza un template de error 500
        return internal_server_error(e=response.status_code)


    elif request.method == 'GET':
        response = requests.get(HOST_API + '/caracteristicas_mascotas')
        if response.status_code == 200:
            caracteristicas_animales = response.json()
            return render_template('form_mascotas.html', caracteristicas_animales=caracteristicas_animales)
        else:
            return internal_server_error(e=response.status_code)

@app.route('/encontrado', methods=["GET", "POST"])
def encontrado():

    # Recibimos las características de los animales para que se puedan usar en los filtros
    datos_caracteristicas = requests.get(f"{HOST_API}{ENDPOINT_API_CARACTERISTICAS}")
    if datos_caracteristicas.status_code == 500:
        return internal_server_error(e=datos_caracteristicas.status_code)
    
    caracteristicas_animales = datos_caracteristicas.json()

    # Inicialmente se solicita la página 1 de las mascotas perdidas
    filtros_busqueda = {'pagina': 1}

    # Recibimos el número de página que se quiere ver, junto a todos los filtros solicitados
    if request.method == "POST":
        filtros_busqueda = dict(request.form)
    
    # Agregamos la cantidad de elementos de la página y filtramos por los animáles que aún no se confirmó que hayan sido encontrados
    filtros_busqueda.update({'elementos': LIMITE_MASCOTAS, 'encontrado': 0})
    
    datos_mascotas = requests.get(f"{HOST_API}{ENDPOINT_API_PERDIDAS}", params=filtros_busqueda)
    if datos_mascotas.status_code == 500:
        return internal_server_error(e=datos_mascotas.status_code)
    
    info_mascotas = datos_mascotas.json()
    mascotas_perdidas = info_mascotas.get('mascotas')

    # Si mascota["info_adicional"] es None, se cambia por un mensaje predefinido para mejor estética
    for mascota in mascotas_perdidas:
        if not mascota["info_adicional"]:
            mascota["info_adicional"] = "No se ingresó ninguna información adicional."
    
    # Devolvemos las características, las mascotas perdidas, la página que se solicitó, y valores booleanos para saber si hay una página anterior o una posterior
    return render_template('mascotas_perdidas.html', caracteristicas = caracteristicas_animales, mascotas = mascotas_perdidas, pagina_actual = info_mascotas.get('pagina'), hay_pagina_previa = info_mascotas.get('hay_pagina_previa'), hay_pagina_siguiente = info_mascotas.get('hay_pagina_siguiente'), filtros = dict(request.form.items()))

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

