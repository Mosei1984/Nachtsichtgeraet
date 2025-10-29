#!/usr/bin/env python3
"""
Debug-Script für Terminal-Integration
Zeigt ob Terminal-Button funktioniert und Touch-Events ankommen
"""

import sys
import os

# Füge den Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 50)
print("DEBUG: Terminal Integration")
print("=" * 50)

# 1. Imports prüfen
print("\n[1] Imports prüfen...")
try:
    from terminal_access.terminal_launcher import TerminalLauncher
    from terminal_access.touch_button import TerminalButton
    print("  ✓ terminal_launcher importiert")
    print("  ✓ touch_button importiert")
except ImportError as e:
    print(f"  ✗ Import-Fehler: {e}")
    sys.exit(1)

# 2. Terminal-Button erstellen
print("\n[2] Terminal-Button erstellen...")
try:
    button = TerminalButton(x=10, y=280, width=70, height=30)
    print(f"  ✓ Button erstellt: Position ({button.x}, {button.y}), Größe {button.width}x{button.height}")
except Exception as e:
    print(f"  ✗ Button-Fehler: {e}")
    sys.exit(1)

# 3. Touch-Test
print("\n[3] Touch-Hit-Testing...")
test_coords = [
    (45, 295, True, "Button-Mitte"),
    (10, 280, True, "Button links-oben"),
    (80, 310, True, "Button rechts-unten"),
    (5, 295, False, "Links außerhalb"),
    (100, 295, False, "Rechts außerhalb"),
    (45, 250, False, "Oben außerhalb"),
    (45, 320, False, "Unten außerhalb"),
]

for x, y, should_hit, desc in test_coords:
    hit = button.is_touched(x, y)
    status = "✓" if hit == should_hit else "✗"
    print(f"  {status} ({x:3d}, {y:3d}): {desc} -> {hit}")

# 4. Terminal-Launcher erstellen
print("\n[4] Terminal-Launcher erstellen...")
try:
    launcher = TerminalLauncher("/dev/fb1", "/dev/input/event0")
    print("  ✓ Launcher erstellt")
except Exception as e:
    print(f"  ✗ Launcher-Fehler: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 5. Verfügbarkeits-Check
print("\n[5] Terminal-Funktionen prüfen...")
try:
    if hasattr(launcher, 'terminal'):
        print(f"  ✓ terminal vorhanden: {launcher.terminal is not None}")
    if hasattr(launcher, 'keyboard'):
        print(f"  ✓ keyboard vorhanden: {launcher.keyboard is not None}")
    if hasattr(launcher, 'active'):
        print(f"  ✓ active state: {launcher.active}")
except Exception as e:
    print(f"  ✗ Fehler: {e}")

# 6. Integration in nachtsicht_fullscreen.py prüfen
print("\n[6] nachtsicht_fullscreen.py Integration prüfen...")
try:
    with open('nachtsicht_fullscreen.py', 'r') as f:
        content = f.read()
        
    checks = [
        ('terminal_access.terminal_launcher import', 'TerminalLauncher' in content),
        ('terminal_access.touch_button import', 'TerminalButton' in content),
        ('TERMINAL_AVAILABLE', 'TERMINAL_AVAILABLE' in content),
        ('terminal_launcher =', 'terminal_launcher = TerminalLauncher' in content),
        ('terminal_button =', 'terminal_button = TerminalButton' in content),
        ('terminal_button.draw', 'terminal_button.draw' in content),
        ('terminal_launcher.toggle', 'terminal_launcher.toggle' in content or 'terminal_launcher.update' in content),
    ]
    
    for name, found in checks:
        status = "✓" if found else "✗"
        print(f"  {status} {name}")
        
except Exception as e:
    print(f"  ✗ Fehler beim Lesen: {e}")

# 7. Rendering-Test
print("\n[7] Rendering-Test...")
try:
    import cv2
    import numpy as np
    
    # Test-Frame erstellen
    frame = np.zeros((320, 480, 3), dtype=np.uint8)
    
    # Button zeichnen
    button.draw(frame)
    
    # Prüfen ob was gezeichnet wurde
    if frame.max() > 0:
        print("  ✓ Button wird auf Frame gerendert")
    else:
        print("  ✗ Button wird NICHT gerendert (Frame ist schwarz)")
        
    # Frame speichern
    cv2.imwrite('/tmp/debug_button.png', frame)
    print("  ✓ Test-Frame gespeichert: /tmp/debug_button.png")
    
except Exception as e:
    print(f"  ✗ Rendering-Fehler: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("Debug abgeschlossen")
print("=" * 50)

# 8. Live-Test-Vorschlag
print("\nZum Live-Test:")
print("  1. Schaue /tmp/debug_button.png an")
print("  2. Prüfe nachtsicht_fullscreen.py auf fehlende Integration")
print("  3. Führe aus: sudo systemctl status nachtsicht.service")
print("  4. Prüfe Logs: sudo journalctl -u nachtsicht.service -n 50")
