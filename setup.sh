#!/bin/bash
# Nachtsichtgerät Auto-Setup für Raspberry Pi 3 B
# Einfach ausführen mit: sudo bash setup.sh
#
# Das Script installiert automatisch:
# - 3.5" SPI Display Treiber (falls nötig, mit Neustart)
# - Alle Python-Abhängigkeiten
# - Nachtsicht-Programm als Service
# - Optional: Terminal-Access

set -e

echo "========================================"
echo "  Nachtsichtgerät Setup"
echo "  Raspberry Pi 3 B + 3.5\" SPI Display"
echo "========================================"
echo ""

# Prüfe ob root
if [ "$EUID" -ne 0 ]; then 
    echo "Fehler: Bitte als root ausführen: sudo bash setup.sh"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Prüfe ob Display bereits eingerichtet ist
echo "[1/8] Display-Treiber prüfen..."
if [ ! -e "/dev/fb1" ]; then
    echo ""
    echo "╔════════════════════════════════════════╗"
    echo "║  Display-Treiber Installation nötig   ║"
    echo "╚════════════════════════════════════════╝"
    echo ""
    echo "Das 3.5\" SPI Display ist noch nicht eingerichtet."
    echo "LCD-show Treiber werden jetzt installiert."
    echo ""
    echo "WICHTIG: Nach der Installation startet das System NEU."
    echo "         Danach dieses Script erneut ausführen:"
    echo "         sudo bash setup.sh"
    echo ""
    read -p "Display-Treiber jetzt installieren? (j/N): " choice
    case "$choice" in 
      j|J|y|Y ) 
        echo ""
        echo "Display-Treiber werden installiert..."
        
        # LCD-show installieren
        cd "$SCRIPT_DIR"
        if [ -d "LCD-show" ]; then
            rm -rf LCD-show
        fi
        
        echo "Repository klonen..."
        git clone https://github.com/goodtft/LCD-show.git
        chmod -R 755 LCD-show
        
        echo ""
        echo "╔════════════════════════════════════════╗"
        echo "║  System startet in 5 Sekunden neu     ║"
        echo "║  Danach: sudo bash setup.sh            ║"
        echo "╚════════════════════════════════════════╝"
        for i in 5 4 3 2 1; do
            echo "  Neustart in $i..."
            sleep 1
        done
        
        cd LCD-show
        ./LCD35-show
        
        exit 0
        ;;
      * ) 
        echo ""
        echo "Installation abgebrochen."
        echo "Display muss vor dem Nachtsicht-Setup eingerichtet werden."
        exit 1
        ;;
    esac
else
    echo "✓ Display gefunden (/dev/fb1)"
fi

# 2. System aktualisieren
echo "[2/8] System aktualisieren..."
apt-get update

# 3. Abhängigkeiten installieren
echo "[3/8] Python-Abhängigkeiten installieren..."
apt-get install -y python3-opencv python3-picamera2 python3-numpy

# 4. Arbeitsverzeichnis erstellen
echo "[4/8] Arbeitsverzeichnis erstellen..."
mkdir -p /opt/nachtsicht
chmod 755 /opt/nachtsicht

# 5. Python-Skripte kopieren
echo "[5/8] Programm-Dateien kopieren..."
cp "$SCRIPT_DIR/nachtsicht_fullscreen.py" /opt/nachtsicht/
cp "$SCRIPT_DIR/nachtsicht_optimized.py" /opt/nachtsicht/
chmod +x /opt/nachtsicht/*.py

if [ -d "$SCRIPT_DIR/terminal_access" ]; then
    echo "  ✓ Terminal Access Modul"
    cp -r "$SCRIPT_DIR/terminal_access" /opt/nachtsicht/
fi

# 6. USB-Mount-Punkt vorbereiten
echo "[6/8] USB-Speicher vorbereiten..."
mkdir -p /media/usb

# 7. Systemd-Service installieren
echo "[7/8] Autostart-Service einrichten..."
cp "$SCRIPT_DIR/nachtsicht.service" /etc/systemd/system/
chmod 644 /etc/systemd/system/nachtsicht.service
systemctl daemon-reload
systemctl enable nachtsicht.service
echo "  ✓ Service aktiviert (startet automatisch beim Boot)"

# 8. Terminal Access Setup anbieten
echo "[8/8] Terminal Access (optional)..."
if [ -d "/opt/nachtsicht/terminal_access" ]; then
    read -p "Terminal-Zugriff installieren? (lxterminal + Tastatur) (j/N): " term_choice
    case "$term_choice" in 
      j|J|y|Y ) 
        cd /opt/nachtsicht/terminal_access
        bash setup_terminal.sh
        cd "$SCRIPT_DIR"
        echo "  ✓ Terminal Access installiert"
        ;;
      * ) 
        echo "  ⊙ Übersprungen (später: cd /opt/nachtsicht/terminal_access && sudo bash setup_terminal.sh)"
        ;;
    esac
fi

echo ""
echo "╔════════════════════════════════════════╗"
echo "║     Installation abgeschlossen! ✓     ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "Nächster Schritt:"
echo "  sudo reboot"
echo ""
echo "Nach dem Neustart:"
echo "  - Nachtsicht startet automatisch"
echo "  - Doppel-Tap auf Display für Live-Ansicht"
echo "  - Terminal-Button unten links (falls installiert)"
echo ""
echo "Service-Befehle:"
echo "  Status:    sudo systemctl status nachtsicht.service"
echo "  Logs:      sudo journalctl -u nachtsicht.service -f"
echo "  Stoppen:   sudo systemctl stop nachtsicht.service"
echo ""
