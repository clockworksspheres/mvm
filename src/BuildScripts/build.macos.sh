#!/bin/bash

# highly modified version of:
# https://www.pythonguis.com/tutorials/packaging-pyside6-applications-pyinstaller-macos-dmg/
# amoung others... including
# https://pyinstaller.org/en/stable/

pushd ..

#if doesn't the packenv directory doesn't exist...
directory="./projEnv"
actfile="./projEnv/bin/activate"
if [ ! -d "$directory" ]  || [ ! -f "$actfile" ] ; then
   python3 -m venv $directory
   source $actfile

   pip install --upgrade pip
   pip install -r requirements.txt

else
   source $actfile
fi

cp BuildScripts/build.macos.spec mvm

pushd mvm

pyinstaller --clean -y build.macos.spec
pyinstaller -y build.macos.spec

rm build.macos.spec

popd
popd


