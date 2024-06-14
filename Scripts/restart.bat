@echo off
echo Closing service windows...

:loop
set "found="
for /f "tokens=2 delims=," %%i in ('tasklist /v /fo csv ^| findstr /i "SHARD_MIND"') do (
    set "found=1"
    taskkill /F /PID %%i
)
if defined found (
    timeout /t 2
    goto loop
)

echo Closing browser windows to localhost:8080 and localhost:8000...

REM Close any open browser windows with localhost:8080 or localhost:8000
for /f "tokens=2 delims=," %%i in ('tasklist /v /fo csv ^| findstr /i "chrome.exe\|firefox.exe\|msedge.exe"') do (
    taskkill /F /PID %%i
)
echo Restarting services...

start "SHARD_MIND debug_server" cmd /K "run_service.bat debug_server.bat"
start "SHARD_MIND index_serve" cmd /K "run_service.bat index_serve.bat"
start "SHARD_MIND plan_server" cmd /K "run_service.bat plan_server.bat"
start "SHARD_MIND app" cmd /K "run_service.bat app.bat"

REM Open the localhost URL in the default browser
timeout /t 1
start http://localhost:8080