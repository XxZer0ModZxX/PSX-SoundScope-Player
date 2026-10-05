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
#     prior FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

from argparse import ArgumentParser
import glob
import os
from os.path import join as path_join
import random
import shutil
import subprocess
import sys
import tempfile
import threading
import time

try:
    from pynput.keyboard import Key, Controller, Listener
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

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

# Global state & thread synchronization for SoundScope automation
auto_scope_active = False
automation_thread = None
toggle_lock = threading.Lock()
last_toggle_time = 0.0  # Cooldown timestamp to ignore repeat key-down events

keyboard_controller = Controller() if PYNPUT_AVAILABLE else None

# Speed offset tracker: -2 (min speed) to +5 (max speed)
speed_level = 0  
# Active visualizer index out of 26 presets (1 to 26)
current_preset_idx = 1  

def press_and_release(key, hold_time=0.04):
    """Utility to trigger a tap or long press of a keyboard key safely."""
    if keyboard_controller:
        try:
            keyboard_controller.press(key)
            time.sleep(hold_time)
            keyboard_controller.release(key)
        except Exception:
            pass

def scope_automation_loop():
    """Loops sending visualizer key combos, jumps across all 26 presets, and handles long motion blur/color holds."""
    global auto_scope_active, speed_level, current_preset_idx
    print("[SoundScope Auto] Automation started!")
    
    # Short initial grace delay to let physical key releases settle
    time.sleep(0.4)
    
    while auto_scope_active:
        action_roll = random.random()
        
        # 1. Color Changes (Q) & Motion Blur (W) with long holds (~45% chance)
        if action_roll < 0.45:
            # 50% chance for long color hold (Q)
            if random.random() < 0.50:
                color_hold = random.uniform(0.5, 1.8)
                press_and_release('q', hold_time=color_hold)
            else:
                press_and_release('q')
            
            # Frequently follow up with long motion blur hold (W)
            if random.random() < 0.70:
                time.sleep(0.05)
                blur_hold = random.uniform(0.5, 2.0) if random.random() < 0.50 else 0.04
                press_and_release('w', hold_time=blur_hold)
            
        # 2. Targeted jump across all 26 visualizer presets (~40% chance)
        elif action_roll < 0.85:
            nav_mode = random.choice(['random_preset', 'shuffle_key'])
            
            if nav_mode == 'shuffle_key':
                press_and_release('s')
                current_preset_idx = random.randint(1, 26)
            else:
                # Pick a target preset between 1 and 26 that isn't the current one
                target_preset = random.choice([p for p in range(1, 27) if p != current_preset_idx])
                
                # Determine relative jumps needed
                if target_preset > current_preset_idx:
                    steps = target_preset - current_preset_idx
                    key_to_press = Key.right
                else:
                    steps = current_preset_idx - target_preset
                    key_to_press = Key.left
                
                for _ in range(steps):
                    if not auto_scope_active:
                        break
                    press_and_release(key_to_press)
                    time.sleep(0.05)
                
                current_preset_idx = target_preset
            
        # 3. Speed Up (Up Arrow) - max 5 steps (~8% chance)
        elif action_roll < 0.93:
            if speed_level < 5:
                press_and_release(Key.up)
                speed_level += 1
            else:
                press_and_release('q', hold_time=0.8)
                
        # 4. Slow Down (Down Arrow) - max 2 steps down (~7% chance)
        else:
            if speed_level > -2:
                press_and_release(Key.down)
                speed_level -= 1
            else:
                press_and_release('w', hold_time=1.2)
        
        # Interval between actions (1.2 to 3.0 seconds)
        time.sleep(random.uniform(1.2, 3.0))
        
    print("[SoundScope Auto] Automation stopped.")

def on_key_press(key):
    """Global key listener callback to catch 'Z' toggle with debouncing."""
    global auto_scope_active, automation_thread, last_toggle_time
    try:
        if hasattr(key, 'char') and key.char in ('z', 'Z'):
            current_time = time.time()
            with toggle_lock:
                # Debounce guard: Ignore extra triggers within 0.3s (prevents key repeat issues)
                if current_time - last_toggle_time < 0.3:
                    return
                last_toggle_time = current_time
                
                if not auto_scope_active:
                    auto_scope_active = True
                    automation_thread = threading.Thread(target=scope_automation_loop, daemon=True)
                    automation_thread.start()
                else:
                    auto_scope_active = False
    except Exception:
        pass

def start_key_listener():
    """Starts global keyboard listener if pynput is available."""
    if PYNPUT_AVAILABLE:
        listener = Listener(on_press=on_key_press)
        listener.daemon = True
        listener.start()
    else:
        print("[WARNING] pynput module not found. Install pynput to enable Z-key auto-visualizer controls.")

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
    """Ensure portable.txt and settings.ini exist, fix keybindings, locate BIOS, and enforce Controller settings."""
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

    start_key_listener()

    ds_cmd = [ds_exe, "-fullscreen", cue_path]
    print(f"Launching DuckStation SoundScope with {len(bin_filenames)} track(s)...")
    subprocess.run(ds_cmd, cwd=ds_dir)
    
    global auto_scope_active
    auto_scope_active = False
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