""" Appliance model.

    Represents a node in the network graph, and may hold additional details
    about each appliance, either for graph display or data enrichment with
    Napalm.
"""

from ipaddress import ip_address
from collections import OrderedDict
from malachite.utils.exceptions import ErrInvalidDriver


class Appliance:
    """ Each L3 node of the graph is a network Appliance.
    """

    def __init__(self, fqdn, driver):

        # Appliance fqdn - node label
        self.fqdn = fqdn

        # Napalm settings
        self.driver = ErrInvalidDriver
        self.port = 0

        # List of IP addresses configured on appliance and ip arp table
        self.ip_local = OrderedDict()
        self.ip_arp_table = {}

    def has_ip(self, ip_addr):
        """ Check if ip_addr is in the ip_local dict

            :params ipaddress ip_addr: The IP to test against.
            :return: True if IP exists in appliance, False otherwise.
            :rtype: bool
        """

        assert(isinstance(ip_addr, ip_address))

        if ip_addr in self.ip_local:
            return True
        return False

    def get_local_ips(self):
        """ Return list of local addresses.

        """
        return list(self.ip_local.keys())
