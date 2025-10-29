#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terminal Emulator für Framebuffer-Display
Verwendet pyte für VT100-Emulation und PTY für bash-Prozess
"""

import os
import sys
import pty
import select
import termios
import struct
import fcntl
import signal
import cv2
import numpy as np

try:
    import pyte
    PYTE_AVAILABLE = True
except ImportError:
    PYTE_AVAILABLE = False
    print("[WARN] pyte nicht verfügbar - installiere mit: pip3 install pyte")

class TerminalEmulator:
    """
    Terminal Emulator mit PTY und pyte VT100-Emulation
    """
    
    def __init__(self, width=480, height=180, cols=60, rows=20):
        """
        Args:
            width: Pixel-Breite des Terminal-Bereichs
            height: Pixel-Höhe des Terminal-Bereichs
            cols: Anzahl Zeichen pro Zeile
            rows: Anzahl Zeilen
        """
        if not PYTE_AVAILABLE:
            raise ImportError("pyte library nicht verfügbar")
            
        self.width = width
        self.height = height
        self.cols = cols
        self.rows = rows
        
        self.master_fd = None
        self.pid = None
        
        # pyte Screen für VT100-Emulation
        self.screen = pyte.Screen(cols, rows)
        self.stream = pyte.ByteStream(self.screen)
        
        self.running = False
        
        # Zeichensatz-Parameter
        self.char_width = 8
        self.char_height = 9
        self.font_scale = 0.35
        self.font_thickness = 1
        
    def start(self, shell="/bin/bash"):
        """
        Startet PTY mit Shell
        
        Args:
            shell: Shell-Programm (default: /bin/bash)
        """
        if self.running:
            return
            
        try:
            pid, master_fd = pty.fork()
            
            if pid == 0:
                # Kind-Prozess: Shell ausführen
                os.environ['TERM'] = 'linux'
                os.environ['COLUMNS'] = str(self.cols)
                os.environ['LINES'] = str(self.rows)
                
                try:
                    os.execvp(shell, [shell])
                except Exception as e:
                    print(f"Fehler beim Starten der Shell: {e}", file=sys.stderr)
                    sys.exit(1)
            else:
                # Eltern-Prozess: PTY verwalten
                self.master_fd = master_fd
                self.pid = pid
                
                # Non-blocking setzen
                flags = fcntl.fcntl(self.master_fd, fcntl.F_GETFL)
                fcntl.fcntl(self.master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
                
                # Window-Size setzen (TIOCSWINSZ)
                winsize = struct.pack("HHHH", self.rows, self.cols, 0, 0)
                fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, winsize)
                
                self.running = True
                print(f"[TERMINAL] Shell gestartet (PID: {pid}, {self.cols}x{self.rows})")
                
        except Exception as e:
            print(f"[TERMINAL] Fehler beim Starten: {e}")
            self.running = False
            
    def stop(self):
        """Beendet Terminal und Shell"""
        if not self.running:
            return
            
        try:
            if self.pid:
                # Versuche graceful shutdown
                try:
                    os.kill(self.pid, signal.SIGTERM)
                    os.waitpid(self.pid, 0)
                except:
                    pass
                    
            if self.master_fd:
                os.close(self.master_fd)
                
            self.running = False
            print("[TERMINAL] Shell beendet")
            
        except Exception as e:
            print(f"[TERMINAL] Fehler beim Beenden: {e}")
            
    def write(self, data):
        """
        Schreibt Daten zum Terminal (Tastatur-Input)
        
        Args:
            data: bytes
        """
        if not self.running or not self.master_fd:
            return
            
        try:
            os.write(self.master_fd, data)
        except OSError as e:
            print(f"[TERMINAL] Schreibfehler: {e}")
            
    def read(self):
        """
        Liest Output vom Terminal (non-blocking)
        Aktualisiert pyte screen buffer
        """
        if not self.running or not self.master_fd:
            return
            
        try:
            # Non-blocking read
            ready, _, _ = select.select([self.master_fd], [], [], 0)
            
            if ready:
                data = os.read(self.master_fd, 4096)
                if data:
                    # Feed zu pyte stream
                    self.stream.feed(data)
                else:
                    # EOF - Shell beendet
                    self.running = False
                    
        except OSError as e:
            if e.errno != 11:  # EAGAIN ist ok bei non-blocking
                print(f"[TERMINAL] Lesefehler: {e}")
                self.running = False
                
    def render(self, frame, x_offset=0, y_offset=0):
        """
        Rendert Terminal-Output auf Frame
        
        Args:
            frame: BGR numpy array
            x_offset: X-Offset für Rendering
            y_offset: Y-Offset für Rendering
        """
        # Hintergrund
        bg_color = (0, 0, 0)
        frame[y_offset:y_offset+self.height, x_offset:x_offset+self.width] = bg_color
        
        # Cursor-Position
        cursor_x = self.screen.cursor.x
        cursor_y = self.screen.cursor.y
        
        # Zeilen rendern
        for row_idx, line in enumerate(self.screen.display):
            y = y_offset + (row_idx * self.char_height) + self.char_height
            
            # Zeile zusammensetzen
            text = "".join(char.data for char in line)
            
            if text.strip():  # Nur nicht-leere Zeilen zeichnen
                cv2.putText(
                    frame, text, (x_offset + 2, y),
                    cv2.FONT_HERSHEY_PLAIN,
                    self.font_scale,
                    (200, 200, 200),
                    self.font_thickness,
                    cv2.LINE_AA
                )
                
        # Cursor zeichnen
        if self.running:
            cursor_px_x = x_offset + (cursor_x * self.char_width)
            cursor_px_y = y_offset + (cursor_y * self.char_height)
            cv2.rectangle(
                frame,
                (cursor_px_x, cursor_px_y),
                (cursor_px_x + self.char_width, cursor_px_y + self.char_height),
                (0, 255, 0),
                1
            )
            
    def is_alive(self):
        """Prüft ob Shell noch läuft"""
        if not self.running or not self.pid:
            return False
            
        try:
            # Non-blocking check
            pid, status = os.waitpid(self.pid, os.WNOHANG)
            if pid != 0:
                # Prozess beendet
                self.running = False
                return False
            return True
        except:
            return False
            
    def get_screen_text(self):
        """
        Gibt kompletten Screen-Text zurück (für Debugging)
        
        Returns:
            String mit allen Zeilen
        """
        lines = []
        for line in self.screen.display:
            text = "".join(char.data for char in line)
            lines.append(text)
        return "\n".join(lines)
