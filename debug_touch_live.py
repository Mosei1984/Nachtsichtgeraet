#!/usr/bin/env python3
"""
Live Touch Debug - zeigt Touch-Events und Button-Position
"""

import os
import sys
import select
import struct as st
import time

TOUCH_DEV = "/dev/input/event0"
ABS_X = 0x00
ABS_Y = 0x01
BTN_TOUCH = 0x14a

# Display-Auflösung
DISPLAY_W = 480
DISPLAY_H = 320

# Terminal-Button Position (sollte gleich wie in nachtsicht_fullscreen.py sein)
BUTTON_X = 10
BUTTON_Y = DISPLAY_H - 40  # 320 - 40 = 280
BUTTON_W = 70
BUTTON_H = 30

print("=" * 60)
print("LIVE TOUCH DEBUG")
print("=" * 60)
print(f"Display: {DISPLAY_W}x{DISPLAY_H}")
print(f"Terminal-Button: ({BUTTON_X}, {BUTTON_Y}) - {BUTTON_W}x{BUTTON_H}")
print(f"Button-Bereich: X={BUTTON_X}-{BUTTON_X+BUTTON_W}, Y={BUTTON_Y}-{BUTTON_Y+BUTTON_H}")
print("=" * 60)
print("\nTippe auf den Bildschirm...")
print("Strg+C zum Beenden\n")

# Touch-Device öffnen
try:
    touch_fd = os.open(TOUCH_DEV, os.O_RDONLY | os.O_NONBLOCK)
    print(f"✓ {TOUCH_DEV} geöffnet\n")
except Exception as e:
    print(f"✗ Fehler beim Öffnen von {TOUCH_DEV}: {e}")
    sys.exit(1)

cur_x = 0
cur_y = 0
finger_down = False
down_time = 0

EVENT_SIZE = 24

try:
    while True:
        # Warte auf Events
        ready, _, _ = select.select([touch_fd], [], [], 0.1)
        
        if ready:
            data = os.read(touch_fd, EVENT_SIZE)
            if len(data) < EVENT_SIZE:
                continue
                
            sec, usec, etype, code, value = st.unpack("llHHI", data)
            
            if etype == 0x03:  # EV_ABS
                if code == ABS_X:
                    cur_x = value
                elif code == ABS_Y:
                    cur_y = value
                    
            elif etype == 0x01 and code == BTN_TOUCH:
                if value == 1 and not finger_down:
                    # Finger down
                    finger_down = True
                    down_time = time.time()
                    
                    # Koordinaten normalisieren
                    norm_x = int(cur_x * DISPLAY_W / 4095)
                    norm_y = int(cur_y * DISPLAY_H / 4095)
                    
                    print(f"\n[DOWN]  Raw: ({cur_x:4d}, {cur_y:4d})  ->  Display: ({norm_x:3d}, {norm_y:3d})")
                    
                elif value == 0 and finger_down:
                    # Finger up
                    finger_down = False
                    press_len = time.time() - down_time
                    
                    # Koordinaten normalisieren
                    norm_x = int(cur_x * DISPLAY_W / 4095)
                    norm_y = int(cur_y * DISPLAY_H / 4095)
                    
                    # Button-Hit-Test
                    in_button_x = BUTTON_X <= norm_x <= (BUTTON_X + BUTTON_W)
                    in_button_y = BUTTON_Y <= norm_y <= (BUTTON_Y + BUTTON_H)
                    in_button = in_button_x and in_button_y
                    
                    status = "✓ BUTTON GETROFFEN!" if in_button else "  außerhalb"
                    
                    print(f"[UP]    Raw: ({cur_x:4d}, {cur_y:4d})  ->  Display: ({norm_x:3d}, {norm_y:3d})  {status}")
                    print(f"        Dauer: {press_len:.3f}s")
                    
                    if in_button:
                        print(f"        >>> TERMINAL SOLLTE JETZT ÖFFNEN! <<<")
                    else:
                        # Zeige Distanz zum Button
                        if norm_x < BUTTON_X:
                            print(f"        -> {BUTTON_X - norm_x}px zu weit links")
                        elif norm_x > BUTTON_X + BUTTON_W:
                            print(f"        -> {norm_x - (BUTTON_X + BUTTON_W)}px zu weit rechts")
                            
                        if norm_y < BUTTON_Y:
                            print(f"        -> {BUTTON_Y - norm_y}px zu weit oben")
                        elif norm_y > BUTTON_Y + BUTTON_H:
                            print(f"        -> {norm_y - (BUTTON_Y + BUTTON_H)}px zu weit unten")
                    
except KeyboardInterrupt:
    print("\n\nAbgebrochen")
finally:
    os.close(touch_fd)
    print("Touch-Device geschlossen")
