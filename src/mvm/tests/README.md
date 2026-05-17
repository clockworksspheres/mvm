README for testing

CI/CD

Currently running Jenkins, and testing per OS family at a time.
 Wrote the [mvm](https://github.com/clockworksspheres/mvm.git) 
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

# Unit testing mvm tools

Tests written to exercise the support libraries - the main tools are 
primarily command line interfaces to the libraries in the mvm
directory.

## Pylint related

Files:

```
PylintIface.py
test_with_pylint.py
test_PylintIface.py
```

harness for running pylint on all the project python files
to expose pylint Error and Failure messages via a python
unittest.

# References:


