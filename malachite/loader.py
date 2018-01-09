""" Load appliance list, enrich our data with napalm and get everything
    ploty-ready !
"""

import yaml

from ipaddress import ip_address

from malachite.models.appliance import Appliance
from malachite.models.link import Link

from malachite.utils.config import CONFIG
from malachite.utils.exceptions import ErrLoadingFailed
from malachite.utils.exceptions import ErrInvalidDriver
from malachite.utils.exceptions import ErrNodesNotLoaded
from malachite.utils.exceptions import ErrRedefinedIP
from malachite.napalm_collector import NapalmMiddleware


class Loader:

    def __init__(self):
        self.nodes = []
        self.edges = []
        self.missing_neighbor = []
        self.middlewares = {}

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

            self.nodes.append(new_appliance)

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

        for node in self.nodes:

            try:
                n_middleware = self._get_middleware(node.driver)
            except ErrInvalidDriver:
                raise ErrInvalidDriver('%s is not a valid driver name (%s)',
                                       node.driver, node.fqdn)

            # Specific connection info (port,..) are stored in the node
            n_middleware.connect(
                appliance=node,
                username=CONFIG['default']['username'],
                password=CONFIG['default']['password'])

            # ARP table at current time
            arp_table = n_middleware.get_arp_table(device_name=node.fqdn)
            node.ip_arp_table = {
                entry['interface']: ip_address(entry['ip']) for entry in arp_table
            }

            # Ip address locally set
            ip_addresses = n_middleware.get_interfaces_ip(
                device_name=node.fqdn
            )
            for interface, entry_data in ip_addresses.items():
                ipv4 = entry_data['ipv4']
                for ip in ipv4.keys():
                    node.ip_local[ip_address(ip)] = interface

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

    def load_edges(self):
        """ After loading every node, create every possible direct link between them.
            This steps makes use of the arp table and local ips of each node.
        """

        if not self.nodes:
            raise ErrNodesNotLoaded

        # Loop on every node
        for node in self.nodes:

            # For each node, look-up its arp table
            for eth, ip in node.ip_arp_table.items():

                # We don't want to graph management links for now.
                if 'Management' not in eth:

                    # find dest in nodes
                    dest = [dnode for dnode in self.nodes if node.has_ip(ip)
                            and dnode != node]

                    if len(dest) > 1:
                        raise ErrRedefinedIP

                    if not dest:
                        # debug
                        print("No matching ip found for %s" % ip)
                        self.missing_neighbor.append((node, ip))
                    else:
                        new_link = Link(node, dest[0])
                        self.edges.append(new_link)
