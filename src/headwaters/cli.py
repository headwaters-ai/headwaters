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
    default=["slow"],
    multiple=True,
    help="specify the engine, fast or slow",
)
def main(engine: str) -> None:

    emit_q = Queue()
    # TODO need a command_q

    # single server, always
    server_proc = Thread(target=server.run, args=(emit_q,))
    server_proc.start()

    # multi engines
    engines_passed = engine  # engine here is a list, as click opt is multiple

    engines = []

    for engine_passed in engines_passed:

        if engine_passed == "fast":
            engines.append(fast_engine.mgr)

        if engine_passed == "slow":
            engines.append(slow_engine.mgr)

    engine_threads = []

    for engine_mgr in engines:
        engine_threads.append(Thread(target=engine_mgr, args=(emit_q,)))

    for engine_thread in engine_threads:
        engine_thread.start()


if __name__ == "__main__":
    main()
