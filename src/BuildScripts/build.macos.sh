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
   python3 -m venv packenv
   source packenv/bin/activate

   pip install --upgrade pip
   pip install astroid
   pip install PyInstaller
   pip install pyside6
   pip install psutil
   pip install packaging
   pip install pylint
   pip install pytest
else
   source packenv/bin/activate
fi

cp BuildScripts/build.macos.spec mvm

pushd mvm

pyinstaller --clean -y build.macos.spec
pyinstaller -y build.macos.spec

rm build.macos.spec

popd
popd


