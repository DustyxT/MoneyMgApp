import subprocess
import sys
import os

def build_exe():
    print("Building Flet executable...")
    
    # Command to package the app
    # --icon assets/icon.ico (we don't have one yet so omitting)
    cmd = [
        "flet", "pack", "app.py",
        "--name", "ManageUrWealth",
        "--product-name", "Manage Ur Wealth",
        "--product-version", "1.0.1",
        "--file-description", "Student Money Manager",
        "--copyright", "Copyright (c) 2026 Dusty",
    ]
    
    try:
        subprocess.check_call(cmd, shell=True)
        print("\nBuild successful! Check the 'dist' directory.")
    except subprocess.CalledProcessError as e:
        print(f"\nError during build: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()
