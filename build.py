import PyInstaller.__main__
import os
from pathlib import Path

# Define paths
BASE_DIR = Path(__file__).parent.absolute()
BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"
ICON_PATH = FRONTEND_DIR / "favicon.ico"

# Ensure output directory exists
DIST_DIR = BASE_DIR / "dist"
if not DIST_DIR.exists():
    DIST_DIR.mkdir()

# Build command arguments
args = [
    str(BACKEND_DIR / "main.py"),  # Script to run
    "--name=ManageUrWealth",       # Name of the executable
    "--noconfirm",                 # Overwrite existing build
    "--clean",                     # Clean cache
    "--onefile",                   # Create a single executable file
    "--windowed",                  # Hide console window
    f"--add-data={FRONTEND_DIR}{os.pathsep}frontend", # Bundle frontend folder
    f"--paths={BACKEND_DIR}",      # Add backend to python path to find modules
    "--icon=" + str(ICON_PATH) if ICON_PATH.exists() else None, # Icon if available
    "--hidden-import=uvicorn",
    "--hidden-import=fastapi",
    "--hidden-import=pandas",
    "--hidden-import=numpy",      # Pandas dependency
    "--hidden-import=math",
    "--hidden-import=uuid",
    "--hidden-import=datetime",
    "--hidden-import=json",
    "--hidden-import=pathlib",
    "--hidden-import=typing",
    "--hidden-import=routes",     # Explicitly include our routes package
    "--hidden-import=services",
    "--hidden-import=models",
    "--hidden-import=utils",
]

# Filter out None values (e.g. missing icon)
args = [arg for arg in args if arg is not None]

print("Building executable with arguments:")
for arg in args:
    print(f"  {arg}")

# Run PyInstaller
PyInstaller.__main__.run(args)

print("\nBuild complete! Executable is in the 'dist' folder.")
