import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
# "packages": ["os"] is used as example only

# base="Win32GUI" should be used only for Windows GUI app

includefiles = ['themes/']
includes = []
excludes = []
packages = []
build_exe_options = {'excludes':excludes,'packages':packages,'include_files':includefiles}
buildOptions = dict(include_files = ['themes/']) #folder,relative path. Use tuple like in the single file to set a absolute path.

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name = "test",
    description = "My GUI application!",
    options = {"build_exe": build_exe_options},
    executables = [Executable("GUI.py", base=base)]
)
