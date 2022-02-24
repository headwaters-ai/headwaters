""" cli.py is the main entry point for the app and the top level """

import click

from . import server


@click.command()
@click.option(
    "--domains",
    "-d",
    default=["timeseries"],
    multiple=True,
    help="specify the domain(s) for the server, with each domain preceded by a -d",
)

# TODO need to be very clear in docs how to pass a list to the cli
# i have forgotten right now and can't start multiple
# hw -e fast -e slow etc...


def main(domains: str) -> None:

    server.run(domains)


if __name__ == "__main__":
    main()
