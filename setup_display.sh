#!/bin/bash
#
# Display Setup für 3.5" SPI LCD (goodtft)
# Muss VOR dem Hauptprogramm einmalig ausgeführt werden
#

set -e

echo "======================================"
echo "3.5\" SPI Display Setup"
echo "======================================"
echo ""
echo "ACHTUNG: Dieses Script installiert LCD-show Treiber"
echo "         für das 3.5\" SPI Display (/dev/fb1)"
echo ""
echo "Nach der Installation:"
echo "  - Das System wird automatisch neu gestartet"
echo "  - Display wird auf /dev/fb1 verfügbar sein"
echo "  - Touch-Interface auf /dev/input/event0"
echo ""

# Prüfe ob als root ausgeführt
if [ "$EUID" -ne 0 ]; then 
    echo "Bitte als root ausführen: sudo $0"
    exit 1
fi

read -p "Fortfahren? (j/N): " choice
case "$choice" in 
  j|J|y|Y ) 
    echo "Setup wird fortgesetzt..."
    ;;
  * ) 
    echo "Abgebrochen."
    exit 0
    ;;
esac

echo ""
echo "[1/5] Alte LCD-show Installation entfernen (falls vorhanden)..."
if [ -d "LCD-show" ]; then
    rm -rf LCD-show
    echo "Alte Installation entfernt"
fi

echo ""
echo "[2/5] LCD-show Repository klonen..."
git clone https://github.com/goodtft/LCD-show.git
echo "Repository geklont"

echo ""
echo "[3/5] Berechtigungen setzen..."
chmod -R 755 LCD-show
echo "Berechtigungen gesetzt"

echo ""
echo "[4/5] Display-Treiber installieren..."
cd LCD-show/
echo "HINWEIS: Das System wird nach der Installation automatisch neu starten!"
echo ""

# 5 Sekunden Warnung
for i in 5 4 3 2 1; do
    echo "Neustart in $i Sekunden... (Strg+C zum Abbrechen)"
    sleep 1
done

echo ""
echo "[5/5] LCD35-show ausführen..."
./LCD35-show

# Das Script wird hier nicht weiterlaufen, da LCD35-show einen Reboot durchführt
