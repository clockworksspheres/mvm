# highly modified version of:
# https://www.pythonguis.com/tutorials/packaging-pyside6-applications-windows-pyinstaller-installforge/
# amoung others... including
# https://pyinstaller.org/en/stable/

# before script is run:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# powershell -File ".\eisenban.windows.ps1"

pushd ..

#if doesn't exist...
# cd to the eisenban source root

$directory = ".\projEnv"
$actfile = $directory\bin\Activate.ps1
if (!(Test-Path -Path $FolderPath -PathType Container)) {
   #if (!(Test-Path -Path ".\packenv" -PathType Container)) {
   
   #python -m venv projEnv
   #.\projEnv\Scripts\Activate.ps1
   python -m venv $directory
   $actfile

   #pip install --upgrade pip
   pip install astroid
   pip install PyInstaller
   pip install psutil
   pip install packaging
   pip install requests
   pip install pylint
   pip install pytest
   pip install pywin32
   pip install pyside6
} else {
   $actfile
}

#####
# Do every time, to make sure everyone knows source of E.ico icon, so 
# proper license can be found
# cp .\resources\icons\Barkerbaggies-Bag-O-Tiles-E.ico .\resources\icons\E.ico

cp BuildScripts/build.windows11.spec mvm

pushd mvm

pyinstaller --clean -y build.windows11.spec
pyinstaller -y build.windows11.spec

rm build.windows11.spec

popd
popd

