from flask import Flask, render_template, redirect, url_for, request
import requests

app = Flask(__name__)

@app.route('/login_admin', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/admin', methods=['POST', 'PATCH', 'PUT', 'DELETE'])
def admin_config():
    if request.method in ('POST', 'PATCH', 'PUT', 'DELETE'):

        usuario = request.form.get("usuario")
        contraseña = request.form.get("contraseña")

        response_sesion = requests.get(HOST_API + ENDPOINT_API_LOGIN, json={"user": usuario, "password": contraseña})

        if response_sesion.status_code >= 500:
            return internal_server_error(e=response_sesion.status_code)

        sesion = response_sesion.json()

        if not isinstance(sesion, dict) or "code" not in sesion or not isinstance(sesion.get("code"), int) or sesion.get("code", -1) < 0 or sesion.get("code", 2) > 1:
            return internal_server_error(e=500)

        if sesion == 1:

            if request.method in ('PATCH', 'PUT', 'DELETE'):

                tipo = request.form.get("tipo").lower() # "refugio" / "reencuentro"
                accion = request.form.get("accion").lower() # "aceptar" / "rechazar"

                if tipo == "refugio":

                    id = request.form.get("id").lower()

                    if accion == "aceptar":
                        requests.patch(HOST_API + ENDPOINT_API_REFUGIO, json={"id": id})

                    elif accion == "rechazar":
                        requests.delete(HOST_API + ENDPOINT_API_REFUGIO, json={"id": id})
                    
                    else:
                        return internal_server_error(e=500)

                elif tipo == "reencuentro":
                    
                    if accion == "aceptar":
                        id_mascota = request.form.get("id_mascota").lower()
                        requests.put(HOST_API + ENDPOINT_API_REPORTES, json={"id mascota": id_mascota})

                    elif accion == "rechazar":
                        id_reporte = request.form.get("id_reporte").lower()
                        requests.patch(HOST_API + ENDPOINT_API_REPORTES, json={"id reporte": id_reporte})
                    
                    else:
                        return internal_server_error(e=500)
                
                else:
                    return internal_server_error(e=500)

            response_refugios = requests.get(HOST_API + ENDPOINT_API_REFUGIO, json={"aceptado": "false"})
            
            if response_refugios.status_code >= 500:
                return internal_server_error(e=response_refugios.status_code)

            response_reportes = requests.get(HOST_API + ENDPOINT_API_REPORTES, json={"fue_procesado": False})

            if response_reportes.status_code >= 500:
                return internal_server_error(e=response_reportes.status_code)

            refugios = response_refugios.json()
            reportes = response_reportes.json()

            return render_template('admin.html', usuario=usuario, contraseña=contraseña, refugios=refugios, reportes=reportes)

        return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(port=PUERTO_APP)