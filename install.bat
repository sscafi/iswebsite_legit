@echo off
echo Installing Domain Checker...
echo.
echo This will install Domain Checker to your system.
echo.
pause

REM Create installation directory
if not exist "C:\Program Files\DomainChecker" mkdir "C:\Program Files\DomainChecker"

REM Copy executable
copy "DomainChecker.exe" "C:\Program Files\DomainChecker\"

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Domain Checker.lnk'); $Shortcut.TargetPath = 'C:\Program Files\DomainChecker\DomainChecker.exe'; $Shortcut.Save()"

echo.
echo Installation complete!
echo Domain Checker has been installed to C:\Program Files\DomainChecker\
echo A shortcut has been created on your desktop.
echo.
pause
