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
echo "[1/4] Warte auf apt-Lock..."
# Warte bis apt-Lock frei ist
while fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1 ; do
    echo "  apt wird gerade verwendet, warte..."
    sleep 2
done

echo ""
echo "[2/4] Python3-Pakete installieren..."
apt-get install -y python3-pip python3-pillow

echo ""
echo "[3/4] pyte Terminal Emulator Library installieren..."
# Verwende --break-system-packages für externally-managed-environment
pip3 install --break-system-packages pyte
echo "pyte installiert"

echo ""
echo "[4/4] User zu video Gruppe hinzufügen..."
# Framebuffer-Zugriff
usermod -a -G video $SUDO_USER 2>/dev/null || usermod -a -G video pi
echo "User zur video Gruppe hinzugefügt"

echo ""
echo "======================================"
echo "Installation abgeschlossen!"
echo "======================================"
echo ""
echo "WICHTIG: System neu starten für Gruppen-Änderungen:"
echo "  sudo reboot"
echo ""
echo "Verwendung:"
echo "  - Terminal-Button im Nachtsicht-Interface antippen"
echo "  - Integriertes Terminal öffnet sich als Overlay"
echo "  - Virtuelle Tastatur am unteren Bildschirmrand"
echo "  - EXIT-Taste auf Tastatur zum Schließen"
echo ""
echo "Konfiguration:"
echo "  - Display: /dev/fb1 (480x320 SPI)"
echo "  - Terminal: 480x180 (20 Zeilen x 60 Spalten)"
echo "  - Tastatur: 480x140 (virtuelle On-Screen-Tastatur)"
echo ""
echo "Features:"
echo "  - Vollständiges QWERTY-Layout"
echo "  - Shift/Ctrl/Alt/Symbols Tasten"
echo "  - Pfeiltasten, ESC, Tab, Enter, Backspace"
echo "  - PTY-basiertes Terminal (bash)"
echo "  - VT100-Emulation mit pyte"
echo ""
