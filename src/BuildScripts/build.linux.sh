#!/bin/bash

pushd ..

#if doesn't the packenv directory doesn't exist...
directory="./projEnv"
actfile="./projEnv/bin/activate"
if [ ! -d "$directory" ]  || [ ! -f "$actfile" ] ; then
   python -m venv $directory
   source $actfile

   pip install --upgrade pip
   pip install astroid
   pip install PyInstaller
   pip install pyside6
   pip install psutil
   pip install packaging
   pip install pylint
   pip install pytest
else
   source $actfile
fi

cp BuildScripts/build.linux.spec mvm

pushd mvm

pyinstaller --clean -y build.linux.spec
pyinstaller -y build.linux.spec

rm build.linux.spec

popd
popd


