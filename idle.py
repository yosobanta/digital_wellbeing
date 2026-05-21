import ctypes

class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint),
                ("dwTime", ctypes.c_uint)]

def get_idle_duration_seconds():
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
        millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
        
        # Handle wrap-around just in case
        if millis < 0:
            millis = 0
            
        return millis / 1000.0
    return 0

def is_idle(threshold_seconds=60):
    return get_idle_duration_seconds() > threshold_seconds
