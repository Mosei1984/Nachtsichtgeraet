#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
USB Manager - Einfaches USB Mount/Unmount Interface
Zeigt USB-Status und bietet sicheren Unmount per Touch
"""

import os
import subprocess
import time

class USBManager:
    def __init__(self, fb_width=480, fb_height=320):
        self.width = fb_width
        self.height = fb_height
        self.usb_dev = "/dev/sda1"
        self.mount_point = "/media/usb"
        
        # Layout
        self.button_height = 60
        self.margin = 20
        self.font_scale = 0.7
        
    def is_mounted(self):
        """Prüfe ob USB gemountet ist"""
        return os.path.ismount(self.mount_point)
    
    def is_device_present(self):
        """Prüfe ob USB-Device existiert"""
        return os.path.exists(self.usb_dev)
    
    def safe_unmount(self):
        """Sicherer USB-Unmount mit sync"""
        if not self.is_mounted():
            return False, "USB nicht gemountet"
        
        try:
            # Sync vor Unmount
            subprocess.run(["sync"], check=True, timeout=10)
            time.sleep(0.5)
            
            # Unmount
            result = subprocess.run(
                ["sudo", "umount", self.mount_point],
                check=True,
                timeout=10,
                capture_output=True,
                text=True
            )
            return True, "USB sicher entfernt"
        except subprocess.TimeoutExpired:
            return False, "Timeout beim Unmount"
        except subprocess.CalledProcessError as e:
            return False, f"Fehler: {e.stderr}"
        except Exception as e:
            return False, f"Fehler: {str(e)}"
    
    def get_status_text(self):
        """Hole USB-Status als Text"""
        if not self.is_device_present():
            return "Kein USB-Stick gefunden", (200, 100, 100)  # Rot
        elif self.is_mounted():
            return f"USB gemountet: {self.mount_point}", (100, 255, 100)  # Grün
        else:
            return "USB gefunden, nicht gemountet", (255, 200, 100)  # Orange
    
    def draw_interface(self, frame):
        """Zeichne USB-Manager Interface auf Frame (OpenCV/NumPy)"""
        import cv2
        import numpy as np
        
        # Hintergrund: Schwarz
        frame.fill(0)
        
        # Titel
        cv2.putText(frame, "USB Manager", (self.margin, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        
        # Status-Text
        status_text, status_color = self.get_status_text()
        cv2.putText(frame, status_text, (self.margin, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, status_color, 2)
        
        # Device-Info
        if self.is_device_present():
            cv2.putText(frame, f"Device: {self.usb_dev}", (self.margin, 130),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        # Buttons
        y_pos = 180
        
        # Unmount-Button (nur wenn gemountet)
        if self.is_mounted():
            self._draw_button(frame, "Sicher Entfernen", (self.margin, y_pos),
                            (self.width - 2*self.margin, self.button_height),
                            (100, 200, 100), "unmount")
            y_pos += self.button_height + 10
        
        # Schließen-Button
        self._draw_button(frame, "Schliessen (ESC)", (self.margin, self.height - self.button_height - self.margin),
                        (self.width - 2*self.margin, self.button_height),
                        (150, 150, 150), "close")
        
        return frame
    
    def _draw_button(self, frame, text, pos, size, color, action):
        """Zeichne einen Button"""
        import cv2
        x, y = pos
        w, h = size
        
        # Button-Rechteck
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.rectangle(frame, (x+2, y+2), (x+w-2, y+h-2), 
                     (color[0]//4, color[1]//4, color[2]//4), -1)
        
        # Text zentriert
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, 2)[0]
        text_x = x + (w - text_size[0]) // 2
        text_y = y + (h + text_size[1]) // 2
        cv2.putText(frame, text, (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, (255, 255, 255), 2)
    
    def handle_touch(self, x, y):
        """
        Behandle Touch-Event
        Returns: ("action", "message") oder (None, None)
        """
        # Unmount-Button
        if self.is_mounted():
            if (self.margin <= x <= self.width - self.margin and
                180 <= y <= 180 + self.button_height):
                success, msg = self.safe_unmount()
                return ("unmount", msg)
        
        # Schließen-Button
        close_y = self.height - self.button_height - self.margin
        if (self.margin <= x <= self.width - self.margin and
            close_y <= y <= close_y + self.button_height):
            return ("close", None)
        
        return (None, None)


if __name__ == "__main__":
    # Test ohne Display
    manager = USBManager()
    print("USB Manager Test")
    print(f"Device vorhanden: {manager.is_device_present()}")
    print(f"Gemountet: {manager.is_mounted()}")
    status, color = manager.get_status_text()
    print(f"Status: {status}")
