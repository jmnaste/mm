# Mouse Mover (MM)

A Python app that prevents your computer from going idle by simulating mouse movements and keyboard input when inactive.

## Features
- **Platform**: Windows (uses `GetLastInputInfo` API)
- **Double-verification system** to prevent interrupting active users
- Mouse movement (1 pixel, instant) + Shift key press during idle periods only
- Configurable idle threshold (default: 2 minutes)
- Real-time status monitoring with timestamped console output

## Enhanced Workflow (Safe Idle-Only Movement)
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

**Why the safety delay?**
- User might press a key/move mouse RIGHT AFTER the idle check but BEFORE mm() executes
- The 2-3 second delay + re-check ensures idle state is sustained
- Prevents interrupting users who just became active
- Example: T+0s: idle check passes ✓ → T+1s: user starts typing → T+2s: re-check fails ✓, movement skipped


## Installation & Usage

**Prerequisites**: Python 3.x, Windows, PyAutoGUI

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run**
   ```bash
   # Safe mode (default, with idle verification)
   python mm.py
   
   # Original mode (without verification)
   python mm.py --original
   ```

3. **Output**
   ```
   ............ 14:30 - Active (idle: 45s)
   ............ 14:32 - MM
   ............ 14:34 - Skipped (user became active)
   ```
   - Dots every 10s, timestamp every 2 min
   - **MM** = movement triggered, **Skipped** = user active, **Active** = working

4. **Stop**: Press `Ctrl+C`

## Configuration

Edit [mm.py](mm.py):
- Idle threshold: `if idle_time >= 120:` (seconds)
- Check interval: `time.sleep(10)` (seconds)
- Mouse movement: `pyautogui.moveTo(x + 1, y, duration=0)` (pixels, duration)

## Use Cases
- Prevent screen timeout during presentations/monitoring
- Keep messaging apps showing "active" status
- Maintain VPN/remote desktop connections

## Troubleshooting
- **Permission errors**: Run terminal as administrator
- **PyAutoGUI not working**: Check security software blocking automation
- **PowerShell execution policy**: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

⚠️ **Use responsibly** - Some organizations prohibit idle prevention tools. Ensure compliance with your policies.

## License
Utility script provided as-is for personal use.
