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
echo "[2/4] Framebuffer Terminal (fbterm) installieren..."
apt-get install -y fbterm

echo ""
echo "[3/4] User zu video Gruppe hinzufügen..."
# fbterm braucht Zugriff auf Framebuffer
usermod -a -G video $SUDO_USER 2>/dev/null || usermod -a -G video pi
echo "User zur video Gruppe hinzugefügt"

echo ""
echo "[4/4] fbterm Berechtigungen setzen..."
# fbterm braucht setuid für direkten Framebuffer-Zugriff
chmod u+s /usr/bin/fbterm 2>/dev/null || true
echo "Berechtigungen gesetzt"

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
echo "  - fbterm öffnet sich auf /dev/fb1"
echo "  - Bedienung mit externer USB-Tastatur"
echo "  - Oder via SSH für Eingaben"
echo ""
echo "Konfiguration:"
echo "  - Display: /dev/fb1 (SPI)"
echo "  - Terminal: fbterm (Framebuffer-basiert)"
echo ""
echo "Hinweis:"
echo "  fbterm läuft direkt auf Framebuffer (kein X11 nötig)"
echo "  Für Eingaben externe USB-Tastatur verwenden"
echo "  Oder via SSH verbinden: ssh valentin@NigthCam.local"
echo ""
