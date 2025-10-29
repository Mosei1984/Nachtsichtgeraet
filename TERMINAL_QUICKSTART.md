# Terminal Access - Quick Start Guide

## Installation (5 minutes)

### On Raspberry Pi

```bash
# 1. Install dependencies
sudo apt-get update
sudo apt-get install -y python3-pip
pip3 install pyte

# 2. Or use automated setup
cd /opt/nachtsicht/terminal_access
sudo bash setup_terminal.sh

# 3. Reboot (for group permissions)
sudo reboot
```

## Usage

### Opening Terminal

1. Start Nachtsicht app (double-tap to go live)
2. Look for orange "TERM" button in bottom-left corner
3. Tap button → Terminal opens with keyboard

### Using Terminal

```
┌─────────────────────────────────┐
│ bash-5.1$ ls                    │ ← Terminal output
│ file1.py file2.txt              │   (180px high)
│ bash-5.1$ _                     │
├─────────────────────────────────┤
│ ` 1 2 3 4 5 6 7 8 9 0 - = BKSP │ ← Virtual keyboard
│ TAB q w e r t y u i o p [ ] \  │   (140px high)
│ ESC a s d f g h j k l ; ' ENTER│
│ SHIFT z x c v b n m , . / ↑ SHT│
│ CTRL ALT SYM [SPACE] SYM ← ↓ → │ ← EXIT button here
└─────────────────────────────────┘
```

### Typing Commands

1. **Tap letters** on keyboard
2. **Tap ENTER** to execute
3. **Tap EXIT** (bottom-right) to close terminal

### Example Session

```
# List files
ls -la
[ENTER]

# Show current directory
pwd
[ENTER]

# Edit a file (requires nano installed)
nano test.txt
[ENTER]

# Exit terminal
[Tap EXIT button]
```

## Keyboard Reference

### Quick Keys

| Key | Action |
|-----|--------|
| ENTER | Execute command |
| BKSP | Backspace/Delete |
| TAB | Tab completion |
| ESC | Escape |
| ↑ ↓ | Command history |
| EXIT | Close terminal |

### Modifiers

| Modifier | How to use |
|----------|------------|
| SHIFT | Tap once → next key is uppercase |
| CTRL | Tap once → next key is Ctrl+key |
| SYM | Toggle symbol layout |
| ABC | Back to normal layout |

### Common Commands

| Command | Tap sequence |
|---------|--------------|
| Ctrl+C | CTRL → c |
| Ctrl+D | CTRL → d (exit shell) |
| ls | l → s → ENTER |
| pwd | p → w → d → ENTER |

## Testing (Before Deployment)

### Test 1: Keyboard Test (30 seconds)

```bash
python3 terminal_access/test_vkeyboard.py
```

Should see:
```
[TEST] Tastatur-Rendering...
  ✓ Tastatur wird gerendert
[TEST] Touch-Hit-Testing...
  ✓ Taste erkannt: `
  ✓ Außerhalb korrekt erkannt
...
ALLE TESTS BESTANDEN ✓
```

### Test 2: Terminal Test (30 seconds)

```bash
python3 terminal_access/test_terminal_emu.py
```

Should see:
```
[TEST] Terminal Start/Stop...
  ✓ Terminal gestartet (PID: 1234)
  ✓ Terminal gestoppt
...
ALLE TESTS BESTANDEN ✓
```

### Test 3: Full System Test (1 minute)

```bash
python3 nachtsicht_fullscreen.py
```

1. Wait for camera to start
2. Tap TERM button
3. Should see terminal + keyboard
4. Tap some keys
5. Text should appear
6. Tap EXIT
7. Back to camera

## Troubleshooting (90% of issues)

### "pyte not found"

```bash
pip3 install pyte
```

### "Terminal doesn't open"

Check dependencies:
```bash
python3 -c "import pyte; print('OK')"
```

### "Keyboard not visible"

Keyboard should appear automatically with terminal. If not:
- Check if terminal_launcher.launch_terminal() succeeded
- Look for errors in console

### "Keys don't work"

- Make sure you're tapping on keyboard area (bottom 140 pixels)
- Wait for finger release before next tap
- Try typing slowly first

