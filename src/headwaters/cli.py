""" cli.py is the main entry point for the app and the top level """

import click
import logging
import time

from colorama import Fore, Back, Style

from . import server
logging.basicConfig(filename='hw.log', force=True, encoding='utf-8', level=logging.DEBUG)

# TODO need to be very clear in docs how to pass a list to the cli
# i have forgotten right now and can't start multiple
# hw -e fast -e slow etc...
@click.command()
@click.option(
    "--sources",
    "-s",
    default=["fruits"],
    multiple=True,
    help="specify the sources(s) for the stream(s), with each source preceded by a -s",
)
def main(sources: str) -> None:

    logging.info('server started')

    
    print()
    time.sleep(0.2)
    print(Fore.BLUE + Style.BRIGHT + "Headwaters:" + Style.NORMAL+ " Simple Stream Sources" + Style.RESET_ALL)
    time.sleep(0.3)
    print()
    server.run(sources)

if __name__ == "__main__":
    main()
