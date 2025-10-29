#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Test für Terminal Access
Testet komplettes System: Terminal + Tastatur + Touch
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import cv2
import numpy as np

try:
    from terminal_access.terminal_launcher import TerminalLauncher
    TERMINAL_AVAILABLE = True
except ImportError as e:
    TERMINAL_AVAILABLE = False
    print(f"[ERROR] Terminal nicht verfügbar: {e}")

def simulate_touch_sequence(launcher, sequence):
    """
    Simuliert Touch-Sequenz
    
    Args:
        launcher: TerminalLauncher Instance
        sequence: Liste von (x, y, label) Tuples
    """
    print(f"  Simuliere {len(sequence)} Touch-Events...")
    
    for x, y, label in sequence:
        print(f"    Touch @ ({x}, {y}) -> {label}")
        exit_req = launcher.handle_touch(x, y)
        
        if exit_req:
            print("    EXIT angefordert")
            return True
            
        time.sleep(0.1)
        launcher.update()
        
    return False

def test_terminal_startup():
    """Test: Terminal starten"""
    print("[TEST] Terminal Startup...")
    
    if not TERMINAL_AVAILABLE:
        print("  [SKIP] Nicht verfügbar")
        return None
        
    launcher = TerminalLauncher()
    
    success = launcher.launch_terminal()
    assert success, "Terminal sollte starten"
    assert launcher.is_active(), "Terminal sollte aktiv sein"
    
    time.sleep(0.5)
    
    assert launcher.terminal is not None, "Terminal sollte existieren"
    assert launcher.keyboard is not None, "Keyboard sollte existieren"
    assert launcher.terminal.running, "Terminal sollte laufen"
    
    print("  ✓ Terminal gestartet")
    print(f"    PID: {launcher.terminal.pid}")
    print(f"    Aktiv: {launcher.is_active()}")
    
    return launcher

def test_keyboard_touch(launcher):
    """Test: Tastatur Touch-Handling"""
    print("[TEST] Keyboard Touch...")
    
    if not launcher:
        print("  [SKIP] Launcher nicht verfügbar")
        return
        
    # Simuliere Touch auf 'l' Taste (sollte ~x=400, y=210 sein)
    # Approximative Koordinaten - in Realität müsste man Key-Rects nutzen
    
    # Hole erstes Key aus Keyboard
    if launcher.keyboard and launcher.keyboard.key_rects:
        # Finde 'l' Taste
        l_key = launcher.keyboard.key_rects.get('l')
        if l_key:
            x = l_key['x'] + l_key['w'] // 2
            y = l_key['y'] + l_key['h'] // 2
            
            print(f"  Touch auf 'l' @ ({x}, {y})")
            exit_req = launcher.handle_touch(x, y)
            
            assert not exit_req, "l-Taste sollte kein Exit sein"
            print("  ✓ Touch auf 'l' verarbeitet")
        else:
            print("  [SKIP] 'l' Taste nicht gefunden")
    else:
        print("  [SKIP] Keyboard key_rects nicht verfügbar")

def test_command_execution(launcher):
    """Test: Kommando-Ausführung"""
    print("[TEST] Kommando-Ausführung...")
    
    if not launcher:
        print("  [SKIP] Launcher nicht verfügbar")
        return
        
    # Kommando direkt schreiben (bypass keyboard)
    print("  Sende: ls")
    launcher.terminal.write(b'ls\n')
    
    # Warte auf Output
    time.sleep(0.5)
    
    # Output lesen
    launcher.update()
    
    # Prüfe Screen-Buffer
    screen_text = launcher.terminal.get_screen_text()
    
    print(f"  Screen-Buffer: {len(screen_text)} Zeichen")
    
    # Sollte irgendwas enthalten (ls output oder prompt)
    assert len(screen_text) > 0, "Screen sollte Content haben"
    print("  ✓ Kommando ausgeführt")

def test_rendering(launcher):
    """Test: Terminal und Tastatur Rendering"""
    print("[TEST] Rendering...")
    
    if not launcher:
        print("  [SKIP] Launcher nicht verfügbar")
        return
        
    # Frame erstellen
    frame = np.zeros((320, 480, 3), dtype=np.uint8)
    
    # Rendern
    launcher.render(frame)
    
    # Prüfe ob Frame modifiziert wurde
    assert frame.any(), "Frame sollte gezeichnet sein"
    
    # Terminal-Bereich (0-180)
    terminal_area = frame[0:180, :, :]
    assert terminal_area.any(), "Terminal-Bereich sollte Content haben"
    
    # Tastatur-Bereich (180-320)
    keyboard_area = frame[180:320, :, :]
    assert keyboard_area.any(), "Tastatur-Bereich sollte Content haben"
    
    print("  ✓ Rendering funktioniert")
    print(f"    Terminal: {terminal_area.sum() / (180*480*3):.2f} avg")
    print(f"    Keyboard: {keyboard_area.sum() / (140*480*3):.2f} avg")

