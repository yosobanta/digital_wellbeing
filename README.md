# Digital Wellbeing Tracker

A hyper-lightweight, privacy-friendly desktop digital wellbeing and application usage tracker for Windows. 

Designed from the ground up for absolute minimal system footprint, this tracker runs completely silently in the background, consuming practically 0% CPU and keeping RAM usage strictly under 10MB by utilizing pure C-Types for Windows API interaction.

## Features

- **Ultra-Lightweight Background Daemon:** The core tracker runs as a single compiled executable (`digital_wellbeing.exe`) fully detached from the console. 
- **Pure `ctypes` Engine:** Bypasses heavy dependencies like `pywin32` and `psutil`, talking directly to Windows `user32.dll` and `kernel32.dll` to keep memory consumption at the absolute bare minimum.
- **Smart Idle Detection:** Tracks system idle time and pauses tracking if you step away from your keyboard/mouse for more than 60 seconds.
- **Privacy First (Local Only):** All your usage statistics are stored safely on your machine using a lightweight SQLite database (`usage.db`). No cloud syncing, no keystroke logging, no screenshots.
- **Graphical Dashboard:** A sleek, minimalistic Tkinter UI that visualizes your daily app usage using an embedded Matplotlib Pie Chart.
- **Dashboard Controls:** Built-in "Start Tracker" and "Stop Tracker" buttons allow you to seamlessly manage the background daemon without ever opening Task Manager.

## Architecture

- `tracker.py`: The core daemon loop. Tracks active foreground windows and logs session durations.
- `idle.py`: Detects system inactivity using `GetLastInputInfo`.
- `database.py`: Manages the local SQLite database creation and querying.
- `report.py`: The visual dashboard and control center.

## Requirements

The core tracker relies solely on Python standard libraries (`ctypes`, `sqlite3`). The graphical dashboard requires:
- `matplotlib`
- `psutil`

To install the dashboard dependencies:
```bash
pip install -r requirements.txt
```

## How to Run

### Option 1: The Dashboard (Recommended)
1. Double-click the **Digital Wellbeing** shortcut on your Desktop (or run `python report.py`).
2. Click **Start Tracker** to spin up the background daemon. You can now close the dashboard; the tracker will continue to run silently.
3. Open the dashboard at any time to view your updated daily usage stats and graphs.
4. Click **Stop Tracker** when you want to safely terminate the background tracking.

### Option 2: Running from Source
If you are developing or haven't compiled the tracker yet, you can run the UI directly:
```bash
python report.py
```
*(Note: To test the Start Tracker button via the UI, you must first compile the tracker into the `dist/` directory as shown below).*

## Compiling the Tracker

To compile the background tracker into a standalone, single-process executable (`digital_wellbeing.exe`), install `pyinstaller` and run:

```bash
pyinstaller --noconsole --onedir --clean --name digital_wellbeing tracker.py
```

This creates the `dist/digital_wellbeing` folder containing the optimized executable that the dashboard UI controls.
