#!/usr/bin/env python3
"""
Interaktiver Keyboard Mapping Test
Zeigt Tastatur mit Kalibrierpunkten, misst Touch-Offset
"""

import cv2
import numpy as np
import os
import select
import struct
import sys

# Touch-Device
TOUCH_DEV = "/dev/input/event0"
ABS_X = 0x00
ABS_Y = 0x01
BTN_TOUCH = 0x14a
EVENT_SIZE = 24

# Display
DISPLAY_W = 480
DISPLAY_H = 320

# Keyboard Bereich
KEYBOARD_Y_OFFSET = 180
KEYBOARD_HEIGHT = 140
KEYBOARD_WIDTH = 400
KEYBOARD_X_OFFSET = 40

# Kalibrierpunkte (soll-Position auf Display)
calibration_points = [
    # Format: (x, y, label)
    (KEYBOARD_X_OFFSET + 20, KEYBOARD_Y_OFFSET + 14, "1 (Zeile 1 links)"),
    (KEYBOARD_X_OFFSET + 200, KEYBOARD_Y_OFFSET + 14, "5 (Zeile 1 mitte)"),
    (KEYBOARD_X_OFFSET + 380, KEYBOARD_Y_OFFSET + 14, "BKSP (Zeile 1 rechts)"),
    
    (KEYBOARD_X_OFFSET + 20, KEYBOARD_Y_OFFSET + 42, "q (Zeile 2 links)"),
    (KEYBOARD_X_OFFSET + 200, KEYBOARD_Y_OFFSET + 42, "u (Zeile 2 mitte)"),
    (KEYBOARD_X_OFFSET + 380, KEYBOARD_Y_OFFSET + 42, "p (Zeile 2 rechts)"),
    
    (KEYBOARD_X_OFFSET + 20, KEYBOARD_Y_OFFSET + 70, "a (Zeile 3 links)"),
    (KEYBOARD_X_OFFSET + 200, KEYBOARD_Y_OFFSET + 70, "h (Zeile 3 mitte)"),
    (KEYBOARD_X_OFFSET + 380, KEYBOARD_Y_OFFSET + 70, "ENTER (Zeile 3 rechts)"),
    
    (KEYBOARD_X_OFFSET + 100, KEYBOARD_Y_OFFSET + 98, "c (Zeile 4)"),
    (KEYBOARD_X_OFFSET + 300, KEYBOARD_Y_OFFSET + 98, "n (Zeile 4)"),
    
    (KEYBOARD_X_OFFSET + 200, KEYBOARD_Y_OFFSET + 126, "SPACE (Zeile 5)"),
]

# Gemessene Touch-Daten
touch_data = []
current_point_idx = 0

# Touch-State
cur_x = 0
cur_y = 0
norm_x = 0
norm_y = 0
finger_down = False

def apply_transform(raw_x, raw_y):
    """Aktuelle Touch-Transformation"""
    temp_x = int(raw_y * 320 / 4095)
    temp_y = int(raw_x * 480 / 4095)
    x = 320 - temp_x
    y = temp_y
    return x, y

def read_touch_event(fd):
    """Liest ein Touch-Event"""
    global cur_x, cur_y, norm_x, norm_y, finger_down
    
    ready, _, _ = select.select([fd], [], [], 0)
    if not ready:
        return None
        
    try:
        data = os.read(fd, EVENT_SIZE)
        if len(data) < EVENT_SIZE:
            return None
            
        sec, usec, etype, code, value = struct.unpack("llHHI", data)
        
        if etype == 0x03:  # EV_ABS
            if code == ABS_X:
                cur_x = value
            elif code == ABS_Y:
                cur_y = value
            norm_x, norm_y = apply_transform(cur_x, cur_y)
            
        elif etype == 0x01 and code == BTN_TOUCH:
            if value == 0 and finger_down:  # Finger up
                finger_down = False
                return ('up', norm_x, norm_y, cur_x, cur_y)
            elif value == 1 and not finger_down:  # Finger down
                finger_down = True
                
    except Exception as e:
        print(f"Error reading touch: {e}")
        
    return None

