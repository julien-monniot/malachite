"""
Malachite main algorithm
"""

from malachite.loader import Loader
from malachite.utils.config import CONFIG
from malachite.utils.exceptions import ErrLoadingFailed


class Malachite:
    """ Malachite lib entry point.
    """


    def __init__(self):
        """Create a few empty objects that will be initialized later."""

        # Malachite loader
        self.loader = None


    def load_appliances(self, config_file=None):
        """Load appliance file, establish connections and fetch add. data"""

        self.loader = Loader()

        config = config_file if config_file else CONFIG['default']['config_file']

        loader.load(config)

    def load_edges():
        """"""

    def generate_graph(self):
        """ Turn the data contained in our models into an igraph,
            ready for drawing
        """
        pass


    def draw_graph(self):
        """Draw 3D graph with plotly"""
        pass
