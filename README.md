# Nachtsichtgerät (Night Vision Device)

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

## Touch-Gesten

### IDLE Modus
- **Doppel-Tap**: Live-Vorschau starten
- **Sehr langer Tap (>2.5s)**: Sicherer Shutdown

### LIVE Modus
- **Kurzer Tap**: Foto aufnehmen
- **Langer Tap (>0.8s)**: Video-Aufnahme starten

### RECORDING Modus
- **Kurzer Tap**: Video stoppen

## Installation

### Automatische Installation (empfohlen)

```bash
# Repository klonen oder Dateien auf Raspberry Pi kopieren
git clone https://github.com/Mosei1984/Nachtsichtgeraet.git
cd Nachtsichtgeraet

# Setup-Skript ausführen
sudo bash setup.sh
```

Das Setup-Skript führt automatisch folgende Schritte aus:
1. System aktualisieren
2. Abhängigkeiten installieren (python3-opencv, python3-picamera2, python3-numpy)
3. Arbeitsverzeichnis `/opt/nachtsicht` erstellen
4. Python-Skripte nach `/opt/nachtsicht` kopieren
5. USB-Mount-Verzeichnis `/media/usb` vorbereiten
6. Systemd-Service installieren und aktivieren

Nach dem Setup:
```bash
# Raspberry Pi neu starten (Service startet automatisch)
sudo reboot

# Oder Service manuell starten
sudo systemctl start nachtsicht.service

# Status prüfen
sudo systemctl status nachtsicht.service

# Live-Logs anzeigen
sudo journalctl -u nachtsicht.service -f
```

### Manuelle Installation

```bash
# Dependencies
sudo apt-get update
sudo apt-get install python3-opencv python3-picamera2 python3-numpy

# Projekt starten
python3 nachtsicht_optimized.py
```

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
