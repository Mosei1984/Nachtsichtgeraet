#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Virtuelle Tastatur für Framebuffer-Display
Rendert Tastatur-Layout mit OpenCV und verarbeitet Touch-Input
"""

import cv2
import numpy as np

class VirtualKeyboard:
    """
    Virtuelle On-Screen Tastatur mit mehreren Layouts
    """
    
    # Tastatur-Layouts
    LAYOUT_NORMAL = [
        ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'BKSP'],
        ['TAB', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'],
        ['ESC', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'", 'ENTER'],
        ['SHIFT', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 'UP', 'SHIFT'],
        ['CTRL', 'ALT', 'SYM', 'SPACE', 'SYM', 'LEFT', 'DOWN', 'RIGHT', 'EXIT']
    ]
    
    LAYOUT_SHIFT = [
        ['~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', 'BKSP'],
        ['TAB', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '{', '}', '|'],
        ['ESC', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ':', '"', 'ENTER'],
        ['SHIFT', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', '<', '>', '?', 'UP', 'SHIFT'],
        ['CTRL', 'ALT', 'SYM', 'SPACE', 'SYM', 'LEFT', 'DOWN', 'RIGHT', 'EXIT']
    ]
    
    LAYOUT_SYMBOLS = [
        ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'BKSP'],
        ['TAB', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', '\\'],
        ['ESC', '~', '{', '}', '[', ']', '|', ';', ':', "'", '"', '<', 'ENTER'],
        ['SHIFT', '/', '?', '.', ',', '<', '>', '=', '+', '-', '_', 'UP', 'SHIFT'],
        ['CTRL', 'ALT', 'ABC', 'SPACE', 'ABC', 'LEFT', 'DOWN', 'RIGHT', 'EXIT']
    ]
    
    def __init__(self, width=480, height=140, y_offset=180):
        """
        Args:
            width: Breite der Tastatur (Display-Breite)
            height: Höhe der Tastatur
            y_offset: Y-Position wo Tastatur beginnt (Rest für Terminal)
        """
        self.width = width
        self.height = height
        self.y_offset = y_offset
        
        self.shift_active = False
        self.ctrl_active = False
        self.alt_active = False
        self.symbols_active = False
        
        self.key_rects = {}
        self.last_key = None
        
        self._calculate_key_positions()
        
    def _calculate_key_positions(self):
        """Berechnet Position und Größe jeder Taste"""
        self.key_rects.clear()
        
        layout = self._get_current_layout()
        num_rows = len(layout)
        row_height = self.height // num_rows
        
        for row_idx, row in enumerate(layout):
            y = self.y_offset + (row_idx * row_height)
            num_keys = len(row)
            
            x_pos = 0
            for key_idx, key in enumerate(row):
                # Breite je nach Taste anpassen
                if key == 'SPACE':
                    key_width = self.width // 4
                elif key in ['BKSP', 'ENTER', 'SHIFT', 'TAB']:
                    key_width = int(self.width / num_keys * 1.5)
                else:
                    key_width = self.width // num_keys
                
                self.key_rects[key] = {
                    'x': x_pos,
                    'y': y,
                    'w': key_width,
                    'h': row_height,
                    'label': key
                }
                
                x_pos += key_width
                
    def _get_current_layout(self):
        """Gibt aktuelles Layout zurück basierend auf Modifier-Tasten"""
        if self.symbols_active:
            return self.LAYOUT_SYMBOLS
        elif self.shift_active:
            return self.LAYOUT_SHIFT
        else:
            return self.LAYOUT_NORMAL
            
    def draw(self, frame):
        """
        Zeichnet Tastatur auf Frame
        
        Args:
            frame: BGR numpy array (480x320x3)
        """
        # Keyboard-Hintergrund
        frame[self.y_offset:self.y_offset+self.height, :] = (30, 30, 30)
        
        layout = self._get_current_layout()
        
        for key_label, rect in self.key_rects.items():
            x, y, w, h = rect['x'], rect['y'], rect['w'], rect['h']
            
            # Farbe basierend auf Zustand
            if key_label == 'SHIFT' and self.shift_active:
                color = (100, 200, 255)
            elif key_label == 'CTRL' and self.ctrl_active:
                color = (100, 200, 255)
            elif key_label == 'ALT' and self.alt_active:
                color = (100, 200, 255)
            elif key_label in ['SYM', 'ABC'] and self.symbols_active:
                color = (100, 200, 255)
            elif key_label == 'EXIT':
                color = (0, 0, 200)
            else:
                color = (80, 80, 80)
            
            # Taste zeichnen
            cv2.rectangle(frame, (x+2, y+2), (x+w-2, y+h-2), color, -1)
            cv2.rectangle(frame, (x+2, y+2), (x+w-2, y+h-2), (150, 150, 150), 1)
            
            # Label
            font_scale = 0.4 if len(key_label) > 1 else 0.5
            text_size = cv2.getTextSize(key_label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 1)[0]
            text_x = x + (w - text_size[0]) // 2
            text_y = y + (h + text_size[1]) // 2
            
            cv2.putText(frame, key_label, (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), 1, cv2.LINE_AA)
                       
    def hit_test(self, x, y):
        """
        Prüft welche Taste getroffen wurde
        
        Args:
            x, y: Touch-Koordinaten (normalisiert auf Display-Auflösung)
            
        Returns:
            Key-Label oder None
        """
        for key_label, rect in self.key_rects.items():
            kx, ky, kw, kh = rect['x'], rect['y'], rect['w'], rect['h']
            if kx <= x < (kx + kw) and ky <= y < (ky + kh):
                return key_label
        return None
        
    def process_key(self, key_label):
        """
        Verarbeitet Tastendruck und gibt Bytes für Terminal zurück
        
        Args:
            key_label: Label der gedrückten Taste
            
        Returns:
            bytes oder None, exit_requested (bool)
        """
        if key_label is None:
            return None, False
            
        self.last_key = key_label
        
        # Exit-Taste
        if key_label == 'EXIT':
            return None, True
            
        # Modifier-Tasten
        if key_label == 'SHIFT':
            self.shift_active = not self.shift_active
            self._calculate_key_positions()
            return None, False
            
        if key_label == 'CTRL':
            self.ctrl_active = not self.ctrl_active
            return None, False
            
        if key_label == 'ALT':
            self.alt_active = not self.alt_active
            return None, False
            
        if key_label in ['SYM', 'ABC']:
            self.symbols_active = not self.symbols_active
            self._calculate_key_positions()
            return None, False
            
        # Spezial-Tasten
        key_bytes = None
        
        if key_label == 'ENTER':
            key_bytes = b'\r'
        elif key_label == 'BKSP':
            key_bytes = b'\x7f'
        elif key_label == 'TAB':
            key_bytes = b'\t'
        elif key_label == 'ESC':
            key_bytes = b'\x1b'
        elif key_label == 'SPACE':
            key_bytes = b' '
        elif key_label == 'UP':
            key_bytes = b'\x1b[A'
        elif key_label == 'DOWN':
            key_bytes = b'\x1b[B'
        elif key_label == 'RIGHT':
            key_bytes = b'\x1b[C'
        elif key_label == 'LEFT':
            key_bytes = b'\x1b[D'
        elif len(key_label) == 1:
            # Normales Zeichen
            char = key_label
            
            # Ctrl-Kombinationen
            if self.ctrl_active:
                if char.lower() in 'abcdefghijklmnopqrstuvwxyz':
                    key_bytes = bytes([ord(char.lower()) - ord('a') + 1])
                else:
                    key_bytes = char.encode('utf-8')
            else:
                key_bytes = char.encode('utf-8')
                
        # Shift zurücksetzen nach Tastendruck (außer bei Modifier-Tasten)
        if key_label not in ['SHIFT', 'CTRL', 'ALT', 'SYM', 'ABC']:
            if self.shift_active:
                self.shift_active = False
                self._calculate_key_positions()
            if self.ctrl_active:
                self.ctrl_active = False
            if self.alt_active:
                self.alt_active = False
                
        return key_bytes, False
        
    def get_info_text(self):
        """Gibt Info-Text über aktive Modifier zurück"""
        info = []
        if self.ctrl_active:
            info.append("CTRL")
        if self.alt_active:
            info.append("ALT")
        if self.shift_active:
            info.append("SHIFT")
        if self.symbols_active:
            info.append("SYM")
        
        return " ".join(info) if info else ""
