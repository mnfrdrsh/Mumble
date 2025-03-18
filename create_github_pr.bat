@echo off
echo Creating GitHub Pull Request...

:: Check if gh CLI is installed
where gh >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo GitHub CLI is not installed or not in your PATH.
    echo Please install GitHub CLI from https://cli.github.com/
    pause
    exit /b 1
)

:: Check if user is authenticated
gh auth status >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo You are not authenticated with GitHub CLI.
    echo Please run 'gh auth login' to authenticate.
    pause
    exit /b 1
)

:: Check current branch
echo Checking current branch...
for /f "tokens=*" %%a in ('git branch --show-current') do set CURRENT_BRANCH=%%a
echo Current branch: %CURRENT_BRANCH%

:: Prompt for PR title
echo.
set /p PR_TITLE="Enter PR title (or press Enter for default): "
if "%PR_TITLE%"=="" set PR_TITLE="Add unified launcher and fix speech recognition freezing issues"

:: Prompt for PR body or use template
echo.
echo Using PR template from .github/PULL_REQUEST_TEMPLATE.md if available.
echo.

:: Create PR
echo Creating pull request...
gh pr create --title "%PR_TITLE%" --body-file ".github/PULL_REQUEST_TEMPLATE.md" --base main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Pull request created successfully!
) else (
    echo.
    echo Failed to create pull request.
    echo Please check the error message above.
)

echo.
echo Done!
pause 