from flask import Flask, jsonify
from flask_socketio import SocketIO
import json
import pkgutil

data = pkgutil.get_data(__package__, 'data.json')
data = json.loads(data)

app = Flask('serverC')
sio = SocketIO(app)

@app.get('/')
def index():
    return jsonify(serverC="says hello")

def run():
    print(data)
    sio.run(app, debug=False)