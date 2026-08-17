@echo off
setlocal

:: 1. 获取标准化日期 (YYYY-mm-dd)
:: 使用 WMIC 获取，不依赖系统区域设置
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set "year=%datetime:~0,4%"
set "month=%datetime:~4,2%"
set "day=%datetime:~6,2%"
set "commit_date=%year%-%month%-%day%"

echo ==========================================
echo  Git Quick Push
echo  Commit Date: %commit_date%
echo ==========================================

:: 2. 执行 Git 命令
echo [1/3] Adding changes...
git add .

echo [2/3] Committing...
git commit -m "%commit_date%"

echo [3/3] Pushing to remote...
git push

echo.
echo ==========================================
echo  All done!
echo ==========================================

:: 暂停一下，以便查看是否有错误信息
pause