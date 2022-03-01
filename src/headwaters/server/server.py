from flask import Flask, jsonify, request, send_file, Response
from flask_socketio import SocketIO

import random
import logging
import pkgutil

logging.basicConfig(level=logging.INFO)


from ..engine import Engine
from ..domains import Domain


app = Flask("hw-server")
sio = SocketIO(app)


@app.get("/")
def index():
    return jsonify(server=f"says hello and {random.random()}")


@app.get("/start")
def start():
    engine = random.choice(engines)
    engine.start()

    return jsonify(server=f"started engine {engine.domain.name}")


@app.get("/stop")
def stop():
    engine = random.choice(engines)
    engine.stop()

    return jsonify(server=f"stopped engine {engine.domain.name}")


@app.get("/frequency")
def command():
    """this could be one route to test in operation param changes across the command_q"""
    new_freq = random.randint(1, 6)

    # so the domain of the engine can be idenfitief here with
    # for engine in engines: if engine.domain == xyz then do soemthing
    engine = random.choice(engines)
    engine.set_frequency(new_freq)
    return jsonify(server=f"adjusted engine {engine.domain.name} freq to {new_freq}")


@app.get("/burst")
def burst():
    engine = random.choice(engines)
    engine.set_burst()

    return jsonify(
        server=f"initiated burst for engine {engine.domain.name} with {engine.burst_limit}"
    )


@app.get("/error_on")
def error_on():
    engine = random.choice(engines)
    engine.set_error_mode_on()

    return jsonify(server=f"error mode set for engine {engine.domain.name}")


@app.post("/add_field")
def add_word():

    data = request.json

    this_domain = data['domain']

    r = "huh"
    for domain in domains:
        if this_domain == domain.name:
            r = domain.set_field(data)
            break

    return jsonify(server=r)

@app.route('/ui', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    print(path)
    if path.endswith('.js'):
        r = pkgutil.get_data("headwaters", f"{path}")
        return Response(r, mimetype="text/javascript")

    elif path.endswith('.css'):
        r = pkgutil.get_data("headwaters", f"{path}")
        return Response(r, mimetype="text/css")

    elif path.endswith('.ico'):
        r = pkgutil.get_data("headwaters", f"{path}")
        return Response(r, mimetype="text/application")

    elif path.endswith('.svg'):
        r = pkgutil.get_data("headwaters", f"{path}")
        return Response(r, mimetype="image/svg+xml")

    else:
        r = pkgutil.get_data("headwaters.ui", "index.html")
        return Response(r, mimetype="text/html")

@sio.event("connect")
def connect_hndlr():
    logging.info(f"sio conneciton rcvd {sio.sid}")


engines = []
domains = []


def run(selected_domains):
    """

    what about: the Engine instances are created, then the generate method of each is multithreaded...
    could the thread have access to the object properties in that thread? NO surely not
    THIS SEEMS TO WORK?!?!?

    ALSO CAN I KNOW INSTNATIATE ENGINE OBKECT OUTWITH SERVER
    CAN I TEST THEM WITHOUT USING HTTP REQUESTS??

    now the thinking is to have the domain classed available in the server scope
    that way i can access the new_event() method of a domain instance fromt he generator thread and
    also access it for CUD ops

    """

    for selected_domain in selected_domains:
        domain = Domain(selected_domain)
        domains.append(domain)
        engines.append(Engine(domain, sio))

    for engine in engines:
        sio.start_background_task(target=engine.generate)

    sio.run(app, debug=False)
