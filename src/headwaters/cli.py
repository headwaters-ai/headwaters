""" this will invoke things """

from .serverA import run
from . import serverB
from .serverC import serverC

import click

@click.command()
@click.option('--server', default='A', help='specify the server, A B or C')
@click.argument('start')
def main(server: str, start: str ) -> None:
    if server == 'A':
        run()
    elif server == 'B':
        serverB.run()
    elif server == 'C':
        serverC.run()
    else:
        raise ValueError(f"server name passed was {server} and this was not recognised")

if __name__ == "__main__":
    main()
