#!/bin/bash

# highly modified version of:
# https://www.pythonguis.com/tutorials/packaging-pyside6-applications-pyinstaller-macos-dmg/
# amoung others... including
# https://pyinstaller.org/en/stable/

pushd ..

#if doesn't the packenv directory doesn't exist...
directory="./packenv"
actfile="./packenv/bin/activate"
if [ ! -d "$directory" ]  || [ ! -f "$actfile" ] ; then
   python -m venv packenv
   source packenv/bin/activate

   pip install --upgrade pip
   pip install PyInstaller
   pip install pyside6
   pip install psutil
   pip install packaging
else
   source packenv/bin/activate
fi

cp BuildScripts/build.macos.spec vmm

pushd vmm

pyinstaller --clean -y build.macos.spec
pyinstaller -y build.macos.spec

rm build.macos.spec

popd
popd


