""" CLI entrypoint for malachite
"""

import click
# from malachite.malachite import main


@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True)
def cli(version):
    """Entrypoint"""
    click.secho("## Malachite - CLI ##", fg='white', bg='green', bold=True)
    if version:
        click.secho("     Version 0.1.0", bold=True)


@cli.command()
@click.option('--text-output', 'text_output', is_flag=True)
def graph(text_output):
    """ Generate graph.

    """

    if text_output:
        click.echo("## Printing edges and nodes...")
    else:
        click.echo("## Drawing graph")
