#!/usr/bin/env python3
"""
Test verschiedene Touch-Rotationen
"""

DISPLAY_W = 480
DISPLAY_H = 320

# Test-Punkt: User tippt unten links (sollte 10, 280 sein)
# Kommt an als: raw_x=2409, raw_y=3644 -> norm: 282, 284

raw_x = 2409
raw_y = 3644

print("=" * 60)
print("TOUCH ROTATION TEST")
print("=" * 60)
print(f"Display: {DISPLAY_W}x{DISPLAY_H}")
print(f"Target: Unten links = (10, 280)")
print(f"Raw Touch: ({raw_x}, {raw_y})")
print()

# Standard normalisierung
norm_x = int(raw_x * DISPLAY_W / 4095)
norm_y = int(raw_y * DISPLAY_H / 4095)
print(f"Standard:           ({norm_x:3d}, {norm_y:3d})")

# Rotation 0° (nur spiegeln)
rot_x = DISPLAY_W - norm_x
rot_y = norm_y
print(f"Spiegeln X:         ({rot_x:3d}, {rot_y:3d})")

rot_x = norm_x
rot_y = DISPLAY_H - norm_y
print(f"Spiegeln Y:         ({rot_x:3d}, {rot_y:3d})")

rot_x = DISPLAY_W - norm_x
rot_y = DISPLAY_H - norm_y
print(f"Spiegeln X+Y:       ({rot_x:3d}, {rot_y:3d})")

# 90° rotation
rot_x = norm_y
rot_y = DISPLAY_W - norm_x
print(f"Rotation 90°:       ({rot_x:3d}, {rot_y:3d})")

# 180° rotation
rot_x = DISPLAY_W - norm_x
rot_y = DISPLAY_H - norm_y
print(f"Rotation 180°:      ({rot_x:3d}, {rot_y:3d})")

# 270° rotation  
rot_x = DISPLAY_H - norm_y
rot_y = norm_x
print(f"Rotation 270°:      ({rot_x:3d}, {rot_y:3d})")

# Achsen tauschen
rot_x = norm_y
rot_y = norm_x
print(f"Achsen tauschen:    ({rot_x:3d}, {rot_y:3d})")

# Achsen tauschen + spiegeln X
rot_x = DISPLAY_H - norm_y
rot_y = norm_x
print(f"Tauschen + Spieg X: ({rot_x:3d}, {rot_y:3d})")

# Achsen tauschen + spiegeln Y
rot_x = norm_y
rot_y = DISPLAY_W - norm_x
print(f"Tauschen + Spieg Y: ({rot_x:3d}, {rot_y:3d})")

# Achsen tauschen + spiegeln beide
rot_x = DISPLAY_H - norm_y
rot_y = DISPLAY_W - norm_x
print(f"Tauschen + Spieg XY:({rot_x:3d}, {rot_y:3d})")

print()
print("=" * 60)
print("Welche Variante kommt näher an (10, 280)?")
