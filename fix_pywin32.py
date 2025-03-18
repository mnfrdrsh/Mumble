import os
import sys
import site
import subprocess
from pathlib import Path

def get_python_paths():
    """Get all possible Python installation paths"""
    paths = []
    
    # Add sys.prefix
    paths.append(Path(sys.prefix))
    
    # Add site-packages directories
    paths.extend([Path(p) for p in site.getsitepackages()])
    
    # Add user site-packages
    if site.USER_SITE:
        paths.append(Path(site.USER_SITE))
    
    return paths

def find_post_install_script():
    """Find the pywin32_postinstall.py script"""
    possible_paths = get_python_paths()
    
    for base_path in possible_paths:
        # Check in Scripts directory
        script_path = base_path / "Scripts" / "pywin32_postinstall.py"
        if script_path.exists():
            return script_path
        
        # Check in Lib/site-packages/pywin32_system32 directory
        alt_path = base_path / "Lib" / "site-packages" / "pywin32_system32" / "pywin32_postinstall.py"
        if alt_path.exists():
            return alt_path
    
    return None

def fix_pywin32():
    """Run the post-install script for pywin32"""
    post_install = find_post_install_script()
    
    if not post_install:
        print("Error: Could not find pywin32_postinstall.py")
        print("Searching in the following locations:")
        for path in get_python_paths():
            print(f"  - {path}")
        return False
    
    try:
        print(f"Found post-install script at: {post_install}")
        print("Running pywin32 post-installation script...")
        subprocess.run([sys.executable, str(post_install), "-install"], check=True)
        print("Successfully fixed pywin32 installation!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running post-install script: {e}")
        print("Try running this script with administrator privileges.")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    if sys.platform != "win32":
        print("This script is for Windows only.")
        sys.exit(1)
    
    print("Python executable:", sys.executable)
    print("Python version:", sys.version)
    print("\nSearching for pywin32 post-install script...")
    
    success = fix_pywin32()
    if not success:
        print("\nPlease try the following steps:")
        print("1. Run this script as administrator")
        print("2. If that doesn't work, try:")
        print("   - Uninstall pywin32: pip uninstall pywin32")
        print("   - Reinstall pywin32: pip install pywin32==305")
        print("   - Run this script again as administrator")
        sys.exit(1) 