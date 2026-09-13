@echo off
setlocal enabledelayedexpansion
TITLE Patch Manual SoundScope

:: Set the script directory and resolve ROOT_DIR
SET "SCRIPT_DIR=%~dp0"
IF "%SCRIPT_DIR:~-1%"=="\" SET "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

FOR %%I IN ("%SCRIPT_DIR%") DO SET "ROOT_DIR=%%~fI"

:: Define correct paths inside Duckstation
SET "MANUAL_INIT=%ROOT_DIR%\Duckstation\Soundscope\Manual\__init__.py"
SET "TARGET_INIT=%ROOT_DIR%\Duckstation\Soundscope\soundscope\__init__.py"

ECHO ========================================================
ECHO         Patch Manual SoundScope by XxZer0ModZxX
ECHO ========================================================
ECHO Root Directory: %ROOT_DIR%
ECHO.

:: -----------------------------------------------------
:: Overwriting __init__.py with Manual version
:: -----------------------------------------------------
ECHO Copying Manual __init__.py...
IF EXIST "%MANUAL_INIT%" (
    COPY /Y "%MANUAL_INIT%" "%TARGET_INIT%" >nul
    IF !ERRORLEVEL! EQU 0 (
        ECHO [OK] Copied to Duckstation\Soundscope\soundscope\__init__.py
    ) ELSE (
        ECHO [ERROR] Failed to overwrite target file.
    )
) ELSE (
    ECHO [ERROR] Source file not found: %MANUAL_INIT%
)

ECHO.
ECHO ========================================================
ECHO      Manual SoundScope Patch Applied Successfully!
ECHO ========================================================
ECHO.
PAUSE
EXIT /B 0