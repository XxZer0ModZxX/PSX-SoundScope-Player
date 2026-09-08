@echo off
setlocal enabledelayedexpansion
TITLE SoundScope Automated Setup Installer

:: Set the script directory and resolve the project ROOT_DIR
SET "SCRIPT_DIR=%~dp0"
IF "%SCRIPT_DIR:~-1%"=="\" SET "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:: When Setup SoundScope.exe is in the root directory, ROOT_DIR is SCRIPT_DIR
FOR %%I IN ("%SCRIPT_DIR%") DO SET "ROOT_DIR=%%~fI"

:: Define relative directory and file paths
SET "DS_DIR=%ROOT_DIR%\Duckstation"
SET "SOUNDSCOPE_DIR=%DS_DIR%\Soundscope"
SET "PATCH_DIR=%ROOT_DIR%\config_patch"
SET "BIOS_DIR=%PATCH_DIR%\bios"
SET "AUDIO_DIR=%ROOT_DIR%\audio_files"

SET "ZIP_URL=https://github.com/stenzek/duckstation/releases/download/latest/duckstation-windows-x64-release.zip"
SET "ZIP_FILE=%ROOT_DIR%\duckstation-windows-x64-release.zip"
SET "EXTRACT_TEMP_DIR=%ROOT_DIR%\duckstation-windows-x64-release"

SET "PYTHON_URL=https://www.python.org/ftp/python/3.14.0/python-3.14.0-amd64.exe"
SET "PYTHON_INSTALLER=%TEMP%\python-installer.exe"
SET "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
SET "PLAYER_EXE=%LOCALAPPDATA%\Programs\Python\Python314\Scripts\soundscope-player.exe"

:: Launcher Executable and Setup Binary Paths
SET "LAUNCHER_EXE=%ROOT_DIR%\Play SoundScope.exe"
SET "SETUP_EXE=%ROOT_DIR%\Setup SoundScope.exe"
SET "EXCLUDE_FILE=%TEMP%\soundscope_xcopy_exclude.txt"

ECHO ========================================================
ECHO        SoundScope Unified Installer by XxZer0ModZxX
ECHO ========================================================
ECHO Root Directory: %ROOT_DIR%
ECHO.

:: -----------------------------------------------------
:: 1. BIOS Verification Check
:: -----------------------------------------------------
ECHO [1/7] Checking BIOS directory requirement...
SET "BIOS_FOUND=0"
IF EXIST "%BIOS_DIR%" (
    FOR %%F IN ("%BIOS_DIR%\*.bin") DO (
        SET "BIOS_FOUND=1"
    )
)

IF "!BIOS_FOUND!"=="0" (
    ECHO [ERROR] No .bin BIOS file found in "%BIOS_DIR%".
    ECHO Please place a valid PlayStation BIOS .bin file in the bios folder and restart setup.
    PAUSE
    EXIT /B 1
)
ECHO [OK] Valid BIOS file detected in "%BIOS_DIR%".
ECHO.

:: -----------------------------------------------------
:: 2. Downloading, Extracting & Restructuring DuckStation
:: -----------------------------------------------------
ECHO [2/7] Preparing DuckStation environment...

:: Download DuckStation zip archive if Duckstation folder doesn't exist
IF NOT EXIST "%DS_DIR%" (
    IF NOT EXIST "%EXTRACT_TEMP_DIR%" (
        ECHO Downloading latest DuckStation release archive...
        powershell -Command "$ProgressPreference = 'SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%ZIP_URL%' -OutFile '%ZIP_FILE%'"
        IF !ERRORLEVEL! EQU 0 (
            ECHO [OK] Archive downloaded successfully.
        ) ELSE (
            ECHO [ERROR] Failed to download DuckStation archive.
            PAUSE
            EXIT /B 1
        )

        ECHO Extracting archive files to duckstation-windows-x64-release...
        IF NOT EXIST "%EXTRACT_TEMP_DIR%" MKDIR "%EXTRACT_TEMP_DIR%"
        powershell -Command "$ProgressPreference = 'SilentlyContinue'; Expand-Archive -Path '%ZIP_FILE%' -DestinationPath '%EXTRACT_TEMP_DIR%' -Force"
        IF !ERRORLEVEL! EQU 0 (
            ECHO [OK] Archive extracted successfully.
        ) ELSE (
            ECHO [ERROR] Failed to extract archive.
            PAUSE
            EXIT /B 1
        )
    )
) ELSE (
    ECHO [INFO] "Duckstation" folder already exists. Skipping download.
)

