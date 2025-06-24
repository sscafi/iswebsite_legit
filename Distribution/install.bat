@echo off
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
if not exist "C:\Program Files\DomainChecker" (
    mkdir "C:\Program Files\DomainChecker"
    echo Created installation directory
)

REM Copy executable
copy "DomainChecker.exe" "C:\Program Files\DomainChecker\" >nul
if %errorLevel% == 0 (
    echo Copied executable to Program Files
) else (
    echo ERROR: Failed to copy executable
    pause
    exit /b 1
)

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Domain Checker.lnk'); $Shortcut.TargetPath = 'C:\Program Files\DomainChecker\DomainChecker.exe'; $Shortcut.WorkingDirectory = 'C:\Program Files\DomainChecker'; $Shortcut.Description = 'Domain Security Checker'; $Shortcut.Save()"

REM Create start menu shortcut
echo Creating start menu shortcut...
if not exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\DomainChecker" (
    mkdir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\DomainChecker"
)
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\DomainChecker\Domain Checker.lnk'); $Shortcut.TargetPath = 'C:\Program Files\DomainChecker\DomainChecker.exe'; $Shortcut.WorkingDirectory = 'C:\Program Files\DomainChecker'; $Shortcut.Description = 'Domain Security Checker'; $Shortcut.Save()"

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Domain Checker has been installed to:
echo C:\Program Files\DomainChecker\
echo.
echo Shortcuts created:
echo - Desktop: Domain Checker
echo - Start Menu: DomainChecker folder
echo.
echo You can now run Domain Checker from your desktop or start menu.
echo.
pause
