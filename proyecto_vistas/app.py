from flask import Flask, render_template, redirect, url_for, request
import requests

app = Flask(__name__)
PUERTO_APP = 5000
HOST_API = 'http://127.0.0.1:5001'

if __name__ == '__main__':
    app.run(port=PUERTO_APP)
