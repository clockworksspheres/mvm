# Nested Virtualization

## Operating system Nested Virtualization

### Windows

Unfortunately the only guest OS that can do nested virtualization on Windows, is Windows.  An attempt to perform nested virtualization with a Linux guest OS on a Windows Hyper-V host is not possible.  It would require enabling KVM on the linux guest, and Hyper-V can't pass through hardware virtualization to KVM, which is not possible.

### MacOS

MacOS dosn't provide a nested virtualization option for the M series arm architectures.  This was tested, but not able to provide support for this.  Any version of emulation inside a guest VM inside a guest VM has not yet been attempted.

### Linux

Currently, the project does not have hardware to test KVM as a host for virtualization and/or emulation for testing.

## Emulation

Emulation is a method of simulating hardware via software.  It is used to provide a framework for simulating operating systems in software, rather than virtualizing directly via VT-x/AMD-V.  Tests run via directly leveraging on VT-x hardare virtualization run much faster than Emulation.

Virtualbox has been used to provide emulation of a Linux OS inside a Hyper-V based linux VM.  QEMU is virtualization and emulation software for providing an operating system platform.  Although UTM is based on QEMU as a Type 2 hypervisor, using QEMU hasn't yet been attempted to simulate operating system inside a guest operating system, as Virtualbox has.  QEMU is a cross platform for operating system virtualization and emulation on top of many hardware systems, that provides virtualization and emulation for many hardware systems.

# References

References to support this document will be provide as time is available.

