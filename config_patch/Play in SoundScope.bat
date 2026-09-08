@echo off 
TITLE SoundScope Launcher 
SET "DS_DIR=C:\Users\Anonymous\Desktop\PSX SoundScope Player\Duckstation" 
SET "AUDIO_DIR=C:\Users\Anonymous\Desktop\PSX SoundScope Player\audio_files" 
SET "PYTHON_EXE=C:\Users\Anonymous\AppData\Local\Programs\Python\Python314\python.exe" 
SET "PLAYER_EXE=C:\Users\Anonymous\AppData\Local\Programs\Python\Python314\Scripts\soundscope-player.exe" 
SET "PATH=%DS_DIR%;C:\Users\Anonymous\AppData\Local\Programs\Python\Python314\Scripts;%PATH%" 
 
IF NOT "%~1"=="" GOTO PLAY_DROPPED 
 
ECHO Loading audio files from audio_files directory... 
"C:\Users\Anonymous\AppData\Local\Programs\Python\Python314\python.exe" -c "import os, glob, subprocess, sys; exts = ('.mp3', '.wav', '.flac', '.ogg'); files = [f for f in glob.glob(os.path.join(r'%AUDIO_DIR%', '*')) if f.lower().endswith(exts)]; sys.exit(subprocess.call([r'%PLAYER_EXE%'] + files)) if files else (print('[WARNING] No audio files found in audio_files folder'), sys.exit(1))" 
IF ERRORLEVEL 1 PAUSE 
EXIT /B 
 
:PLAY_DROPPED 
ECHO Processing dropped audio file(s)... 
"C:\Users\Anonymous\AppData\Local\Programs\Python\Python314\Scripts\soundscope-player.exe" %* 
IF ERRORLEVEL 1 PAUSE 
EXIT /B 
