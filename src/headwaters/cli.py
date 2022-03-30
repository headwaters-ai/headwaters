""" cli.py is the main entry point for the app and the top level """

import click
import logging
import time

logging.basicConfig(level=logging.ERROR)
from colorama import Fore, Back, Style

from . import server

# TODO need to be very clear in docs how to pass a list to the cli
# i have forgotten right now and can't start multiple
# hw -e fast -e slow etc...
@click.command()
@click.option(
    "--domains",
    "-d",
    default=["fruits"],
    multiple=True,
    help="specify the domain(s) for the server, with each domain preceded by a -d",
)
def main(domains: str) -> None:

    logging.info('server started')

    
    print()
    time.sleep(0.2)
    print(Fore.BLUE + Style.BRIGHT + "Headwaters:" + Style.NORMAL+ " Simple Stream Sources" + Style.RESET_ALL)
    time.sleep(0.3)
    print()
    server.run(domains)

if __name__ == "__main__":
    main()
