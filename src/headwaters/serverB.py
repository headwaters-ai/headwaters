from flask import Flask, jsonify
from flask_socketio import SocketIO

app = Flask('serverB')
sio = SocketIO(app)

@app.get('/')
def index():
    return jsonify(serverB="says hello")

def run():
    sio.run(app, debug=False)