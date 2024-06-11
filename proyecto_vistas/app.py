from flask import Flask, render_template, redirect, url_for, request
import requests

app = Flask(__name__)
PUERTO_APP = 5000

@app.route('/')
def home():
    return render_template('home.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('base_errores.html', numero_error=404), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('base_errores.html', numero_error=500), 500

if __name__ == '__main__':
    app.run(port=PUERTO_APP)