:: Rename folder "duckstation-windows-x64-release" to "Duckstation"
IF EXIST "%EXTRACT_TEMP_DIR%" (
    ECHO Renaming folder "duckstation-windows-x64-release" to "Duckstation"...
    REN "%EXTRACT_TEMP_DIR%" "Duckstation"
    IF !ERRORLEVEL! EQU 0 (
        ECHO [OK] Folder renamed successfully.
    ) ELSE (
        ECHO [ERROR] Failed to rename folder.
    )
)

:: Rename executable duckstation-qt-x64-ReleaseLTCG.exe to duckstation-qt.exe
IF EXIST "%DS_DIR%\duckstation-qt-x64-ReleaseLTCG.exe" (
    ECHO Renaming executable "duckstation-qt-x64-ReleaseLTCG.exe" to "duckstation-qt.exe"...
    REN "%DS_DIR%\duckstation-qt-x64-ReleaseLTCG.exe" "duckstation-qt.exe"
    IF !ERRORLEVEL! EQU 0 (
        ECHO [OK] Executable renamed successfully.
    ) ELSE (
        ECHO [ERROR] Failed to rename executable.
    )
) ELSE (
    ECHO [INFO] Executable "duckstation-qt-x64-ReleaseLTCG.exe" not found. Skipping executable rename.
)

:: Create audio_files directory if missing
IF NOT EXIST "%AUDIO_DIR%" MKDIR "%AUDIO_DIR%"
ECHO.

:: -----------------------------------------------------
:: 3. Applying Patch & Configuration Files
:: -----------------------------------------------------
ECHO [3/7] Applying preconfigured patch files...
IF EXIST "%PATCH_DIR%" (
    :: Copy launcher executable to root folder
    IF EXIST "%PATCH_DIR%\Play SoundScope.exe" (
        ECHO Copying "Play SoundScope.exe" to root directory...
        COPY /Y "%PATCH_DIR%\Play SoundScope.exe" "%LAUNCHER_EXE%" >nul
    )

    IF EXIST "%DS_DIR%" (
        ECHO Copying all contents from "%PATCH_DIR%" to "%DS_DIR%"...
        
        :: Create temporary exclude file for xcopy to skip root launcher and setup binaries
        ECHO Setup SoundScope.exe> "%EXCLUDE_FILE%"
        ECHO Play SoundScope.exe>> "%EXCLUDE_FILE%"

        XCOPY "%PATCH_DIR%\*" "%DS_DIR%\" /E /H /C /I /Y /EXCLUDE:%EXCLUDE_FILE% >nul
        IF !ERRORLEVEL! EQU 0 (
            ECHO [OK] Configuration patch applied successfully.
        ) ELSE (
            ECHO [ERROR] An error occurred during patch file copy.
        )
        IF EXIST "%EXCLUDE_FILE%" DEL "%EXCLUDE_FILE%" >nul 2>&1
    ) ELSE (
        ECHO [WARNING] Target folder "%DS_DIR%" does not exist. Cannot copy patch.
    )
) ELSE (
    ECHO [INFO] Source folder "%PATCH_DIR%" not found. Skipping configuration patch.
)
ECHO.

:: -----------------------------------------------------
:: 4. Python Verification & Auto-Installation
:: -----------------------------------------------------
ECHO [4/7] Checking Python installation...
"%PYTHON_EXE%" --version >nul 2>&1
IF !ERRORLEVEL! EQU 0 GOTO PYTHON_OK

