
# This script will build the distribution package of OSM 2 PNG
# The zip file will contain:
#   OsmToPng.exe    --> The main executable
#   resources       --> Directory with important files used by the program
#   help            --> Directory containing the Help files;
#   lang            --> Directory containing the Language files for UI localixìzation
#
# The script is optimized to run on a Windows computer, some adaptation might be
# needed to run on Linux.


import subprocess
import sys
from time import sleep
from pathlib import Path
from shutil import copytree, rmtree, copy

sitepackages = r".venv\Lib\site-packages"
pyinstaller = r".venv\Scripts\pyinstaller.exe"
# appicon = 'User_Red.ico'

ziparch = 'OsmToPng.zip'
exename = 'OsmToPng.exe'


print("Deleting old PyInstaller directories...")
sleep(1)
try:
    rmtree('dist', ignore_errors=True)
    rmtree('build', ignore_errors=True)
    rmtree('libs', ignore_errors=True)
except PermissionError:
    print("Some directory could not be deleted. Close all the applications using it and retry.")
    quit(-1)


print(f'Building Executable')
print(f'pyinstaller:  {pyinstaller}\n'
      f'sitepackages: {sitepackages}\n')

sp = Path(sitepackages)
spp = Path(sp).resolve()
pyinst = Path(pyinstaller)
pyinstp = Path(pyinst).resolve()

try:
    if not Path.exists(spp):
        raise FileNotFoundError(f'File {spp} not found. Please check the build_exe script')
    if not Path.exists(pyinstp):
        raise FileNotFoundError(f'File {pyinstp} not found. Please check the build_exe script')
except FileNotFoundError:
    sys.exit(-1)


# ---------------------------------------------------------------------
print("\nBuilding EXE...\n")
sleep(2)

cmd = (f'{pyinst} '
       f'--onefile '
       '--windowed '
       f'--name {exename} '
       # f'--hidden-import "requests" '
       # f'--hidden-import "markdown" '
       # f'--hidden-import "tkhtmlview" '
       # f'--hidden-import "tkinter" '
       # f'--hidden-import "tkintermapview" '
       r'-i.\resources\osm2png.ico '
       f'main.py')

subprocess.run(cmd)

# ---------------------------------------------------------------------
# Main files that are present in the program directory.
items = ['config.ini.template']
destpath = Path('dist')

dp = destpath.resolve()
for src in items:
    print(f" -> Copying to {dp}")
    print(f"      {src}")
    srcpath = Path(src).resolve()
    sleep(0.5)
    # copyfile(srcpath, destpath)
    copy(src, dp / str(Path(srcpath).name).replace('.template',''))


# ---------------------------------------------------------------------
# Resource files that are required by the program to work.
print("\nCopying program Resources...\n")
sleep(2)
sourcepath = 'resources'
destpath = Path('dist') / 'resources'
copytree(sourcepath, destpath, dirs_exist_ok=True)

# ---------------------------------------------------------------------
# The 'lang' directory contains the ini files for app localization.
sleep(2)
sourcepath = 'lang'
destpath = Path('dist') / 'lang'
copytree(sourcepath, destpath, dirs_exist_ok=True)

# ---------------------------------------------------------------------
# The 'help' directory contains the localized help files.
sleep(2)
sourcepath = 'help'
destpath = Path('dist') / 'help'
copytree(sourcepath, destpath, dirs_exist_ok=True)

# ---------------------------------------------------------------------
# Create final zip file!
print("Creating .zip")
print(" -> Adding main files...")
sourcepath = 'dist\\*.*'
cmd = (f'powershell Compress-Archive '
       f'-Path "{sourcepath} '
       rf'-DestinationPath dist\{ziparch} '
       f'-Force ')
subprocess.run(cmd)

items = ['dist\\resources',
         'dist\\lang',
         'dist\\help',
         'config.ini',
         f'{exename}',
         ]
for sourcepath in items:
    print(f" -> Adding {sourcepath}...")
    sleep(1)
    cmd = (f'powershell Compress-Archive '
           f'-Path "{sourcepath} '
           rf'-DestinationPath dist\{ziparch} '
           f'-Update ')

    subprocess.run(cmd)

print('\nDone.')
