# Changelog

Alle nennenswerten Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt [Semantic Versioning](https://semver.org/lang/de/).

## [Unreleased]

### Added
- GitHub Community Health Dateien (Issue-Templates, PR-Template, Contributing, CoC, Security)
- Auto-Setup-Skript (`setup.sh`) für einfache Installation
- Pyrightconfig für Windows-Entwicklung
- Erweiterte README mit Installationsanleitung

### Changed
- Service-Datei umbenannt: `nachtsicht.service.py` → `nachtsicht.service`

## [0.1.0] - 2025-01-28

### Added
- Initiale Version des Nachtsichtgerät-Projekts
- IR-optimierte Live-Ansicht mit Histogram-Equalizing
- Touchscreen-Steuerung (Doppel-Tap, Langer Tap, Sehr langer Tap)
- Foto-Aufnahme mit Auto-Nummerierung
- Video-Aufnahme (H.264)
- USB-Speicher Support mit Fallback auf internes Speicher
- Grünes HUD mit Statusanzeige (Modus, Zeit, Speicherplatz)
- Sicherer Shutdown per Touch (>2.5s)
- Optimierte Version (`nachtsicht_optimized.py`) mit:
  - Pre-allocated Buffers
  - In-place Operations
  - Caching (USB-Mountpoint, Speicherplatz)
  - ~30% weniger Speicher-Allokationen
  - ~20% weniger CPU-Last
- Systemd-Service für Autostart
- MIT Lizenz
- Deutsche Dokumentation

### Technical Details
- **Platform**: Raspberry Pi 3 B
- **OS**: Raspbian (Trixy)
- **Display**: 3.5" SPI (/dev/fb1)
- **Touch**: ADS7846 (/dev/input/event0)
- **Camera**: IR-optimierte Picamera2
- **Language**: Python 3
- **Dependencies**: opencv, picamera2, numpy

### Known Issues
- Keine Verschlüsselung für gespeicherte Medien
- Service benötigt root-Rechte für Hardware-Zugriff
- Keine automatische USB-Unmount beim Entfernen

---

## Kategorien

- **Added**: Neue Features
- **Changed**: Änderungen an bestehenden Features
- **Deprecated**: Bald zu entfernende Features
- **Removed**: Entfernte Features
- **Fixed**: Bugfixes
- **Security**: Sicherheitsrelevante Änderungen

[Unreleased]: https://github.com/Mosei1984/Nachtsichtgeraet/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Mosei1984/Nachtsichtgeraet/releases/tag/v0.1.0
