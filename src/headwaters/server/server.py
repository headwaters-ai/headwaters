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

    return jsonify(pong=random.randint(1, 100))


@app.get("/start")
def start():

    """route to start the stream provided a stream_name in the url params

    returns the stream_status so the client can retieve latest state
    """

    # first, check the request has parameter arguments
    if request.args:
        # NB for request arg this is an ImmutableMultiDict from werkzeug, so can access using ['key'] format
        # but it generates it's own error messages if a key is not found, this is useful in general, but complicates
        # things in this case, so we convert to regular dictionary, so this keeps code handling args
        # keys similar to handling json keys
        data = dict(request.args)
    else:
        return (
            jsonify(
                msg=f"RequestError: request must contain url arguments (probably missing 'stream_name')"
            ),
            400,
        )

    try:
        stream_name = data["stream_name"]
        if not stream_name:
            raise ValueError("'stream_name' must not be empty")

    except KeyError as e:
        return (
            jsonify(msg=f"missing key: {str(e)}"),
            400,
        )
    except ValueError as e:
        return (
            jsonify(msg=f"value error: {str(e)}"),
            400,
        )

    # check that the value of stream_name is of type 'str'
    if not isinstance(stream_name, str):
        return jsonify(
            msg=f"TypeError: stream name (stream_name) must be an integer; supplied value was of type {type(stream_name)}"
        )

    for stream in streams:
        if stream.name == stream_name:
            try:
                stream.start()
                r = stream.stream_status
                return jsonify(r)
            except ValueError as e:
                return (
                    jsonify(msg=f"{str(e)}"),
                    400,
                )

    return (
        jsonify(
            msg=f"ValueError: seems like stream '{stream_name}' has not been created...?"
        ),
        404,
    )


@app.get("/stop")
def stop():

    """route to stop the stream provided a stream_name in the url params

    returns the stream_status so the client can retieve latest state
    """

    # first, check the request has parameter arguments
    if request.args:
        # NB for request arg this is an ImmutableMultiDict from werkzeug, so can access using ['key'] format
        # but it generates it's own error messages if a key is not found, this is useful in general, but complicates
        # things in this case, so we convert to regular dictionary, so this keeps code handling args
        # keys similar to handling json keys
        data = dict(request.args)
    else:
        return (
            jsonify(
                msg=f"RequestError: request must contain url arguments (probably missing 'stream_name')"
            ),
            400,
        )

    try:
        stream_name = data["stream_name"]
        if not stream_name:
            raise ValueError("'stream_name' must not be empty")

    except KeyError as e:
        return (
            jsonify(msg=f"missing key: {str(e)}"),
            400,
        )
    except ValueError as e:
        return (
            jsonify(msg=f"value error: {str(e)}"),
            400,
        )

    # check that the value of stream_name is of type 'str'
    if not isinstance(stream_name, str):
        return jsonify(
            msg=f"TypeError: stream name (stream_name) must be an integer; supplied value was of type {type(stream_name)}"
        )

    for stream in streams:
        if stream.name == stream_name:
            try:
                stream.stop()
                r = stream.stream_status
                return jsonify(r)
            except ValueError as e:
                return (
                    jsonify(msg=f"{str(e)}"),
                    400,
                )

    return (
        jsonify(
            msg=f"ValueError: seems like stream '{stream_name}' has not been created...?"
        ),
        404,
    )


