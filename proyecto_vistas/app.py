from flask import Flask, render_template, redirect, url_for, request
import requests

app = Flask(__name__)
PUERTO_APP = 5000

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(port=PUERTO_APP)