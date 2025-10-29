# Nachtsichtgerät

**IR-optimiertes Nachtsichtgerät mit Touchscreen-Steuerung und Terminal-Zugriff** (Night Vision Device)

[![CI](https://github.com/Mosei1984/Nachtsichtgeraet/actions/workflows/ci.yml/badge.svg)](https://github.com/Mosei1984/Nachtsichtgeraet/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Platform: Raspberry Pi](https://img.shields.io/badge/platform-Raspberry%20Pi-red.svg)](https://www.raspberrypi.org/)

Raspberry Pi 3 B basiertes Nachtsichtgerät mit Touchscreen-Steuerung.

> **Quick Links**: [Installation](#installation) | [Contributing](CONTRIBUTING.md) | [Security](SECURITY.md) | [Changelog](CHANGELOG.md)

## Hardware

- Raspberry Pi 3 B
- Raspbian (Trixy)
- 3.5" SPI Display (/dev/fb1)
- ADS7846 Touchscreen (/dev/input/event0)
- IR-optimierte Kamera (Picamera2)

## Features

- IR-optimierte Live-Ansicht mit Histogram-Equalizing
- Touchscreen-Steuerung
- Foto & Video Aufnahme mit Auto-Nummerierung
- USB-Speicher Support mit Fallback
- Grünes HUD mit Statusanzeige
- Sicherer Shutdown per Touch
- **Touchscreen-Terminal-Zugriff** ohne externe Peripherie (NEU!)
  - On-Screen Terminal-Button
  - Virtuelle Tastatur
  - Vollständiger System-Zugriff für Updates & Wartung

## Touch-Gesten

### IDLE Modus
- **Doppel-Tap**: Live-Vorschau starten
- **Sehr langer Tap (>2.5s)**: Sicherer Shutdown

### LIVE Modus
- **Kurzer Tap**: Foto aufnehmen
- **Langer Tap (>0.8s)**: Video-Aufnahme starten

### RECORDING Modus
- **Kurzer Tap**: Video stoppen

### Terminal-Zugriff
- **Terminal-Button** (unten links, orange): Terminal öffnen/schließen
- Virtuelle Tastatur startet automatisch
- Vollständiger Zugriff auf System-Kommandos

## Installation

### Einfache Installation (empfohlen)

Auf frischem Raspbian OS:

```bash
# Repository klonen
git clone https://github.com/Mosei1984/Nachtsichtgeraet.git
cd Nachtsichtgeraet

# Setup ausführen
sudo bash setup.sh
```

**Das war's!** Das Script macht alles automatisch:

1. **Installiert Display-Treiber** (falls `/dev/fb1` nicht existiert)
   - LCD-show für 3.5" SPI Display
   - **Startet automatisch neu** → danach `sudo bash setup.sh` nochmal ausführen
2. **Installiert Python-Abhängigkeiten**
   - python3-opencv, python3-picamera2, python3-numpy
3. **Richtet Programm ein**
   - Kopiert nach `/opt/nachtsicht`
   - Erstellt Autostart-Service
4. **Fragt nach Terminal-Access** (optional)
   - lxterminal + matchbox-keyboard
   - Für Touchscreen-Terminal ohne externe Tastatur

### Installation Workflow

```bash
# Erstes Mal (falls Display nicht eingerichtet)
sudo bash setup.sh
# → Installiert Display-Treiber
# → System startet neu

# Nach Neustart
sudo bash setup.sh
# → Installiert Programm
# → Fragt nach Terminal-Access

# Fertig
sudo reboot
```

### Nach der Installation

```bash
# Raspberry Pi neu starten
sudo reboot

# Nachtsicht startet automatisch!
# - Display zeigt Kamera-Interface
# - Doppel-Tap zum Starten
```

**Service-Befehle:**
```bash
# Status prüfen
sudo systemctl status nachtsicht.service

# Logs anzeigen
sudo journalctl -u nachtsicht.service -f

# Manuell starten/stoppen
sudo systemctl start nachtsicht.service
sudo systemctl stop nachtsicht.service
```

### Erweiterte Optionen

**Terminal-Access nachträglich installieren:**
```bash
cd /opt/nachtsicht/terminal_access
sudo bash setup_terminal.sh
```

**Manuelle Installation ohne Service:**
```bash
# Dependencies
sudo apt-get update
sudo apt-get install python3-opencv python3-picamera2 python3-numpy

# Display-Treiber (falls nötig)
git clone https://github.com/goodtft/LCD-show.git
cd LCD-show && sudo ./LCD35-show

# Programm direkt starten
python3 nachtsicht_fullscreen.py
```

Siehe [INSTALL.md](INSTALL.md) für detaillierte Anleitung.

## Optimierungen

Die optimierte Version (`nachtsicht_optimized.py`) enthält:

### Performance
- **Pre-allocated Buffers**: Reduziert Garbage Collection
- **In-place Operations**: OpenCV Operationen nutzen vorhandene Buffers
- **Caching**: USB-Mountpoint & Speicherplatz werden gecached
- **Optimized Parsing**: Schnellere Dateinummern-Extraktion
- **Adaptive HUD Updates**: HUD nur 1x/Sekunde aktualisiert

### Speicher
- ~30% weniger Speicher-Allokationen pro Frame
- Wiederverwendung von numpy Arrays
- Optimierte RGB565 Konvertierung

### CPU
- ~20% weniger CPU-Last durch Buffer-Wiederverwendung
- Schnellere Touch-Event Verarbeitung
- Reduzierte I/O Operationen

### Robustheit
- Besseres Exception Handling
- Graceful Shutdown (Ctrl+C)
- Touch-Device Fehlerbehandlung
- Sichere USB-Unmount beim Herunterfahren

## Verzeichnisstruktur

```
USB/Intern:
├── Nachtsicht_Fotos/
│   ├── Nachtsicht_Foto1.jpg
│   ├── Nachtsicht_Foto2.jpg
│   └── ...
└── Nachtsicht_Videos/
    ├── Nachtsicht_Video1.h264
    ├── Nachtsicht_Video2.h264
    └── ...
```

## Konfiguration

Anpassungen in der Datei vornehmen:

```python
FB_PATH        = "/dev/fb1"           # Framebuffer Display
TOUCH_DEV      = "/dev/input/event0"  # Touch-Device
SHORT_LONG     = 0.8                  # Long-Press Schwelle
IDLE_SHUT      = 2.5                  # Shutdown-Zeit
DBL_GAP        = 0.35                 # Doppel-Tap Fenster
EST_PHOTO_BYTES= 500_000              # Geschätzte Foto-Größe
EST_VIDEO_MBPS = 0.5                  # Video Bitrate (MB/s)
```

## Autostart

Der Autostart wird durch `setup.sh` automatisch konfiguriert. Der Service:
- Startet automatisch beim Booten (10 Sekunden Verzögerung)
- Nutzt `/opt/nachtsicht/nachtsicht_fullscreen.py`
- Läuft als root (für Hardware-Zugriff)
- Neustart bei Fehler mit 15s Verzögerung
- Logs in systemd journal

Service-Details siehe `nachtsicht.service`

### Service-Befehle

```bash
# Service starten/stoppen/neu starten
sudo systemctl start nachtsicht.service
sudo systemctl stop nachtsicht.service
sudo systemctl restart nachtsicht.service

# Autostart aktivieren/deaktivieren
sudo systemctl enable nachtsicht.service
sudo systemctl disable nachtsicht.service

# Status und Logs
sudo systemctl status nachtsicht.service
sudo journalctl -u nachtsicht.service -f
```

## Lizenz

MIT
