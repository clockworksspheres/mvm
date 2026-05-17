import inspect
from mvm.lib.loggers import CyLogger
from mvm.lib.loggers import LogPriority as lp


class MethodNotImplementedError(Exception):
    '''Meant for being thrown in the template, for when a class that
    inherits ServiceHelperTemplate does not implement a method, this

    '''
    def __init__(self, *args, **kwargs):
        super(MethodNotImplementedError, self).__init__(self, *args, **kwargs)


class ManageVirtualMachinesTemplate:

    def __init__(self, **kwargs):
        """
        """
        self.logger = CyLogger()
        self.logger.initializeLogs()

        self.logger.log(lp.ERROR, f"Initializing {self.__class__.__name__} class")

    def __calledBy(self):
        """
        Log the caller of the method that calls this method

        """
        try:
            filename = inspect.stack()[2][1]
            functionName = str(inspect.stack()[2][3])
            lineNumber = str(inspect.stack()[2][2])
        except Exception as err:
            raise err
        else:
            self.logger.log(lp.DEBUG, "called by: " + \
                            filename + ": " + \
                            functionName + " (" + \
                            lineNumber + ")")

    def list_vms(self):
        """
           
        """
        self.logger.log(lp.INFO,
                        f"--{self.__class__.__name__} not yet in production.")
        self.__calledBy()
        raise MethodNotImplementedError

    def start_vm(self, vm: str = "", headless: bool = False):
        """
         Start a virtual machine

        """
        self.logger.log(lp.INFO,
                        f"--{self.__class__.__name__} not yet in production.")
        self.__calledBy()
        raise MethodNotImplementedError

    def stop_vm(self, vm: str = "", hard: bool = True):
        """
         Stop a virtual machine
        """
        self.logger.log(lp.INFO,
                        f"--{self.__class__.__name__} not yet in production.")
        self.__calledBy()
        raise MethodNotImplementedError

    def pause_vm(self, vm: str = ""):
        """
         
        """
        self.logger.log(lp.INFO,
                        f"--{self.__class__.__name__} not yet in production.")
        self.__calledBy()
        raise MethodNotImplementedError

    def unpause_vm(self, vm: str = ""):
        """
         
        """
        self.logger.log(lp.INFO,
                        f"--{self.__class__.__name__} not yet in production.")
        self.__calledBy()
        raise MethodNotImplementedError

    def reset_vm(self, vm: str = "", hard: bool = True):
        """
         
        """
        self.logger.log(lp.INFO,
                        f"--{self.__class__.__name__} not yet in production.")
        self.__calledBy()
        raise MethodNotImplementedError

    def get_vm_status(self, vm: str):
        """
         
        """
        self.logger.log(lp.INFO,
                        f"--{self.__class__.__name__} not yet in production.")
        self.__calledBy()
        raise MethodNotImplementedError

    def get_ip(self, vm: str = ""):
        """
         
        """
        self.logger.log(lp.INFO,
                        f"--{self.__class__.__name__} not yet in production.")
        self.__calledBy()
        raise MethodNotImplementedError


