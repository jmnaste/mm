import ctypes
import pyautogui
import time
import sys
from datetime import datetime

class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ('cbSize', ctypes.c_uint),
        ('dwTime', ctypes.c_uint),
    ]

def get_idle_duration():
    last_input_info = LASTINPUTINFO()
    last_input_info.cbSize = ctypes.sizeof(last_input_info)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(last_input_info))
    millis = ctypes.windll.kernel32.GetTickCount() - last_input_info.dwTime
    return millis / 1000.0

def mm_original():
    """Original mouse movement: 5 pixels right and back with animation"""
    x, y = pyautogui.position()
    pyautogui.moveTo(x + 5, y, duration=0.25)
    pyautogui.moveTo(x, y, duration=0.25)
    pyautogui.press('shift')

def mm_minimal():
    """Minimal mouse movement: 1 pixel right, instant"""
    x, y = pyautogui.position()
    pyautogui.moveTo(x + 1, y, duration=0)
    pyautogui.press('shift')

def safe_mm(use_original=False):
    """
    Executes mouse movement only if system is confirmed to be idle.
    Includes pre-movement verification to prevent interrupting active users.
    
    Args:
        use_original: If True, uses original movement pattern, else minimal movement
    
    Returns:
        bool: True if movement executed, False if skipped
    """
    # Final safety check before movement
    idle_time = get_idle_duration()
    if idle_time < 120:
        print(" - Skipped (user became active)", end="")
        return False
    
    # Safety delay and double-check for sustained idle
    time.sleep(2)
    idle_time = get_idle_duration()
    if idle_time < 122:  # Account for the 2-second delay
        print(" - Skipped (user became active)", end="")
        return False
    
    # User is confirmed idle, safe to move
    if use_original:
        mm_original()
    else:
        mm_minimal()
    return True
    
if __name__ == "__main__":
    # Check for command line argument for original behavior
    use_original_mode = len(sys.argv) > 1 and sys.argv[1] in ['--original', '-o']
    
    mode_text = "ORIGINAL mode" if use_original_mode else "SAFE mode (default)"
    print(f"Starting Mouse Mover in {mode_text}")
    print("Press Ctrl+C to stop")
    
    if use_original_mode:
        print("Using original behavior: immediate movement without verification")
    else:
        print("Using safe behavior: idle verification before movement")
    
    print("")
    
    try:
        secs = 0
        while True:
            print(".", end="", flush=True)
            
            secs += 10
            if secs >= 120:
                current_time = datetime.now().strftime("%H:%M")
                print(f" {current_time}", end="", flush=True)
                
                idle_time = get_idle_duration()
                if idle_time >= 120:
                    if use_original_mode:
                        # Original behavior: immediate movement
                        mm_original()
                        print(" - MM", end="")
                    else:
                        # New safe behavior: verify before movement
                        if safe_mm():
                            print(" - MM", end="")
                else:
                    # User is active, no movement needed
                    print(f" - Active (idle: {int(idle_time)}s)", end="")
                    
                print("")
                secs = 0
                
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
