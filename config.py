import os
import sys

if getattr(sys, 'frozen', False):
    # running in a bundle (e.g. dist/digital_wellbeing/digital_wellbeing.exe)
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(sys.executable)))
else:
    # running in a normal Python environment
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(ROOT_DIR, "usage.db")
STOP_FLAG_PATH = os.path.join(ROOT_DIR, "stop.flag")
