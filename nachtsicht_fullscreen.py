#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# NightCam Touch Edition
#
# - IR-optimierte Live-Ansicht direkt aufs 3.5" SPI-Display (/dev/fb1)
# - Grünes HUD mit Status / Rest-Speicher
# - Fotos & Videos mit Autonummerierung
# - Speichern bevorzugt auf USB (/media/usb*), sonst /home/pi
# - Steuerung nur per Touchscreen (ADS7846 @ /dev/input/event0)
#
# Touch-Gesten:
#   STATE idle:
#       Doppel-Tap      -> state = "live" (Livevorschau starten)
#       Sehr langer Tap (>2.5 s gedrückt halten) -> sicherer Shutdown
#
#   STATE live:
#       Kurzer Tap      -> Foto aufnehmen
#       Langer Tap (>0.8 s gedrückt halten) -> Video starten (state="recording")
#
#   STATE recording:
#       Kurzer Tap      -> Video stoppen (back to "live")
#
# Hinweis:
#   "Tap" = Finger runter und wieder hoch.
#   "Langer Tap" = Finger halten und dann loslassen nach >0.8s.
#   "Sehr langer Tap" = Finger halten in idle nach >2.5s.
#
# Autor: Martin Hofer

import os, time, glob, shutil, fcntl, mmap, struct, subprocess, sys, select, struct as st, threading
import cv2, numpy as np
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput

try:
    from terminal_access.terminal_launcher import TerminalLauncher
    from terminal_access.touch_button import TerminalButton
    from terminal_access.usb_manager import USBManager
    TERMINAL_AVAILABLE = True
except ImportError:
    TERMINAL_AVAILABLE = False
    print("[WARN] Terminal Access Modul nicht verfügbar")

############################
# KONFIG
############################

FB_PATH        = "/dev/fb1"    # fest auf dein TFT
TOUCH_DEV      = "/dev/input/event0"  # ADS7846 Touchscreen
SHORT_LONG     = 0.8           # >0.8s in LIVE => Video starten
IDLE_SHUT      = 2.5           # >2.5s in IDLE => Shutdown
DBL_GAP        = 0.35          # Doppeltap-Fenster
EST_PHOTO_BYTES= 500_000       # ~0.5MB/JPG
EST_VIDEO_MBPS = 0.5           # ~0.5 MB/s => ~30 MB/min

FBIOGET_VSCREENINFO = 0x4600

############################
# SPEICHER / USB
############################

_usb_cache = None
_usb_cache_time = 0
_usb_last_check = 0  # Für häufigere Hot-Unplug-Checks
_manual_unmount = False  # Verhindert Auto-Mount nach manuellem Unmount

def usb_mountpoint():
    global _usb_cache, _usb_cache_time, _usb_last_check, _manual_unmount
    now = time.time()
    
    # Wenn USB physisch entfernt wurde, manual_unmount Flag zurücksetzen
    usb_dev = "/dev/sda1"
    if not os.path.exists(usb_dev):
        if _manual_unmount:
            print(f"[USB] Device entfernt, Auto-Mount wieder aktiviert")
            _manual_unmount = False
    
    # Häufige Checks (alle 2s) ob noch gemountet, auch wenn Cache gültig
    if _usb_cache is not None and (now - _usb_last_check) > 2.0:
        if not os.path.ismount(_usb_cache):
            print(f"[USB] Hot-Unplug erkannt: {_usb_cache} nicht mehr gemountet")
            _usb_cache = None
            _usb_cache_time = 0
        _usb_last_check = now
    
    # Cache nur verwenden wenn Mountpoint noch existiert UND gemountet ist
    if _usb_cache is not None and (now - _usb_cache_time) < 5.0:
        if os.path.ismount(_usb_cache):
            return _usb_cache
        else:
            print(f"[USB] Cache ungültig: {_usb_cache} nicht mehr gemountet")
            _usb_cache = None
    
    # Auto-Mount: Prüfe ob USB-Device existiert aber nicht gemountet
    # ABER: Überspringe wenn manuell unmountet wurde
    mount_target = "/media/usb"
    
    if os.path.exists(usb_dev) and not os.path.ismount(mount_target) and not _manual_unmount:
        print(f"[USB] {usb_dev} gefunden aber nicht gemountet")
        os.makedirs(mount_target, exist_ok=True)
        try:
            # Mount mit User-Rechten (uid/gid vom aktuellen User)
            uid = os.getuid()
            gid = os.getgid()
            subprocess.run(["sudo", "mount", "-o", f"uid={uid},gid={gid},umask=000", 
                          usb_dev, mount_target], check=True, timeout=5)
            print(f"[USB] Auto-Mount erfolgreich: {mount_target}")
            time.sleep(0.5)  # Kurz warten bis Mount sichtbar
        except Exception as e:
            print(f"[USB] Auto-Mount fehlgeschlagen: {e}")
    
    # Mehrere mögliche Base-Pfade für verschiedene Raspbian-Versionen
    base_paths = [
        "/media/valentin",  # User valentin
        "/media/pi",        # Ältere Raspbian-Versionen
        "/media"            # Fallback für allgemeine Struktur
    ]
    
    for base in base_paths:
        if not os.path.isdir(base):
            continue
        
        for e in os.scandir(base):
            if e.is_dir() and e.name.startswith("usb"):
                # NUR wenn tatsächlich als Mountpoint gemountet
                if os.path.ismount(e.path):
                    return e.path
    
    return None

