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
