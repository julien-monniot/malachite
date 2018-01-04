""" CLI entrypoint for malachite
"""

import click
# from malachite.malachite import main


@click.group(invoke_without_command=True)
@click.version_option()
@click.option('--config', type=click.Path(exists=True, readable=True))
def cli(config):
    """Entrypoint"""
    click.secho("## Malachite - CLI ##", fg='white', bg='green', bold=True)


@cli.command()
@click.option('--text-output', 'text_output', is_flag=True)
@click.argument('appliances', type=click.Path(exists=True, readable=True))
def graph(text_output, appliances):
    """ Generate graph.
    """

    click.secho('Using appliances file %s' % appliances)

    if text_output:
        click.echo("Printing edges and nodes...")
    else:
        click.echo("Drawing graph")
