#!/bin/bash
# Nachtsichtgerät Auto-Setup für Raspberry Pi 3 B
# Führe aus mit: sudo bash setup.sh

set -e  # Bei Fehler abbrechen

echo "=== Nachtsichtgerät Setup ==="
echo ""

# Prüfe ob root
if [ "$EUID" -ne 0 ]; then 
    echo "Fehler: Bitte als root ausführen (sudo bash setup.sh)"
    exit 1
fi

# 1. System aktualisieren
echo "[1/7] System aktualisieren..."
apt-get update

# 2. Abhängigkeiten installieren
echo "[2/7] Abhängigkeiten installieren..."
apt-get install -y python3-opencv python3-picamera2 python3-numpy

# 3. Arbeitsverzeichnis erstellen
echo "[3/7] Arbeitsverzeichnis erstellen..."
mkdir -p /opt/nachtsicht
chmod 755 /opt/nachtsicht

# 4. Python-Skripte kopieren
echo "[4/7] Python-Skripte kopieren..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$SCRIPT_DIR/nachtsicht_fullscreen.py" /opt/nachtsicht/
cp "$SCRIPT_DIR/nachtsicht_optimized.py" /opt/nachtsicht/
chmod +x /opt/nachtsicht/*.py

# 5. USB-Mount-Punkt vorbereiten
echo "[5/7] USB-Mount-Verzeichnis vorbereiten..."
mkdir -p /media/usb

# 6. Systemd-Service installieren
echo "[6/7] Systemd-Service installieren..."
cp "$SCRIPT_DIR/nachtsicht.service" /etc/systemd/system/
chmod 644 /etc/systemd/system/nachtsicht.service
systemctl daemon-reload
systemctl enable nachtsicht.service

# 7. Fertig
echo "[7/7] Setup abgeschlossen!"
echo ""
echo "=== Nächste Schritte ==="
echo "1. Raspberry Pi neu starten: sudo reboot"
echo "2. Service manuell starten: sudo systemctl start nachtsicht.service"
echo "3. Status prüfen: sudo systemctl status nachtsicht.service"
echo "4. Logs anzeigen: sudo journalctl -u nachtsicht.service -f"
echo ""
echo "Der Service startet automatisch nach dem Neustart."
