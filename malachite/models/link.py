""" Link model.

    Represents and edge in the network graph.
    The edge has a source and destination points, but may be used as
    birdirectional.
"""


class Link:
    """ Edge between two nodes.
        It can be directed, although the most basic usage
        (L3 relations graph using ip/arp table) doesn't require it)
    """

    def __init__(self, source, destination):
        self.source = source
        self.destination = destination
        self.bidirectionnal = False

    def __str__(self):
        """Edge description"""

        desc = "Link from %s to %s" % (
            self.source.name,
            self.destination.name
        )

        return desc
