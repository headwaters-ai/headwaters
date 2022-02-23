from flask import Flask, jsonify
from flask_socketio import SocketIO
import json
import pkgutil
import random

from ..engine import Engine

data = pkgutil.get_data(__package__, "data.json")
data = json.loads(data)

app = Flask("hw-server")
sio = SocketIO(app)


@app.get("/")
def index():
    return jsonify(server=f"says hello and {random.random()}")


@app.get("/command")
def command():
    """this could be one route to test in operation param changes across the command_q"""
    new_freq = random.randint(1,6)

    # so the domain of the engine can be idenfitief here with
    # for engine in engines: if engine.domain == xyz then do soemthing
    engine = random.choice(engines)
    engine.set_frequency(new_freq)
    return jsonify(server=f"adjusted engine {engine.domain} freq to {new_freq}")


def emit_mock():
    """JUST EMIT DIRECTLY
    """
    pass

engines = []

def run(domains):
    """

    what about: the Engine instances are created, then the generate method of each is multithreaded...
    could the thread have access to the object properties in that thread? NO surely not
    THIS SEEMS TO WORK?!?!?

    """

    for domain in domains:
        engines.append(Engine(domain, sio))

    for engine in engines:
        sio.start_background_task(target=engine.generate)

    sio.run(app, debug=False)
