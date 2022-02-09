from distutils.log import debug
from flask import Flask, jsonify
from flask_socketio import SocketIO

app = Flask('serverA')
sio = SocketIO(app)

@app.get('/')
def index():
    return jsonify(serverA="says hello")

def run():
    sio.run(app, debug=False)