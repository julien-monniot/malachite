""" Messy mix of temorary nodes/edges storage and functions for
    creating those objects.

    It exposes three steps of the graphing process:
    -   load_nodes : reads from a list of appliances and gather data about them
        (from config files and with the help of Napalm). This is the step
        responsible for both 'appliances' AND 'nodes' creation, although nodes
        are not ready for use rigth away. Each node encapsulates a single
        appliance.
    -   build_edges : uses data from appliances in order to define the link
        between them. Those links are stored as "Edge"(s) objects, which
        refer to a source and a destination 'node' object.
    -   use iGraph in order to generate a fitting layout for our set of edges.
        Coordinates of each node are stored in the corresponding 'node' object.

    These three steps must be invoked in that order before plotting.

    Maybe this class does too much things, but for now, it seems useless to
    decouple its tasks.
"""

import yaml

import igraph as ig
from ipaddress import ip_address

from malachite.models.appliance import Appliance
from malachite.models.node import Node
from malachite.models.edge import Edge

from malachite.napalm_collector import NapalmMiddleware

from malachite.utils.config import CONFIG
from malachite.utils.exceptions import (
    ErrLoadingFailed,
    ErrInvalidDriver,
    ErrNodesNotLoaded,
    ErrRedefinedIP
)


class Loader:

    def __init__(self):
        """ Init loader class.
            Currently, it acts as a temporary storage class
            for every objects needed during the graphin process
            (nodes, edges, igraph and layout, etc).
            In further devs, it might rely on some DB middleware
            for added persistence.
        """
        # List of network appliances (containing data gathered with Napalm)
        self.appliances = []

        # Unique node id, will become useless with db
        self.node_uid = 0

        # List of graph nodes (coordinates, uid...)
        self.nodes = []

        # List of computed edges, each one refs 2 nodes
        self.edges = []

        self.missing_neighbor = []  # See 'build_edges'

        # napalm middlewares (see how napalm_collector works for more details.
        self.middlewares = {}

    def _get_uid(self):
        """ Return next available uid (which is basically a node counter)
            and increment the value for next call.

            :return: First available UID value.
            :rtype: int
        """
        ret = self.node_uid
        self.node_uid += 1
        return ret

    def _get_middleware(self, driver):
        """ Return a local Napalm middleware or create one
            for given driver, if necessary.

            :params str driver: Name of the Napalm driver needed.
            :return: Napalm middleware configured with correct driver.
            :rtype: napalm.driver
        """
        if driver in self.middlewares:
            return self.middlewares[driver]
        else:
            new_middleware = NapalmMiddleware(driver)
            self.middlewares[driver] = new_middleware
            return new_middleware

    def _build_appliances(self, yaml_appliances):
        """ Populate internal appliance list from yaml file.
            They will be completed later with data obtained from Napalm.
            In the same fashion, alos create nodes that encapsulate every
            appliance, and will also be completed later.

            :params dict yaml_appliances: List of appliances read from a
                                          yaml file.
        """
        for appliance in yaml_appliances:
            new_appliance = Appliance(
                appliance['fqdn'],
                appliance['driver'],
                appliance['name']
            )

            if 'port' in appliance:
                new_appliance.port = appliance['port']

            self.appliances.append(new_appliance)
            self.nodes.append(Node(self._get_uid(), new_appliance))

    def _napalm_enrich(self):
        """ Enrich appliance data with napalm

            Currently :
            - get arp table
            - get locally set up IPv4 (from every routed int)
        """
        for appliance in self.appliances:

            try:
                n_middleware = self._get_middleware(appliance.driver)
            except ErrInvalidDriver:
                raise ErrInvalidDriver('%s is not a valid driver name (%s)',
                                       appliance.driver, appliance.fqdn)

            # Specific connection info (port,..) are stored in the node
            n_middleware.connect(
                appliance=appliance,
                username=CONFIG['default']['username'],
                password=CONFIG['default']['password'])

            # ARP table at current time
            arp_table = n_middleware.get_arp_table(device_name=appliance.fqdn)
            appliance.ip_arp_table = {
                entry['interface']: ip_address(entry['ip'])
                for entry in arp_table
            }

            # Ip address locally set
            ip_addresses = n_middleware.get_interfaces_ip(
                device_name=appliance.fqdn
            )
            for interface, entry_data in ip_addresses.items():
                ipv4 = entry_data['ipv4']
                for ip in ipv4.keys():
                    appliance.ip_local[ip_address(ip)] = interface

    def load_nodes(self, node_file):
        """ Load appliances from file, build corresponding nodes
            and gather additional data using a NapalmMiddleware.

            :params str node_file: Filename of yaml containing the
                                   appliance list
        """
        try:
            with open(node_file, 'r') as n_file:
                appliances = yaml.load(n_file)
        except FileNotFoundError:
            raise ErrLoadingFailed('File %s not found' % node_file)
        else:
            self._build_appliances(appliances)

        self._napalm_enrich()

    def build_edges(self):
        """ After loading every appliance/node, create every possible direct
            link between them (making use of the arp table and local IPv4 of
            each appliance)
        """
        if not self.nodes:
            raise ErrNodesNotLoaded(
                'Call "load_nodes()" or make sure appliance file is not empty'
            )

        for node in self.nodes:
            # Shortcut to the appliance inside the node (contains network data)
            app = node.appliance
            for eth, ip in app.ip_arp_table.items():
                # We don't want to graph management links for now
                # TODO: needs to be replaced with a generic regex (Mgt/mgmt/..)
                if 'Management' not in eth:

                    dest = [dnode for dnode in self.nodes
                            if dnode.appliance.has_ip(ip) and dnode != node]

                    if len(dest) > 1:
                        raise ErrRedefinedIP(
                            "Nodes %s all have an IP %s" % (dest, ip)
                        )

                    if not dest:
                        # TODO: we don't use 'missing_neighbors' yet...
                        self.missing_neighbor.append((node, ip))
                    else:
                        self.edges.append(Edge(node, dest[0]))

    def build_coordinates(self):
        """ Compute a layout of coordinates using igraph and set each node
            coordinates.

            Edges don't get to have any more processing yet : the
            plotly-specific coordinates are computed in PlotlyHelper
            when needed (so far, we have only one set of nodes and
            on set of edges, but later on, we may have multiple
            sets of edges
        """

        # Create a list of tuples with node indexes instead of the
        # full objects (so that we can feed it to iGraph)
        edge_idx = [
            e.to_indexes()
            for e in self.edges
        ]

        igraph = ig.Graph(edge_idx, directed=False)
        layout = igraph.layout('kk', dim=3)

        for idx, coord in enumerate(layout):
            self.nodes[idx].x_coord = coord[0]
            self.nodes[idx].y_coord = coord[1]
            self.nodes[idx].z_coord = coord[2]
