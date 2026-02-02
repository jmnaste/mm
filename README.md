# Mouse Mover (MM)

A lightweight Python application that prevents your computer from going idle by automatically simulating mouse movements and keyboard input when the system has been inactive.

## Specifications

### Overview
- **Purpose**: Keeps your computer active by simulating user input when idle time exceeds a threshold
- **Platform**: Windows
- **Language**: Python 3.x
- **Main Dependencies**: PyAutoGUI, ctypes (Windows API)

### Key Features
- Monitors system idle time using Windows API
- Automatic mouse movement simulation **only during genuine idle periods**
- **Double-verification system** to prevent interrupting active users
- Keyboard input simulation (Shift key press)
- Real-time status monitoring with timestamped console output
- Configurable idle timeout threshold (default: 2 minutes)
- Graceful shutdown with Ctrl+C

### Technical Details
- **Idle Detection**: Uses Windows `GetLastInputInfo` API to track last user input
- **Check Interval**: 10 seconds
- **Idle Threshold**: 120 seconds (2 minutes)
- **Safety Verification**: Re-checks idle status immediately before movement to ensure user is still inactive
- **Minimum Idle Time**: Requires consistent idle state (prevents action if user just became active)
- **Status Update**: Every 2 minutes with timestamp
- **Mouse Movement**: Minimal horizontal movement (1-2 pixels right only, no return movement)
- **Movement Duration**: Instant (no animation duration to minimize disruption)
- **Keyboard Action**: Simulates Shift key press

### Proposed Enhancement: Safe Movement Execution

**Problem**: Current implementation may trigger mouse movement when user becomes active between idle check and movement execution, causing interruption.

**Solution**: Implement a multi-stage verification process:

1. **Initial Idle Check** (existing)
   - Every 2 minutes, check if system idle >= 2 minutes

2. **Pre-Movement Verification** (NEW)
   - Immediately before executing movement, re-check idle status
   - Ensure idle time is still >= threshold (120 seconds)
   - Only proceed if verification confirms continued idle state

3. **Optional: Sustained Idle Requirement** (RECOMMENDED)
   - **Why needed**: There's a time gap between checking idle status and executing movement
   - **The problem**: User might press a key/move mouse RIGHT AFTER the idle check but BEFORE the mm() execution
   - **The solution**: Wait 2-3 seconds after initial check, then verify again
   - **Net effect**: Effectively increases the minimum idle threshold from 120s to 122-123s
   - **Example scenario**:
     - T+0s: System checks, finds user idle for 120s ✓
     - T+1s: User returns to keyboard and starts typing
     - T+2s: Without safety delay, mm() would execute and interrupt user ✗
     - T+2s: With safety delay, re-check detects user is active (only 1s idle), skips movement ✓
   - **In other words**: Verifies the idle state is sustained/maintained for the duration of the safety delay

**Benefits**:
- ✅ Prevents interrupting users who just became active
- ✅ Ensures movements only occur during genuine idle periods
- ✅ Eliminates annoying mouse movements during work
- ✅ Maintains original functionality for keeping system active

## Solution

### Architecture
The application consists of three main components:

1. **Idle Detection System** (`get_idle_duration()`)
   - Utilizes Windows API via ctypes
   - Queries `GetLastInputInfo` to get the last input timestamp
   - Calculates idle duration by comparing with current tick count

2. **Mouse Mover Function** (`mm()`)
   - Captures current mouse position
   - Moves cursor slightly (5 pixels right and back)
   - Presses the Shift key to simulate keyboard activity

3. **Main Loop**
   - Runs continuously until interrupted
   - Prints progress dots every 10 seconds
   - Checks idle time every 2 minutes
   - Triggers mouse movement if idle threshold exceeded
   - Displays timestamped status updates

### Current Workflow
```
Start → Check every 10s → 2 min elapsed?
                              ↓ Yes
                        Get idle time → Idle > 2 min?
                              ↓ Yes
                        Execute mm() → Move mouse & press key
                              ↓
                        Display timestamp & status
                              ↓
                        Continue loop
```

### Proposed Enhanced Workflow (Safe Idle-Only Movement)
```
Start → Check every 10s → 2 min elapsed?
                              ↓ Yes
                        Get idle time → Idle > 2 min?
                              ↓ Yes
                        Wait 2-3 seconds (optional safety delay)
                              ↓
                        Re-check idle time → Still Idle > 2 min?
                              ↓ Yes               ↓ No
                        Execute mm()        Skip (user is active)
                              ↓                   ↓
                        Display timestamp & status
                              ↓
                        Continue loop
```

### Proposed Code Changes

**Enhanced `mm()` function with safety check:**

```python
def safe_mm():
    """
    Executes mouse movement only if system is confirmed to be idle.
    Includes pre-movement verification to prevent interrupting active users.
    """
    # Final safety check before movement
    idle_time = get_idle_duration()
    if idle_time < 120:
        print(" - Skipped (user became active)", end="")
        return False
    
    # Optional: Add a small delay and double-check
    time.sleep(2)
    idle_time = get_idle_duration()
    if idle_time < 122:  # Account for the 2-second delay
        print(" - Skipped (user became active)", end="")
        return False
    
    # User is confirmed idle, safe to move
    x, y = pyautogui.position()
    # Minimal horizontal movement only (1 pixel, instant)
    pyautogui.moveTo(x + 1, y, duration=0)
    pyautogui.press('shift')
    return True
```