### "Terminal freezes"

- Terminal uses non-blocking I/O, shouldn't freeze
- If frozen, tap EXIT button
- Check logs: `journalctl -u nachtsicht.service -f`

## Common Tasks

### System Update

```
Tap TERM
Type: sudo apt-get update
Tap ENTER
Type password if prompted
Type: sudo apt-get upgrade
Tap ENTER
Wait for completion
Tap EXIT
```

### Edit Configuration

```
Tap TERM
Type: nano /opt/nachtsicht/nachtsicht_fullscreen.py
Tap ENTER
Use arrow keys to navigate
Edit file
Ctrl+X to exit
y to save
ENTER to confirm
Tap EXIT
```

### Reboot System

```
Tap TERM
Type: sudo reboot
Tap ENTER
System will restart
```

### Check Disk Space

```
Tap TERM
Type: df -h
Tap ENTER
Read output
Tap EXIT
```

## Performance Tips

1. **Type slowly** - Touch detection needs time
2. **Wait for output** - Commands may take 0.5-1s to appear
3. **Don't spam keys** - Each tap is registered
4. **Use EXIT button** - Don't type "exit" unless necessary

## Keyboard Layouts

### Normal Layout (default)

```
` 1 2 3 4 5 6 7 8 9 0 - = BKSP
TAB q w e r t y u i o p [ ] \
ESC a s d f g h j k l ; ' ENTER
SHIFT z x c v b n m , . / ↑ SHIFT
```

### Shift Layout (tap SHIFT once)

```
~ ! @ # $ % ^ & * ( ) _ + BKSP
TAB Q W E R T Y U I O P { } |
ESC A S D F G H J K L : " ENTER
SHIFT Z X C V B N M < > ? ↑ SHIFT
```

### Symbol Layout (tap SYM)

```
` 1 2 3 4 5 6 7 8 9 0 - = BKSP
TAB ! @ # $ % ^ & * ( ) _ + \
ESC ~ { } [ ] | ; : ' " < ENTER
SHIFT / ? . , < > = + - _ ↑ SHIFT
```

Tap ABC to go back to normal.

## Advanced Usage

### Scripting

You can send commands programmatically:

```python
from terminal_access.terminal_launcher import TerminalLauncher

launcher = TerminalLauncher()
launcher.launch_terminal()

# Send command
launcher.terminal.write(b'ls -la\n')

# Read output
time.sleep(0.5)
launcher.update()
screen = launcher.terminal.get_screen_text()
print(screen)
```

### Custom Keyboard Layouts

Edit `terminal_access/vkeyboard.py`:

```python
LAYOUT_NORMAL = [
    ['your', 'custom', 'layout'],
    [...],
]
```

### Terminal Size

Edit `terminal_access/terminal_launcher.py`:

```python
self.terminal = TerminalEmulator(
    width=480,
    height=180,  # Change this
    cols=60,     # And this
    rows=20      # And this
)
```

## Documentation

- **Full docs**: `terminal_access/README_VKEYBOARD.md`
- **Implementation**: `TERMINAL_IMPLEMENTATION.md`
- **Original README**: `terminal_access/README.md`

## Support

If terminal access doesn't work:

1. Check dependencies: `pip3 list | grep pyte`
2. Run tests: `python3 terminal_access/test_*.py`
3. Check logs: `journalctl -u nachtsicht.service -f`
4. Try manual start: `python3 nachtsicht_fullscreen.py`
5. Review error messages in console

## Quick Reference Card

```
┌─────────────────────────────────┐
│  TERMINAL ACCESS QUICK REF      │
├─────────────────────────────────┤
│ Open:    Tap TERM button        │
│ Close:   Tap EXIT button        │
│ Execute: Tap ENTER              │
│ Delete:  Tap BKSP               │
│ Cancel:  CTRL → c               │
│ Quit:    CTRL → d               │
│ Upper:   Tap SHIFT once         │
│ Symbols: Tap SYM toggle         │
│ Arrows:  ↑ ↓ ← → at bottom      │
└─────────────────────────────────┘
```

---

**Ready to use!** Start with the tests, then try the main app.
