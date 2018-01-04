"""

    Malachite custom exceptions.

"""


class MalachiteException(Exception):
    """Top-level custom exception"""

    def __init__(self, *args):
        super().__init__(self, *args)


class ErrInvalidDriver(MalachiteException):
    """Invalid driver name passed to napalm"""
    pass


class ErrConnectionFailed(MalachiteException):
    """Napalm was unable to connect to a given appliance"""
    pass


class ErrNotImplemented(MalachiteException):
    """Planned feature not yet available"""
    pass


class ErrLoadingFailed(MalachiteException):
    """Appliance file loading failed at some point"""
    pass


class ErrNodesNotLoaded(MalachiteException):
    """Asking to compute something from nodes, but node list is empty"""
    pass


class ErrRedefinedIP(MalachiteException):
    """Multiple nodes claim to have the same IP"""
    pass