def draw_calibration_screen(current_idx):
    """Zeichnet Kalibrier-Bildschirm"""
    frame = np.zeros((DISPLAY_H, DISPLAY_W, 3), dtype=np.uint8)
    
    # Tastatur-Bereich
    cv2.rectangle(frame, 
                  (KEYBOARD_X_OFFSET, KEYBOARD_Y_OFFSET),
                  (KEYBOARD_X_OFFSET + KEYBOARD_WIDTH, KEYBOARD_Y_OFFSET + KEYBOARD_HEIGHT),
                  (50, 50, 50), -1)
    
    # Zeige alle Kalibrierpunkte
    for idx, (x, y, label) in enumerate(calibration_points):
        if idx == current_idx:
            # Aktueller Punkt - groß und grün
            color = (0, 255, 0)
            radius = 15
        elif idx < current_idx:
            # Fertige Punkte - klein und blau
            color = (255, 100, 0)
            radius = 5
        else:
            # Kommende Punkte - grau
            color = (100, 100, 100)
            radius = 5
            
        cv2.circle(frame, (x, y), radius, color, -1)
        cv2.circle(frame, (x, y), radius+2, (255, 255, 255), 1)
    
    # Anleitung
    if current_idx < len(calibration_points):
        target_x, target_y, label = calibration_points[current_idx]
        cv2.putText(frame, f"Tippe auf: {label}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, f"Punkt {current_idx+1}/{len(calibration_points)}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    else:
        cv2.putText(frame, "FERTIG! Druecke Strg+C", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    return frame

def analyze_results():
    """Analysiert gesammelte Touch-Daten"""
    print("\n" + "=" * 60)
    print("KALIBRIERUNGS-ERGEBNISSE")
    print("=" * 60)
    
    if len(touch_data) == 0:
        print("Keine Daten gesammelt")
        return
    
    print(f"\nGesammelte Punkte: {len(touch_data)}")
    print("\nSOLL -> IST (Offset):")
    print("-" * 60)
    
    offset_x_sum = 0
    offset_y_sum = 0
    
    for i, (target_x, target_y, label, touch_x, touch_y, raw_x, raw_y) in enumerate(touch_data):
        offset_x = touch_x - target_x
        offset_y = touch_y - target_y
        offset_x_sum += offset_x
        offset_y_sum += offset_y
        
        print(f"{i+1}. {label}")
        print(f"   Soll: ({target_x:3d}, {target_y:3d})")
        print(f"   Ist:  ({touch_x:3d}, {touch_y:3d})")
        print(f"   Offset: ({offset_x:+4d}, {offset_y:+4d})")
        print(f"   Raw: ({raw_x:4d}, {raw_y:4d})")
        print()
    
    # Durchschnittlicher Offset
    avg_x = offset_x_sum / len(touch_data)
    avg_y = offset_y_sum / len(touch_data)
    
    print("=" * 60)
    print(f"DURCHSCHNITTLICHER OFFSET:")
    print(f"  X: {avg_x:+.1f} px")
    print(f"  Y: {avg_y:+.1f} px")
    print("=" * 60)
    
    # Empfehlung
    print("\nEMPFOHLENE KORREKTUR in terminal_launcher.py:")
    print(f"  adjusted_x = x - {int(avg_x)}")
    print(f"  adjusted_y = y - {int(avg_y)}")
    print()

def main():
    global current_point_idx
    
    print("=" * 60)
    print("KEYBOARD MAPPING KALIBRIERUNG")
    print("=" * 60)
    print(f"\nKalibrierpunkte: {len(calibration_points)}")
    print("Tippe nacheinander auf die grünen Punkte")
    print("Strg+C zum Abbrechen\n")
    
    # Touch öffnen
    try:
        touch_fd = os.open(TOUCH_DEV, os.O_RDONLY | os.O_NONBLOCK)
        print(f"✓ {TOUCH_DEV} geöffnet\n")
    except Exception as e:
        print(f"✗ Fehler: {e}")
        return
    
    # Framebuffer öffnen (optional - könnte auch cv2.imshow verwenden)
    try:
        fb_path = "/dev/fb1"
        fb_fd = os.open(fb_path, os.O_RDWR)
        fb_size = DISPLAY_W * DISPLAY_H * 2
        import mmap
        fb_mem = mmap.mmap(fb_fd, fb_size, mmap.MAP_SHARED,
                          mmap.PROT_WRITE | mmap.PROT_READ, 0)
        use_fb = True
        print(f"✓ {fb_path} geöffnet")
    except:
        use_fb = False
        print("! Framebuffer nicht verfügbar, nur Console-Ausgabe")
    
    print("\nStart!\n")
    
    try:
        while current_point_idx < len(calibration_points):
            # Zeichne Screen
            frame = draw_calibration_screen(current_point_idx)
            
            # Zum Framebuffer schreiben
            if use_fb:
                # BGR -> RGB565
                b = (frame[:,:,0]>>3).astype(np.uint16)
                g = (frame[:,:,1]>>2).astype(np.uint16)
                r = (frame[:,:,2]>>3).astype(np.uint16)
                rgb565 = ((r<<11)|(g<<5)|b).tobytes()
                fb_mem.seek(0)
                fb_mem.write(rgb565)
            
            # Touch-Events lesen
            event = read_touch_event(touch_fd)
            if event and event[0] == 'up':
                _, touch_x, touch_y, raw_x, raw_y = event
                target_x, target_y, label = calibration_points[current_point_idx]
                
                # Daten speichern
                touch_data.append((target_x, target_y, label, touch_x, touch_y, raw_x, raw_y))
                
                offset_x = touch_x - target_x
                offset_y = touch_y - target_y
                
                print(f"✓ Punkt {current_point_idx+1}: {label}")
                print(f"  Soll: ({target_x}, {target_y}), Ist: ({touch_x}, {touch_y})")
                print(f"  Offset: ({offset_x:+d}, {offset_y:+d})\n")
                
                current_point_idx += 1
                
        # Fertig - zeige Ergebnis
        frame = draw_calibration_screen(current_point_idx)
        if use_fb:
            b = (frame[:,:,0]>>3).astype(np.uint16)
            g = (frame[:,:,1]>>2).astype(np.uint16)
            r = (frame[:,:,2]>>3).astype(np.uint16)
            rgb565 = ((r<<11)|(g<<5)|b).tobytes()
            fb_mem.seek(0)
            fb_mem.write(rgb565)
        
        # Analysiere Ergebnisse
        analyze_results()
        
        # Warte auf Strg+C
        print("\nDrücke Strg+C zum Beenden...")
        while True:
            import time
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\nAbgebrochen")
        if current_point_idx > 0:
            analyze_results()
    finally:
        os.close(touch_fd)
        if use_fb:
            fb_mem.close()
            os.close(fb_fd)

if __name__ == "__main__":
    main()
