import libvirt
import sys

def get_guest_ips(vm_name):
    try:
        # Open a connection to the system QEMU daemon
        conn = libvirt.open("qemu:///system")
        if conn is None:
            print("Failed to open connection to qemu:///system")
            return

        # Locate the virtual machine by name
        dom = conn.lookupByName(vm_name)
        
        # Use the Guest Agent as the source (equivalent to --source agent)
        source = libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT
        
        # Alternatively, use DHCP leases if the agent isn't available:
        # source = libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE

        # Fetch the interface dictionary
        interfaces = dom.interfaceAddresses(source)
        
        if not interfaces:
            print(f"No interface data returned for {vm_name}. Is the guest agent running?")
            return

        # Parse and print out the interfaces and their IP addresses
        for name, info in interfaces.items():
            print(f"Interface: {name}")
            print(f"  MAC Address: {info['hwaddr']}")
            if info['addrs']:
                for addr in info['addrs']:
                    ip_type = "IPv4" if addr['type'] == libvirt.VIR_IP_ADDR_TYPE_IPV4 else "IPv6"
                    print(f"  {ip_type} Address: {addr['addr']}/{addr['prefix']}")
            else:
                print("  No IP configuration found.")
                
    except libvirt.libvirtError as e:
        print(f"Libvirt error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    # Replace with 'debian13' or your exact VM name
    get_guest_ips("debian13")