**Updated main loop:**

```python
if idle_time >= 120:
    if safe_mm():
        print(" - MM", end="")
    # Status already printed by safe_mm() if skipped
```

### Implementation Benefits

| Aspect | Current | Enhanced |
|--------|---------|----------|
| **User Interruption** | Possible if user becomes active between check and movement | Prevented with pre-movement verification |
| **Idle Verification** | Single check every 2 minutes | Double/triple verification before action |
| **Movement Disruption** | 5 pixels right and back (noticeable) | 1 pixel horizontal only (minimal) |
| **Movement Speed** | 0.25s animated (visible) | Instant (imperceptible) |
| **User Experience** | May annoy active users | Only acts during genuine idle periods with minimal disruption |
| **Reliability** | High | Higher - reduces false positives |
| **Execution Time** | Immediate | +2-3 seconds delay (negligible) |

## How to Use

### Prerequisites
- Python 3.x installed
- Windows operating system
- Administrator privileges (recommended for keyboard/mouse simulation)

### Installation

1. **Clone or download the repository**
   ```bash
   cd d:\_dev2025\_mm
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv_mm
   ```

3. **Activate the virtual environment**
   ```bash
   # Windows PowerShell
   .\venv_mm\Scripts\Activate.ps1
   
   # Windows Command Prompt
   .\venv_mm\Scripts\activate.bat
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. **Activate the virtual environment** (if not already activated)
   ```bash
   .\venv_mm\Scripts\Activate.ps1
   ```

2. **Run the script**
   
   **Default (Safe Mode - Recommended)**:
   ```bash
   python mm.py
   ```
   This uses the new safe behavior with idle verification and minimal movement.
   
   **Original Mode**:
   ```bash
   python mm.py --original
   # or
   python mm.py -o
   ```
   This uses the original behavior without verification (may interrupt active users).

3. **Monitor the output**
   
   **Safe Mode**:
   ```
   Starting Mouse Mover in SAFE mode (default)
   Press Ctrl+C to stop
   Using safe behavior: idle verification before movement
   
   ............ 14:30 - Active (idle: 45s)
   ............ 14:32 - MM
   ............ 14:34 - Skipped (user became active)
   ............ 14:36 - Active (idle: 12s)
   ```
   
   **Original Mode**:
   ```
   Starting Mouse Mover in ORIGINAL mode
   Press Ctrl+C to stop
   Using original behavior: immediate movement without verification
   
   ............ 14:30 - Active (idle: 45s)
   ............ 14:32 - MM
   ............ 14:34 - Active (idle: 8s)
   ```
   
   - Progress dots (.) appear every 10 seconds
   - Timestamp appears every 2 minutes
   - **"Active"** shows when user is working (with idle seconds)
   - **"MM"** indicator shows when mouse movement is triggered
   - **"Skipped"** message shows when movement is prevented (safe mode only)

4. **Stop the application**
   - Press `Ctrl+C` to gracefully terminate

### Configuration

To modify the behavior, edit [mm.py](mm.py):

- **Idle threshold**: Change `if idle_time >= 120:` (line 38) - value in seconds
- **Check interval**: Change `time.sleep(10)` (line 45) - value in seconds
- **Status update frequency**: Change `if secs >= 120:` (line 30) - value in seconds
- **Mouse movement distance**: Change `pyautogui.moveTo(x + 1, y, duration=0)` - value in pixels (currently 1 pixel, horizontal only)
- **Movement animation**: `duration=0` for instant movement (no animation)

### Use Cases

- Prevent screen timeout during presentations or long-running tasks
- Keep messaging/collaboration apps showing "active" status
- Maintain VPN or remote desktop connections
- Prevent screen savers from activating during monitoring tasks

### Troubleshooting

**Issue**: Permission errors when running the script
- **Solution**: Run terminal as administrator

**Issue**: Mouse/keyboard simulation not working
- **Solution**: Ensure PyAutoGUI has necessary permissions; some security software may block automation

**Issue**: Application doesn't detect idle time correctly
- **Solution**: Verify you're on Windows OS; the `GetLastInputInfo` API is Windows-specific

**Issue**: Virtual environment activation fails in PowerShell
- **Solution**: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Safety Notes

⚠️ **Important Considerations**:
- This tool simulates user input and may interfere with security policies
- Some organizations prohibit the use of idle prevention tools
- Use responsibly and in accordance with your company's policies
- The application will continue running until manually stopped

## License

This is a utility script provided as-is for personal use.

## Contributing

Feel free to fork and modify for your needs. Suggestions for improvements:
- Cross-platform support (macOS, Linux)
- GUI interface
- Configurable settings file
- Multiple movement patterns
- Logging to file
