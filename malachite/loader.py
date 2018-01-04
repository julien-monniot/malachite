""" Load appliance list, enrich our data with napalm and get everything
    ploty-ready !
"""

import yaml
from malachite.models.appliance import Appliance
from malachite.utils.exceptions import ErrLoadingFailed
from malachite.utils.exceptions import ErrInvalidDriver
from malachite.utils.exceptions import ErrNodesNotLoaded
from malachite.utils.exceptions import ErrRedefinedIPd
from malachite.napalm_collector import NapalmMiddleware


class Loader:

    def __init__(self):
        self.nodes = []
        self.edges = []
        self.middlewares = {}

    def _build_nodes(self, yaml_appliances):
        """ Populate internal node list from yaml file
            They will be completed later with data obtained from Napalm.
        """
        for fqdn, settings in yaml_appliances:
            new_appliance = Appliance(fqdn, settings['driver'])

            if 'port' in settings:
                new_appliance.port = settings['port']

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

            # TODO : replace username and password by parameters/configuration values.
            n_middleware.connect(
                appliance=node,
                username='vagrant',
                password='vagrant')

            arp_table = n_middleware.get_arp_table(device_name=node.fqdn)
            print("ARP Table : %s" % arp_table)
            nodes.ip_arp_table = arp_table

            ip_addresses = n_middleware.get_interfaces_ip(
                device_name=node.fqdn
            )
            print("IP addresses : %s" % ip_addresses)
            node.ip_local = ip_addresses

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
            for entry in node.ip_arp_table:

                eth = entry['interface']
                ip_on_eth = entry['ip']

                # We don't want to graph management links for now.
                if 'Management' not in eth:
                    # find dest in nodes
                    dest = [dnode for dnode in self.nodes if node.has_ip(entry['ip'] and dnode != node)]
                    if len(dest) > 1:
                        raise ErrRedefinedIP

                    new_link = Link(node, dest[0])
                    link.append(new_link)
