# Nachtsichtgerät (Night Vision Device)

Raspberry Pi 3 B basiertes Nachtsichtgerät mit Touchscreen-Steuerung.

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

```bash
# Systemd Service erstellen
sudo nano /etc/systemd/system/nachtsicht.service
```

```ini
[Unit]
Description=Nachtsicht Device
After=multi-user.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi
ExecStart=/usr/bin/python3 /home/pi/nachtsicht_optimized.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
# Service aktivieren
sudo systemctl enable nachtsicht.service
sudo systemctl start nachtsicht.service
```

## Lizenz

MIT
