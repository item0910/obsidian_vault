@echo off
setlocal

:: Get current date (YYYY-MM-DD)
for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd"') do set "commit_date=%%I"

echo ==========================================
echo  Git Quick Sync
echo  Commit Date: %commit_date%
echo ==========================================
echo.

echo [1/4] Adding changes...
git add .
echo.

echo [2/4] Committing...
git commit -m "%commit_date%"
echo.

echo [3/4] Pulling latest changes...
git pull --rebase
echo.
echo Pull finished. Press any key to continue...
pause >nul
echo.

echo [4/4] Pushing to remote...
git push
echo.

echo ==========================================
echo  Sync finished.
echo ==========================================
echo.
echo Press any key to close...
pause >nul