@app.get("/stream_status")
def stream_status():
    """a general purpose route to enable quick acquisition of a stream state

    uses the stream_status @property (not a method to call)

    returns relevant properties of a Stream instance so the client can retieve latest state
    """
    # first, check the request has parameter arguments
    if request.args:
        # NB for request arg this is an ImmutableMultiDict from werkzeug, so can access using ['key'] format
        # this keeps code handling args similar to handling json
        data = dict(request.args)
    else:
        return (
            jsonify(
                msg=f"RequestError: request must contain url arguments (probably missing 'stream_name')"
            ),
            400,
        )

    try:
        stream_name = data["stream_name"]
        if not stream_name:
            raise ValueError("'stream_name' must not be empty")

    except KeyError as e:
        return (
            jsonify(msg=f"missing key: {str(e)}"),
            400,
        )
    except ValueError as e:
        return (
            jsonify(msg=f"value error: {str(e)}"),
            400,
        )

    # check that the value of stream_name is of type 'str'
    if not isinstance(stream_name, str):
        return jsonify(
            msg=f"TypeError: stream name (stream_name) must be an integer; supplied value was of type {type(stream_name)}"
        )

    for stream in streams:
        if stream.name == stream_name:
            try:
                r = stream.stream_status
                return jsonify(r)

            # handle an error which as of writing is of unknown type...
            except Exception as e:
                return (
                    jsonify(msg=f"{str(e)}"),
                    400,
                )

    return (
        jsonify(
            msg=f"ValueError: seems like stream '{stream_name}' has not been created...?"
        ),
        404,
    )


@app.get("/source")
def get_source():
    """a GET route to enable acquisition of a source instance state

    uses the source_status @property (not a method to call)

    returns the state of one or all Source instance(s) in the 'sources' list
    so the client can retrieve latest state

    """
    # first, check the request has parameter arguments
    if request.args:
        # NB for request arg this is an ImmutableMultiDict from werkzeug, so can access using ['key'] format
        # this keeps code handling args similar to handling json
        data = dict(request.args)

        try:
            stream_name = data["stream_name"]
            if not stream_name:
                raise ValueError("'stream_name' must not be empty")

        except KeyError as e:
            return (
                jsonify(msg=f"missing key: {str(e)}"),
                400,
            )
        except ValueError as e:
            return (
                jsonify(msg=f"value error: {str(e)}"),
                400,
            )

        # check that the value of stream_name is of type 'str'
        if not isinstance(stream_name, str):
            return jsonify(
                msg=f"TypeError: stream name (stream_name) must be an integer; supplied value was of type {type(stream_name)}"
            )

        for source in sources:
            if source.name == stream_name:
                try:
                    r = source.get_source_state
                    return jsonify(r)

                # handle an error which as of writing is of unknown type...
                except Exception as e:
                    return (
                        jsonify(msg=f"{str(e)}"),
                        400,
                    )

        return (
            jsonify(
                msg=f"ValueError: seems like stream '{stream_name}' has not been created...?"
            ),
            404,
        )
    else:
        # NOTE this will be dropped to return all source instances in sources list eveutally
        return (
            jsonify(
                msg=f"RequestError: request must contain url arguments (probably missing 'stream_name')"
            ),
            400,
        )


@app.patch("/freq")
def freq():
    """PATCH that is sent the new required value for the freq of stream new_freq
    and use the stream.set_freq(new_freq) setter

    in milliseconds as an integer ie 1,200 ms
    """
    # first, check the request has a json data payload
    if request.json:
        data = request.json
    else:
        return (
            jsonify(msg=f"RequestError: request must contain a json payload"),
            400,
        )

    # then, check all keys are present and have a value
    try:
        stream_name = data["stream_name"]
        if not stream_name:
            raise ValueError("'stream_name' must not be empty")

        new_freq = data["new_freq"]
        if not new_freq:
            raise ValueError("'new_freq' must not be zero")

    except KeyError as e:
        return (
            jsonify(msg=f"missing key: {str(e)}"),
            400,
        )
    except ValueError as e:
        return (
            jsonify(msg=f"value error: {str(e)}"),
            400,
        )

    # check that the value of stream_name is of type 'str'
    # NB Stream class instances handle type checking for their own properties and methods
    if not isinstance(stream_name, str):
        return jsonify(
            msg=f"TypeError: stream name (stream_name) must be an integer; supplied value was of type {type(stream_name)}"
        )

    for stream in streams:
        if stream.name == stream_name:
            try:
                stream.set_freq(new_freq)
                r = stream.stream_status
                return jsonify(r)
            except ValueError as e:
                return (
                    jsonify(msg=f"{str(e)}"),
                    400,
                )
            except TypeError as e:
                return (
                    jsonify(msg=f"{str(e)}"),
                    400,
                )
        else:
            return (
                jsonify(
                    msg=f"ValueError: seems like stream '{stream_name}' has not been created...?"
                ),
                404,
            )


