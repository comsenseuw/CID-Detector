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

for /f "delims=" %%A in ('D:\PortableApps\WPy64-38123\pypy3.8-v7.3.9-win64\python.exe D:\optimation\u810x_detection\read_csv_v3.3.py') do (
    echo [%dtf%] %%A >> "%LOG_FILE%"
    echo %%A
)
echo -----------------------------------------------------------------
echo START Cleaning

for /f "delims=" %%A in ('D:\PortableApps\WPy64-38123\pypy3.8-v7.3.9-win64\python.exe D:\optimation\u810x_detection\cleaning.py') do (
    echo [%dtf%] %%A >> "%LOG_FILE%"
    echo %%A
)

echo END AUTO
echo -----------------------------------------------------------------

endlocal