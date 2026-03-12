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

#$FolderPath = ".\packenv"
#if (!(Test-Path -Path $FolderPath -PathType Container)) {
if (!(Test-Path -Path ".\packenv" -PathType Container)) {
   
   python -m venv packenv
   .\packenv\Scripts\Activate.ps1

   #pip install --upgrade pip
   pip install PyInstaller
   pip install psutil
   pip install packaging
   pip install requests
   pip install pytest
   pip install pywin32
   pip install pyside6
} else {
    .\packenv\Scripts\Activate.ps1
}

#####
# Do every time, to make sure everyone knows source of E.ico icon, so 
# proper license can be found
# cp .\resources\icons\Barkerbaggies-Bag-O-Tiles-E.ico .\resources\icons\E.ico

cp BuildScripts/build.windows11.spec vmm

pushd vmm

pyinstaller --clean -y build.windows11.spec
pyinstaller -y build.windows11.spec

rm build.windows11.spec

popd
popd

