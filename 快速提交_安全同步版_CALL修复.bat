@echo off
setlocal EnableExtensions

cd /d "%~dp0"

echo ==========================================
echo   Obsidian Git Safe Sync
echo ==========================================
echo.

echo Git executable:
where git
echo.

call git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Current directory is not a Git repository.
    echo Path: %CD%
    goto :FAIL
)

for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HH-mm-ss"') do set "commit_time=%%I"

echo [1/4] Staging local changes...
call git add .
if errorlevel 1 (
    echo [ERROR] git add failed.
    goto :FAIL
)

call git diff --cached --quiet
if errorlevel 1 (
    echo [2/4] Committing local changes...
    call git commit -m "Obsidian sync %commit_time%"
    if errorlevel 1 (
        echo [ERROR] git commit failed.
        goto :FAIL
    )
) else (
    echo [2/4] No local changes to commit.
)

echo [3/4] Pulling remote changes with rebase...
call git pull --rebase
set "PULL_RC=%ERRORLEVEL%"

echo.
echo git pull --rebase exit code: %PULL_RC%

if not "%PULL_RC%"=="0" (
    echo.
    echo [ERROR] Pull/Rebase failed.
    echo There may be a merge conflict, network problem, or authentication problem.
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
call git push
set "PUSH_RC=%ERRORLEVEL%"

echo.
echo git push exit code: %PUSH_RC%

if not "%PUSH_RC%"=="0" (
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
call git status --short --branch
goto :END

:FAIL
echo.
echo ==========================================
echo   Sync FAILED - nothing was force-pushed.
echo ==========================================
echo.
call git status --short --branch

:END
echo.
echo ==========================================
echo   Press any key to close this window...
echo ==========================================
pause >nul
exit /b
