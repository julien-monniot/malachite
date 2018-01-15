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
@click.option('-o', '--output', 'output_file')
@click.option('-c', '--conf', default=None)
@click.option('-v', '--verbose', is_flag=True)
@click.argument('appliances', type=click.Path(exists=True, readable=True))
def graph(output_file, appliances, conf, verbose):
    """ Generate graph.
    """

    # Malachite init with correct appliance file.
    click.secho('# Using appliances file %s' % appliances, fg='green')
    malachite = Malachite(appliances_file=appliances)

    # Use custom configuration file  or built-in
    conf_file = conf if conf else 'default'
    click.secho('# Using config file : %s' % conf_file, fg='green')

    # Loading nodes from appliance file and napalm
    click.secho('-- Loading appliances nodes...', fg='green')
    malachite.load_appliances()
    if verbose:
        [click.secho("%s" % n, fg='white') for n in malachite.loader.nodes]

    # Building model edges.
    click.secho('-- Building appliances edges...', fg='green')
    malachite.load_edges()

    # Creating igraph and setting nodes coordinates:
    click.secho(
        '-- Generating layout and setting nodes coordinates',
        fg='green'
    )
    malachite.build_coordinates()
    if verbose:
        click.secho('-- Current state of edges is : ', fg='green')
        [click.secho("%s" % e, fg='white') for e in malachite.loader.edges]

    # Ploting plotly graph
    click.secho('-- Ploting graph...', fg='green')
    malachite.plot(output_file)
