import sys
from cx_Freeze import setup,Executable
import requests.certs

base = None
if sys.platform == 'win32':
	base = 'Win32GUI'
	
exe = Executable(
        script  = 'Main.py',
        icon    = 'icns\\steam.ico',
		base = base
        )
includefiles    = ['docs\\',
                   'fnts\\',
                   'icns',
                   'imgs\\',
				   'snd\\',
				   'App.py',
				   'Container.py',
				   'Database.py',
				   'FileProcessor.py',
				   'FrontEnd.py',
				   'LogFile.py',
                   'StatusBar.py',
				   'Window.py',
				   (requests.certs.where(),
				   'cacert.pem')]
excludes = []
packages = ['os', 'site', 're', 'requests', 'sys', 'win32com', 'shutil', 'PIL']

setup(
    name        = 'Steam Shortcut Creator',
    version     = '0.1',
    description = 'null',
    options     = {'build_exe': {'excludes':excludes,'packages':packages,'include_files':includefiles}},
    executables = [exe]
)
