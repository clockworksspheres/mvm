

class MemoryNotAvailableError(Exception):
    """
    Meant for being thrown when an action/class being run/instanciated is not
    applicable for the running operating system.

    
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class UnsupportedOSError(Exception):
    """
    Meant for being thrown when an action/class being run/instanciated is not
    applicable for the running operating system.

    
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class NotValidForThisOS(Exception):
    """
    Meant for being thrown when an action/class being run/instanciated is not
    applicable for the running operating system.

    
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class NotACyLoggerError(Exception):
    """
    Custom Exception
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class UserMustBeRootError(Exception):
    """
    Custom Exception
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class HypervisorNotApplicable(Exception):
    """
    Custom Exception
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

