import unittest
from vmm.VirtualMachineManageTemplate import (
    VirtualMachineManageTemplate,
    MethodNotImplementedError,
)


class DummyTemplate(VirtualMachineManageTemplate):
    """
    A concrete subclass that does not override the abstract methods.

    This lets us test that the base class raises MethodNotImplementedError.
    """
    pass


class TestVirtualMachineManageTemplate(unittest.TestCase):

    def setUp(self):
        # Use a dummy subclass so __init__ still runs
        self.template = DummyTemplate()

    def test_list_vms_raises(self):
        with self.assertRaises(MethodNotImplementedError):
            self.template.list_vms()

    def test_start_vm_raises(self):
        with self.assertRaises(MethodNotImplementedError):
            self.template.start_vm("vm1", headless=True)

    def test_stop_vm_raises(self):
        with self.assertRaises(MethodNotImplementedError):
            self.template.stop_vm("vm2", hard=False)

    def test_pause_vm_raises(self):
        with self.assertRaises(MethodNotImplementedError):
            self.template.pause_vm("vm3")

    def test_unpause_vm_raises(self):
        with self.assertRaises(MethodNotImplementedError):
            self.template.unpause_vm("vm4")

    def test_reset_vm_raises(self):
        with self.assertRaises(MethodNotImplementedError):
            self.template.reset_vm("vm5", hard=True)

    def test_get_vm_status_raises(self):
        with self.assertRaises(MethodNotImplementedError):
            self.template.get_vm_status("vm6")

    def test_get_ip_raises(self):
        with self.assertRaises(MethodNotImplementedError):
            self.template.get_ip("vm7")


if __name__ == "__main__":
    unittest.main()

