""" Edge model.

    Represents and edge in the network graph.
    The edge has a source and destination points, but may be used as
    birdirectional.
"""


class Edge:
    """ Edge between two nodes.
        It can be directed, although the most basic usage
        (L3 relations graph using ip/arp table) doesn't require it)
    """

    def __init__(self, source, destination):
        self.source = source
        self.destination = destination
        self.bidirectionnal = False

    def to_indexes(self):
        """ Return plotly friendly representation of edge,
            using source and dest nodes index.
        """
        return (self.source.uid, self.destination.uid)

    def __str__(self):
        """Edge description"""

        desc = "EDGE FROM %s <- TO -> %s" % (
            self.source.__repr__(),
            self.destination.__repr__()
        )
        return desc

    def __repr__(self):
        """Short description"""

        desc = "Edge from %s to %s" % (
            self.source.__repr__(),
            self.destination.__repr__()
        )
        return desc
