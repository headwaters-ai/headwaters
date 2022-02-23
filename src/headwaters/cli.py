""" cli.py is the main entry point for the app and the top level """

import click
from threading import Thread
from queue import Queue

from . import server
from . import fast_engine
from . import slow_engine


@click.command()
@click.option(
    "--engine",
    "-e",
    default=["fast"],
    multiple=True,
    help="specify the engine, fast and/or slow with -e fast -e slow",
)

# TODO need to be very clear in docs how to pass a list to the cli
# i have forgotten right now and can't start multiple
# hw -e fast -e slow etc...

#### FOR NOW JUST USE THE FAST ENGINE, this is where dev of engine objects is happening ###

def main(engine: str) -> None:

    emit_q = Queue()

    command_q = Queue() # TODO but i will need to send a queue to each engine, there could be many
    # how to do this?

    # single server, always
    server_proc = Thread(target=server.run, args=(emit_q, command_q))
    server_proc.start()

    # multi engines
    engines_passed = engine  # engine here is a list, as click opt is multiple

    engines = []

    for engine_passed in engines_passed:

        if engine_passed == "fast":
            engines.append(fast_engine.Fast)


        if engine_passed == "slow":
            engines.append(slow_engine.mgr)

    engine_threads = []

    for engine in engines:
        engine_threads.append(Thread(target=engine, args=(emit_q, command_q)))

    for engine_thread in engine_threads:
        engine_thread.start()


if __name__ == "__main__":
    main()
