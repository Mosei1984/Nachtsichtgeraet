# Vollständige Installationsanleitung

Schritt-für-Schritt Anleitung zur Installation des Nachtsichtgeräts auf Raspberry Pi 3 B.

## Voraussetzungen

- **Hardware**:
  - Raspberry Pi 3 B
  - 3.5" SPI Display (goodtft kompatibel)
  - ADS7846 Touchscreen
  - IR-optimierte Picamera (oder normale Picamera2)
  - microSD Karte (min. 8GB empfohlen)
  - Stromversorgung (5V, min. 2.5A)

- **Software**:
  - Raspbian OS (Bookworm oder neuer empfohlen)
  - Netzwerkverbindung (für Installation)
  - SSH-Zugriff oder direkte Konsole

## Installation

### Schritt 1: Raspbian OS installieren

1. Raspbian OS Image herunterladen: https://www.raspberrypi.org/software/
2. Image auf microSD Karte flashen (mit Raspberry Pi Imager)
3. Raspberry Pi booten
4. Grundkonfiguration durchführen:
   ```bash
   sudo raspi-config
   # - Tastaturlayout einstellen
   # - WiFi konfigurieren (falls benötigt)
   # - SSH aktivieren (Interface Options -> SSH)
   # - Kamera aktivieren (Interface Options -> Legacy Camera -> Enable)
   ```

### Schritt 2: Repository herunterladen

```bash
# System aktualisieren
sudo apt-get update
sudo apt-get upgrade -y

# Git installieren (falls nicht vorhanden)
sudo apt-get install -y git

# Repository klonen
cd ~
git clone https://github.com/Mosei1984/Nachtsichtgeraet.git
cd Nachtsichtgeraet
```

### Schritt 3: Display-Treiber installieren

**WICHTIG**: Dies ist ein einmaliger Vorgang und startet das System automatisch neu!

```bash
# Display Setup ausführen
sudo bash setup_display.sh
```

**Was passiert**:
1. Alte LCD-show Installation wird entfernt (falls vorhanden)
2. goodtft/LCD-show Repository wird geklont
3. 3.5" Display Treiber werden installiert
4. Bootloader-Konfiguration wird angepasst
5. **System startet automatisch neu**

Nach dem Neustart:
- Display sollte aktiv sein auf `/dev/fb1`
- Touch-Interface verfügbar auf `/dev/input/event0`
- Konsole erscheint auf dem Display

**Verifizierung**:
```bash
# Display Device prüfen
ls -l /dev/fb1
# Sollte ausgeben: crw-rw---- 1 root video ...

# Touch Device prüfen
ls -l /dev/input/event0
# Sollte ausgeben: crw-rw---- 1 root input ...

# Display-Auflösung testen
fbset -fb /dev/fb1
# Sollte 480x320 anzeigen
```

**Troubleshooting**:
- Falls Display nicht funktioniert: `sudo reboot` und erneut prüfen
- Falls Touch nicht reagiert: `sudo apt-get install xserver-xorg-input-evdev`
- Kalibrierung nötig: Siehe LCD-show Dokumentation

### Schritt 4: Hauptprogramm installieren

```bash
cd ~/Nachtsichtgeraet
sudo bash setup.sh
```

**Setup-Prozess**:
1. Prüft ob `/dev/fb1` existiert (Display-Treiber installiert)
2. Installiert Python-Abhängigkeiten:
   - python3-opencv
   - python3-picamera2
   - python3-numpy
3. Erstellt `/opt/nachtsicht` Verzeichnis
4. Kopiert Python-Skripte:
   - `nachtsicht_fullscreen.py`
   - `nachtsicht_optimized.py`
   - `terminal_access/` Modul
5. Erstellt USB-Mount-Punkt `/media/usb`
6. Installiert Systemd-Service
7. Fragt nach Terminal-Access Installation

