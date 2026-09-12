# PSX SoundScope Player (DuckStation Edition)

[![Python 3.x Support](https://img.shields.io/pypi/pyversions/Django.svg)](https://python.org)
[![License: AGPL v3+](https://img.shields.io/badge/license-AGPL%20v3%2B-blue.svg)](http://www.gnu.org/licenses/agpl-3.0) 

A PlayStation media player wrapper and audio visualizer frontend built to run original PS1 CD-ROM soundscapes via DuckStation on PC.

## About

This project is a modified version based on [SoundScope Player](https://github.com/tallero/soundscope-player) originally created by Pellegrino Prevete.
Modified and updated by XxZer0ModZxX (<XxZer0ModZxX@gmail.com>).

This software is licensed under the [GNU Affero General Public License v3 or later](https://www.gnu.org/licenses/agpl-3.0.en.html).

## Features & Modifications

* Converted for Windows environment integration.
* Automated multi-track `BIN`/`CUE` Audio CD generation using FFmpeg and FLAC tools.
* Direct launching via `duckstation-qt.exe` in fullscreen mode.
* Bundled audio utility binaries for out-of-the-box processing.

## Prerequisites & Legal Notices

To use this application, you must supply your own copy of **DuckStation** and a valid **PlayStation BIOS**.

1. **DuckStation Emulator:** Download the official release directly from [duckstation.org](https://www.duckstation.org/) or the official [DuckStation GitHub](https://github.com/stenzek/duckstation). *DuckStation is NOT bundled or redistributed with this software.*
2. **PS1 BIOS File:** You must provide a legimately dumped PS1 BIOS file (e.g., `SCPH-7000.BIN` or newer, as required for SoundScope visualizer support). *BIOS files are copyrighted property of Sony Interactive Entertainment and are NOT provided or linked by this project.*

## Included Third-Party Executables

For convenience, compiled command-line utilities are included inside the distribution. These executables are subject to their respective open-source licenses:

| Tool | Executable | License |
| :--- | :--- | :--- |
| **FFmpeg** | `ffmpeg.exe` | LGPL v2.1+ / GPL v2+ |
| **FLAC** | `flac.exe` | BSD 3-Clause |
| **MetaFLAC** | `metaflac.exe` | GPL v2 |
| **Shntool** | `shntool.exe` | GPL v2+ |

Full terms for these components are detailed in the `LICENSE` file.

## Installation & Usage

1. Download and extract **PSX SoundScope Player**.
2. Place the bios file (`SCPH-7000` or newer) into the following path -> PSX SoundScope Player\config_patch\bios
3. Launch the application Setup SoundScope.exe, a cmd prompt will open, when done press any key to finish.
4. Place your audio files in the following folder -> PSX SoundScope Player\audio_files
5. Now run Play SoundScope.exe, once compiled the player will auto startup, able to play music and able to activate the classic PSX SoundScope visualizer.

## Controls & Navigation

When running **SoundScope Player** via DuckStation, use the following controller inputs or keyboard mappings to operate the SoundScope audio visualizer:

| Action / Visualizer Function | PlayStation Controller | Default Keyboard Mapping |
| :--- | :--- | :--- |
| **Play / Pause Track** | `Cross (X)` | `X` |
| **Stop Track** | `Square` | `Z` |
| **Next / Previous Track** | `R1` / `L1` | `S` / `A` |
| **Fast Forward / Rewind** | `R2` / `L2` | `W` / `Q` |
| **Toggle Visualizer Mode** | `Triangle` | `A` / `S` |
| **Cycle Visualizer Patterns** | `D-Pad Up` / `Down` | `Up` / `Down` Arrow |
| **Adjust Visualizer Colors** | `D-Pad Left` / `Right` | `Left` / `Right` Arrow |
| **Exit / Close Emulator** | `Escape` | `Esc` |

*Note: Controls can also be customized directly within DuckStation's input settings.*
