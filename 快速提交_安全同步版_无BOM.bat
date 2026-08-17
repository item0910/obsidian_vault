@echo off
setlocal EnableExtensions

cd /d "%~dp0"

echo ==========================================
echo   Obsidian Git Safe Sync
echo ==========================================
echo.

git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Current directory is not a Git repository.
    echo Path: %CD%
    goto :FAIL
)

for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HH-mm-ss"') do set "commit_time=%%I"

echo [1/4] Staging local changes...
git add .
if errorlevel 1 (
    echo [ERROR] git add failed.
    goto :FAIL
)

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

echo [3/4] Pulling remote changes with rebase...
git pull --rebase
if errorlevel 1 (
    echo.
    echo [ERROR] Pull/Rebase failed.
    echo There may be a merge conflict or network/authentication problem.
    echo.
    echo If Git reports CONFLICT:
    echo   1. Resolve the conflicting file(s).
    echo   2. Run: git add .
    echo   3. Run: git rebase --continue
    echo.
    echo To cancel the rebase:
    echo   git rebase --abort
    goto :FAIL
)

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
