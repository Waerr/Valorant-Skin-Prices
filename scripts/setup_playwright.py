#!/usr/bin/env python3
"""
Setup script for Playwright browsers.
Run this script to install the required browsers for Playwright.
"""

import subprocess
import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def install_playwright_browsers():
    """Install Playwright browsers."""
    try:
        print("Installing Playwright browsers...")
        subprocess.run([
            sys.executable, "-m", "playwright", "install", "chromium"
        ], check=True)
        print("Playwright browsers installed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"Error installing Playwright browsers: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    
    return True


def check_playwright_installation():
    """Check if Playwright is properly installed."""
    try:
        import playwright
        print("Playwright package is installed")
        return True
    except ImportError:
        print("Playwright package is not installed")
        return False


def main():
    """Main setup function."""
    print("Setting up Playwright for Valorant Skin Prices")
    print("=" * 50)
    
    # Check if Playwright is installed
    if not check_playwright_installation():
        print("\nPlease install Playwright first:")
        print("pip install playwright")
        return False
    
    # Install browsers
    if install_playwright_browsers():
        print("\nSetup completed successfully!")
        print("\nYou can now run the application with enhanced scraping capabilities:")
        print("python main.py")
        return True
    else:
        print("\nSetup failed. Please check the error messages above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 