@app.patch("/start_burst")
def start_burst():
    """trigger a burst by setting the stream.burst_mode to True via
    calling the stream.start_burst() setter method

    """
    # first, check the request has a json data payload
    if request.json:
        data = request.json
    else:
        return (
            jsonify(msg=f"RequestError: request must contain a json payload"),
            400,
        )

    # then, check all keys are present and have a value
    try:
        stream_name = data["stream_name"]
        if not stream_name:
            raise ValueError("'stream_name' must not be empty")

    except KeyError as e:
        return (
            jsonify(msg=f"missing key: {str(e)}"),
            400,
        )
    except ValueError as e:
        return (
            jsonify(msg=f"value error: {str(e)}"),
            400,
        )

    # check that the value of stream_name is of type 'str'
    # NB Stream class instances handle type checking for their own properties and methods
    if not isinstance(stream_name, str):
        return jsonify(
            msg=f"TypeError: stream name (stream_name) must be an integer; supplied value was of type {type(stream_name)}"
        )

    for stream in streams:
        if stream.name == stream_name:
            try:
                stream.start_burst()
                r = stream.stream_status
                return jsonify(r)
            except ValueError as e:
                return (
                    jsonify(msg=f"{str(e)}"),
                    400,
                )
            except TypeError as e:
                return (
                    jsonify(msg=f"{str(e)}"),
                    400,
                )
        else:
            return (
                jsonify(
                    msg=f"ValueError: seems like stream '{stream_name}' has not been created...?"
                ),
                404,
            )


@app.patch("/burst_freq")
def burst_freq():
    """set the burst frequency by calling stream.set_burst_freq method"""

    # first, check the request has a json data payload
    if request.json:
        data = request.json
    else:
        return (
            jsonify(msg=f"RequestError: request must contain a json payload"),
            400,
        )

    # then, check all keys are present and have a value
    try:
        stream_name = data["stream_name"]
        if not stream_name:
            raise ValueError("'stream_name' must not be empty")

        burst_freq = data["burst_freq"]
        if not burst_freq:
            raise ValueError("'burst_freq' must not be zero")

    except KeyError as e:
        return (
            jsonify(msg=f"missing key: {str(e)}"),
            400,
        )
    except ValueError as e:
        return (
            jsonify(msg=f"value error: {str(e)}"),
            400,
        )

    # check that the value of stream_name is of type 'str'
    # NB Stream class instances handle type checking for their own properties and methods
    if not isinstance(stream_name, str):
        return jsonify(
            msg=f"TypeError: stream name (stream_name) must be an integer; supplied value was of type {type(stream_name)}"
        )

    for stream in streams:
        if stream.name == stream_name:
            try:
                stream.set_burst_freq(burst_freq)
                r = stream.stream_status
                return jsonify(r)
            except ValueError as e:
                return (
                    jsonify(msg=f"{str(e)}"),
                    400,
                )
            except TypeError as e:
                return (
                    jsonify(msg=f"{str(e)}"),
                    400,
                )
        else:
            return (
                jsonify(
                    msg=f"ValueError: seems like stream '{stream_name}' has not been created...?"
                ),
                404,
            )


