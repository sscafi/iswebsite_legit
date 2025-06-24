#!/usr/bin/env python3
"""
Quick Start Script for Domain Checker
Guides users through initial setup and launches the application
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True, text=True)
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_config():
    """Setup configuration file"""
    config_file = Path('.env')
    example_file = Path('config.env.example')
    
    if config_file.exists():
        print("✓ Configuration file already exists")
        return True
    
    if example_file.exists():
        print("\n⚙️  Setting up configuration...")
        try:
            with open(example_file, 'r') as src:
                with open(config_file, 'w') as dst:
                    dst.write(src.read())
            print("✓ Configuration file created (.env)")
            print("💡 Edit .env to add your API keys for full functionality")
            return True
        except Exception as e:
            print(f"❌ Failed to create config file: {e}")
            return False
    else:
        print("⚠️  No config template found, continuing without API keys")
        return True

def run_tests():
    """Run component tests"""
    print("\n🧪 Running component tests...")
    try:
        result = subprocess.run([sys.executable, 'test_app.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ All tests passed")
            return True
        else:
            print("⚠️  Some tests failed, but continuing...")
            print(result.stdout)
            return True
    except Exception as e:
        print(f"⚠️  Could not run tests: {e}")
        return True

def launch_app():
    """Launch the main application"""
    print("\n🚀 Launching Domain Checker...")
    try:
        subprocess.run([sys.executable, 'main.py'])
    except KeyboardInterrupt:
        print("\n👋 Application closed by user")
    except Exception as e:
        print(f"❌ Failed to launch application: {e}")

def main():
    """Main quick start process"""
    print("Domain Checker - Quick Start")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n💡 Try running: pip install -r requirements.txt")
        sys.exit(1)
    
    # Setup configuration
    setup_config()
    
    # Run tests
    run_tests()
    
    # Launch application
    launch_app()

if __name__ == "__main__":
    main() 