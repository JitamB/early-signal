@echo off
echo ========================================================
echo  Internship Tracker - Daily Windows Task Scheduler Setup
echo ========================================================
echo.
echo Setting up daily automatic scan at 09:00 AM IST...
echo.

set SCRIPT_DIR=%~dp0
set SCRIPT_PATH=%SCRIPT_DIR%check_openings.py

schtasks /create /tn "InternshipTrackerDailyScan" /tr "python \"%SCRIPT_PATH%\" --scan --notify" /sc daily /st 09:00 /f

if %ERRORLEVEL% equ 0 (
    echo.
    echo [+] SUCCESS: Daily task 'InternshipTrackerDailyScan' registered!
    echo [+] It will run automatically every day at 09:00 AM.
    echo [+] Any new openings will be pushed to your ntfy app immediately.
) else (
    echo.
    echo [-] Note: If registration failed, please run CMD or PowerShell as Administrator and run this batch file again.
)

echo.
pause
