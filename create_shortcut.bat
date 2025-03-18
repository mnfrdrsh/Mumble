@echo off
echo Creating Mumble Launcher shortcut on desktop...

set SCRIPT_DIR=%~dp0
set DESKTOP_DIR=%USERPROFILE%\Desktop
set VBS_PATH=%SCRIPT_DIR%launch_mumble.vbs
set ICON_PATH=%SCRIPT_DIR%src\assets\icon.png

:: Create the shortcut using PowerShell
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP_DIR%\Mumble Launcher.lnk'); $Shortcut.TargetPath = '%VBS_PATH%'; $Shortcut.WorkingDirectory = '%SCRIPT_DIR%'; $Shortcut.Description = 'Launch Mumble Applications'; $Shortcut.Save()"

echo Shortcut created successfully!
echo You can now launch Mumble from your desktop.
pause 