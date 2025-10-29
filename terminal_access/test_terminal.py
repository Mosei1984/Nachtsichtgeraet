#!/usr/bin/env python3
"""
Test-Script für Terminal Access
Startet Terminal manuell zum Debuggen
"""

import subprocess
import os
import time

print("Terminal Access Test")
print("=" * 40)

# Test 1: lxterminal vorhanden?
print("\n[1] Prüfe lxterminal...")
try:
    result = subprocess.run(['which', 'lxterminal'], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✓ lxterminal gefunden: {result.stdout.strip()}")
    else:
        print("✗ lxterminal NICHT gefunden!")
        print("  Installation: sudo apt-get install lxterminal")
        exit(1)
except Exception as e:
    print(f"✗ Fehler: {e}")
    exit(1)

# Test 2: Display verfügbar?
print("\n[2] Prüfe Display...")
if os.path.exists('/dev/fb1'):
    print("✓ /dev/fb1 vorhanden")
else:
    print("✗ /dev/fb1 NICHT vorhanden!")

# Test 3: DISPLAY Variable
print("\n[3] Umgebungsvariablen...")
print(f"  DISPLAY: {os.environ.get('DISPLAY', 'nicht gesetzt')}")
print(f"  FRAMEBUFFER: {os.environ.get('FRAMEBUFFER', 'nicht gesetzt')}")

# Test 4: Terminal starten
print("\n[4] Starte lxterminal...")
print("  Drücke Strg+C zum Beenden")
print()

try:
    env = os.environ.copy()
    env['DISPLAY'] = ':0'
    
    # Verschiedene Geometrie-Optionen testen
    geometries = [
        '60x20',      # Spalten x Zeilen
        '480x320',    # Pixel (sollte ignoriert werden)
        '70x24',      # Größer
    ]
    
    for geom in geometries:
        print(f"\n  Teste Geometrie: {geom}")
        print(f"  Befehl: lxterminal --geometry={geom}")
        
        proc = subprocess.Popen(
            ['lxterminal', f'--geometry={geom}', '--title=Test Terminal'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print(f"  ✓ Gestartet (PID: {proc.pid})")
        print(f"  Warte 3 Sekunden...")
        time.sleep(3)
        
        # Prüfe ob noch läuft
        if proc.poll() is None:
            print(f"  ✓ Terminal läuft noch")
            proc.terminate()
            proc.wait()
            print(f"  ✓ Terminal beendet")
        else:
            stdout, stderr = proc.communicate()
            print(f"  ✗ Terminal beendet sich selbst!")
            if stderr:
                print(f"  Fehler: {stderr.decode()}")
        
        print()
        
except KeyboardInterrupt:
    print("\n\nAbgebrochen")
except Exception as e:
    print(f"\n✗ Fehler: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 40)
print("Test abgeschlossen")