def test_exit_button(launcher):
    """Test: Exit-Button"""
    print("[TEST] Exit-Button...")
    
    if not launcher:
        print("  [SKIP] Launcher nicht verfügbar")
        return
        
    # Finde EXIT-Taste
    if launcher.keyboard and launcher.keyboard.key_rects:
        exit_key = launcher.keyboard.key_rects.get('EXIT')
        if exit_key:
            x = exit_key['x'] + exit_key['w'] // 2
            y = exit_key['y'] + exit_key['h'] // 2
            
            print(f"  Touch auf EXIT @ ({x}, {y})")
            exit_req = launcher.handle_touch(x, y)
            
            assert exit_req, "EXIT sollte exit_requested=True zurückgeben"
            print("  ✓ EXIT-Button funktioniert")
        else:
            print("  [SKIP] EXIT-Taste nicht gefunden")
    else:
        print("  [SKIP] Keyboard nicht verfügbar")

def test_terminal_shutdown(launcher):
    """Test: Terminal beenden"""
    print("[TEST] Terminal Shutdown...")
    
    if not launcher:
        print("  [SKIP] Launcher nicht verfügbar")
        return
        
    launcher.close_terminal()
    
    assert not launcher.is_active(), "Terminal sollte nicht mehr aktiv sein"
    assert launcher.terminal is None, "Terminal sollte None sein"
    assert launcher.keyboard is None, "Keyboard sollte None sein"
    
    print("  ✓ Terminal beendet")

def visual_integration_test():
    """Visueller Integrations-Test"""
    print("[TEST] Visueller Integrations-Test...")
    print("  Läuft 15 Sekunden lang")
    print("  Drücke 'q' zum Beenden")
    
    if not TERMINAL_AVAILABLE:
        print("  [SKIP] Nicht verfügbar")
        return
        
    launcher = TerminalLauncher()
    launcher.launch_terminal()
    
    time.sleep(0.5)
    
    # Begrüßung
    launcher.terminal.write(b'echo "=== Integration Test ==="\n')
    launcher.terminal.write(b'pwd\n')
    
    start_time = time.time()
    
    try:
        while time.time() - start_time < 15:
            launcher.update()
            
            # Frame rendern
            frame = np.zeros((320, 480, 3), dtype=np.uint8)
            launcher.render(frame)
            
            # Info overlay
            elapsed = int(time.time() - start_time)
            cv2.putText(frame, f"Integration Test: {elapsed}s / 15s", (10, 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(frame, "Druecke 'q' zum Beenden", (10, 310),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, (200, 200, 200), 1, cv2.LINE_AA)
            
            # Terminal info
            if launcher.keyboard:
                info = launcher.keyboard.get_info_text() or "Ready"
                cv2.putText(frame, info, (300, 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1, cv2.LINE_AA)
            
            cv2.imshow('Terminal Integration Test', frame)
            
            key = cv2.waitKey(100) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('1'):
                # Simuliere 'ls' Kommando
                launcher.terminal.write(b'ls\n')
            elif key == ord('2'):
                # Simuliere 'pwd'
                launcher.terminal.write(b'pwd\n')
                
    finally:
        cv2.destroyAllWindows()
        launcher.cleanup()
    
    print("  ✓ Visueller Test abgeschlossen")

def main():
    print("=" * 50)
    print("TERMINAL ACCESS INTEGRATION TEST")
    print("=" * 50)
    print()
    
    if not TERMINAL_AVAILABLE:
        print("[ERROR] Terminal Access nicht verfügbar!")
        print("[INFO] Installation: pip3 install pyte")
        return
    
    # Tests durchführen
    launcher = test_terminal_startup()
    
    if launcher:
        test_keyboard_touch(launcher)
        test_command_execution(launcher)
        test_rendering(launcher)
        test_exit_button(launcher)
        test_terminal_shutdown(launcher)
    
    print()
    print("=" * 50)
    print("ALLE TESTS BESTANDEN ✓")
    print("=" * 50)
    print()
    
    # Visueller Test
    try:
        response = input("Visuellen Test starten? (j/n): ")
        if response.lower() == 'j':
            visual_integration_test()
    except:
        pass

if __name__ == "__main__":
    main()
