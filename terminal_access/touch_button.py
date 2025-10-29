#!/usr/bin/env python3
"""
Touch Button Modul für Terminal Access
Zeichnet einen Button auf dem Display und prüft Touch-Koordinaten
"""

import cv2
import numpy as np

class TouchButton:
    """Einfacher rechteckiger Touch-Button"""
    
    def __init__(self, x, y, width, height, label="", color=(0, 255, 0)):
        """
        Args:
            x, y: Obere linke Ecke des Buttons
            width, height: Größe des Buttons
            label: Text auf dem Button
            color: BGR Farbe des Buttons
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        self.color = color
        self.active_color = tuple([min(255, c + 50) for c in color])
        self.is_pressed = False
        
    def draw(self, frame):
        """Zeichnet den Button auf dem Frame"""
        x1, y1 = self.x, self.y
        x2, y2 = self.x + self.width, self.y + self.height
        
        color = self.active_color if self.is_pressed else self.color
        
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        if self.label:
            text_size = cv2.getTextSize(self.label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            text_x = x1 + (self.width - text_size[0]) // 2
            text_y = y1 + (self.height + text_size[1]) // 2
            cv2.putText(frame, self.label, (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
                       
    def is_touched(self, touch_x, touch_y, display_width=480, display_height=320):
        """
        Prüft ob Touch-Koordinaten innerhalb des Buttons liegen
        
        Args:
            touch_x, touch_y: Rohe Touch-Koordinaten vom ADS7846
            display_width, display_height: Display Auflösung
            
        Returns:
            True wenn Button getroffen wurde
        """
        # ADS7846 liefert meist Werte im Bereich 0-4095
        # Diese müssen auf Display-Koordinaten gemappt werden
        # Die genaue Kalibrierung hängt vom Display ab
        
        # Beispiel-Mapping (muss ggf. angepasst werden):
        # Annahme: touch_x und touch_y sind bereits normalisiert 0-480 / 0-320
        
        if self.x <= touch_x <= (self.x + self.width):
            if self.y <= touch_y <= (self.y + self.height):
                return True
        return False
        
    def normalize_touch(self, raw_x, raw_y, 
                       raw_x_min=0, raw_x_max=4095,
                       raw_y_min=0, raw_y_max=4095,
                       display_width=480, display_height=320):
        """
        Konvertiert rohe Touch-Koordinaten zu Display-Koordinaten
        
        Returns:
            (normalized_x, normalized_y)
        """
        norm_x = int((raw_x - raw_x_min) * display_width / (raw_x_max - raw_x_min))
        norm_y = int((raw_y - raw_y_min) * display_height / (raw_y_max - raw_y_min))
        
        norm_x = max(0, min(display_width - 1, norm_x))
        norm_y = max(0, min(display_height - 1, norm_y))
        
        return norm_x, norm_y


class TerminalButton(TouchButton):
    """Spezieller Button für Terminal-Zugriff"""
    
    def __init__(self, x=10, y=280, width=80, height=30):
        super().__init__(x, y, width, height, "TERM", (255, 165, 0))
        

class KeyboardButton(TouchButton):
    """Spezieller Button für Tastatur"""
    
    def __init__(self, x=100, y=280, width=80, height=30):
        super().__init__(x, y, width, height, "KBD", (255, 200, 0))
