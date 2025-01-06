@echo off
REM Example batch file to run BIMcloud Backup Script using Windows Task Scheduler

REM Set the command prompt to use UTF-8
chcp 65001 > NUL

REM Define the path to the Python executable and the script location
SET PYTHON_PATH=C:\path\to\python.exe
SET SCRIPT_PATH=C:\path\to\bimcloud_backup\main.py

REM Define arguments for the script
SET MANAGER_URL=https://your-bimcloud-manager-url.com

REM CLIENT_ID also used as log file name
SET CLIENT_ID=your-client-id

SET USERNAME=your-username
SET PASSWORD=your-password

REM Options: all, edited, selected
SET TASK=all

REM Optional: Set PROJECT_PATH to an empty string if TASK is not selected
SET PROJECT_PATH=directory/filename

REM Define the target root directory for copying backup files
SET TARGET_ROOT=C:\path\to\target\directory

REM Define the file extension for backups (depending on Archicad version)
SET FILE_EXTENSION=".BIMProject26"

REM Run the script with the defined arguments
%PYTHON_PATH% %SCRIPT_PATH% -m %MANAGER_URL% -c %CLIENT_ID% -u %USERNAME% -p %PASSWORD% -t %TASK% -prj %PROJECT_PATH% -tgt %TARGET_ROOT% -ext %FILE_EXTENSION%

REM pause