python --version >nul 2>&1
IF !ERRORLEVEL! EQU 0 (
    SET "PYTHON_EXE=python"
    GOTO PYTHON_OK
)

ECHO [INFO] Python not found. Downloading Python 3.14 installer...
powershell -Command "$ProgressPreference = 'SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'"
IF !ERRORLEVEL! NEQ 0 (
    ECHO [ERROR] Failed to download Python installer.
    PAUSE
    EXIT /B 1
)

ECHO Installing Python silently (adding to PATH)...
START /WAIT "" "%PYTHON_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
IF EXIST "%PYTHON_INSTALLER%" DEL /F /Q "%PYTHON_INSTALLER%" >nul 2>&1

"%PYTHON_EXE%" --version >nul 2>&1
IF !ERRORLEVEL! EQU 0 GOTO PYTHON_OK

python --version >nul 2>&1
IF !ERRORLEVEL! EQU 0 (
    SET "PYTHON_EXE=python"
    GOTO PYTHON_OK
)

ECHO [ERROR] Python installation completed but could not be verified.
PAUSE
EXIT /B 1

:PYTHON_OK
ECHO [OK] Using Python binary: %PYTHON_EXE%
ECHO.

:: -----------------------------------------------------
:: 5. Binary & Package Verification
:: -----------------------------------------------------
ECHO [5/7] Installing SoundScope Python package...
IF NOT EXIST "%DS_DIR%\duckstation-qt.exe" ECHO [WARNING] Missing duckstation-qt.exe in %DS_DIR%
IF NOT EXIST "%DS_DIR%\ffmpeg.exe" ECHO [WARNING] Missing ffmpeg.exe in %DS_DIR%

CD /D "%SOUNDSCOPE_DIR%"
"%PYTHON_EXE%" -m pip install -e .
IF ERRORLEVEL 1 (
    ECHO [ERROR] Failed to install SoundScope package.
    PAUSE
    EXIT /B 1
)
ECHO [OK] SoundScope package installed.
ECHO.

:: -----------------------------------------------------
:: 6. Cleanup Temporary Download Archive
:: -----------------------------------------------------
ECHO [6/7] Cleaning up temporary files...
IF EXIST "%ZIP_FILE%" (
    DEL /F /Q "%ZIP_FILE%" >nul 2>&1
    ECHO [OK] Deleted downloaded zip archive.
) ELSE (
    ECHO [INFO] No zip archive to delete.
)
ECHO.

:: -----------------------------------------------------
:: 7. Refresh Windows Explorer View
:: -----------------------------------------------------
ECHO [7/7] Refreshing folder view...
powershell -Command "$code = '[DllImport(\"shell32.dll\")] public static extern void SHChangeNotify(int wEventId, uint uFlags, IntPtr dwItem1, IntPtr dwItem2);'; $type = Add-Type -MemberDefinition $code -Name 'WinAPI' -Namespace 'Explorer' -PassThru; $type::SHChangeNotify(0x8000000, 0, [IntPtr]::Zero, [IntPtr]::Zero)" >nul 2>&1
ECHO [OK] Folder view updated.

ECHO.
ECHO ======================================================
ECHO         SoundScope Setup Completed Successfully!
ECHO ======================================================
ECHO Executable placed at:
ECHO %LAUNCHER_EXE%
ECHO.
ECHO Add audio files like '.mp3', '.wav', '.flac', '.ogg' in the audio_files folder.
ECHO When done, click on Play SoundScope.exe in the root folder.
ECHO.

PAUSE

:: Switch working directory to SystemRoot so no folder locks remain
CD /D "%SystemRoot%"

:: Schedule config_patch and Setup SoundScope.exe deletion in an independent background cmd session after script exits
START "" /MIN cmd /c "timeout /t 1 /nobreak >nul & if exist "%PATCH_DIR%" rmdir /s /q "%PATCH_DIR%" & if exist "%SETUP_EXE%" del /f /q "%SETUP_EXE%""

EXIT