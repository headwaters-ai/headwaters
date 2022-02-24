"""Mock sio client for testing the server but already has useful bits and lessons for Fuse.

Especially:

    - inital connection retry
    - sub and unsub funcs and their use in on.connect and if name main:

"""
import socketio


sio = socketio.Client()

# initial startup conneciton error handling
connected = False

while not connected:
    try:
        sio.connect(f"http://127.0.0.1:5000")
    except socketio.exceptions.ConnectionError:
        print("startup connection to server failed... retrying")
        sio.sleep(1)
    else:
        connected = True

print(f"startup connection success with sid {sio.get_sid()}")

def subscribe(subs: list[str]) -> None:
    """Subscribes to each room in passed list."""

    if not isinstance(subs, list) or not all(isinstance(sub, str) for sub in subs):
        raise TypeError(f"subs must be a list of str, supplied {type(subs)}")
    for sub in subs:
        print(f"client subbed to room {sub}")
        # TODO make this a POST call 
        # then an ack can be rcvd
        sio.emit("subscribe", data={"room": sub})


def unsubscribe(unsubs: list[str]) -> None:
    """Unsubscribes from each room in passed list."""

    if not isinstance(unsubs, list) or not all(
        isinstance(unsub, str) for unsub in unsubs
    ):
        raise TypeError(f"subs must be a list of str, supplied {type(unsubs)}")
    for unsub in unsubs:
        print(f"client unsubbed from room {unsub}")
        # TODO make this a POST call 
        # then an ack can be rcvd
        sio.emit("unsubscribe", data={"room": unsub})


@sio.on("stream")
def new_price(payload):
    print(f"rcvd event {payload}")


@sio.on("connect")
def connect():
    print(f"sio client connected")
    # subscribe(subs)

@sio.on("connect_error")
def connect_error(e):
    print(f"connection error during operation... retrying")


@sio.on("disconnect")
def disconnect():
    print(f"sio client disconnected")

if __name__ == "__main__":
    # subscribe(subs)
    pass