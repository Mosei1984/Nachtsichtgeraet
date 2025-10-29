#!/usr/bin/env python3
"""
Terminal Access Launcher für Nachtsichtgerät
Ermöglicht Touchscreen-basierte Terminal- und Tastatur-Zugriffe
"""

import subprocess
import os
import signal
import logging

logger = logging.getLogger(__name__)

FB_DEVICE = "/dev/fb1"
TOUCH_DEVICE = "/dev/input/event0"

TERMINAL_CMD = "lxterminal"
KEYBOARD_CMD = "matchbox-keyboard"

class TerminalLauncher:
    """Verwaltet Terminal und virtuelle Tastatur Prozesse"""
    
    def __init__(self, fb_device=FB_DEVICE, touch_device=TOUCH_DEVICE):
        self.fb_device = fb_device
        self.touch_device = touch_device
        self.terminal_process = None
        self.keyboard_process = None
        self.terminal_active = False
        
    def launch_terminal(self):
        """Startet Terminal Emulator auf SPI Display"""
        if self.terminal_active and self.terminal_process:
            logger.info("Terminal bereits aktiv")
            return True
            
        try:
            env = os.environ.copy()
            env['FRAMEBUFFER'] = self.fb_device
            env['TSLIB_TSDEVICE'] = self.touch_device
            env['DISPLAY'] = ':0'
            
            # Für 480x320 Display optimierte Größe
            # 60 Spalten x 20 Zeilen passt gut auf 480x320
            self.terminal_process = subprocess.Popen(
                [TERMINAL_CMD, 
                 '--geometry=60x20',
                 '--title=Nachtsicht Terminal',
                 '-e', 'bash'],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.terminal_active = True
            print(f"[TERMINAL] Gestartet (PID: {self.terminal_process.pid})")
            logger.info("Terminal erfolgreich gestartet")
            return True
            
        except FileNotFoundError:
            print(f"[TERMINAL] FEHLER: {TERMINAL_CMD} nicht gefunden")
            logger.error(f"{TERMINAL_CMD} nicht gefunden. Installation: sudo apt-get install lxterminal")
            return False
        except Exception as e:
            print(f"[TERMINAL] FEHLER: {e}")
            logger.error(f"Fehler beim Starten des Terminals: {e}")
            return False
            
    def launch_keyboard(self):
        """Startet virtuelle Tastatur"""
        if self.keyboard_process and self.keyboard_process.poll() is None:
            logger.info("Tastatur bereits aktiv")
            return True
            
        try:
            env = os.environ.copy()
            env['FRAMEBUFFER'] = self.fb_device
            env['TSLIB_TSDEVICE'] = self.touch_device
            env['DISPLAY'] = ':0'
            
            self.keyboard_process = subprocess.Popen(
                [KEYBOARD_CMD],
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            logger.info("Virtuelle Tastatur gestartet")
            return True
            
        except FileNotFoundError:
            logger.error(f"{KEYBOARD_CMD} nicht gefunden. Installation: sudo apt-get install matchbox-keyboard")
            return False
        except Exception as e:
            logger.error(f"Fehler beim Starten der Tastatur: {e}")
            return False
            
    def close_terminal(self):
        """Schließt Terminal Emulator"""
        if self.terminal_process:
            try:
                self.terminal_process.terminate()
                self.terminal_process.wait(timeout=3)
                logger.info("Terminal geschlossen")
            except subprocess.TimeoutExpired:
                self.terminal_process.kill()
                logger.warning("Terminal musste forciert beendet werden")
            except Exception as e:
                logger.error(f"Fehler beim Schließen des Terminals: {e}")
            finally:
                self.terminal_process = None
                self.terminal_active = False
                
    def close_keyboard(self):
        """Schließt virtuelle Tastatur"""
        if self.keyboard_process:
            try:
                self.keyboard_process.terminate()
                self.keyboard_process.wait(timeout=3)
                logger.info("Tastatur geschlossen")
            except subprocess.TimeoutExpired:
                self.keyboard_process.kill()
                logger.warning("Tastatur musste forciert beendet werden")
            except Exception as e:
                logger.error(f"Fehler beim Schließen der Tastatur: {e}")
            finally:
                self.keyboard_process = None
                
    def toggle_terminal(self):
        """Terminal ein/ausschalten"""
        if self.terminal_active:
            self.close_terminal()
            self.close_keyboard()
            return False
        else:
            success = self.launch_terminal()
            if success:
                self.launch_keyboard()
            return success
            
    def cleanup(self):
        """Beendet alle Prozesse"""
        self.close_terminal()
        self.close_keyboard()
        logger.info("Terminal Launcher aufgeräumt")


def check_dependencies():
    """Prüft ob benötigte Programme installiert sind"""
    missing = []
    
    try:
        subprocess.run(['which', TERMINAL_CMD], 
                      check=True, 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        missing.append(f"{TERMINAL_CMD} (sudo apt-get install lxterminal)")
        
    try:
        subprocess.run(['which', KEYBOARD_CMD], 
                      check=True, 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        missing.append(f"{KEYBOARD_CMD} (sudo apt-get install matchbox-keyboard)")
        
    return missing
