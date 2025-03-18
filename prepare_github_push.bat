@echo off
echo Preparing to push changes to GitHub...

:: Check if git is installed
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Git is not installed or not in your PATH.
    echo Please install Git from https://git-scm.com/downloads
    pause
    exit /b 1
)

:: Check current branch
echo Checking current branch...
git branch

:: Show status of changes
echo.
echo Current status of changes:
git status

:: Show diff of changes
echo.
echo Summary of changes:
git diff --stat

:: Prompt for commit message
echo.
set /p COMMIT_MESSAGE="Enter commit message (or press Enter for default): "
if "%COMMIT_MESSAGE%"=="" set COMMIT_MESSAGE="Add unified launcher and fix speech recognition freezing issues"

:: Add all changes
echo.
echo Adding all changes...
git add .

:: Commit changes
echo.
echo Committing changes with message: %COMMIT_MESSAGE%
git commit -m "%COMMIT_MESSAGE%"

:: Show log
echo.
echo Recent commits:
git log -3 --oneline

:: Prompt to push
echo.
set /p PUSH_CONFIRM="Push changes to remote repository? (y/n): "
if /i "%PUSH_CONFIRM%"=="y" (
    echo Pushing changes...
    git push
    echo.
    echo Changes pushed successfully!
) else (
    echo.
    echo Changes committed but not pushed.
    echo To push later, run: git push
)

echo.
echo Done!
pause 