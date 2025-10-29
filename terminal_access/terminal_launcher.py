#!/usr/bin/env python3
"""
Terminal Access Launcher für Nachtsichtgerät
Ermöglicht Touchscreen-basierte Terminal- und Tastatur-Zugriffe
Integrierte virtuelle Tastatur und Terminal-Emulator
"""

import subprocess
import os
import signal
import logging
import time

try:
    from .terminal_emulator import TerminalEmulator
    from .vkeyboard import VirtualKeyboard
    TERMINAL_EMU_AVAILABLE = True
except ImportError:
    TERMINAL_EMU_AVAILABLE = False
    print("[WARN] Terminal Emulator/VKeyboard nicht verfügbar")

logger = logging.getLogger(__name__)

FB_DEVICE = "/dev/fb1"
TOUCH_DEVICE = "/dev/input/event0"

class TerminalLauncher:
    """Verwaltet integriertes Terminal mit virtueller Tastatur"""
    
    def __init__(self, fb_device=FB_DEVICE, touch_device=TOUCH_DEVICE):
        self.fb_device = fb_device
        self.touch_device = touch_device
        self.terminal_active = False
        
        # Integrierte Terminal-Komponenten
        self.terminal = None
        self.keyboard = None
        
        # Legacy external terminal support
        self.terminal_process = None
        self.keyboard_process = None
        
    def launch_terminal(self):
        """Startet integriertes Terminal mit virtueller Tastatur"""
        if self.terminal_active:
            logger.info("Terminal bereits aktiv")
            return True
            
        if not TERMINAL_EMU_AVAILABLE:
            print("[TERMINAL] Terminal Emulator nicht verfügbar")
            print("[TERMINAL] Installation: pip3 install pyte")
            return False
            
        try:
            # Terminal-Emulator (oben, 180px für ~20 Zeilen)
            self.terminal = TerminalEmulator(width=480, height=180, cols=60, rows=20)
            self.terminal.start(shell="/bin/bash")
            
            # Tastatur (unten, 140px, startet bei y=180)
            # Mit +30px Touch-Offset-Korrektur wird das zu y=180+30=210 für Touches
            self.keyboard = VirtualKeyboard(width=480, height=140, y_offset=180)
            
            self.terminal_active = True
            print("[TERMINAL] Integriertes Terminal gestartet")
            print(f"[TERMINAL] Terminal: 480x180 bei y=0")
            print(f"[TERMINAL] Tastatur: 480x140 bei y=180")
            logger.info("Integriertes Terminal erfolgreich gestartet")
            return True
            
        except Exception as e:
            print(f"[TERMINAL] FEHLER: {e}")
            logger.error(f"Fehler beim Starten des Terminals: {e}")
            return False
            
    def update(self):
        """
        Update-Loop für Terminal (liest Output, prüft Status)
        Sollte regelmäßig aufgerufen werden wenn Terminal aktiv
        """
        if not self.terminal_active or not self.terminal:
            return
            
        # Terminal-Output lesen und Screen-Buffer aktualisieren
        self.terminal.read()
        
        # Prüfen ob Shell noch läuft
        if not self.terminal.is_alive():
            print("[TERMINAL] Shell beendet - schließe Terminal")
            self.close_terminal()
            
    def render(self, frame):
        """
        Rendert Terminal und Tastatur auf Frame
        
        Args:
            frame: BGR numpy array (480x320x3)
        """
        if not self.terminal_active:
            return
            
        if self.terminal:
            self.terminal.render(frame, x_offset=0, y_offset=0)
            
        if self.keyboard:
            self.keyboard.draw(frame)
            
    def handle_touch(self, x, y):
        """
        Verarbeitet Touch-Event für Tastatur
        
        Args:
            x, y: Touch-Koordinaten (normalisiert)
            
        Returns:
            True wenn Exit angefordert, sonst False
        """
        if not self.terminal_active or not self.keyboard:
            return False
        
        # Touch-Koordinaten-Korrektur für Tastatur (aus Kalibrierung)
        # Gemessener Offset: X=-82px, Y=+85px
        adjusted_x = x + 82  # Touch kommt 82px zu weit links
        adjusted_y = y - 85  # Touch kommt 85px zu weit unten
        
        # Hit-Test auf Tastatur mit korrigierten Koordinaten
        key = self.keyboard.hit_test(adjusted_x, adjusted_y)
        
        if key:
            # Taste verarbeiten
            key_bytes, exit_requested = self.keyboard.process_key(key)
            
            if exit_requested:
                return True
                
            # Bytes zum Terminal senden
            if key_bytes and self.terminal:
                self.terminal.write(key_bytes)
                
        return False
            
    def close_terminal(self):
        """Schließt integriertes Terminal"""
        if self.terminal:
            try:
                self.terminal.stop()
                logger.info("Terminal geschlossen")
            except Exception as e:
                logger.error(f"Fehler beim Schließen des Terminals: {e}")
            finally:
                self.terminal = None
                self.keyboard = None
                self.terminal_active = False
                
    def toggle_terminal(self):
        """Terminal ein/ausschalten"""
        if self.terminal_active:
            self.close_terminal()
            return False
        else:
            return self.launch_terminal()
            
    def is_active(self):
        """Gibt zurück ob Terminal aktiv ist"""
        return self.terminal_active
            
    def cleanup(self):
        """Beendet alle Prozesse"""
        self.close_terminal()
        logger.info("Terminal Launcher aufgeräumt")


def check_dependencies():
    """Prüft ob benötigte Python-Module installiert sind"""
    missing = []
    
    try:
        import pyte
    except ImportError:
        missing.append("pyte (pip3 install pyte)")
        
    return missing
