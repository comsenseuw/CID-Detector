@echo off
setlocal enabledelayedexpansion

rem Define the log file path
set "LOG_FILE=log.txt"
echo -----------------------------------------------------------------
echo START AUTO

rem Set date format
set dtf=%date:~-4%-%date:~-7,2%-%date:~-10,2% %time:~0,2%:%time:~3,2%:%time:~6,2%

rem Run the Python script with logging
echo -----------------------------------------------------------------
echo START U810x checking

for /f "delims=" %%A in ('py cid.py') do (
    echo [%dtf%] %%A >> "%LOG_FILE%"
    echo %%A
)
echo -----------------------------------------------------------------
echo START Cleaning

for /f "delims=" %%A in ('py housekeeping.py') do (
    echo [%dtf%] %%A >> "%LOG_FILE%"
    echo %%A
)

echo END AUTO
echo -----------------------------------------------------------------

endlocal