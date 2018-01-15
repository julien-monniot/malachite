""" Load appliance list, enrich our data with napalm and get everything
    ploty-ready !
"""

import yaml

import igraph as ig
from ipaddress import ip_address

from malachite.models.appliance import Appliance
from malachite.models.node import Node
from malachite.models.edge import Edge

from malachite.utils.config import CONFIG
from malachite.utils.exceptions import ErrLoadingFailed
from malachite.utils.exceptions import ErrInvalidDriver
from malachite.utils.exceptions import ErrNodesNotLoaded
from malachite.utils.exceptions import ErrRedefinedIP
from malachite.napalm_collector import NapalmMiddleware


class Loader:

    def __init__(self):
        """ Init loader class.

            Currently, it acts as a temporary storage class
            for every objects needed during the graphin process
            (nodes, edges, igraph and layout, etc).

            In further devs, it might rely on some DB middleware
            for added persistence.
        """
        self.node_uid = 0       # Unique node id, will become useless with db
        self.appliances = []    # List of network appliances
        self.nodes = []         # List of graph nodes
        self.edges = []         # List of computed edges, each one refs 2 nodes
        self.missing_neighbor = []  # See 'build_edges'
        self.middlewares = {}   # napalm middlewares for != types of appliances

    def _get_uid(self):
        """ Return next available uid (which is basically a node counter)
            and increment the value for next call.
        """
        ret = self.node_uid
        self.node_uid += 1
        return ret

    def _build_nodes(self, yaml_appliances):
        """ Populate internal node list from yaml file
            They will be completed later with data obtained from Napalm.
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

    def _get_middleware(self, driver):
        """ Return a local Napalm middleware or create one
            for given driver, if necessary.
        """

        if driver in self.middlewares:
            return self.middlewares[driver]
        else:
            new_middleware = NapalmMiddleware(driver)
            self.middlewares[driver] = new_middleware
            return new_middleware

    def _napalm_enrich(self):
        """Enrich node data with napalm"""

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
        """Load appliances and enrich their data"""
        # Load YAML file:
        try:
            with open(node_file, 'r') as n_file:
                appliances = yaml.load(n_file)
        except FileNotFoundError:
            raise ErrLoadingFailed('File not found')
        else:
            self._build_nodes(appliances)

        # Fetch additional data with Napalm
        self._napalm_enrich()

    def build_edges(self):
        """ After loading every node, create every possible direct link between them.
            This steps makes use of the arp table and local ips of each node.
        """

        if not self.nodes:
            raise ErrNodesNotLoaded

        # Loop on every node
        for node in self.nodes:

            app = node.appliance

            # For each node, look-up its arp table
            for eth, ip in app.ip_arp_table.items():

                # We don't want to graph management links for now.
                if 'Management' not in eth:

                    # find dest in nodes
                    dest = [dnode
                            for dnode in self.nodes
                            if dnode.appliance.has_ip(ip) and dnode != node]

                    if len(dest) > 1:
                        raise ErrRedefinedIP

                    if not dest:
                        # debug
                        print("No matching ip found for %s" % ip)
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
