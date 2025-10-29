#!/bin/bash
#
# Setup-Script für Terminal Access Modul
# Installiert Terminal Emulator und virtuelle Tastatur
#

set -e

echo "======================================"
echo "Terminal Access Setup für Nachtsichtgerät"
echo "======================================"

# Prüfe ob als root ausgeführt
if [ "$EUID" -ne 0 ]; then 
    echo "Bitte als root ausführen: sudo $0"
    exit 1
fi

echo ""
echo "[1/4] System aktualisieren..."
apt-get update

echo ""
echo "[2/4] Terminal Emulator (lxterminal) installieren..."
apt-get install -y lxterminal

echo ""
echo "[3/4] Virtuelle Tastatur (matchbox-keyboard) installieren..."
apt-get install -y matchbox-keyboard

echo ""
echo "[4/4] Alternative: Onboard Tastatur (optional)..."
read -p "Möchten Sie zusätzlich Onboard installieren? (j/N): " choice
case "$choice" in 
  j|J|y|Y ) 
    apt-get install -y onboard
    echo "Onboard installiert"
    ;;
  * ) 
    echo "Onboard übersprungen"
    ;;
esac

echo ""
echo "======================================"
echo "Installation abgeschlossen!"
echo "======================================"
echo ""
echo "Verwendung:"
echo "  - Terminal-Button im Nachtsicht-Interface antippen"
echo "  - Terminal öffnet sich auf dem Display"
echo "  - Virtuelle Tastatur erscheint automatisch"
echo ""
echo "Konfiguration:"
echo "  - Display: /dev/fb1 (SPI)"
echo "  - Touch: /dev/input/event0 (ADS7846)"
echo ""
echo "Hinweis:"
echo "  Für Netzwerkzugriff WiFi/Ethernet konfigurieren"
echo "  Updates: sudo apt-get update && sudo apt-get upgrade"
echo ""
