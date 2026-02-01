import sys
from pathlib import Path

def get_base_path() -> Path:
    """
    Get the base path for static resources (frontend).
    If frozen (PyInstaller), returns sys._MEIPASS.
    Otherwise returns the project root (parent of backend).
    """
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent.parent

def get_data_path() -> Path:
    """
    Get the path for user variable data (CSV/JSON).
    If frozen (PyInstaller), returns the directory containing the executable.
    Otherwise returns the project root.
    """
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent.parent
