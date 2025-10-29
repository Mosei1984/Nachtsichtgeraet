#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test-Skript für virtuelle Tastatur
Simuliert Touch-Events und prüft Key-Mapping
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import cv2
import numpy as np
from terminal_access.vkeyboard import VirtualKeyboard

def test_keyboard_rendering():
    """Test: Tastatur-Rendering"""
    print("[TEST] Tastatur-Rendering...")
    
    keyboard = VirtualKeyboard(width=480, height=140, y_offset=180)
    
    frame = np.zeros((320, 480, 3), dtype=np.uint8)
    keyboard.draw(frame)
    
    # Prüfe ob Frame modifiziert wurde
    assert frame[180:320].any(), "Tastatur-Bereich sollte gezeichnet sein"
    print("  ✓ Tastatur wird gerendert")
    
    return keyboard

def test_key_hit_testing(keyboard):
    """Test: Touch-Hit-Testing"""
    print("[TEST] Touch-Hit-Testing...")
    
    # Teste Taste in linker oberer Ecke (sollte '`' sein)
    key = keyboard.hit_test(10, 190)
    assert key is not None, "Taste sollte erkannt werden"
    print(f"  ✓ Taste erkannt: {key}")
    
    # Teste außerhalb der Tastatur
    key = keyboard.hit_test(10, 10)
    assert key is None, "Außerhalb sollte keine Taste sein"
    print("  ✓ Außerhalb korrekt erkannt")
    
def test_normal_keys(keyboard):
    """Test: Normale Tasten"""
    print("[TEST] Normale Tasten...")
    
    # Teste Buchstaben
    key_bytes, exit_req = keyboard.process_key('a')
    assert key_bytes == b'a', "Taste 'a' sollte 'a' zurückgeben"
    assert not exit_req, "Exit sollte nicht angefordert sein"
    print("  ✓ Buchstabe 'a' korrekt")
    
    # Teste Zahlen
    key_bytes, exit_req = keyboard.process_key('5')
    assert key_bytes == b'5', "Taste '5' sollte '5' zurückgeben"
    print("  ✓ Zahl '5' korrekt")
    
def test_special_keys(keyboard):
    """Test: Spezial-Tasten"""
    print("[TEST] Spezial-Tasten...")
    
    # Enter
    key_bytes, exit_req = keyboard.process_key('ENTER')
    assert key_bytes == b'\r', "ENTER sollte \\r sein"
    print("  ✓ ENTER korrekt")
    
    # Backspace
    key_bytes, exit_req = keyboard.process_key('BKSP')
    assert key_bytes == b'\x7f', "BKSP sollte DEL sein"
    print("  ✓ BACKSPACE korrekt")
    
    # ESC
    key_bytes, exit_req = keyboard.process_key('ESC')
    assert key_bytes == b'\x1b', "ESC sollte ESC sein"
    print("  ✓ ESC korrekt")
    
    # Arrow keys
    key_bytes, exit_req = keyboard.process_key('UP')
    assert key_bytes == b'\x1b[A', "UP sollte ANSI-Sequenz sein"
    print("  ✓ UP-Arrow korrekt")
    
def test_modifier_keys(keyboard):
    """Test: Modifier-Tasten"""
    print("[TEST] Modifier-Tasten...")
    
    # Shift aktivieren
    assert not keyboard.shift_active, "Shift sollte initial aus sein"
    keyboard.process_key('SHIFT')
    assert keyboard.shift_active, "Shift sollte jetzt aktiv sein"
    print("  ✓ SHIFT toggle funktioniert")
    
    # Ctrl aktivieren
    keyboard.process_key('CTRL')
    assert keyboard.ctrl_active, "CTRL sollte aktiv sein"
    print("  ✓ CTRL toggle funktioniert")
    
    # Ctrl+C testen
    key_bytes, exit_req = keyboard.process_key('c')
    assert key_bytes == b'\x03', "Ctrl+C sollte \\x03 sein"
    assert not keyboard.ctrl_active, "CTRL sollte nach Taste aus sein"
    print("  ✓ Ctrl+C korrekt")
    
def test_shift_layout(keyboard):
    """Test: Shift-Layout"""
    print("[TEST] Shift-Layout...")
    
    keyboard.shift_active = False
    keyboard.process_key('SHIFT')
    
    # Großbuchstabe
    key_bytes, exit_req = keyboard.process_key('A')
    assert key_bytes == b'A', "Shift+'a' sollte 'A' sein"
    assert not keyboard.shift_active, "Shift sollte nach Taste aus sein"
    print("  ✓ Shift-Layout korrekt")
    
def test_symbols_layout(keyboard):
    """Test: Symbol-Layout"""
    print("[TEST] Symbol-Layout...")
    
    keyboard.process_key('SYM')
    assert keyboard.symbols_active, "Symbols sollte aktiv sein"
    print("  ✓ Symbol-Layout aktiviert")
    
    keyboard.process_key('ABC')
    assert not keyboard.symbols_active, "ABC sollte Symbols deaktivieren"
    print("  ✓ ABC zurück zu normal")
    
def test_exit_key(keyboard):
    """Test: Exit-Taste"""
    print("[TEST] Exit-Taste...")
    
    key_bytes, exit_req = keyboard.process_key('EXIT')
    assert exit_req, "EXIT sollte exit_requested=True zurückgeben"
    assert key_bytes is None, "EXIT sollte keine Bytes senden"
    print("  ✓ EXIT-Taste korrekt")

def visual_test():
    """Visueller Test: Zeigt Tastatur-Layouts an"""
    print("[TEST] Visueller Test...")
    print("  Drücke 'n' für Normal, 's' für Shift, 'y' für Symbols, 'q' zum Beenden")
    
    keyboard = VirtualKeyboard(width=480, height=140, y_offset=0)
    
    while True:
        frame = np.zeros((140, 480, 3), dtype=np.uint8)
        keyboard.draw(frame)
        
        # Info-Text
        info = keyboard.get_info_text() or "NORMAL"
        cv2.putText(frame, info, (10, 130), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1, cv2.LINE_AA)
        
        cv2.imshow('VKeyboard Test', frame)
        
        key = cv2.waitKey(100) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('n'):
            keyboard.shift_active = False
            keyboard.symbols_active = False
            keyboard._calculate_key_positions()
        elif key == ord('s'):
            keyboard.shift_active = True
            keyboard.symbols_active = False
            keyboard._calculate_key_positions()
        elif key == ord('y'):
            keyboard.symbols_active = True
            keyboard._calculate_key_positions()
    
    cv2.destroyAllWindows()
    print("  ✓ Visueller Test abgeschlossen")

def main():
    print("=" * 50)
    print("VIRTUELLE TASTATUR TEST")
    print("=" * 50)
    
    keyboard = test_keyboard_rendering()
    test_key_hit_testing(keyboard)
    test_normal_keys(keyboard)
    test_special_keys(keyboard)
    test_modifier_keys(keyboard)
    test_shift_layout(keyboard)
    test_symbols_layout(keyboard)
    test_exit_key(keyboard)
    
    print()
    print("=" * 50)
    print("ALLE TESTS BESTANDEN ✓")
    print("=" * 50)
    print()
    
    # Visueller Test (optional)
    try:
        visual_test()
    except Exception as e:
        print(f"  Visueller Test übersprungen: {e}")

if __name__ == "__main__":
    main()