**Während der Installation**:
```
[0/8] Display-Treiber prüfen...
/dev/fb1 gefunden - Display ist eingerichtet
[1/7] System aktualisieren...
[2/7] Abhängigkeiten installieren...
[3/7] Arbeitsverzeichnis erstellen...
[4/7] Python-Skripte kopieren...
    Terminal Access Modul wird kopiert...
[5/7] USB-Mount-Verzeichnis vorbereiten...
[6/7] Systemd-Service installieren...
[7/7] Terminal Access (optional)...
Terminal Access jetzt installieren? (lxterminal + matchbox-keyboard) (j/N):
```

**Empfehlung**: Beantworte mit `j` (ja) um Terminal-Access sofort zu installieren.

### Schritt 5: Terminal Access (optional)

Falls während `setup.sh` übersprungen, kann später installiert werden:

```bash
cd /opt/nachtsicht/terminal_access
sudo bash setup_terminal.sh
```

**Installiert**:
- **lxterminal** - Leichtgewichtiger Terminal-Emulator
- **matchbox-keyboard** - Virtuelle On-Screen Tastatur
- Optional: **onboard** - Alternative Tastatur

### Schritt 6: System starten

```bash
# Raspberry Pi neu starten
sudo reboot
```

Nach dem Neustart:
- Nachtsicht-Service startet automatisch
- Display zeigt Kamera-Interface
- IDLE-Modus aktiv

## Bedienung

### Erste Schritte

1. **Live-Ansicht starten**: Doppel-Tap auf Display
2. **Foto aufnehmen**: Kurzer Tap (im LIVE-Modus)
3. **Video aufnehmen**: Langer Tap >0.8s (im LIVE-Modus)
4. **Video stoppen**: Kurzer Tap (im RECORDING-Modus)
5. **Terminal öffnen**: Tap auf orange "TERM"-Button (unten links)
6. **Shutdown**: Sehr langer Tap >2.5s im IDLE-Modus

### USB-Speicher

1. USB-Stick einstecken
2. System erkennt automatisch Mount-Punkt unter `/media/usb*`
3. Fotos/Videos werden auf USB gespeichert
4. HUD zeigt "USB" an

Ohne USB:
- Speicherung nach `/home/pi/Nachtsicht_Fotos` und `/home/pi/Nachtsicht_Videos`
- HUD zeigt "INT" an

## Service-Verwaltung

```bash
# Service Status prüfen
sudo systemctl status nachtsicht.service

# Service stoppen
sudo systemctl stop nachtsicht.service

# Service starten
sudo systemctl start nachtsicht.service

# Service neu starten
sudo systemctl restart nachtsicht.service

# Service deaktivieren (nicht mehr beim Boot starten)
sudo systemctl disable nachtsicht.service

# Service aktivieren
sudo systemctl enable nachtsicht.service

# Logs anzeigen
sudo journalctl -u nachtsicht.service -f

# Letzte 100 Zeilen
sudo journalctl -u nachtsicht.service -n 100
```

## Manuelle Ausführung

Für Tests oder Entwicklung:

```bash
# Service stoppen (falls aktiv)
sudo systemctl stop nachtsicht.service

# Programm direkt ausführen
cd /opt/nachtsicht
python3 nachtsicht_fullscreen.py

# Oder optimierte Version
python3 nachtsicht_optimized.py

# Mit Strg+C beenden
```

## Updates

### Programm aktualisieren

```bash
cd ~/Nachtsichtgeraet
git pull

# Neue Version installieren
sudo bash setup.sh
sudo reboot
```

### System aktualisieren

Via Terminal-Access Button oder SSH:

```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo reboot
```

## Deinstallation

```bash
# Service stoppen und deaktivieren
sudo systemctl stop nachtsicht.service
sudo systemctl disable nachtsicht.service
sudo rm /etc/systemd/system/nachtsicht.service
sudo systemctl daemon-reload

# Programm entfernen
sudo rm -rf /opt/nachtsicht

# USB-Mount-Punkt entfernen (optional)
sudo rmdir /media/usb

# Display auf HDMI zurücksetzen
cd ~/LCD-show
sudo ./LCD-hdmi
```

## Troubleshooting

### Display zeigt nichts

```bash
# Display-Device prüfen
ls -l /dev/fb1

# Falls nicht vorhanden: Display-Setup erneut ausführen
cd ~/Nachtsichtgeraet
sudo bash setup_display.sh
```