def ensure_dirs():
    usb = usb_mountpoint()
    if usb:
        pdir = os.path.join(usb, "Nachtsicht_Fotos")
        vdir = os.path.join(usb, "Nachtsicht_Videos")
    else:
        # Verwende HOME-Verzeichnis des aktuellen Users
        home = os.path.expanduser("~")
        pdir = os.path.join(home, "Nachtsicht_Fotos")
        vdir = os.path.join(home, "Nachtsicht_Videos")
    os.makedirs(pdir, exist_ok=True)
    os.makedirs(vdir, exist_ok=True)
    return pdir, vdir

def next_photo():
    pdir, _ = ensure_dirs()
    ex = glob.glob(os.path.join(pdir, "Nachtsicht_Foto*.jpg"))
    n = 0
    for p in ex:
        b = os.path.basename(p)
        try:
            num = int(b.replace("Nachtsicht_Foto","").replace(".jpg",""))
            n = max(n, num)
        except:
            pass
    return os.path.join(pdir, f"Nachtsicht_Foto{n+1}.jpg")

def next_video():
    _, vdir = ensure_dirs()
    ex = glob.glob(os.path.join(vdir, "Nachtsicht_Video*.h264"))
    n = 0
    for p in ex:
        b = os.path.basename(p)
        try:
            num = int(b.replace("Nachtsicht_Video","").replace(".h264",""))
            n = max(n, num)
        except:
            pass
    return os.path.join(vdir, f"Nachtsicht_Video{n+1}.h264")

def next_video_ts():
    _, vdir = ensure_dirs()
    ts = time.strftime("%Y-%m-%d_%H%M%S")
    us = int((time.time() % 1) * 1_000_000)
    return os.path.join(vdir, f"Nachtsicht_Video_{ts}_{us:06d}.h264")

def free_bytes_path():
    path = usb_mountpoint() or os.path.expanduser("~")
    st2 = shutil.disk_usage(path)
    return st2.free

