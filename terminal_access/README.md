# Terminal Access Modul

Touchscreen-basierter Terminal-Zugriff für das Nachtsichtgerät ohne externe Peripherie.

## Features

- **Terminal Emulator** auf dem SPI-Display (/dev/fb1)
- **Virtuelle Tastatur** (Touchscreen-gesteuert)
- **Nahtlose Integration** in die Kamera-Oberfläche
- **On-Screen Button** zum Aktivieren/Deaktivieren
- **Vollständiger System-Zugriff** für Updates und Wartung

## Installation

### Automatische Installation

```bash
cd terminal_access
chmod +x setup_terminal.sh
sudo ./setup_terminal.sh
```

### Manuelle Installation

```bash
sudo apt-get update
sudo apt-get install -y lxterminal matchbox-keyboard
```

Optional (alternative Tastatur):
```bash
sudo apt-get install -y onboard
```

## Verwendung

### Im Nachtsicht-Programm

1. Starte `nachtsicht_fullscreen.py` wie gewohnt
2. Ein orangefarbener "TERM"-Button erscheint unten links
3. Tippe auf den Button um Terminal zu öffnen/schließen
4. Virtuelle Tastatur startet automatisch mit dem Terminal

### Terminal-Button Position

- **Position**: Unten links (10px vom Rand)
- **Größe**: 70x30 Pixel
- **Farbe**: Orange (RGB: 255, 165, 0)
- **Label**: "TERM"

### Tastenkombinationen im Terminal

- Terminal schließen: Tippe erneut auf "TERM"-Button
- Oder verwende `exit` Kommando

## Konfiguration

### Display und Touch Einstellungen

Die Standardwerte werden automatisch übernommen:
- **Framebuffer**: `/dev/fb1` (3.5" SPI Display)
- **Touch Device**: `/dev/input/event0` (ADS7846)
- **Display**: `:0` (X11 Display)

### Touch-Kalibrierung

Falls die Touch-Koordinaten nicht stimmen, passe die Werte in `touch_button.py` an:

```python
def normalize_touch(self, raw_x, raw_y, 
                   raw_x_min=0, raw_x_max=4095,
                   raw_y_min=0, raw_y_max=4095,
                   display_width=480, display_height=320):
```

### Alternative Tastatur

Um Onboard statt matchbox-keyboard zu verwenden, ändere in `terminal_launcher.py`:

```python
KEYBOARD_CMD = "onboard"  # statt "matchbox-keyboard"
```

## Systemzugriff

### Updates durchführen

```bash
# Im Terminal auf dem Gerät:
sudo apt-get update
sudo apt-get upgrade
```

### Programm bearbeiten

```bash
# Nano Editor:
nano ~/nachtsicht_fullscreen.py

# Vim (falls installiert):
vim ~/nachtsicht_fullscreen.py
```

### System neustarten

```bash
sudo reboot
```

## Architektur

### Komponenten

1. **terminal_launcher.py** - Prozess-Management für Terminal & Tastatur
2. **touch_button.py** - Button-Rendering und Touch-Detection
3. **__init__.py** - Modul-Initialisierung

### Integration in nachtsicht_fullscreen.py

```python
# Import
from terminal_access.terminal_launcher import TerminalLauncher
from terminal_access.touch_button import TerminalButton

# Initialisierung
terminal_launcher = TerminalLauncher(FB_PATH, TOUCH_DEV)
terminal_button = TerminalButton(x=10, y=H-40)

# Touch-Handling
if terminal_button.is_touched(cur_x, cur_y):
    terminal_launcher.toggle_terminal()

# Rendering
terminal_button.draw(frame)

# Cleanup
terminal_launcher.cleanup()
```

## Fehlerbehebung

### Terminal startet nicht

```bash
# Prüfe ob lxterminal installiert ist:
which lxterminal

# Falls nicht installiert:
sudo apt-get install lxterminal
```

### Tastatur erscheint nicht

```bash
# Prüfe matchbox-keyboard:
which matchbox-keyboard

# Installation:
sudo apt-get install matchbox-keyboard
```

### Touch-Koordinaten falsch

Die Touch-Koordinaten müssen eventuell kalibriert werden. Passe die `normalize_touch()` Funktion in `touch_button.py` an.

### Terminal auf falschem Display

Prüfe die Umgebungsvariable:
```bash
echo $FRAMEBUFFER  # sollte /dev/fb1 sein
```

## Sicherheit

### Sudo-Zugriff

Für systemweite Änderungen benötigt das Terminal sudo-Rechte:

```bash
# Passwortloses sudo für pi-User (optional):
sudo visudo
# Füge hinzu:
# pi ALL=(ALL) NOPASSWD: ALL
```

**Achtung**: Dies reduziert die Sicherheit. Nur in vertrauenswürdigen Umgebungen verwenden.

### Netzwerk-Zugriff

Für Updates muss WiFi oder Ethernet konfiguriert sein:

```bash
# WiFi konfigurieren:
sudo raspi-config
# Wähle: 1 System Options -> S1 Wireless LAN
```

## Logs und Debugging

### Logging aktivieren

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Prozesse prüfen

```bash
# Terminal-Prozess finden:
ps aux | grep lxterminal

# Tastatur-Prozess:
ps aux | grep matchbox-keyboard
```

## Lizenz

Siehe LICENSE Datei im Hauptverzeichnis.
