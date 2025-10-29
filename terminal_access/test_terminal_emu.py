#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test-Skript für Terminal Emulator
Testet PTY-Management und pyte-Integration
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import cv2
import numpy as np

try:
    from terminal_access.terminal_emulator import TerminalEmulator
    TERMINAL_AVAILABLE = True
except ImportError as e:
    TERMINAL_AVAILABLE = False
    print(f"[ERROR] Terminal Emulator nicht verfügbar: {e}")
    print("[INFO] Installation: pip3 install pyte")

def test_terminal_start_stop():
    """Test: Terminal starten und stoppen"""
    if not TERMINAL_AVAILABLE:
        print("[SKIP] Terminal nicht verfügbar")
        return None
        
    print("[TEST] Terminal Start/Stop...")
    
    terminal = TerminalEmulator(width=480, height=180, cols=60, rows=20)
    
    assert not terminal.running, "Terminal sollte initial nicht laufen"
    
    terminal.start()
    time.sleep(0.5)
    
    assert terminal.running, "Terminal sollte jetzt laufen"
    assert terminal.pid is not None, "PID sollte gesetzt sein"
    assert terminal.master_fd is not None, "Master FD sollte gesetzt sein"
    print(f"  ✓ Terminal gestartet (PID: {terminal.pid})")
    
    terminal.stop()
    time.sleep(0.2)
    
    assert not terminal.running, "Terminal sollte gestoppt sein"
    print("  ✓ Terminal gestoppt")
    
    return terminal

def test_terminal_write_read():
    """Test: Schreiben und Lesen vom Terminal"""
    if not TERMINAL_AVAILABLE:
        print("[SKIP] Terminal nicht verfügbar")
        return
        
    print("[TEST] Terminal Write/Read...")
    
    terminal = TerminalEmulator(width=480, height=180, cols=60, rows=20)
    terminal.start()
    time.sleep(0.5)
    
    # Kommando senden
    terminal.write(b'echo "Hello Terminal"\n')
    time.sleep(0.3)
    
    # Output lesen
    terminal.read()
    
    # Screen-Text holen
    screen_text = terminal.get_screen_text()
    assert "Hello Terminal" in screen_text or "echo" in screen_text, \
        "Output sollte im Screen-Buffer sein"
    print("  ✓ Write/Read funktioniert")
    print(f"  Screen enthält: {len(screen_text)} Zeichen")
    
    terminal.stop()

def test_terminal_rendering():
    """Test: Terminal-Rendering"""
    if not TERMINAL_AVAILABLE:
        print("[SKIP] Terminal nicht verfügbar")
        return
        
    print("[TEST] Terminal Rendering...")
    
    terminal = TerminalEmulator(width=480, height=180, cols=60, rows=20)
    terminal.start()
    time.sleep(0.5)
    
    # Etwas Text generieren
    terminal.write(b'ls -la\n')
    time.sleep(0.3)
    terminal.read()
    
    # Frame rendern
    frame = np.zeros((320, 480, 3), dtype=np.uint8)
    terminal.render(frame, x_offset=0, y_offset=0)
    
    # Prüfe ob Frame modifiziert wurde
    assert frame[:180].any(), "Terminal-Bereich sollte gezeichnet sein"
    print("  ✓ Terminal wird gerendert")
    
    terminal.stop()

def test_terminal_is_alive():
    """Test: Terminal Alive-Check"""
    if not TERMINAL_AVAILABLE:
        print("[SKIP] Terminal nicht verfügbar")
        return
        
    print("[TEST] Terminal is_alive...")
    
    terminal = TerminalEmulator(width=480, height=180, cols=60, rows=20)
    terminal.start()
    time.sleep(0.5)
    
    assert terminal.is_alive(), "Terminal sollte laufen"
    print("  ✓ is_alive() = True")
    
    # Shell beenden
    terminal.write(b'exit\n')
    time.sleep(0.5)
    terminal.read()
    
    # Nach exit sollte Shell tot sein
    assert not terminal.is_alive(), "Terminal sollte nach exit tot sein"
    print("  ✓ is_alive() = False nach exit")
    
    terminal.stop()

def interactive_test():
    """Interaktiver Test: Terminal mit visueller Ausgabe"""
    if not TERMINAL_AVAILABLE:
        print("[SKIP] Terminal nicht verfügbar")
        return
        
    print("[TEST] Interaktiver Test...")
    print("  Drücke 'q' zum Beenden")
    print("  Terminal läuft 10 Sekunden lang")
    
    terminal = TerminalEmulator(width=480, height=180, cols=60, rows=20)
    terminal.start()
    
    # Begrüßung
    terminal.write(b'echo "=== Terminal Emulator Test ==="\n')
    terminal.write(b'echo "Zeige Verzeichnis-Inhalt:"\n')
    terminal.write(b'ls -la\n')
    
    start_time = time.time()
    
    try:
        while time.time() - start_time < 10:
            terminal.read()
            
            frame = np.zeros((320, 480, 3), dtype=np.uint8)
            terminal.render(frame, x_offset=0, y_offset=0)
            
            # Info-Text
            elapsed = int(time.time() - start_time)
            cv2.putText(frame, f"Zeit: {elapsed}s / 10s", (10, 200),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
            cv2.putText(frame, "Druecke 'q' zum Beenden", (10, 220),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1, cv2.LINE_AA)
            
            cv2.imshow('Terminal Test', frame)
            
            key = cv2.waitKey(100) & 0xFF
            if key == ord('q'):
                break
    finally:
        cv2.destroyAllWindows()
        terminal.stop()
    
    print("  ✓ Interaktiver Test abgeschlossen")

def main():
    print("=" * 50)
    print("TERMINAL EMULATOR TEST")
    print("=" * 50)
    print()
    
    if not TERMINAL_AVAILABLE:
        print("[ERROR] Terminal Emulator nicht verfügbar!")
        print("[INFO] Installation: pip3 install pyte")
        return
    
    test_terminal_start_stop()
    test_terminal_write_read()
    test_terminal_rendering()
    test_terminal_is_alive()
    
    print()
    print("=" * 50)
    print("ALLE TESTS BESTANDEN ✓")
    print("=" * 50)
    print()
    
    # Interaktiver Test (optional)
    try:
        response = input("Interaktiven Test starten? (j/n): ")
        if response.lower() == 'j':
            interactive_test()
    except:
        pass

if __name__ == "__main__":
    main()
