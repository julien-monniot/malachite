""" CLI entrypoint for malachite
"""

import click
from malachite.malachite import Malachite


@click.group(invoke_without_command=True)
@click.version_option()
@click.option('--config', type=click.Path(exists=True, readable=True))
def cli(config):
    """Entrypoint"""
    click.secho("## Malachite - CLI ##", fg='green', bg='black', bold=True)


@cli.command()
@click.option('--text-output', 'text_output', is_flag=True)
@click.option('--conf', default=None)
@click.argument('appliances', type=click.Path(exists=True, readable=True))
def graph(text_output, appliances, conf):
    """ Generate graph.
    """

    click.secho('# Using appliances file %s' % appliances, fg='green')
    malachite = Malachite(appliances_file=appliances)

    if conf:
        click.secho('# Using custom config file %s' % conf, fg='green')
    else:
        click.secho('# Using default (built-in) config', fg='green')

    click.secho('-- Loading appliances nodes...', fg='green')
    malachite.load_appliances()
    for node in malachite.loader.nodes:
        click.secho("%s" % node, fg='white')

    click.secho('-- Building appliances edges...', fg='green')
    malachite.load_edges()
    print("edges : %s" % malachite.loader.edges)
    for edge in malachite.loader.edges:
        click.secho("%s" % edge, fg='white')

    click.secho('-- Generating iGraph...', fg='green')
    # malachite.generate_graph()

    if text_output:
        click.echo("Printing edges and nodes...")
    else:
        click.echo("Drawing graph")
