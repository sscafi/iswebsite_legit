#!/usr/bin/env python3
"""
Build script for Domain Checker application
Creates a standalone executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_executable():
    """Build the executable using PyInstaller"""
    
    # Clean previous builds
    print("Cleaning previous builds...")
    for path in ['build', 'dist']:
        if os.path.exists(path):
            shutil.rmtree(path)
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',  # Single executable
        '--windowed',  # No console window
        '--name=DomainChecker',
        '--icon=icon.ico',  # Add icon if available
        '--add-data=config.env.example;.',  # Include config example
        '--hidden-import=whois',
        '--hidden-import=requests',
        '--hidden-import=cryptography',
        '--hidden-import=dotenv',
        '--hidden-import=reportlab',
        '--hidden-import=openpyxl',
        'main.py'
    ]
    
    # Remove icon flag if icon doesn't exist
    if not os.path.exists('icon.ico'):
        cmd.remove('--icon=icon.ico')
    
    print("Building executable...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        print(f"Executable created in: {os.path.abspath('dist')}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_installer():
    """Create a complete installer script"""
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
    
    with open('install.bat', 'w') as f:
        f.write(installer_content)
    
    print("Installer script created: install.bat")

def create_self_installing_package():
    """Create a self-installing package"""
    # Create a batch file that combines installer and executable
    package_content = '''@echo off
echo ========================================
echo    Domain Checker - Self Installing
echo ========================================
echo.
echo This package will install Domain Checker automatically.
echo.

REM Extract executable to temp location
echo Extracting files...
set "TEMP_DIR=%TEMP%\\DomainChecker_Install"
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"

REM Copy executable to temp
copy "%~dpnx0" "%TEMP_DIR%\\DomainChecker.exe" >nul

REM Run installer
echo Installing Domain Checker...
cd /d "%TEMP_DIR%"
call install.bat

REM Cleanup
echo Cleaning up temporary files...
rmdir /s /q "%TEMP_DIR%"

echo.
echo Installation complete! You can now run Domain Checker.
pause
'''
    
    # Create the package script
    with open('DomainChecker_Installer.bat', 'w') as f:
        f.write(package_content)
    
    print("Self-installing package created: DomainChecker_Installer.bat")

def main():
    print("Domain Checker Build Script")
    print("=" * 40)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
    
    # Build the executable
    if build_executable():
        # Create installer
        create_installer()
        
        # Create self-installing package
        create_self_installing_package()
        
        print("\nBuild completed successfully!")
        print("Files created:")
        print("- dist/DomainChecker.exe (standalone executable)")
        print("- install.bat (installer script)")
        print("- DomainChecker_Installer.bat (self-installing package)")
        print("\nTo distribute:")
        print("1. Share DomainChecker_Installer.bat for easy installation")
        print("2. Or share DomainChecker.exe + install.bat separately")
        print("3. Users just need to run the installer as administrator")
    else:
        print("\nBuild failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 