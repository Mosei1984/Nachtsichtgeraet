#!/usr/bin/env python3
"""
Test Keyboard Y-Mapping
"""

# Display Setup
DISPLAY_H = 320
KEYBOARD_Y_OFFSET = 180  # Tastatur beginnt bei Y=180
KEYBOARD_HEIGHT = 140     # 180 bis 320
NUM_ROWS = 5
ROW_HEIGHT = KEYBOARD_HEIGHT // NUM_ROWS  # 28px pro Zeile

print("=" * 60)
print("KEYBOARD Y-MAPPING TEST")
print("=" * 60)
print(f"Display Höhe: {DISPLAY_H}")
print(f"Tastatur Y-Offset: {KEYBOARD_Y_OFFSET}")
print(f"Tastatur Höhe: {KEYBOARD_HEIGHT}")
print(f"Zeilen: {NUM_ROWS}, Höhe pro Zeile: {ROW_HEIGHT}")
print()

print("Tastatur-Zeilen (Display-Koordinaten):")
for i in range(NUM_ROWS):
    y_start = KEYBOARD_Y_OFFSET + (i * ROW_HEIGHT)
    y_end = y_start + ROW_HEIGHT
    row_names = ["1-9-0-BKSP", "q-w-e...", "a-s-d...", "SHIFT-z-x...", "CTRL-ESC..."]
    print(f"  Zeile {i+1} ({row_names[i]:12s}): Y={y_start:3d} bis {y_end:3d}")

print()
print("=" * 60)
print("TOUCH-TEST Ergebnisse:")
print("=" * 60)

# Aus dem Debug-Log:
# User tippt Zeile 1, trifft aber SHIFT (Zeile 4) bei y=264
user_touch_y = 276  # Durchschnitt aus Debug (273-281)
hit_row = "SHIFT (Zeile 4)"
hit_y = 264

print(f"User tippt auf: Zeile 1 (1-9-0-BKSP)")
print(f"Touch kommt an: y={user_touch_y}")
print(f"Getroffen: {hit_row} @ y={hit_y}")
print()

# Berechne Differenz
offset = user_touch_y - hit_y
print(f"Offset: {offset}px zu hoch")
print()

# Wo SOLLTE der Touch ankommen für Zeile 1?
zeile1_y_start = KEYBOARD_Y_OFFSET + 0  # 180
zeile1_y_end = zeile1_y_start + ROW_HEIGHT  # 208
zeile1_y_mitte = (zeile1_y_start + zeile1_y_end) // 2  # 194

print(f"Zeile 1 sollte sein: y={zeile1_y_start}-{zeile1_y_end} (Mitte: {zeile1_y_mitte})")
print(f"Touch kam an bei: y={user_touch_y}")
print(f"Differenz: {user_touch_y - zeile1_y_mitte}px")
print()

print("=" * 60)
print("LÖSUNG:")
print("=" * 60)

# Die Touch-Y-Koordinate muss transformiert werden
# Aktuell: raw_y -> norm_y direkt
# Vermutung: Y-Achse muss auch gespiegelt werden

print("Aktuelle Transformation:")
print("  norm_y = cur_x * 480 / 4095")
print()
print("Mögliche Fixes:")
print("  1. Y-Achse spiegeln: norm_y = 480 - (cur_x * 480 / 4095)")
print("  2. Y-Offset korrigieren")
print("  3. Andere Achsen-Zuordnung")
