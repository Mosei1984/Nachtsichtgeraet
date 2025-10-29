# Nachtsichtgerät - Agent Instructions

## Commands
- **Run main script**: `python3 nachtsicht_fullscreen.py` or `python3 nachtsicht_optimized.py`
- **Install dependencies**: `sudo apt-get install python3-opencv python3-picamera2 python3-numpy python3-pip && pip3 install pyte`
- **Terminal tests**: `python3 terminal_access/test_vkeyboard.py` and `python3 terminal_access/test_terminal_emu.py`
- **No formal tests**: Test manually on Raspberry Pi hardware

## Architecture
- **Platform**: Raspberry Pi 3 B with Raspbian (Trixy)
- **Hardware**: 3.5" SPI Display (/dev/fb1), ADS7846 Touch (/dev/input/event0), IR-optimized Picamera2
- **Main files**: `nachtsicht_fullscreen.py` (current), `nachtsicht_optimized.py` (performance optimized)
- **Storage**: USB-first (/media/usb*), fallback to /home/valentin for photos/videos
- **State machine**: idle → live → recording → live
- **Terminal Access**: Integrated virtual keyboard + PTY terminal (480x180 terminal, 480x140 keyboard)

## Code Style
- **Language**: Python 3, German comments/documentation
- **Imports**: stdlib first, then third-party (cv2, numpy, picamera2)
- **Naming**: snake_case functions/variables, UPPER_CASE constants
- **Config**: Top-level constants section (FB_PATH, TOUCH_DEV, timing thresholds)
- **Error handling**: Try/except with fallbacks; graceful shutdown on KeyboardInterrupt
- **Performance**: Pre-allocated buffers, in-place operations, caching for optimized version
- **No type hints**: Existing code doesn't use them, keep consistent

## Terminal Access Module
- **Virtual Keyboard**: `terminal_access/vkeyboard.py` - QWERTY layout with shift/ctrl/alt/symbols
- **Terminal Emulator**: `terminal_access/terminal_emulator.py` - PTY-based with pyte VT100 emulation
- **Launcher**: `terminal_access/terminal_launcher.py` - Integration and lifecycle management
- **Tests**: `test_vkeyboard.py`, `test_terminal_emu.py`, `test_integration.py`
- **Setup**: `setup_terminal.sh` installs pyte and dependencies
