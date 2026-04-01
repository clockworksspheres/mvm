README for testing

CI/CD

Currently running Jenkins, and testing per OS family at a time.
 Wrote the [vmm](https://github.com/clockworksspheres/vmm.git) 
program and [jenkinsTools](https://github.com/clockworksspheres/jenkinsTools.git)
tools to assist in automation of CI/CT.  Currently building
app/executables with PyInstaller.

Still need to create installer builds for project across operating
systems, to get the CD part going.  Jenkins server currently running
in a container.

Skipped tests are not necessarily bad, they just are not applicable to the
operating system they are being run on.

Need to add linux tests for vmware workstation and oracle virtualbox -
should be pretty simple once I can get on a linux box... May set up
hyperv in a way I can do nested virtualization to do this type of
testing as I don't have direct access to a linux box.


