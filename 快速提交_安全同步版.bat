@echo off
setlocal EnableExtensions

:: Always run from the directory where this script is located.
cd /d "%~dp0"

echo ==========================================
echo   Obsidian Git Safe Sync
echo ==========================================
echo.

:: 0. Check whether this is a Git repository.
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Current directory is not a Git repository.
    echo Path: %CD%
    goto :FAIL
)

:: Use PowerShell for a locale-independent timestamp.
for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HH-mm-ss"') do set "commit_time=%%I"

:: 1. Stage local changes.
echo [1/4] Staging local changes...
git add .
if errorlevel 1 (
    echo [ERROR] git add failed.
    goto :FAIL
)

:: 2. Commit only when staged changes exist.
git diff --cached --quiet
if errorlevel 1 (
    echo [2/4] Committing local changes...
    git commit -m "Obsidian sync %commit_time%"
    if errorlevel 1 (
        echo [ERROR] git commit failed.
        goto :FAIL
    )
) else (
    echo [2/4] No local changes to commit.
)

:: 3. Pull remote changes and replay local commit(s) on top.
echo [3/4] Pulling remote changes with rebase...
git pull --rebase
if errorlevel 1 (
    echo.
    echo [ERROR] Pull/Rebase failed.
    echo There may be a merge conflict or network/authentication problem.
    echo.
    echo If Git reports CONFLICT:
    echo   1. Open the conflicting file(s) and resolve them.
    echo   2. Run: git add .
    echo   3. Run: git rebase --continue
    echo.
    echo To cancel the rebase and return to the previous state:
    echo   git rebase --abort
    goto :FAIL
)

:: 4. Push the integrated result.
echo [4/4] Pushing to remote...
git push
if errorlevel 1 (
    echo.
    echo [ERROR] git push failed.
    echo Check the error message above. Your local commits are still safe.
    goto :FAIL
)

echo.
echo ==========================================
echo   Sync completed successfully.
echo ==========================================
echo.
git status --short --branch
echo.
pause
exit /b 0

:FAIL
echo.
echo ==========================================
echo   Sync FAILED - nothing was force-pushed.
echo ==========================================
echo.
git status --short --branch
echo.
pause
exit /b 1
