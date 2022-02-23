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
    return jsonify(server=f"says hello and {random.random()}")


@app.get("/command")
def command():
    """this could be one route to test in operation param changes across the command_q"""
    new_freq = random.randint(2,5)
    place_command(new_freq)
    return jsonify(server=f"adjusted freq to {new_freq}")

def place_command(command):
    """called by the /command endpoint and places the command onto the cmd_q
    
    first test is a single rand int for freq of fast engine
    
    """
    cmd_q.put(command)

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

cmd_q = None # this is so ugly cant be right

def run(emit_q, command_q):

    global cmd_q
    cmd_q = command_q
    print(f"mpserver running in namespace {__name__} with pid {os.getpid()}")
    print()
    print(f"data accessed from pacakge file {data}")
    print()
    # rcv the emit_q object from the process spawn and pass through to the background thread of the server process
    sio.start_background_task(target=q_printer, emit_q=emit_q)
    sio.run(app, debug=False)
