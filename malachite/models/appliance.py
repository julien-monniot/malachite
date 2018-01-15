""" Appliance model.

    Holds data from a specific appliance in the network.
    In order to be displayed in a 3D graph, it must first
    be encapsulated into a Node object.
"""

# from ipaddress import ip_address
from collections import OrderedDict
# from malachite.utils.exceptions import ErrInvalidDriver


class Appliance:
    """ Holds data extracted from a single network appliance
        (routing table, local ip defined on any interface,
        arp table, etc)
    """

    def __init__(self, fqdn, driver, name=None):

        # Appliance fqdn - can be used as node label
        self.fqdn = fqdn
        # Appliance common name - default node label
        # especially if an ip addr is used instead of fqdn.
        self.name = name if name else self.fqdn

        # Napalm settings
        self.driver = driver
        self.port = 0  # set manually if needed, after object creation

        # List of IP addresses configured on appliance and ip arp table
        self.ip_local = OrderedDict()
        self.ip_arp_table = {}

    def __repr__(self):
        """Simple representation"""
        short_desc = "Appliance %s, %s ip on eth and %s arp entries" % (
            self.fqdn,
            len(self.ip_local),
            len(self.ip_arp_table)
        )
        return short_desc

    def __str__(self):
        """Appliance text representation"""

        if self.name != self.fqdn:
            desc = "Appliance %s (%s) : " % (self.name, self.fqdn,)
        else:
            desc = "Appliance %s : " % (self.fqdn,)

        desc += "\n - driver : %s" % (self.driver,)
        desc += "\n - port : %s" % ('NA' if not self.port else self.port)
        desc += "\n - local ips :"
        desc += '\n   - '
        desc += '\n   - '.join(
            ["%s <-> %s" % (ip, ifname)
             for ip, ifname in self.ip_local.items()]
        )
        desc += "\n - arp table :"
        desc += '\n   - '
        desc += '\n   - '.join(
            ["%s <-> %s" % (ifname, ip)
             for ifname, ip in self.ip_arp_table.items()]
        )
        return desc

    def has_ip(self, ip_addr):
        """ Check if ip_addr is in the ip_local dict

            :params ipaddress ip_addr: The IP to test against.
            :return: True if IP exists in appliance, False otherwise.
            :rtype: bool
        """
        if ip_addr in self.ip_local:
            return self.ip_local[ip_addr]
        return None

    def get_local_ips(self):
        """ Return list of local addresses.

        """
        return list(self.ip_local.keys())
