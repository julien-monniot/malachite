"""
    Napalm based link and requests to appliances.
"""

from napalm import get_network_driver
from napalm.base.exceptions import ModuleImportError, ConnectionException

from malachite.exceptions import ErrInvalidDriver, ErrConnectionFailed, ErrNotImplemented


class NapalmMiddleware:

    def __init__(self, net_os):

        # Set self.driver or raise ErrInvalidDriver
        try:
            self.driver = get_network_driver(net_os)
        except ModuleImportError:
            raise ErrInvalidDriver()

        # Dict of connected (reachable) devices (appliance name/addr ; device)
        self.devices = {}

    def _open_connection(self, appliance, login=None):
        """Open conenction to a device"""

        assert(isinstance(appliance, malachite.model.Appliance))

        # Set optional arguments if needed :
        opt_args = {}
        if appliance.port:
            opt_args['port'] = appliance.port

        # Login is a tuple username/password:
        if login:
            username = login[0]
            password = login[1]
        else:
            raise ErrNotImplemented('Login field must be non-empty')

        # Create napalm device
        device = self.driver(
            hostname=appliance.fqdn,
            username=username,
            password=password,
            optional_args=opt_args
        )

        # Try to open the connection
        try:
            device.open()
        except ConnectionException:
            raise ErrConnectionFailed('Appliance %s', appliance.fqdn)

        # If everything went well up to that point, keep device
        self.devices[appliance.fqdn] = device

    def _close_connection(self, device_fqdn):
        """Close connection to a device"""

        if device_fqdn in self.devices:
            self.devices[device_fqdn].close()
            return True
        return False

    def connect(self, *, appliance, username, password):
        """ Connect to every appliances known to the middleware, and
            return list (hopefully empty if everything goes right) of
            nodes to which the connection was not possible.

            Note : for now, we assume that all appliances are configured
            so that a single username/password fits all.
            This behaviour might be altered later.

            :params str username: Appliance username
            :params str password: Appliance password
            :return: List of appliances to which the connection failed.
            :rtype: list()
        """

        broken_connections = []

        try:
            self._open_connection(appliance, (username, password))
        except ErrConnectionFailed:
            broken_connections.append(appliance.fqdn)

        return broken_connections

    def disconnect(self, *, device=None):
        """Close connection to a specific device or all if none is specified"""

        if device:
            return self._close_connection(device)
        else:
            for device in self.devices:
                self._close_connection(device)

    def get_arp_table(self, vrf=None, device_name=None):
        """ Get arp table for a single device or all of them is device=None
        """

        if vrf:
            raise ErrNotImplemented('VRF table is not in use currently.')

        arp_tables = {}

        if device_name and device_name in self.devices:
            arp_table[device_name] = self.devices[device_name].get_arp_table()
            return arp_tables

        for name, device in self.devices.items():
            arp_table[name] = device.get_arp_table()

        return arp_tables

    def get_interfaces_ip(self, device_name=None):
        """ Get every interfaces IP
        """
        interfaces_ip = {}

        if device_name and device_name in self.devices:
            interfaces_ip[device_name] = self.devices[device_name].get_interfaces_ip()

        for name, device in devices.items():
            interfaces_ip[name] = device[name].get_interfaces_ip()

        return interfaces_ip
