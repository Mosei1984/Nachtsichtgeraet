# Terminal Access - Virtuelle Tastatur Edition

Integriertes Terminal mit virtueller On-Screen-Tastatur für das Nachtsichtgerät.

## Überblick

Diese Implementation bietet ein vollständig integriertes Terminal-System mit virtueller Tastatur, das **keine externe Hardware** (USB-Tastatur) oder **externe Software** (fbterm) benötigt.

## Features

### ✅ Terminal Emulator
- **PTY-basiert**: Echtes Pseudo-Terminal mit bash
- **VT100-Emulation**: Vollständige ANSI-Escape-Sequenzen via pyte
- **Non-blocking I/O**: Asynchrones Lesen/Schreiben
- **480x180 Pixel**: 20 Zeilen x 60 Spalten

### ✅ Virtuelle Tastatur
- **QWERTY-Layout**: Vollständige Tastatur mit allen Zeichen
- **Multiple Layouts**: Normal, Shift, Symbols
- **Modifier-Tasten**: Shift, Ctrl, Alt
- **Spezial-Tasten**: Pfeiltasten, ESC, Tab, Enter, Backspace
- **480x140 Pixel**: Optimiert für Touch-Bedienung

### ✅ Touch-Integration
- **Overlay-Modus**: Terminal überlagert Kamera-Ansicht
- **Touch-Optimiert**: Große Tasten für präzises Tippen
- **Visual Feedback**: Aktive Modifier werden hervorgehoben

## Display-Layout

```
┌─────────────────────────────────┐  480x320 Pixel
│  Terminal Output                │  SPI Display
│  (480x180 Pixel)                │  /dev/fb1
│  20 Zeilen x 60 Spalten         │
│  VT100 Emulation                │
│  bash Shell                     │
├─────────────────────────────────┤
│  Virtuelle Tastatur             │
│  (480x140 Pixel)                │
│  ` 1 2 3 4 5 6 7 8 9 0 - = BKSP│
│  TAB q w e r t y u i o p [ ] \  │
│  ESC a s d f g h j k l ; ' ENTER│
│  SHIFT z x c v b n m , . / ↑ SHT│
│  CTRL ALT SYM [SPACE] LEFT ↓ →  │
└─────────────────────────────────┘
```

## Installation

### Abhängigkeiten installieren

```bash
cd terminal_access
sudo ./setup_terminal.sh
sudo reboot
```

Das Script installiert:
- `python3-pip`
- `pyte` (VT100 Terminal Emulator Library)
- Video-Gruppen-Berechtigungen

### Manuelle Installation

```bash
sudo apt-get install -y python3-pip
pip3 install pyte
sudo usermod -a -G video $USER
```

## Verwendung

### Terminal öffnen

1. Starte Nachtsicht-App: `python3 nachtsicht_fullscreen.py`
2. Tippe auf "TERM"-Button (untere linke Ecke, orange)
3. Terminal öffnet sich mit Tastatur

### Terminal schließen

- Tippe auf "EXIT"-Taste auf der Tastatur (unten rechts)
- Oder gib `exit` ein und drücke ENTER

### Befehle eingeben

1. Tippe Zeichen auf virtueller Tastatur
2. Text erscheint im Terminal
3. ENTER zum Ausführen

### Beispiele

```bash
# Verzeichnis anzeigen
ls -la

# Aktuelles Verzeichnis
pwd

# System-Info
uname -a

# Python starten
python3
>>> print("Hello from Terminal!")
>>> exit()

# Datei bearbeiten (Nano)
nano test.txt
```

## Tastatur-Referenz

### Normale Tasten

```
` 1 2 3 4 5 6 7 8 9 0 - = BKSP
TAB q w e r t y u i o p [ ] \
ESC a s d f g h j k l ; ' ENTER
SHIFT z x c v b n m , . / ↑ SHIFT
CTRL ALT SYM [SPACE] SYM ← ↓ → EXIT
```

### Shift-Layout

Tippe SHIFT für Großbuchstaben und Sonderzeichen:

```
~ ! @ # $ % ^ & * ( ) _ + BKSP
TAB Q W E R T Y U I O P { } |
ESC A S D F G H J K L : " ENTER
SHIFT Z X C V B N M < > ? ↑ SHIFT
CTRL ALT SYM [SPACE] SYM ← ↓ → EXIT
```

### Symbol-Layout

Tippe SYM für zusätzliche Symbole:

