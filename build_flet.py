"""
Flet Build Script for Manage Ur Wealth Native App
Packages the app as a Windows executable using Flet's built-in packaging.
"""

import subprocess
import sys
import shutil
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
APP_FILE = BASE_DIR / "app.py"
DATA_SERVICE = BASE_DIR / "data_service.py"
CHART_SERVICE = BASE_DIR / "chart_service.py"
DIST_DIR = BASE_DIR / "dist_native"

def main():
    print("=" * 50)
    print("Manage Ur Wealth - Flet Native Build")
    print("=" * 50)
    
    # Check if flet is installed
    try:
        import flet
        print(f"[OK] Flet version: {flet.__version__}")
    except ImportError:
        print("[ERROR] Flet not installed. Run: pip install flet")
        sys.exit(1)
    
    # Create dist directory
    DIST_DIR.mkdir(exist_ok=True)
    
    # Copy data files to include with the app
    print("\nCopying data files...")
    data_files = ["budget_config.csv", "transactions.csv", "profile.json"]
    for file in data_files:
        src = BASE_DIR / file
        if src.exists():
            shutil.copy(src, DIST_DIR / file)
            print(f"  [OK] Copied {file}")
    
    print("\n" + "=" * 50)
    print("Building with Flet...")
    print("=" * 50)
    
    # Build command using flet pack
    # flet pack creates a standalone executable
    cmd = [
        sys.executable, "-m", "flet", "pack",
        str(APP_FILE),
        "--name", "ManageUrWealth",
        "--add-data", f"{DATA_SERVICE};.",
        "--add-data", f"{CHART_SERVICE};.",
    ]
    
    print(f"\nRunning: {' '.join(cmd)}")
    print("\nThis may take a few minutes...")
    
    result = subprocess.run(cmd, cwd=str(BASE_DIR))
    
    if result.returncode == 0:
        print("\n" + "=" * 50)
        print("[OK] BUILD SUCCESSFUL!")
        print("=" * 50)
        print(f"\nExecutable created in: {BASE_DIR / 'dist'}")
        print("\nTo run: Double-click ManageUrWealth.exe")
        print("\nNote: Copy the data files (budget_config.csv, etc.)")
        print("      to the same folder as the executable.")
    else:
        print("\n[ERROR] Build failed. Check the error messages above.")
        print("\nAlternative: You can still run the app with:")
        print("  python app.py")
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
