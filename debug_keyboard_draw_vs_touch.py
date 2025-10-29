#!/usr/bin/env python3
"""
Debug: Zeigt wo Tasten GEZEICHNET werden vs. wo TOUCH ankommt
Direkter Vergleich ohne Offsets
"""

import cv2
import numpy as np
import os
import select
import struct
import time

# Display
DISPLAY_W = 480
DISPLAY_H = 320

# Touch
TOUCH_DEV = "/dev/input/event0"
ABS_X = 0x00
ABS_Y = 0x01
BTN_TOUCH = 0x14a
EVENT_SIZE = 24

# Touch State
cur_x = 0
cur_y = 0
norm_x = 0
norm_y = 0
finger_down = False

# Touch History
touch_marks = []

def apply_transform(raw_x, raw_y):
    """Aktuelle Touch-Transformation (wie in nachtsicht_fullscreen.py)"""
    temp_x = int(raw_y * 320 / 4095)
    temp_y = int(raw_x * 480 / 4095)
    x = 320 - temp_x
    y = temp_y
    return x, y

def draw_keyboard_outline():
    """Zeichnet Tastatur GENAU wie VirtualKeyboard es tut"""
    frame = np.zeros((DISPLAY_H, DISPLAY_W, 3), dtype=np.uint8)
    
    # Keyboard Parameter (aus vkeyboard.py)
    kbd_width = 400
    kbd_height = 140
    kbd_y_offset = 180
    kbd_x_offset = 40
    
    # Layout
    layout = [
        ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'BKSP'],
        ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
        ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'ENTER'],
        ['SHIFT', 'z', 'x', 'c', 'v', 'b', 'n', 'm', '.', '/', 'UP'],
        ['CTRL', 'ESC', 'TAB', 'SPACE', 'SYM', 'LF', 'DN', 'RT', 'EXIT']
    ]
    
    num_rows = len(layout)
    row_height = kbd_height // num_rows  # 28px
    
    # Zeichne jede Zeile
    for row_idx, row in enumerate(layout):
        y = kbd_y_offset + (row_idx * row_height)
        num_keys = len(row)
        
        # Einfach: jede Taste gleich breit
        key_width = kbd_width // num_keys
        
        x_pos = kbd_x_offset
        for key in row:
            # Taste zeichnen
            cv2.rectangle(frame, 
                         (x_pos, y),
                         (x_pos + key_width - 2, y + row_height - 2),
                         (0, 100, 200), 2)
            
            # Label
            label_x = x_pos + 5
            label_y = y + 18
            cv2.putText(frame, key, (label_x, label_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            x_pos += key_width
    
    # Legende
    cv2.putText(frame, "BLAU: Gezeichnete Tasten", (10, 20),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 100, 0), 1)
    cv2.putText(frame, "GRUEN: Touch-Positionen", (10, 40),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv2.putText(frame, "Tippe auf Tasten!", (10, 160),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    
    # Zeichne Touch-Marks
    for tx, ty, raw_x, raw_y in touch_marks[-20:]:  # Letzte 20
        cv2.circle(frame, (tx, ty), 5, (0, 255, 0), -1)
        cv2.circle(frame, (tx, ty), 7, (255, 255, 255), 1)
        # Info
        cv2.putText(frame, f"({tx},{ty})", (tx+10, ty-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)
    
    return frame

def read_touch():
    """Liest Touch-Events"""
    global cur_x, cur_y, norm_x, norm_y, finger_down
    
    if not os.path.exists(TOUCH_DEV):
        return None
        
    try:
        fd = os.open(TOUCH_DEV, os.O_RDONLY | os.O_NONBLOCK)
    except:
        return None
    
    events = []
    
    while True:
        ready, _, _ = select.select([fd], [], [], 0)
        if not ready:
            break
            
        try:
            data = os.read(fd, EVENT_SIZE)
            if len(data) < EVENT_SIZE:
                break
                
            sec, usec, etype, code, value = struct.unpack("llHHI", data)
            
            if etype == 0x03:  # EV_ABS
                if code == ABS_X:
                    cur_x = value
                elif code == ABS_Y:
                    cur_y = value
                norm_x, norm_y = apply_transform(cur_x, cur_y)
                
            elif etype == 0x01 and code == BTN_TOUCH:
                if value == 0 and finger_down:  # Up
                    finger_down = False
                    events.append(('up', norm_x, norm_y, cur_x, cur_y))
                elif value == 1:  # Down
                    finger_down = True
        except:
            break
    
    os.close(fd)
    return events

def main():
    print("=" * 60)
    print("KEYBOARD DRAW vs TOUCH DEBUG")
    print("=" * 60)
    print("\nZeigt wo Tasten GEZEICHNET werden (blau)")
    print("und wo TOUCH ankommt (grün)")
    print("\nTippe auf verschiedene Tasten!")
    print("Strg+C zum Beenden\n")
    
    # Framebuffer öffnen
    try:
        fb_fd = os.open("/dev/fb1", os.O_RDWR)
        import mmap
        fb_mem = mmap.mmap(fb_fd, DISPLAY_W * DISPLAY_H * 2,
                          mmap.MAP_SHARED, mmap.PROT_WRITE | mmap.PROT_READ, 0)
        print("✓ Framebuffer geöffnet\n")
    except Exception as e:
        print(f"✗ Fehler: {e}")
        return
    
    try:
        while True:
            # Touch lesen
            events = read_touch()
            if events:
                for event in events:
                    if event[0] == 'up':
                        _, tx, ty, raw_x, raw_y = event
                        touch_marks.append((tx, ty, raw_x, raw_y))
                        print(f"Touch: ({tx:3d}, {ty:3d}) <- raw({raw_x:4d}, {raw_y:4d})")
            
            # Frame zeichnen
            frame = draw_keyboard_outline()
            
            # Zu Framebuffer
            b = (frame[:,:,0]>>3).astype(np.uint16)
            g = (frame[:,:,1]>>2).astype(np.uint16)
            r = (frame[:,:,2]>>3).astype(np.uint16)
            rgb565 = ((r<<11)|(g<<5)|b).tobytes()
            fb_mem.seek(0)
            fb_mem.write(rgb565)
            
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\n\nAbgebrochen")
        print(f"Gesammelte Touch-Punkte: {len(touch_marks)}")
        
        if touch_marks:
            print("\nLetzte 5 Touch-Punkte:")
            for tx, ty, raw_x, raw_y in touch_marks[-5:]:
                print(f"  Touch: ({tx:3d}, {ty:3d}) <- Raw: ({raw_x:4d}, {raw_y:4d})")
                
    finally:
        fb_mem.close()
        os.close(fb_fd)

if __name__ == "__main__":
    main()
