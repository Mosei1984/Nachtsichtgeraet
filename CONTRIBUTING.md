# Contributing zu Nachtsichtgerät

Vielen Dank für dein Interesse, zu diesem Projekt beizutragen! 🎉

## Wie kann ich beitragen?

Es gibt verschiedene Möglichkeiten, zum Projekt beizutragen:

- **Code**: Bugfixes, neue Features, Performance-Verbesserungen
- **Dokumentation**: README, Anleitungen, Code-Kommentare
- **Tests**: Manuelle Tests auf verschiedenen Hardware-Konfigurationen
- **Feedback**: Bug-Reports, Feature-Requests, Verbesserungsvorschläge

## Issues melden

### Bug Reports

Wenn du einen Bug findest, erstelle bitte ein Issue mit dem Bug-Report-Template. Bitte inkludiere:

- Detaillierte Beschreibung des Problems
- Schritte zur Reproduktion
- Erwartetes vs. tatsächliches Verhalten
- Hardware-Details (Pi-Modell, Kamera, Display)
- Logs (`sudo journalctl -u nachtsicht.service -n 200`)

**Labels**: `bug`, `help wanted`

### Feature Requests

Für neue Feature-Ideen nutze das Feature-Request-Template:

- Beschreibe das Problem/den Bedarf
- Schlage eine Lösung vor
- Nenne Alternativen

**Labels**: `enhancement`, `discussion`

### Sicherheitsprobleme

**Melde Sicherheitslücken NICHT öffentlich!** Nutze stattdessen:
- GitHub Security Advisories
- Siehe [SECURITY.md](SECURITY.md) für Details

## Development Setup

### Voraussetzungen

- Raspberry Pi 3 B (oder neuer)
- Raspbian OS (Bookworm empfohlen)
- IR-optimierte Kamera (Picamera2 kompatibel)
- 3.5" SPI Display (/dev/fb1)
- ADS7846 Touchscreen (/dev/input/event0)

### Installation für Entwickler

```bash
# Repository klonen
git clone https://github.com/Mosei1984/Nachtsichtgeraet.git
cd Nachtsichtgeraet

# Abhängigkeiten installieren
sudo apt-get update
sudo apt-get install python3-opencv python3-picamera2 python3-numpy

# Manuell testen (ohne Service)
python3 nachtsicht_fullscreen.py
# oder die optimierte Version:
python3 nachtsicht_optimized.py
```

### Tests auf Hardware

Da das Projekt hardware-spezifisch ist, erfolgen Tests manuell:

```bash
# Direkt ausführen
python3 nachtsicht_fullscreen.py

# Als Service testen
sudo systemctl start nachtsicht.service
sudo journalctl -u nachtsicht.service -f

# Service Status prüfen
sudo systemctl status nachtsicht.service
```

**Test-Checkliste**:
- [ ] Live-Ansicht startet per Doppel-Tap
- [ ] Foto wird per kurzem Tap gespeichert
- [ ] Video startet/stoppt per langem Tap
- [ ] HUD zeigt korrekte Informationen (Speicher, Modus, Zeit)
- [ ] USB-Speicher wird erkannt und genutzt
- [ ] Shutdown per sehr langem Tap (>2.5s) funktioniert
- [ ] Keine Crashes in den Logs

## Branching-Modell

Wir nutzen ein einfaches Git-Flow-Modell:

- **`main`**: Stabile, produktionsreife Version
- **`develop`**: Entwicklungsbranch für kommende Features
- **Feature-Branches**: `feature/<name>` für neue Features
- **Bugfix-Branches**: `fix/<name>` für Bugfixes
- **Docs-Branches**: `docs/<name>` für Dokumentation

### Workflow

1. Fork das Repository
2. Erstelle einen Feature-Branch von `develop`:
   ```bash
   git checkout develop
   git checkout -b feature/meine-neue-funktion
   ```
3. Committe deine Änderungen mit aussagekräftigen Commit-Messages
4. Pushe deinen Branch zu deinem Fork
5. Erstelle einen Pull Request nach `develop`

### Commit-Messages

Halte Commit-Messages kurz und aussagekräftig:

```
Add battery status to HUD display

- Show battery percentage in top-right corner
- Update HUD every second
- Add low-battery warning (<20%)
```

## Code-Style

### Python

- **Indentation**: 4 Spaces (kein Tab)
- **Kommentare**: Auf Deutsch
- **Naming**: 
  - `snake_case` für Funktionen und Variablen
  - `UPPER_CASE` für Konstanten
  - Sprechende Namen (z.B. `find_usb_mount()` statt `usb()`)
- **Imports**: 
  - Standard-Library zuerst
  - Dann Third-Party (cv2, numpy, picamera2)
- **Guards**: Nutze `if __name__ == "__main__":` für ausführbare Skripte
- **Error Handling**: Try/Except mit Fallbacks, graceful Shutdown

### Beispiel

```python
import os
import time
from pathlib import Path

import cv2
import numpy as np
from picamera2 import Picamera2

# Konstanten
FB_PATH = "/dev/fb1"
TOUCH_DEV = "/dev/input/event0"
SHORT_LONG = 0.8

def find_usb_mount():
    """Findet den ersten USB-Mount-Punkt unter /media/usb*"""
    for usb_dir in Path("/media").glob("usb*"):
        if usb_dir.is_mount():
            return usb_dir
    return None

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Shutdown...")
```

## Pull Request Guidelines

Bevor du einen PR erstellst:

1. **Teste lokal**: Stelle sicher, dass dein Code auf echter Hardware funktioniert
2. **Code-Style**: Folge den Style-Guidelines
3. **Dokumentation**: Aktualisiere README/Docs falls nötig
4. **Keine Secrets**: Prüfe, dass keine Passwörter, Keys oder persönliche Daten committed wurden
5. **Saubere History**: Verwende `git rebase` um unnötige Merge-Commits zu vermeiden

### PR-Template

Nutze das PR-Template und fülle alle Sektionen aus:
- Beschreibung der Änderungen
- Art der Änderung
- Test-Details (Hardware, OS, Schritte)
- Checkliste

### Review-Prozess

1. Ein Maintainer reviewed deinen PR
2. Ggf. werden Änderungen angefragt
3. Nach Approval wird der PR gemerged
4. Deine Änderungen erscheinen im nächsten Release

## Lizenz

Indem du zum Projekt beiträgst, stimmst du zu, dass deine Beiträge unter der [MIT License](LICENSE) lizenziert werden.

## Fragen?

- **Discussions**: https://github.com/Mosei1984/Nachtsichtgeraet/discussions
- **Issues**: https://github.com/Mosei1984/Nachtsichtgeraet/issues

Danke für deine Beiträge! 🚀
