""" Malachite main algorithm

    Still in a messed up state (CLI has to know the algorithm)
    but not for long.
"""

from malachite.loader import Loader
from malachite.plotly_helper import PlotlyHelper
from malachite.utils.config import CONFIG
from malachite.utils.exceptions import ErrNodesNotLoaded


class Malachite:
    """ Malachite lib entry point.
        Basically wraps Loader and templates graph creation.
    """

    def __init__(self, config_file=None, app_file=None, graph_file=None):
        """Create a few empty objects that will be initialized later."""

        # Malachite loader
        self.loader = None

        # TODO : Incorrect but just a reminder that we want to handle custom
        # config file some day.
        self.config = config_file

        self.graph_file = graph_file

        if app_file:
            self.appliances_file = app_file
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

    def plot(self):
        """Draw 3D graph with plotly"""

        # Init with main node list (our appliances)
        plotlyhelper = PlotlyHelper(self.loader.nodes)

        # Add edges as a new scatter
        plotlyhelper.build_edge_scatter(
            self.loader.edges,
            "L3 direct connections",
        )

        # Plot graph (node scatter + any edge scatter added before this call)
        if not self.graph_file:
            self.graph_file = self.config['default']['graph_file']
        plotlyhelper.plot(self.graph_file)

    def algorithm(self):
        """ Full plotting algorithm
        """
        # TODO: yield status/objects __str__ after completion of each step so
        # that CLI can use this function directly instead of calling every
        # sub functions.
        self.load_appliances()
        self.load_edges()
        self.build_coordinates()
        self.plot()
