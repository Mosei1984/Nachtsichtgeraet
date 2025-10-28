# Nachtsichtgerät - Agent Instructions

## Commands
- **Run main script**: `python3 nachtsicht_fullscreen.py` or `python3 nachtsicht_optimized.py`
- **Install dependencies**: `sudo apt-get install python3-opencv python3-picamera2 python3-numpy`
- **No formal tests**: Test manually on Raspberry Pi hardware

## Architecture
- **Platform**: Raspberry Pi 3 B with Raspbian (Trixy)
- **Hardware**: 3.5" SPI Display (/dev/fb1), ADS7846 Touch (/dev/input/event0), IR-optimized Picamera2
- **Main files**: `nachtsicht_fullscreen.py` (current), `nachtsicht_optimized.py` (performance optimized)
- **Storage**: USB-first (/media/usb*), fallback to /home/valentin for photos/videos
- **State machine**: idle → live → recording → live

## Code Style
- **Language**: Python 3, German comments/documentation
- **Imports**: stdlib first, then third-party (cv2, numpy, picamera2)
- **Naming**: snake_case functions/variables, UPPER_CASE constants
- **Config**: Top-level constants section (FB_PATH, TOUCH_DEV, timing thresholds)
- **Error handling**: Try/except with fallbacks; graceful shutdown on KeyboardInterrupt
- **Performance**: Pre-allocated buffers, in-place operations, caching for optimized version
- **No type hints**: Existing code doesn't use them, keep consistent
