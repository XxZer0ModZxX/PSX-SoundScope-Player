#!/usr/bin/env python3
"""SoundScope PlayStation media player."""

#     soundscope-player
#
#     ----------------------------------------------------------------------
#     Copyright © 2022  Pellegrino Prevete
#
#     All rights reserved
#     ----------------------------------------------------------------------
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

from argparse import ArgumentParser
import glob
import os
from os.path import join as path_join
import shutil
import subprocess
import sys
import tempfile
import time

# Dynamic directory resolution pointing to Duckstation folder
current_file_dir = os.path.dirname(os.path.abspath(__file__))
ds_dir = os.path.abspath(path_join(current_file_dir, "..", ".."))

if ds_dir not in os.environ.get("PATH", ""):
    os.environ["PATH"] = ds_dir + os.pathsep + os.environ.get("PATH", "")

# Temporary cache folder
temp_cache_dir = path_join(tempfile.gettempdir(), "soundscope-cache")

dirs = {
    'data': temp_cache_dir,
    'config': temp_cache_dir,
    'cache': temp_cache_dir
}

def err(msg):
    print(msg)
    sys.exit(1)

def set_dirs():
    os.makedirs(dirs['cache'], exist_ok=True)

def kill_duckstation():
    """Kill running DuckStation process to release file locks on cached CUE/BIN files."""
    try:
        subprocess.run(["taskkill", "/F", "/IM", "duckstation-qt.exe"], 
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def clean_cache():
    kill_duckstation()
    time.sleep(0.3)
    
    if os.path.exists(dirs['cache']):
        files = glob.glob(f"{dirs['cache']}/*")
        for f in files:
            if os.path.isfile(f):
                try:
                    os.chmod(f, 0o777)
                    os.unlink(f)
                except Exception:
                    pass

def convert_to_bin(input_file, output_bin):
    """Convert input audio file directly to standard 44.1kHz 16-bit STEREO PCM BIN format."""
    ffmpeg_exe = os.path.join(ds_dir, "ffmpeg.exe")
    if not os.path.exists(ffmpeg_exe):
        err(f"ffmpeg.exe executable not found at: {ffmpeg_exe}")

    cmd = [
        ffmpeg_exe, "-y", "-i", input_file,
        "-f", "s16le", "-ar", "44100", "-ac", "2", output_bin
    ]
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=ds_dir)
    if res.returncode != 0:
        err(f"Failed to convert {input_file} to raw CD-DA BIN format.")

def generate_multi_track_cue(bin_files, cue_path):
    """Generate a multi-track redbook Audio CD CUE sheet from multiple BIN files."""
    cue_lines = []
    for idx, bin_filename in enumerate(bin_files, start=1):
        track_num = f"{idx:02d}"
        cue_lines.append(f'FILE "{bin_filename}" BINARY')
        cue_lines.append(f'  TRACK {track_num} AUDIO')
        cue_lines.append(f'    INDEX 01 00:00:00')
    
    cue_content = "\n".join(cue_lines) + "\n"
    with open(cue_path, "w", encoding="utf-8") as f:
        f.write(cue_content)

def setup_portable_mode():
    """Ensure portable.txt and settings.ini exist, fix keybindings, locate BIOS, and enforce Controller 1 Analog controller settings."""
    portable_flag = os.path.join(ds_dir, "portable.txt")
    if not os.path.exists(portable_flag):
        try:
            with open(portable_flag, "w") as f:
                f.write("")
        except Exception:
            pass

    ini_target = os.path.join(ds_dir, "settings.ini")
    ini_source = os.path.join(current_file_dir, "settings.ini")
    
    if os.path.exists(ini_source) and not os.path.exists(ini_target):
        try:
            shutil.copy2(ini_source, ini_target)
        except Exception:
            pass

    bios_dir_abs = os.path.join(ds_dir, "bios")
    
    # Automatically scan bios folder for any available .bin, .rom, or .img BIOS filename
    found_bios_filename = None
    if os.path.exists(bios_dir_abs):
        for file in os.listdir(bios_dir_abs):
            if file.lower().endswith(('.bin', '.rom', '.img')):
                found_bios_filename = file
                break

    if os.path.exists(ini_target):
        try:
            with open(ini_target, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            
            new_lines = []
            for line in lines:
                s_line = line.strip()
                if s_line.startswith("SearchDirectory"):
                    new_lines.append("SearchDirectory = bios\n")
                elif found_bios_filename and s_line.startswith("PathNTSCU"):
                    new_lines.append(f"PathNTSCU = {found_bios_filename}\n")
                elif found_bios_filename and s_line.startswith("PathNTSCJ"):
                    new_lines.append(f"PathNTSCJ = {found_bios_filename}\n")
                elif found_bios_filename and s_line.startswith("PathPAL"):
                    new_lines.append(f"PathPAL = {found_bios_filename}\n")
                elif s_line.startswith("ToggleFullscreen"):
                    new_lines.append("ToggleFullscreen = Keyboard/Alt+Return\n")
                elif s_line.startswith("Alt+Enter"):
                    new_lines.append(line.replace("Alt+Enter", "Alt+Return"))
                else:
                    new_lines.append(line)
            
            with open(ini_target, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
        except Exception:
            pass

def play(*media_src):
    set_dirs()
    clean_cache()
    setup_portable_mode()
    
    if not media_src:
        err("No media source specified.")
        
    unique_prefix = f"playback_{int(time.time())}"
    bin_filenames = []
    
    for idx, source_file in enumerate(media_src, start=1):
        bin_filename = f"{unique_prefix}_track_{idx:02d}.bin"
        bin_path = path_join(dirs['cache'], bin_filename)
        
        print(f"[{idx}/{len(media_src)}] Converting {source_file} to CD-DA format...")
        convert_to_bin(source_file, bin_path)
        bin_filenames.append(bin_filename)
    
    cue_path = path_join(dirs['cache'], f"{unique_prefix}.cue")
    print("Generating multi-track CUE sheet...")
    generate_multi_track_cue(bin_filenames, cue_path)
    
    ds_exe = os.path.join(ds_dir, "duckstation-qt.exe")
    if not os.path.exists(ds_exe):
        err(f"DuckStation executable not found at: {ds_exe}")

    # Standard launcher parameters supported by DuckStation
    ds_cmd = [ds_exe, "-fullscreen", cue_path]
    print(f"Launching DuckStation SoundScope with {len(bin_filenames)} track(s)...")
    subprocess.run(ds_cmd, cwd=ds_dir)
    clean_cache()

def main():
    parser_args = {"description": "PlayStation SoundScope player"}
    parser = ArgumentParser(**parser_args)

    media_source = {'args': ['media_source'],
                    'kwargs': {'nargs': '*',
                               'action': 'store',
                               'help': ("media source; default: current directory")}}

    parser.add_argument(*media_source['args'], **media_source['kwargs'])
    args = parser.parse_args()

    if not args.media_source:
        err("Please specify an audio file path directly in the command line.")
    else:
        media_source = args.media_source
    play(*media_source)

if __name__ == "__main__":
    main()