```
` 1 2 3 4 5 6 7 8 9 0 - = BKSP
TAB ! @ # $ % ^ & * ( ) _ + \
ESC ~ { } [ ] | ; : ' " < ENTER
SHIFT / ? . , < > = + - _ ↑ SHIFT
CTRL ALT ABC [SPACE] ABC ← ↓ → EXIT
```

### Spezial-Tasten

| Taste | Funktion | Bytes |
|-------|----------|-------|
| ENTER | Befehl ausführen | `\r` |
| BKSP | Zeichen löschen | `\x7f` (DEL) |
| TAB | Tabulator | `\t` |
| ESC | Escape | `\x1b` |
| SPACE | Leertaste | ` ` |
| ↑ | Hoch (History) | `\x1b[A` |
| ↓ | Runter (History) | `\x1b[B` |
| → | Rechts | `\x1b[C` |
| ← | Links | `\x1b[D` |
| EXIT | Terminal schließen | - |

### Modifier-Tasten

| Taste | Funktion | Verhalten |
|-------|----------|-----------|
| SHIFT | Großbuchstaben / Sonderzeichen | Sticky (bleibt aktiv bis nächste Taste) |
| CTRL | Ctrl-Kombinationen | Sticky |
| ALT | Alt-Taste | Sticky |
| SYM | Symbol-Layout | Toggle |
| ABC | Zurück zu Normal-Layout | Toggle |

### Tastatur-Kombinationen

| Kombination | Funktion | Bytes |
|-------------|----------|-------|
| Ctrl+C | Prozess unterbrechen | `\x03` |
| Ctrl+D | EOF / Shell beenden | `\x04` |
| Ctrl+L | Screen löschen | `\x0c` |
| Ctrl+Z | Prozess suspendieren | `\x1a` |
| Ctrl+A | Zeilenanfang | `\x01` |
| Ctrl+E | Zeilenende | `\x05` |

## Technische Details

### Architektur

```
┌────────────────────────────────────────┐
│  nachtsicht_fullscreen.py              │
│  (Main Application)                    │
├────────────────────────────────────────┤
│  terminal_launcher.py                  │
│  - Lifecycle Management                │
│  - Rendering Coordination              │
│  - Touch Event Routing                 │
├────────────────────┬───────────────────┤
│  terminal_emulator.py │ vkeyboard.py   │
│  - PTY Management     │ - Layouts      │
│  - pyte Integration   │ - Hit-Testing  │
│  - VT100 Rendering    │ - Key-Mapping  │
└────────────────────┴───────────────────┘
```

### Datenfluss

```
Touch Event → handle_gestures()
    ↓
terminal_launcher.handle_touch(x, y)
    ↓
vkeyboard.hit_test(x, y) → Key-Label
    ↓
vkeyboard.process_key(label) → Bytes + Exit-Flag
    ↓
terminal_emulator.write(bytes) → PTY
    ↓
bash processes input
    ↓
PTY → terminal_emulator.read()
    ↓
pyte.Stream.feed(data)
    ↓
pyte.Screen (VT100 Buffer)
    ↓
terminal_emulator.render() → Frame
    ↓
Framebuffer /dev/fb1
```

### Module

#### vkeyboard.py

```python
class VirtualKeyboard:
    - LAYOUT_NORMAL: Standard-Layout
    - LAYOUT_SHIFT: Shift-Layout
    - LAYOUT_SYMBOLS: Symbol-Layout
    
    Methods:
    - draw(frame): Rendert Tastatur
    - hit_test(x, y): Prüft Touch-Koordinaten
    - process_key(label): Verarbeitet Tastendruck
    - get_info_text(): Aktive Modifier
```

#### terminal_emulator.py

```python
class TerminalEmulator:
    - screen: pyte.Screen (VT100 Buffer)
    - stream: pyte.ByteStream
    - master_fd: PTY File Descriptor
    - pid: Shell Process ID
    
    Methods:
    - start(shell): Startet Shell in PTY
    - stop(): Beendet Shell
    - write(data): Schreibt zu PTY
    - read(): Liest von PTY (non-blocking)
    - render(frame): Rendert Terminal-Output
    - is_alive(): Prüft Shell-Status
```

#### terminal_launcher.py

```python
class TerminalLauncher:
    - terminal: TerminalEmulator Instance
    - keyboard: VirtualKeyboard Instance
    
    Methods:
    - launch_terminal(): Startet Terminal+Keyboard
    - close_terminal(): Beendet Terminal
    - toggle_terminal(): Toggle Terminal
    - update(): Terminal-Update-Loop
    - render(frame): Rendert Terminal+Keyboard
    - handle_touch(x, y): Touch-Event-Handling
```

### Konfiguration

#### Terminal-Größe anpassen

In `terminal_launcher.py`:

```python
self.terminal = TerminalEmulator(
    width=480,    # Pixel-Breite
    height=180,   # Pixel-Höhe
    cols=60,      # Zeichen pro Zeile
    rows=20       # Anzahl Zeilen
)
```

#### Tastatur-Größe anpassen

```python
self.keyboard = VirtualKeyboard(
    width=480,      # Pixel-Breite
    height=140,     # Pixel-Höhe
    y_offset=180    # Y-Position (nach Terminal)
)
```

#### Layout anpassen

In `vkeyboard.py` die LAYOUT-Arrays editieren:

```python
LAYOUT_NORMAL = [
    ['`', '1', '2', ...],
    ['TAB', 'q', 'w', ...],
    ...
]
```

## Testing

### Tastatur testen

```bash
python3 terminal_access/test_vkeyboard.py
```

Tests:
- ✓ Rendering
- ✓ Hit-Testing
- ✓ Normale Tasten
- ✓ Spezial-Tasten
- ✓ Modifier-Tasten
- ✓ Shift-Layout
- ✓ Symbol-Layout
- ✓ Exit-Taste
- ✓ Visueller Test (interaktiv)

### Terminal testen

```bash
python3 terminal_access/test_terminal_emu.py
```

Tests:
- ✓ Start/Stop
- ✓ Write/Read
- ✓ Rendering
- ✓ is_alive Check
- ✓ Interaktiver Test (10 Sekunden)

### Integration testen

```bash
# Vollständiger Test auf Raspberry Pi
python3 nachtsicht_fullscreen.py
```

1. Terminal-Button antippen
2. Terminal sollte erscheinen
3. Tippe "ls" + ENTER
4. Verzeichnis-Inhalt sollte erscheinen
5. Tippe EXIT zum Schließen

## Troubleshooting

### "pyte nicht verfügbar"

```bash
pip3 install pyte
# Oder
sudo apt-get install python3-pip
pip3 install pyte
```

### "Terminal startet nicht"

Prüfe Dependencies:

```bash
python3 -c "import pyte; print('pyte OK')"
python3 -c "import cv2; print('cv2 OK')"
python3 -c "import numpy; print('numpy OK')"
```

### "Tastatur wird nicht angezeigt"

Prüfe Rendering:

```python
# In nachtsicht_fullscreen.py main loop
if terminal_launcher.is_active():
    terminal_launcher.render(disp)  # Muss aufgerufen werden
```

### "Touch reagiert nicht"

Prüfe Touch-Koordinaten:

```python
# In handle_gestures()
print(f"Touch: {cur_x}, {cur_y}")
```

Koordinaten sollten zwischen 0-480 (x) und 0-320 (y) sein.

### "Terminal-Output fehlt"

Shell braucht Zeit zum Starten:

```python
terminal.start()
time.sleep(0.5)  # Warte auf Shell-Startup
terminal.write(b'ls\n')
```

### "Shell beendet sich sofort"

Prüfe PTY:

```bash
# Im Terminal-Test
terminal.is_alive()  # Sollte True sein
```

Wenn False, prüfe:
- Bash installiert: `which bash`
- PTY-Berechtigungen: `ls -l /dev/ptmx`

## Performance

### Optimierungen

1. **Pre-allocated Buffers**: Tastatur-Rectangles werden nur einmal berechnet
2. **Non-blocking I/O**: Terminal liest ohne zu blockieren
3. **Efficient Rendering**: Nur geänderte Bereiche werden aktualisiert
4. **Fixed Font**: 8x9 Pixel Zeichen für schnelles Rendering

### Benchmarks (Raspberry Pi 3B)

- Terminal-Startup: ~500ms
- Frame-Rendering: ~10ms (Terminal + Tastatur)
- Touch-Response: <50ms
- Terminal-Output: ~10ms (pro Read-Zyklus)

## Known Issues

1. **Font-Größe**: Fixed 8x9 Pixel, nicht skalierbar
2. **Scrollback**: Limitiert auf 20 Zeilen (Screen-Buffer)
3. **Touch-Debouncing**: Schnelles Tippen kann Tasten auslassen
4. **ANSI-Farben**: Nicht implementiert (nur Graustufen)
5. **Mouse**: Kein Mouse-Support im Terminal

## Future Improvements

- [ ] Scrollback via Touch-Swipe
- [ ] ANSI-Farben-Support
- [ ] Variable Font-Größe
- [ ] Alternative Layouts (QWERTZ, AZERTY)
- [ ] Auto-Completion Overlay
- [ ] Command History Browser
- [ ] Copy/Paste Funktionalität
- [ ] Tastatur-Haptik (Touch-Vibration)
- [ ] Tastatur-Sound-Feedback

## Lizenz

Siehe LICENSE im Projekt-Root.

## Credits

- **pyte**: Terminal Emulator Library (https://github.com/selectel/pyte)
- **OpenCV**: Computer Vision Library
- **NumPy**: Array Processing
