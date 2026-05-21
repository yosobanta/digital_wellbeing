import time
from datetime import datetime
import logging
import ctypes
import os
import gc
from database import init_db, save_session
from idle import is_idle

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

IDLE_THRESHOLD_SECONDS = 60
from config import STOP_FLAG_PATH

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010

def get_active_window_info():
    try:
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return None, None
            
        # Get window title
        length = user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        window_title = buf.value
        
        # Get process name
        pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        
        app_name = "Unknown"
        h_process = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
        if h_process:
            exe_buf = ctypes.create_unicode_buffer(260)
            size = ctypes.c_ulong(260)
            if kernel32.QueryFullProcessImageNameW(h_process, 0, exe_buf, ctypes.byref(size)):
                app_name = os.path.basename(exe_buf.value)
            kernel32.CloseHandle(h_process)
            
        return app_name, window_title
    except Exception as e:
        logging.error(f"Error getting window info: {e}")
        return None, None

def run_tracker():
    init_db()
    logging.info("Starting extremely optimized usage tracker...")
    
    current_app = None
    current_title = None
    session_start_time = None
    was_idle = False
    
    while True:
        try:
            if os.path.exists(STOP_FLAG_PATH):
                logging.info("Stop flag detected. Terminating tracker...")
                os.remove(STOP_FLAG_PATH)
                if current_app and not was_idle:
                    now = datetime.now()
                    duration = int((now - session_start_time).total_seconds())
                    save_session(current_app, current_title, session_start_time, now, duration)
                break

            currently_idle = is_idle(IDLE_THRESHOLD_SECONDS)
            
            if currently_idle:
                if not was_idle and current_app:
                    end_time = datetime.now()
                    duration = int((end_time - session_start_time).total_seconds())
                    save_session(current_app, current_title, session_start_time, end_time, duration)
                    current_app = None
                
                was_idle = True
                # Aggressively collect garbage when idle to keep RAM absolutely minimal
                gc.collect() 
                time.sleep(2)
                continue
                
            app_name, window_title = get_active_window_info()
            
            if app_name and app_name != current_app:
                now = datetime.now()
                if current_app and not was_idle:
                    duration = int((now - session_start_time).total_seconds())
                    save_session(current_app, current_title, session_start_time, now, duration)
                
                current_app = app_name
                current_title = window_title
                session_start_time = now
            
            was_idle = False
            time.sleep(2)
            
        except KeyboardInterrupt:
            if current_app and not was_idle:
                now = datetime.now()
                duration = int((now - session_start_time).total_seconds())
                save_session(current_app, current_title, session_start_time, now, duration)
            break
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_tracker()