### Kamera funktioniert nicht

```bash
# Kamera-Modul prüfen
vcgencmd get_camera

# Sollte ausgeben: supported=1 detected=1

# Falls nicht: Legacy Camera in raspi-config aktivieren
sudo raspi-config
# -> Interface Options -> Legacy Camera -> Enable
sudo reboot
```

### Touch reagiert nicht

```bash
# Touch-Events testen
sudo apt-get install evtest
sudo evtest /dev/input/event0

# Mit Finger auf Display tippen - sollte Events zeigen

# Falls nicht: Touchscreen-Treiber prüfen
dmesg | grep -i touch
```

### Service startet nicht

```bash
# Logs prüfen
sudo journalctl -u nachtsicht.service -n 50

# Häufige Fehler:
# - /dev/fb1 nicht gefunden -> Display-Setup
# - Kamera nicht verfügbar -> raspi-config
# - Import-Fehler -> Abhängigkeiten installieren:
sudo apt-get install python3-opencv python3-picamera2 python3-numpy
```

### Terminal-Button funktioniert nicht

```bash
# Terminal-Emulator prüfen
which lxterminal

# Falls nicht installiert:
cd /opt/nachtsicht/terminal_access
sudo bash setup_terminal.sh
```

### Zu wenig Speicherplatz

```bash
# Speicherplatz prüfen
df -h

# Alte Logs löschen
sudo journalctl --vacuum-time=7d

# Alte Aufnahmen löschen
rm ~/Nachtsicht_Fotos/Nachtsicht_Foto*.jpg
rm ~/Nachtsicht_Videos/Nachtsicht_Video*.h264
```

## Performance-Optimierung

### Optimierte Version verwenden

```bash
# In /opt/nachtsicht/nachtsicht.service ändern:
sudo nano /etc/systemd/system/nachtsicht.service

# Zeile ändern von:
# ExecStart=/usr/bin/python3 /opt/nachtsicht/nachtsicht_fullscreen.py
# zu:
# ExecStart=/usr/bin/python3 /opt/nachtsicht/nachtsicht_optimized.py

# Service neu laden
sudo systemctl daemon-reload
sudo systemctl restart nachtsicht.service
```

### RAM-Optimierung

```bash
# GPU-Speicher erhöhen (für Kamera)
sudo raspi-config
# -> Performance Options -> GPU Memory -> 256

# Reboot
sudo reboot
```

## Sicherheit

### SSH absichern

```bash
# Passwort ändern
passwd

# SSH-Key-Authentifizierung einrichten
# Auf lokalem Rechner:
ssh-keygen -t ed25519
ssh-copy-id pi@raspberrypi.local

# Passwort-Login deaktivieren
sudo nano /etc/ssh/sshd_config
# PasswordAuthentication no
sudo systemctl restart ssh
```

### Sudo ohne Passwort (für Terminal-Access)

```bash
sudo visudo

# Am Ende hinzufügen:
# pi ALL=(ALL) NOPASSWD: ALL

# WARNUNG: Reduziert Sicherheit!
```

## Backup

### Konfiguration sichern

```bash
# Skripte sichern
cd /opt/nachtsicht
tar -czf ~/nachtsicht-backup-$(date +%Y%m%d).tar.gz *.py terminal_access/

# Auf lokalen Rechner kopieren (via scp)
# Auf lokalem Rechner:
scp pi@raspberrypi.local:~/nachtsicht-backup-*.tar.gz .
```

### SD-Karte Image erstellen

Auf lokalem Rechner (Linux/Mac):

```bash
# SD-Karte Image erstellen
sudo dd if=/dev/sdX of=~/nachtsicht-sdcard-backup.img bs=4M status=progress

# Komprimieren
gzip ~/nachtsicht-sdcard-backup.img
```

## Support

- **GitHub Issues**: https://github.com/Mosei1984/Nachtsichtgeraet/issues
- **Dokumentation**: [README.md](README.md)
- **Terminal Access**: [terminal_access/README.md](terminal_access/README.md)
