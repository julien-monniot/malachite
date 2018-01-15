""" Malachite main algorithm
"""

from malachite.loader import Loader
from malachite.plotly_helper import PlotlyHelper
from malachite.utils.config import CONFIG
from malachite.utils.exceptions import ErrNodesNotLoaded


class Malachite:
    """ Malachite lib entry point.
        Basically wraps Loader and templates graph creation.
    """

    def __init__(self, config_file=None, appliances_file=None):
        """Create a few empty objects that will be initialized later."""

        # Malachite loader
        self.loader = None

        # TODO : Incorrect but just a reminder that we want to handle custom
        # config file some day.
        self.config = config_file

        if appliances_file:
            self.appliances_file = appliances_file
        else:
            self.appliances_file = CONFIG['default']['appliances_file']

    def load_appliances(self):
        """Load appliance file, establish connections and fetch add. data"""

        self.loader = Loader()
        self.loader.load_nodes(self.appliances_file)

    def load_edges(self):
        """Tell the loader to build and store edge list from node list"""

        if not self.loader:
            raise ErrNodesNotLoaded

        self.loader.build_edges()

    def build_coordinates(self):
        """Set node coordinates from igraph"""
        self.loader.build_coordinates()

    def plot(self, filename="graph.html"):
        """Draw 3D graph with plotly"""

        # Init with main node list (our appliances)
        plotlyhelper = PlotlyHelper(self.loader.nodes)

        # Add edges as a new scatter
        plotlyhelper.build_edge_scatter(
            self.loader.edges,
            "L3 direct connections",
        )

        # Plot graph (node scatter + any edge scatter added before this call)
        plotlyhelper.plot(filename)
