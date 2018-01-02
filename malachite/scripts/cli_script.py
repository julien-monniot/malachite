""" CLI entrypoint for malachite
"""

import click
from malachite.malachite import main


@click.command()
def cli():
    """Entrypoint"""
    click.echo("## Malachite - CLI ##")
    main()
