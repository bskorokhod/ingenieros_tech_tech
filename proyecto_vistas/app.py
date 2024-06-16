from flask import Flask, render_template, redirect, url_for, request
import requests

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(port=PUERTO_APP)