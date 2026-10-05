@echo off
setlocal enabledelayedexpansion
TITLE Patch Auto SoundScope

:: Set the script directory and resolve ROOT_DIR
SET "SCRIPT_DIR=%~dp0"
IF "%SCRIPT_DIR:~-1%"=="\" SET "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

FOR %%I IN ("%SCRIPT_DIR%") DO SET "ROOT_DIR=%%~fI"

:: Define correct paths inside Duckstation
SET "AUTO_INIT=%ROOT_DIR%\Duckstation\Soundscope\Automatic\__init__.py"
SET "TARGET_INIT=%ROOT_DIR%\Duckstation\Soundscope\soundscope\__init__.py"

SET "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"

ECHO ========================================================
ECHO         Patch Auto SoundScope by XxZer0ModZxX
ECHO ========================================================
ECHO Root Directory: %ROOT_DIR%
ECHO.

:: -----------------------------------------------------
:: Checking & Installing Required Dependencies (pynput)
:: -----------------------------------------------------
ECHO Checking dependencies (pynput)...
"%PYTHON_EXE%" --version >nul 2>&1
IF !ERRORLEVEL! NEQ 0 (
    python --version >nul 2>&1
    IF !ERRORLEVEL! EQU 0 (
        SET "PYTHON_EXE=python"
    )
)

"%PYTHON_EXE%" -c "import pynput" >nul 2>&1
IF !ERRORLEVEL! NEQ 0 (
    ECHO [INFO] pynput module not detected. Installing via pip...
    "%PYTHON_EXE%" -m pip install pynput
    IF !ERRORLEVEL! EQU 0 (
        ECHO [OK] pynput installed successfully.
    ) ELSE (
        ECHO [WARNING] Failed to install pynput. Z-key visualizer controls may be disabled.
    )
) ELSE (
    ECHO [OK] pynput is already installed.
)
ECHO.

:: -----------------------------------------------------
:: Overwriting __init__.py with Automatic version
:: -----------------------------------------------------
ECHO Copying Automatic __init__.py...
IF EXIST "%AUTO_INIT%" (
    COPY /Y "%AUTO_INIT%" "%TARGET_INIT%" >nul
    IF !ERRORLEVEL! EQU 0 (
        ECHO [OK] Copied to Duckstation\Soundscope\soundscope\__init__.py
    ) ELSE (
        ECHO [ERROR] Failed to overwrite target file.
    )
) ELSE (
    ECHO [ERROR] Source file not found: %AUTO_INIT%
)

ECHO.
ECHO ========================================================
ECHO       Auto SoundScope Patch Applied Successfully!
ECHO ========================================================
ECHO.
PAUSE
EXIT /B 0