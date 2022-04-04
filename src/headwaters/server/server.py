from flask import Flask, jsonify, request, Response, abort
from flask_socketio import SocketIO
from flask_cors import CORS

import random
import logging
import pkgutil
import threading
import click
import time

from colorama import Fore, Back, Style

flask_log = logging.getLogger("werkzeug")
flask_log.setLevel(logging.ERROR)


def secho(text, file=None, nl=None, err=None, color=None, **styles):
    pass


def echo(text, file=None, nl=None, err=None, color=None, **styles):
    pass


click.echo = echo
click.secho = secho


from ..stream import Stream
from ..source import Source


app = Flask("hw-server")
CORS(app)
sio = SocketIO(app)


@app.get("/")
def index():
    return jsonify(msg=f"says hello and {random.random()}")


@app.get("/ping")
def ping():
    logging.info(f"pong")
    return jsonify(pong=random.randint(1, 100))


@app.get("/start")
def start():

    """route to start the stream provided a stream_name in the url params

    returns the stream_status so the client can retieve latest state
    """

    stream_name = request.args.get("stream_name", None)

    if stream_name:
        for stream in streams:
            if stream.name == stream_name:
                stream.start()
                r = stream.stream_status
                logging.info(f"start route for {stream_name}, response: {r}")
                return jsonify(r)

        return (
            jsonify(msg=f"perhaps stream stream {stream_name} has not been created"),
            404,
        )

    else:
        return (
            jsonify(
                msg=f"please specify a stream name in url params using 'stream_name' = "
            ),
            400,
        )


@app.get("/stop")
def stop():

    """route to stop the stream provided a stream_name in the url params

    returns the stream_status so the client can retieve latest state
    """

    stream_name = request.args.get("stream_name", None)

    if stream_name:
        for stream in streams:
            if stream.name == stream_name:
                stream.stop()
                r = stream.stream_status
                logging.info(f"stop route for {stream_name}, response: {r}")
                return jsonify(r)

        return jsonify(msg=f"seems like stream {stream_name} has not been created"), 404
    else:
        return (
            jsonify(
                msg=f"please specify a stream name in url params using 'stream_name' = "
            ),
            400,
        )


@app.get("/stream_status")
def stream_status():
    """a general purpose route to enable quick acquisition of a stream state

    uses the stream_status @property (not a method to call)

    returns the stream_status so the client can retieve latest state
    """

    stream_name = request.args.get("stream_name", None)

    if stream_name:
        for stream in streams:
            if stream.name == stream_name:
                r = stream.stream_status
                return jsonify(r)

        return (
            jsonify(msg=f"seems like stream {stream_name} has not been created...?"),
            404,
        )
    else:
        return (
            jsonify(
                msg=f"please specify a stream name in url params using 'stream_name' = "
            ),
            400,
        )


@app.patch("/freq")
def command():
    """PATCH that is sent the new required value for the freq of stream

    in milliseconds as an integer ie 1,200 ms
    """
    if request.json:
        data = request.json
        stream_name = data["stream_name"]
        new_freq = data["new_freq"]

        if stream_name and new_freq:
            for stream in streams:
                if stream.name == stream_name:
                    try:
                        stream.set_freq(new_freq)
                        r = stream.stream_status
                        return jsonify(r)
                    except ValueError:
                        return (
                            jsonify(
                                msg=f"PATCH request to /freq must contain postive integer gte 100ms"
                            ),
                            400,
                        )
                else:
                    logging.error(f"reuqested stream {stream_name} was not found in stream_list")
                    return (
                        jsonify(
                            msg=f"seems like stream {stream_name} has not been created...?"
                        ),
                        404,
                    )
        else:
            return (
                jsonify(
                    msg=f"PATCH request to /freq must contain stream_name and new_freq params in json payload"
                ),
                400,
            )

    else:
        return jsonify(msg=f"PATCH request must contain json payload data"), 400


@app.get("/burst")
def burst():
    stream = random.choice(streams)
    stream.set_burst()

    return jsonify(
        msg=f"initiated burst for stream {stream.name} with {stream.burst_limit}"
    )


@app.get("/error_on")
def error_on():
    stream = random.choice(streams)
    stream.set_error_mode_on()

    return jsonify(msg=f"error mode set for stream {stream.name}")


@app.post("/add_field")
def add_word():

    data = request.json

    this_domain = data["source"]

    r = "huh"
    for source in sources:
        if this_domain == source.name:
            r = source.set_field(data)
            break

    return jsonify(msg=r)


@app.route("/ui", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    if path.endswith(".js"):
        r = pkgutil.get_data("headwaters", f"{path}")
        logging.info(f"request on ui/ to {path}")

        return Response(r, mimetype="text/javascript")

    elif path.endswith(".css"):
        r = pkgutil.get_data("headwaters", f"{path}")
        logging.info(f"request on ui/ to {path}")

        return Response(r, mimetype="text/css")

    elif path.endswith(".ico"):
        r = pkgutil.get_data("headwaters", f"{path}")
        logging.info(f"request on ui/ to {path}")

        return Response(r, mimetype="text/application")

    elif path.endswith(".svg"):
        r = pkgutil.get_data("headwaters", f"{path}")
        logging.info(f"request on ui/ to {path}")

        return Response(r, mimetype="image/svg+xml")

    else:
        r = pkgutil.get_data("headwaters.ui", "index.html")
        logging.info(f"request on ui/ to {path}")
        return Response(r, mimetype="text/html")


@sio.event("connect")
def connect_hndlr():
    logging.info(f"sio connection rcvd {sio.sid}")


streams = []
sources = []


def run(selected_domains):
    """ """

    for selected_domain in selected_domains:
        source = Source(selected_domain)
        sources.append(source)
        streams.append(Stream(source, sio))

    stream_threads = []
    for stream in streams:
        stream_threads.append(threading.Thread(target=stream.flow))

    for stream_thread in stream_threads:
        stream_thread.start()

    port = 5555  # set up a config file

    print(
        Fore.GREEN
        + Style.BRIGHT
        + f"STREAMS: http://127.0.0.1:{port}"
        + Style.RESET_ALL
    )
    print(
        Fore.CYAN + Style.BRIGHT + f"UI: http://127.0.0.1:{port}/ui" + Style.RESET_ALL
    )
    print()
    print(Fore.RED + Style.DIM + "(CTRL-C to stop)" + Style.RESET_ALL)

    sio.run(app, debug=False, port=port)

    print()
    print(f"Server stopping...")
    print()

    for stream in streams:
        stream.stop()