def estimate_capacity():
    fb = free_bytes_path()
    photos = int(fb // EST_PHOTO_BYTES)
    mins   = int((fb/1024/1024) / EST_VIDEO_MBPS) // 60
    return photos, mins

############################
# FRAMEBUFFER HANDLING
############################

def open_fb(path):
    fd = os.open(path, os.O_RDWR)

    # Try ioctl to get resolution. Fallback to 480x320 if parsing fails.
    try:
        raw = fcntl.ioctl(fd, FBIOGET_VSCREENINFO, b"\x00"*160)
        # fb_var_screeninfo beginnt mit:
        # __u32 xres, yres, xres_virtual, yres_virtual,
        # xoffset, yoffset, bits_per_pixel, grayscale, ...
        # Das sind 8 * u32 = 8 * 4 = 32 Bytes.
        xres, yres, xrv, yrv, xoff, yoff, bpp, gray = struct.unpack_from("8I", raw, 0)
        if xres == 0 or yres == 0:
            raise ValueError("bad ioctl dims")
    except Exception:
        # Fallback für exotische Treiber
        xres, yres, bpp = 480, 320, 16

    # wir rendern sowieso als RGB565 (16bpp)
    fbsize = xres * yres * 2
    mm = mmap.mmap(fd, fbsize, mmap.MAP_SHARED,
                   mmap.PROT_WRITE | mmap.PROT_READ, 0)
    print(f"[FB] {path} {xres}x{yres}@{bpp}bpp")
    return fd, mm, xres, yres, bpp

def bgr_to_rgb565(bgr):
    b = (bgr[:,:,0]>>3).astype(np.uint16)
    g = (bgr[:,:,1]>>2).astype(np.uint16)
    r = (bgr[:,:,2]>>3).astype(np.uint16)
    return ((r<<11)|(g<<5)|b).tobytes()

def fb_draw(bgr, fb_mem, w, h):
    resized = cv2.resize(bgr, (w,h), interpolation=cv2.INTER_LINEAR)
    fb_mem.seek(0)
    fb_mem.write(bgr_to_rgb565(resized))

############################
# KAMERA
############################

picam = Picamera2()
picam.configure(
    picam.create_preview_configuration(
        main={"size": (640,480)},
        controls={"AeEnable":True, "AwbEnable":True}
    )
)
encoder = H264Encoder(bitrate=int(4_000_000))
video_out = None

############################
# STATE UND AUFNAHME
############################

state = "idle"
rec_name = None
_stopping_video = False

def take_photo():
    fn = next_photo()
    frame = picam.capture_array()
    gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    enh   = cv2.equalizeHist(gray)
    cv2.imwrite(fn, enh)
    ph, mn = estimate_capacity()
    print(f"[FOTO] {fn} | Rest ~{ph} Fotos / ~{mn} min Video")

def _stop_video_thread(rec_file, out_handle):
    global _stopping_video
    try:
        picam.stop_recording()
    except Exception as e:
        print(f"[VIDEO] ERROR stop_recording: {e}")
    
    if out_handle:
        try:
            out_handle.close()
        except Exception as e:
            print(f"[VIDEO] ERROR close: {e}")
    
    _stopping_video = False
    print(f"[VIDEO] SAVED -> {rec_file}")

def start_video():
    global state, rec_name, video_out, _stopping_video
    if _stopping_video or state == "recording":
        return
    rec_name = next_video_ts()
    print(f"[VIDEO] START -> {rec_name}")
    video_out = FileOutput(rec_name)
    picam.start_recording(encoder, video_out)
    state = "recording"

def stop_video():
    global state, video_out, _stopping_video
    if state == "recording":
        print("[VIDEO] STOP")
        _stopping_video = True
        state = "live"
        
        worker = threading.Thread(target=_stop_video_thread, args=(rec_name, video_out))
        worker.daemon = True
        worker.start()
        
        video_out = None

def safe_shutdown():
    global _stopping_video
    print("[SHUTDOWN] init")
    if state == "recording":
        stop_video()
    
    while _stopping_video:
        print("[SHUTDOWN] warte auf Video-Stop...")
        time.sleep(0.1)
    
    os.sync()

    base = "/media"
    if os.path.isdir(base):
        for e in os.scandir(base):
            if e.is_dir() and e.name.startswith("usb"):
                print(f"[SHUTDOWN] umount {e.path}")
                subprocess.call(["sudo","umount","-l", e.path])

    os.sync()
    print("[SHUTDOWN] poweroff ...")
    subprocess.call(["sudo","poweroff"])

############################
# TOUCH-EVENT HANDLING
############################
#
# Wir lesen /dev/input/event0 roh.
# Abs-Events (ABS_X / ABS_Y) geben Position, Key-Events (BTN_TOUCH)
# sagen "Finger down/up".
#
# Wir brauchen:
# - down_time
# - up_time
# - last_tap_time
# - click_pending für Doppeltap
#

touch_fd = None
ABS_X = 0x00
ABS_Y = 0x01
BTN_TOUCH = 0x14a  # oft 330 dezimal

cur_x = 0
cur_y = 0
norm_x = 0  # Normalisierte Display-Koordinaten (0-480)
norm_y = 0  # Normalisierte Display-Koordinaten (0-320)
finger_down = False
down_time = 0.0

click_pending = False
last_tap_time = 0.0

terminal_launcher = None
terminal_button = None
usb_manager_active = False
usb_manager = None
fb_w = 480  # Wird in main() gesetzt
fb_h = 320  # Wird in main() gesetzt

def open_touch():
    global touch_fd
    try:
        touch_fd = os.open(TOUCH_DEV, os.O_RDONLY | os.O_NONBLOCK)
        print(f"[TOUCH] opened {TOUCH_DEV}")
    except Exception as e:
        print(f"[TOUCH] FAIL open {TOUCH_DEV}: {e}")
        touch_fd = None

def read_touch_events():
    """
    Liest alle pending Events und aktualisiert cur_x, cur_y und Finger-Zustand.
    Gibt eine Liste von "touch_up" Events zurück, jede mit (press_dauer_sek).
    """
    global cur_x, cur_y, norm_x, norm_y, finger_down, down_time
    ups = []

    if touch_fd is None:
        return ups

    # Linux input event struct = timeval(sec,usec), type, code, value
    # 16 bytes time + 2 + 2 + 4 = 24 bytes
    EVENT_SIZE = 24
    while True:
        r,_,_ = select.select([touch_fd],[],[],0)
        if not r:
            break
        data = os.read(touch_fd, EVENT_SIZE)
        if len(data) < EVENT_SIZE:
            break
        sec, usec, etype, code, value = st.unpack("llHHI", data)

        if etype == 0x03:  # EV_ABS
            if code == ABS_X:
                cur_x = value
            elif code == ABS_Y:
                cur_y = value
                
            # Touch-Kalibrierung basierend auf gemessenen Daten
            # Achsen tauschen: raw_y->display_x, raw_x->display_y
            # Y-Achse: raw_x=2251→y=194, raw_x=3385→y=306
            # X-Achse: komprimiert 52-271 → gestreckt 40-440
            temp_x = int(cur_y * 479 / 4095)
            temp_x_flipped = 479 - temp_x
            # X-Offset: 15px nach links (Tastatur war zu weit rechts)
            norm_x = int(1.826 * temp_x_flipped - 55) 
            # Y-Offset: 50px nach oben (Buttons waren zu tief)
            norm_y = int((cur_x - 286) * 194.0 / 1965.0) + 50

        elif etype == 0x01 and code == BTN_TOUCH:
            # value 1 = down, 0 = up
            if value == 1 and not finger_down:
                finger_down = True
                down_time = time.time()
            elif value == 0 and finger_down:
                press_len = time.time() - down_time
                finger_down = False
                ups.append(press_len)

    return ups

def handle_gestures():
    """
    Nutzt die "ups" Events (Finger losgelassen),
    plus timing-Logik für short/long/double/superlong.
    Prüft auch Terminal-Button Touch und Terminal-Tastatur.
    """
    global state, click_pending, last_tap_time, usb_manager_active, _stopping_video

    ups = read_touch_events()
    now = time.time()
    
    # Wenn Video gerade gestoppt wird, ignoriere alle Touches
    if _stopping_video:
        return

    # USB-Manager-Modus: Alle Touches an Manager weiterleiten
    if usb_manager_active and usb_manager and ups:
        action, msg = usb_manager.handle_touch(norm_x, norm_y)
        if action == "close":
            print("[USB] Manager geschlossen")
            usb_manager_active = False
        elif action == "unmount":
            print(f"[USB] {msg}")
            # Flag setzen: Auto-Mount deaktivieren bis USB physisch entfernt
            global _manual_unmount
            _manual_unmount = True
            # Nach Unmount noch kurz anzeigen, dann schließen
            time.sleep(1.5)
            usb_manager_active = False
        return
    
    # Terminal-Modus: Alle Touches an Tastatur weiterleiten
    if TERMINAL_AVAILABLE and terminal_launcher and terminal_launcher.is_active():
        if ups:
            # Nur bei Touch-Up (Finger losgelassen)
            exit_requested = terminal_launcher.handle_touch(norm_x, norm_y)
            if exit_requested:
                print("[TERMINAL] EXIT-Taste gedrückt")
                terminal_launcher.toggle_terminal()
        return

    # Terminal/USB-Buttons prüfen (nur bei kurzen Taps)
    if TERMINAL_AVAILABLE and ups:
        for press_len in ups:
            if press_len < SHORT_LONG:
                # Terminal-Button (links oben)
                if terminal_button and terminal_button.is_touched(norm_x, norm_y):
                    print("[TOUCH] Terminal-Button aktiviert")
                    if terminal_launcher:
                        terminal_launcher.toggle_terminal()
                    return
                # USB-Button (rechts neben Terminal-Button)
                term_btn_x = 10
                term_btn_y = fb_h - 40  # 280
                term_btn_w = 70
                term_btn_h = 30
                usb_btn_x = term_btn_x + term_btn_w + 10  # 90
                usb_btn_y = term_btn_y  # 280
                usb_btn_w = 70
                usb_btn_h = 30
                if (usb_btn_x <= norm_x <= usb_btn_x + usb_btn_w and
                    usb_btn_y <= norm_y <= usb_btn_y + usb_btn_h):
                    print("[TOUCH] USB-Manager aktiviert")
                    usb_manager_active = True
                    return

    # Long-hold auswerten (wenn Finger weiterhin down ist)
    # Für super-long-shutdown brauchen wir nicht loslassen, aber in idle nur.
    if finger_down and state == "idle":
        held = now - down_time
        if held >= IDLE_SHUT:
            print("[TOUCH] superlong idle -> shutdown")
            safe_shutdown()
            return

    for press_len in ups:
        # press_len = wie lange Finger unten war
        # Verhalte dich wie beim Button:

        if press_len >= IDLE_SHUT and state == "idle":
            print("[TOUCH] superlong idle -> shutdown")
            safe_shutdown()
            continue

        elif press_len >= SHORT_LONG:
            # langer Tap
            if state == "live":
                print("[TOUCH] long live -> start video")
                start_video()
            # in recording ignorieren
            # in idle ignorieren (außer superlong)
            click_pending = False

        else:
            # kurzer Tap -> Kandidat für single/double
            if click_pending and ((now - last_tap_time) < DBL_GAP):
                # double tap
                click_pending = False
                if state == "idle":
                    print("[TOUCH] double -> LIVE")
                    state = "live"
                else:
                    print("[TOUCH] double ignored (not idle)")
            else:
                click_pending = True
                last_tap_time = now

    # single tap finalisieren falls Zeit vorbei und noch pending
    if click_pending and ((now - last_tap_time) >= DBL_GAP):
        if state == "live":
            print("[TOUCH] single live -> photo")
            take_photo()
        elif state == "recording":
            print("[TOUCH] single rec -> stop video")
            stop_video()
        else:
            print("[TOUCH] single idle (noop)")
        click_pending = False

############################
# MAIN LOOP
############################

def main():
    global state, terminal_launcher, terminal_button

    print("NightCam Touch start")
    picam.start()
    open_touch()

    global fb_w, fb_h
    fbfd, fbmem, W, H, BPP = open_fb(FB_PATH)
    fb_w, fb_h = W, H
    
    if TERMINAL_AVAILABLE:
        terminal_launcher = TerminalLauncher(FB_PATH, TOUCH_DEV)
        terminal_button = TerminalButton(x=10, y=H-40, width=70, height=30)
        global usb_manager
        usb_manager = USBManager(fb_width=W, fb_height=H)
        print("[TERMINAL] Terminal Access & USB Manager aktiviert")

    try:
        while True:
            # Touch-Logik (z.B. Start/Stop Video, Foto, Shutdown)
            handle_gestures()

            # USB-Manager-Modus: USB-Interface rendern
            if usb_manager_active and usb_manager:
                disp = np.zeros((H, W, 3), dtype=np.uint8)
                usb_manager.draw_interface(disp)
                fb_draw(disp, fbmem, W, H)
                time.sleep(0.05)
                continue
            
            # Terminal-Modus: Terminal und Tastatur rendern
            if TERMINAL_AVAILABLE and terminal_launcher and terminal_launcher.is_active():
                # Terminal-Update (liest Shell-Output)
                terminal_launcher.update()
                
                # Schwarzer Hintergrund für Terminal
                disp = np.zeros((H, W, 3), dtype=np.uint8)
                
                # Terminal und Tastatur rendern
                terminal_launcher.render(disp)
                
                # zum Display pushen
                fb_draw(disp, fbmem, W, H)
                time.sleep(0.01)
                continue

            # Kameraframe holen
            frame = picam.capture_array()

            # Nacht-Boost
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            enh  = cv2.equalizeHist(gray)
            disp = cv2.cvtColor(enh, cv2.COLOR_GRAY2BGR)

            # HUD
            photos_left, minutes_left = estimate_capacity()
            usb_txt = "USB" if usb_mountpoint() else "INT"
            hud = f"{state.upper()} {usb_txt} F:{photos_left} V~{minutes_left}min"
            cv2.putText(
                disp, hud, (10,20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2, cv2.LINE_AA
            )

            # Aufnahme-Anzeige
            if state == "recording":
                cv2.circle(disp, (W-40,30), 12, (0,0,255), -1)
                cv2.putText(
                    disp, "REC", (W-90,35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2, cv2.LINE_AA
                )
            
            # Terminal-Button zeichnen (nur wenn Terminal nicht aktiv)
            if TERMINAL_AVAILABLE and terminal_button:
                terminal_button.draw(disp)
            
            # USB-Button zeichnen (rechts neben Terminal-Button)
            if TERMINAL_AVAILABLE:
                usb_color = (100, 255, 100) if usb_mountpoint() else (150, 150, 150)
                cv2.rectangle(disp, (90, H-40), (160, H-10), usb_color, 2)
                cv2.putText(disp, "USB", (100, H-20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, usb_color, 2, cv2.LINE_AA)

            # zum Display pushen
            fb_draw(disp, fbmem, W, H)

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n[EXIT] KeyboardInterrupt")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        if state == "recording":
            stop_video()
        if terminal_launcher:
            terminal_launcher.cleanup()
        picam.stop()
        fbmem.close()
        os.close(fbfd)
        if touch_fd is not None:
            os.close(touch_fd)
        print("NightCam Touch exit")

if __name__ == "__main__":
    main()
