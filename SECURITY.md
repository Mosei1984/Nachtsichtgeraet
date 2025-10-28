# Security Policy

## Unterstützte Versionen

Wir unterstützen Sicherheitsupdates für die folgenden Versionen:

| Version | Unterstützt          |
| ------- | -------------------- |
| main    | :white_check_mark:   |
| latest  | :white_check_mark:   |
| < 0.1.0 | :x:                  |

## Sicherheitslücke melden

Wir nehmen Sicherheitsprobleme sehr ernst. Wenn du eine Sicherheitslücke im Nachtsichtgerät-Projekt entdeckst, bitte **melde sie NICHT öffentlich** über Issues.

### Wie melde ich eine Sicherheitslücke?

Nutze eine der folgenden Methoden:

1. **GitHub Security Advisories** (bevorzugt)
   - Gehe zu https://github.com/Mosei1984/Nachtsichtgeraet/security/advisories
   - Klicke auf "Report a vulnerability"
   - Fülle das Formular mit Details aus

2. **Private Kontaktaufnahme**
   - Kontaktiere die Maintainer direkt über GitHub
   - Nutze verschlüsselte Kommunikation wenn möglich

### Was sollte der Report enthalten?

- **Beschreibung**: Was ist die Sicherheitslücke?
- **Auswirkung**: Welche Schäden können entstehen?
- **Reproduktion**: Wie kann die Lücke reproduziert werden?
- **Proof of Concept**: Code oder Schritte zur Demonstration
- **Betroffene Versionen**: Welche Versionen sind betroffen?
- **Vorgeschlagener Fix**: Falls du eine Lösung hast

### Was passiert nach dem Report?

1. **Bestätigung**: Wir bestätigen den Erhalt innerhalb von **7 Tagen**
2. **Analyse**: Wir bewerten die Schwere und den Umfang
3. **Fix**: Wir entwickeln einen Patch
4. **Koordination**: Wir koordinieren die Veröffentlichung mit dir
5. **Veröffentlichung**: Wir veröffentlichen den Fix und ein Security Advisory
6. **Anerkennung**: Du wirst im Advisory erwähnt (falls gewünscht)

## Sicherheitsüberlegungen

### Hardware-Sicherheit

Das Nachtsichtgerät ist ein **Hardware-Projekt** mit besonderen Sicherheitsaspekten:

- **Root-Rechte**: Der systemd-Service läuft als root für Hardware-Zugriff (Framebuffer, Touch, Kamera)
- **Physischer Zugang**: Das Gerät ist für physischen Zugriff konzipiert
- **USB-Speicher**: Externe USB-Medien werden automatisch gemountet
- **Netzwerk**: Das Gerät sollte NICHT an unvertrauenswürdige Netzwerke angeschlossen werden

### Best Practices für Nutzer

Um die Sicherheit zu gewährleisten:

1. **Netzwerk-Isolation**: Verbinde das Pi nicht mit öffentlichen Netzwerken
2. **USB-Vorsicht**: Nutze nur vertrauenswürdige USB-Speicher
3. **Updates**: Halte Raspbian OS und Abhängigkeiten aktuell:
   ```bash
   sudo apt-get update && sudo apt-get upgrade
   ```
4. **Passwörter**: Ändere das Standard-Passwort des Pi
5. **SSH**: Deaktiviere SSH wenn nicht benötigt, oder nutze Key-basierte Authentifizierung
6. **Firewall**: Konfiguriere eine Firewall wenn Netzwerk genutzt wird

### Bekannte Einschränkungen

- **Root-Service**: Der Service benötigt root-Rechte für `/dev/fb1` und `/dev/input/event0`
- **Keine Verschlüsselung**: Gespeicherte Fotos/Videos sind nicht verschlüsselt
- **Keine Authentifizierung**: Physischer Zugang = voller Zugriff
- **Auto-Mount**: USB-Speicher werden automatisch verwendet

## Verantwortungsvolle Offenlegung

Wir bitten dich:

- Gib uns angemessene Zeit (mindestens **90 Tage**) um das Problem zu beheben
- Veröffentliche keine Details bevor ein Fix verfügbar ist
- Nutze die Lücke nicht für böswillige Zwecke
- Handle in gutem Glauben

Wir verpflichten uns:

- Dich über den Fortschritt zu informieren
- Dich bei der Lösung zu erwähnen (falls gewünscht)
- Transparent über die Lücke zu kommunizieren nach dem Fix

## Kontakt

- **GitHub Security**: https://github.com/Mosei1984/Nachtsichtgeraet/security
- **Maintainer**: @Mosei1984

Vielen Dank für deine Hilfe, das Projekt sicherer zu machen! 🔒