@app.patch("/burst_vol")
def burst_vol():
    """set the burst volume by calling stream.set_burst_vol method"""

    # first, check the request has a json data payload
    if request.json:
        data = request.json
    else:
        return (
            jsonify(msg=f"RequestError: request must contain a json payload"),
            400,
        )

    # then, check all keys are present and have a value
    try:
        stream_name = data["stream_name"]
        if not stream_name:
            raise ValueError("'stream_name' must not be empty")

        burst_vol = data["burst_vol"]
        if not burst_vol:
            raise ValueError("'burst_vol' must not be zero")

    except KeyError as e:
        return (
            jsonify(msg=f"missing key: {str(e)}"),
            400,
        )
    except ValueError as e:
        return (
            jsonify(msg=f"value error: {str(e)}"),
            400,
        )

    # check that the value of stream_name is of type 'str'
    # NB Stream class instances handle type checking for their own properties and methods
    if not isinstance(stream_name, str):
        return jsonify(
            msg=f"TypeError: stream name (stream_name) must be an integer; supplied value was of type {type(stream_name)}"
        )

    for stream in streams:
        if stream.name == stream_name:
            try:
                stream.set_burst_vol(burst_vol)
                r = stream.stream_status
                return jsonify(r)
            except ValueError as e:
                return (
                    jsonify(msg=f"{str(e)}"),
                    400,
                )
            except TypeError as e:
                return (
                    jsonify(msg=f"{str(e)}"),
                    400,
                )
        else:
            return (
                jsonify(
                    msg=f"ValueError: seems like stream '{stream_name}' has not been created...?"
                ),
                404,
            )


@app.patch("/source")
def patch_source():

    # first, check the request has a json data payload
    if request.json:
        data = request.json
    else:
        return (
            jsonify(msg=f"RequestError: request must contain a json payload"),
            400,
        )

    # then, check all required keys are present and have a value
    try:
        source_name = data["stream_name"]
        if not source_name:
            raise ValueError("'stream_name' must not be empty")

        config_area = data["config_area"]
        if not config_area:
            raise ValueError(f"'config_area' cannot be blank for a patch")

        setting = data["setting"]
        if not setting:
            raise ValueError("'setting' must not be empty")

        new_setting_val = data["new_setting_val"]

    except KeyError as e:
        return (
            jsonify(msg=f"missing key: {str(e)}"),
            400,
        )
    except ValueError as e:
        return (
            jsonify(msg=f"value error: {str(e)}"),
            400,
        )

    except Exception as e:
        return (
            jsonify(msg=f"unkown error: {str(e)}"),
            400,
        )
    # OPTIONAL KEYS
    try:
        field_name = data["field_name"]
        if not field_name:
            raise ValueError("'field_name' must not be empty")
    except KeyError as e:
        field_name = None
    except ValueError as e:
        # but if it is there it needs a value!
        return (
            jsonify(msg=f"value error: {str(e)}"),
            400,
        )

    # check that the value of stream_name is of type 'str'
    # NB Stream class instances handle type checking for their own properties and methods
    if not isinstance(source_name, str):
        return jsonify(
            msg=f"TypeError: source name {source_name} must be an string; supplied value was of type {type(source_name)}"
        )

    for source in sources:
        if source.name == source_name:
            try:
                print("made it to set source call in server")
                source.set_source_element(
                    config_area=config_area,
                    field_name=field_name,
                    setting=setting,
                    new_setting_val=new_setting_val,
                )
                r = source.get_source_state
                return jsonify(r)
            except ValueError as e:
                return (
                    jsonify(msg=f"{str(e)}"),
                    400,
                )
            except TypeError as e:
                return (
                    jsonify(msg=f"{str(e)}"),
                    400,
                )
            except Exception as e:
                return (
                    jsonify(msg=f"unknown error {str(e)}"),
                    400,
                )
        else:
            return (
                jsonify(
                    msg=f"ValueError: seems like stream '{source_name}' has not been created...?"
                ),
                404,
            )


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


def run(selected_sources):
    """ """

    for selected_source in selected_sources:
        try:
            source = Source(selected_source)
        except FileNotFoundError:
            print(
                Fore.YELLOW
                + f"   source name '{selected_source}' not resolved in schema lookup"
                + Style.RESET_ALL
            )
            print()
            continue
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
    print(Style.DIM + "(CTRL-C to stop)" + Style.RESET_ALL)

    sio.run(app, debug=False, port=port)

    print()
    print(Fore.RED + Style.BRIGHT + f"Stopping streams..." + Style.RESET_ALL)

    for stream in streams:
        try:
            stream.stop()
            print(Fore.RED + f"   stopped stream '{stream.name}'" + Style.RESET_ALL)
        except ValueError as e:
            print(
                Fore.RED
                + f"   stream '{stream.name}' already stopped"
                + Style.RESET_ALL
            )

    print()
