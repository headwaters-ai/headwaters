from flask import Flask, jsonify
from flask_socketio import SocketIO
import json
import pkgutil
import os
import random

data = pkgutil.get_data(__package__, "data.json")
data = json.loads(data)

app = Flask("hw-server")
sio = SocketIO(app)


@app.get("/")
def index():
    return jsonify(mpserver=f"says hello and {random.random()}")


@app.post("/command")
def command():
    """this could be one route to test in operation param changes across the command_q"""
    pass


def q_printer(emit_q):
    """will become emitter, for now run on bg task,
    emptys queue when item enqued and prints to console
    """

    while True:
        while not emit_q.empty():
            item = emit_q.get()
            # emit here
            print(f"sio.bgt rcvd and prints {item}")

        # this sleep amount severly impacts CPU and idle wake up statistics
        sio.sleep(0.001)


def run(emit_q):
    print(f"mpserver running in namespace {__name__} with pid {os.getpid()}")
    print()
    print(f"data accessed from pacakge file {data}")
    print()
    # rcv the emit_q object from the process spawn and pass through to the background thread of the server process
    sio.start_background_task(target=q_printer, emit_q=emit_q)
    sio.run(app, debug=False)
