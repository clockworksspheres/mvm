# Requirements for python's Libvirt package

# What linux packages need to be installed to be able to install the python libvirt package?

What linux packages need to be installed to be able to install the python libvirt package?

To install the **libvirt-python** package via pip, you must first install system-level development headers and build tools. The specific package names depend on your Linux distribution:

*   **Debian/Ubuntu**: Install `libvirt-dev`, `pkg-config`, `python3-dev` (or `python-dev` for Python 2), `build-essential`, and `autoconf`.
    ```bash
    sudo apt-get install libvirt-dev pkg-config python3-dev build-essential autoconf
    ```
*   **Fedora/RHEL/CentOS**: Install `libvirt-devel`, `pkgconfig`, and `python3-devel`.
    ```bash
    sudo dnf install libvirt-devel pkgconfig python3-devel
    ```
*   **Arch Linux**: The `libvirt` package includes the necessary bindings, or you can install `libvirt-python` directly from the official repositories.

The installation script uses **pkg-config** to locate the `libvirt.pc` file, so ensuring `pkg-config` and the corresponding `-dev` or `-devel` packages are present is critical for success. If you require specific API bindings not included in the default repository version, you may need to compile **libvirt** and **libvirt-python** from source, which requires additional dependencies like `libxml2-dev`, `libnl-3-dev`, and `xsltproc`.