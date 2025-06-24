#!/usr/bin/env python3
"""
Create Distribution Package for Domain Checker
Builds executable with API keys and creates installer
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def create_config_with_api_keys():
    """Create a .env file with your API keys"""
    print("Setting up API keys...")
    
    # Get API keys from user
    print("Enter your API keys (press Enter to skip if you don't have them):")
    
    dns_key = input("DNS Tracking API Key: ").strip()
    vt_key = input("VirusTotal API Key: ").strip()
    abuse_key = input("AbuseIPDB API Key: ").strip()
    
    # Create .env file
    env_content = f"""# DNS Tracking API Configuration
DNS_TRACKING_API_KEY={dns_key}

# VirusTotal API (for malware checking)
VIRUSTOTAL_API_KEY={vt_key}

# AbuseIPDB API (for blacklist checking)
ABUSEIPDB_API_KEY={abuse_key}

# Application Settings
ENABLE_ANALYTICS=false
ENABLE_CRASH_REPORTING=false
DARK_MODE=false
AUTO_UPDATE=true
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✓ API keys configured")

def build_executable():
    """Build the executable"""
    print("\nBuilding executable...")
    
    # Clean previous builds
    for path in ['build', 'dist']:
        if os.path.exists(path):
            shutil.rmtree(path)
    
    # Build command
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=DomainChecker',
        '--add-data=.env;.',
        '--hidden-import=whois',
        '--hidden-import=requests',
        '--hidden-import=cryptography',
        '--hidden-import=dotenv',
        '--hidden-import=reportlab',
        '--hidden-import=openpyxl',
        'main.py'
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ Executable built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed: {e}")
        return False

def create_installer_package():
    """Create the installer package"""
    print("\nCreating installer package...")
    
    # Create distribution directory
    dist_dir = Path("Distribution")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    
    # Copy files
    shutil.copy("dist/DomainChecker.exe", dist_dir / "DomainChecker.exe")
    shutil.copy("install.bat", dist_dir / "install.bat")
    shutil.copy("README.md", dist_dir / "README.md")
    shutil.copy("LICENSE", dist_dir / "LICENSE")
    
    # Create simple README for end users
    user_readme = """# Domain Checker - Security Tool

## Installation
1. Right-click on `install.bat`
2. Select "Run as administrator"
3. Follow the installation prompts

## Usage
- Double-click the "Domain Checker" icon on your desktop
- Enter a domain name to check
- View comprehensive security analysis

## Features
- WHOIS information
- SSL certificate validation
- Malware detection
- Risk scoring
- Export results

## Support
For issues or questions, contact the developer.
"""
    
    with open(dist_dir / "README.txt", 'w') as f:
        f.write(user_readme)
    
    print("✓ Distribution package created")

def create_single_installer():
    """Create a single file installer"""
    print("\nCreating single file installer...")
    
    # Create a batch file that includes everything
    installer_content = '''@echo off
echo ========================================
echo    Domain Checker - Security Tool
echo ========================================
echo.
echo This installer will install Domain Checker to your system.
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as administrator - proceeding with installation...
) else (
    echo WARNING: Not running as administrator
    echo Some features may not work properly.
    echo.
    pause
)

echo.
echo Installing Domain Checker...

REM Create installation directory
if not exist "C:\\Program Files\\DomainChecker" (
    mkdir "C:\\Program Files\\DomainChecker"
    echo Created installation directory
)

REM Copy executable
copy "DomainChecker.exe" "C:\\Program Files\\DomainChecker\\" >nul
if %errorLevel% == 0 (
    echo Copied executable to Program Files
) else (
    echo ERROR: Failed to copy executable
    pause
    exit /b 1
)

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\Domain Checker.lnk'); $Shortcut.TargetPath = 'C:\\Program Files\\DomainChecker\\DomainChecker.exe'; $Shortcut.WorkingDirectory = 'C:\\Program Files\\DomainChecker'; $Shortcut.Description = 'Domain Security Checker'; $Shortcut.Save()"

REM Create start menu shortcut
echo Creating start menu shortcut...
if not exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\DomainChecker" (
    mkdir "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\DomainChecker"
)
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\DomainChecker\\Domain Checker.lnk'); $Shortcut.TargetPath = 'C:\\Program Files\\DomainChecker\\DomainChecker.exe'; $Shortcut.WorkingDirectory = 'C:\\Program Files\\DomainChecker'; $Shortcut.Description = 'Domain Security Checker'; $Shortcut.Save()"

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Domain Checker has been installed to:
echo C:\\Program Files\\DomainChecker\\
echo.
echo Shortcuts created:
echo - Desktop: Domain Checker
echo - Start Menu: DomainChecker folder
echo.
echo You can now run Domain Checker from your desktop or start menu.
echo.
pause
'''
    
    with open("Distribution/install.bat", 'w') as f:
        f.write(installer_content)
    
    print("✓ Single file installer created")

def main():
    print("Domain Checker - Distribution Package Creator")
    print("=" * 50)
    
    # Step 1: Configure API keys
    create_config_with_api_keys()
    
    # Step 2: Build executable
    if not build_executable():
        print("Build failed. Exiting.")
        sys.exit(1)
    
    # Step 3: Create installer package
    create_installer_package()
    create_single_installer()
    
    print("\n" + "=" * 50)
    print("DISTRIBUTION PACKAGE CREATED SUCCESSFULLY!")
    print("=" * 50)
    print("\nFiles created in 'Distribution' folder:")
    print("- DomainChecker.exe (20MB executable with your API keys)")
    print("- install.bat (installer script)")
    print("- README.txt (user instructions)")
    print("- LICENSE (license file)")
    print("\nTo distribute:")
    print("1. Share the entire 'Distribution' folder")
    print("2. Users run 'install.bat' as administrator")
    print("3. Desktop icon will be created automatically")
    print("\nYour API keys are included in the executable!")

if __name__ == "__main__":
    main() 