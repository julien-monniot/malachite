""" Graph node.

    Contains a single appliance, coordinates and a uid for a simpler list of
    edges. The logic behind node vs appliance is to keep all network data (as
    in L3 connections, routing, pbr...) inside the appliance object, and put
    all graph data (coordinates, etc) inside the node (which also holds an
    appliance).
    Edges are then only aware of nodes, but allow for indirect access to i
    appliances
"""


class Node:
    """ A node of the final 3D graph.
    """

    def __init__(self, uid, appliance):
        self.uid = uid
        self.x_coord = 0
        self.y_coord = 0
        self.z_coord = 0
        self.appliance = appliance

    def __repr__(self):
        """Short desc"""
        short_desc = "node n°%s (%s) (coords: %s; %s; %s)" % (
            self.uid,
            self.appliance.name,
            self.x_coord,
            self.y_coord,
            self.z_coord,
        )

        return short_desc

    def __str__(self):
        """Node test representation"""
        desc = "# NODE n°%s\n" % self.uid
        desc += "With coordinates [%s; %s; %s]\n" % (
            self.x_coord,
            self.y_coord,
            self.z_coord,
        )
        desc += "Wrapping appliance %s" % self.appliance

        return desc
