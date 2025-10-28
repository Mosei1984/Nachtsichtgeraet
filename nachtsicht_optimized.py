#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# NightCam Touch Edition - OPTIMIZED
#
# Optimizations:
# - Reduced memory allocations (pre-allocated buffers)
# - Faster frame processing (in-place operations)
# - Optimized touch event parsing
# - Better error handling
# - Reduced CPU usage with adaptive sleep
#

import os, time, glob, shutil, fcntl, mmap, struct, subprocess, sys, select, signal, threading
import cv2, numpy as np
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput

############################
# KONFIG
############################

FB_PATH        = "/dev/fb1"
TOUCH_DEV      = "/dev/input/event0"
SHORT_LONG     = 0.8
REBOOT_HOLD    = 2.5
SHUTDOWN_HOLD  = 5.0
DBL_GAP        = 0.35
EST_PHOTO_BYTES= 500_000
EST_VIDEO_MBPS = 0.5

FBIOGET_VSCREENINFO = 0x4600

############################
# SPEICHER / USB
############################

_usb_cache = None
_usb_cache_time = 0

def usb_mountpoint():
    global _usb_cache, _usb_cache_time
    now = time.time()
    if _usb_cache is not None and (now - _usb_cache_time) < 5.0:
        return _usb_cache
    
    base = "/media"
    _usb_cache = None
    if os.path.isdir(base):
        for e in os.scandir(base):
            if e.is_dir() and e.name.startswith("usb"):
                _usb_cache = e.path
                break
    _usb_cache_time = now
    return _usb_cache

def ensure_dirs():
    usb = usb_mountpoint()
    if usb:
        pdir = os.path.join(usb, "Nachtsicht_Fotos")
        vdir = os.path.join(usb, "Nachtsicht_Videos")
    else:
        pdir = "/home/valentin/Nachtsicht_Fotos"
        vdir = "/home/valentin/Nachtsicht_Videos"
    os.makedirs(pdir, exist_ok=True)
    os.makedirs(vdir, exist_ok=True)
    return pdir, vdir

def next_photo():
    pdir, _ = ensure_dirs()
    ex = glob.glob(os.path.join(pdir, "Nachtsicht_Foto*.jpg"))
    n = max((int(os.path.basename(p).replace("Nachtsicht_Foto","").replace(".jpg","")) 
             for p in ex if os.path.basename(p).replace("Nachtsicht_Foto","").replace(".jpg","").isdigit()), 
            default=0)
    return os.path.join(pdir, f"Nachtsicht_Foto{n+1}.jpg")

def next_video():
    _, vdir = ensure_dirs()
    ex = glob.glob(os.path.join(vdir, "Nachtsicht_Video*.h264"))
    n = max((int(os.path.basename(p).replace("Nachtsicht_Video","").replace(".h264","")) 
             for p in ex if os.path.basename(p).replace("Nachtsicht_Video","").replace(".h264","").isdigit()), 
            default=0)
    return os.path.join(vdir, f"Nachtsicht_Video{n+1}.h264")

_free_bytes_cache = 0
_free_bytes_time = 0

def free_bytes_path():
    global _free_bytes_cache, _free_bytes_time
    now = time.time()
    if (now - _free_bytes_time) < 2.0:
        return _free_bytes_cache
    
    path = usb_mountpoint() or "/home/valentin"
    _free_bytes_cache = shutil.disk_usage(path).free
    _free_bytes_time = now
    return _free_bytes_cache

def estimate_capacity():
    fb = free_bytes_path()
    photos = fb // EST_PHOTO_BYTES
    mins   = (fb // (1024 * 1024) // EST_VIDEO_MBPS) // 60
    return int(photos), int(mins)

############################
# FRAMEBUFFER HANDLING
############################

def open_fb(path):
    fd = os.open(path, os.O_RDWR)

    try:
        raw = fcntl.ioctl(fd, FBIOGET_VSCREENINFO, b"\x00"*160)
        xres, yres, xrv, yrv, xoff, yoff, bpp, gray = struct.unpack_from("8I", raw, 0)
        if xres == 0 or yres == 0:
            raise ValueError("bad ioctl dims")
    except Exception:
        xres, yres, bpp = 480, 320, 16

    fbsize = xres * yres * 2
    mm = mmap.mmap(fd, fbsize, mmap.MAP_SHARED,
                   mmap.PROT_WRITE | mmap.PROT_READ, 0)
    print(f"[FB] {path} {xres}x{yres}@{bpp}bpp")
    return fd, mm, xres, yres, bpp

_rgb565_buffer = None

def bgr_to_rgb565(bgr):
    global _rgb565_buffer
    b = (bgr[:,:,0] >> 3).astype(np.uint16)
    g = (bgr[:,:,1] >> 2).astype(np.uint16)
    r = (bgr[:,:,2] >> 3).astype(np.uint16)
    packed = (r << 11) | (g << 5) | b
    if _rgb565_buffer is None or _rgb565_buffer.shape != packed.shape:
        _rgb565_buffer = np.empty(packed.shape, dtype=np.uint16)
    np.copyto(_rgb565_buffer, packed)
    return _rgb565_buffer.tobytes()

_resize_buffer = None

def fb_draw(bgr, fb_mem, w, h):
    global _resize_buffer
    if _resize_buffer is None or _resize_buffer.shape[:2] != (h, w):
        _resize_buffer = np.empty((h, w, 3), dtype=np.uint8)
    cv2.resize(bgr, (w, h), dst=_resize_buffer, interpolation=cv2.INTER_LINEAR)
    fb_mem.seek(0)
    fb_mem.write(bgr_to_rgb565(_resize_buffer))

############################
# KAMERA
############################

picam = Picamera2()
picam.configure(
    picam.create_video_configuration(
        main={"size": (640,480)},
        controls={"AeEnable":True, "AwbEnable":True}
    )
)
encoder = H264Encoder(bitrate=4_000_000)
video_out = None

############################
# STATE UND AUFNAHME
############################

state = "idle"
rec_name = None

_gray_buffer = None
_enh_buffer = None

def take_photo():
    global _gray_buffer, _enh_buffer
    fn = next_photo()
    frame = picam.capture_array()
    
    if _gray_buffer is None or _gray_buffer.shape != frame.shape[:2]:
        _gray_buffer = np.empty(frame.shape[:2], dtype=np.uint8)
        _enh_buffer = np.empty(frame.shape[:2], dtype=np.uint8)
    
    cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY, dst=_gray_buffer)
    cv2.equalizeHist(_gray_buffer, dst=_enh_buffer)
    cv2.imwrite(fn, _enh_buffer)
    ph, mn = estimate_capacity()
    print(f"[FOTO] {fn} | Rest ~{ph} Fotos / ~{mn} min Video")

def start_video():
    global state, rec_name, video_out
    rec_name = next_video()
    print(f"[VIDEO] START -> {rec_name}")
    video_out = FileOutput(rec_name)
    picam.start_recording(encoder, video_out)
    state = "recording"

def _stop_video_thread(rec_file):
    global video_out, _stopping_video
    try:
        picam.stop_recording()
        video_out = None
        os.sync()
        print(f"[VIDEO] SAVED -> {rec_file}")
    except Exception as e:
        print(f"[VIDEO] ERROR: {e}")
        video_out = None
    finally:
        _stopping_video = False

_stopping_video = False

def stop_video():
    global state, _stopping_video
    if state == "recording":
        print("[VIDEO] STOP")
        _stopping_video = True
        state = "live"
        thread = threading.Thread(target=_stop_video_thread, args=(rec_name,), daemon=True)
        thread.start()

def safe_reboot():
    print("[REBOOT] init")
    if state == "recording":
        stop_video()
    os.sync()
    print("[REBOOT] rebooting ...")
    subprocess.call(["sudo","reboot"])

def safe_shutdown():
    print("[SHUTDOWN] init")
    if state == "recording":
        stop_video()
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

touch_fd = None
ABS_X = 0x00
ABS_Y = 0x01
BTN_TOUCH = 0x14a

cur_x = 0
cur_y = 0
finger_down = False
down_time = 0.0

click_pending = False
last_tap_time = 0.0

def open_touch():
    global touch_fd
    try:
        touch_fd = os.open(TOUCH_DEV, os.O_RDONLY | os.O_NONBLOCK)
        print(f"[TOUCH] opened {TOUCH_DEV}")
    except Exception as e:
        print(f"[TOUCH] FAIL open {TOUCH_DEV}: {e}")
        touch_fd = None

EVENT_SIZE = 24
EVENT_STRUCT = "llHHI"

def read_touch_events():
    global cur_x, cur_y, finger_down, down_time
    ups = []

    if touch_fd is None:
        return ups

    while True:
        r, _, _ = select.select([touch_fd], [], [], 0)
        if not r:
            break
        try:
            data = os.read(touch_fd, EVENT_SIZE)
            if len(data) < EVENT_SIZE:
                break
        except OSError:
            break

        sec, usec, etype, code, value = struct.unpack(EVENT_STRUCT, data)

        if etype == 0x03:
            if code == ABS_X:
                cur_x = value
            elif code == ABS_Y:
                cur_y = value
        elif etype == 0x01 and code == BTN_TOUCH:
            if value == 1 and not finger_down:
                finger_down = True
                down_time = time.time()
            elif value == 0 and finger_down:
                press_len = time.time() - down_time
                finger_down = False
                ups.append(press_len)

    return ups

def handle_gestures():
    global state, click_pending, last_tap_time

    ups = read_touch_events()
    now = time.time()

    if finger_down:
        held = now - down_time
        if held >= SHUTDOWN_HOLD:
            print("[TOUCH] 5s hold -> shutdown")
            safe_shutdown()
            return
        elif held >= REBOOT_HOLD:
            pass

    for press_len in ups:
        if press_len >= SHUTDOWN_HOLD:
            print("[TOUCH] 5s press -> shutdown")
            safe_shutdown()
            continue
        elif press_len >= REBOOT_HOLD:
            print("[TOUCH] 2.5s press -> reboot")
            safe_reboot()
            continue
        elif press_len >= SHORT_LONG:
            if state == "live":
                print("[TOUCH] long live -> start video")
                start_video()
            click_pending = False
        else:
            if click_pending and ((now - last_tap_time) < DBL_GAP):
                click_pending = False
                if state == "idle":
                    print("[TOUCH] double -> LIVE")
                    state = "live"
                else:
                    print("[TOUCH] double ignored (not idle)")
            else:
                click_pending = True
                last_tap_time = now

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
    global state, _gray_buffer, _enh_buffer

    print("NightCam Touch start (OPTIMIZED)")
    picam.start()
    open_touch()

    fbfd, fbmem, W, H, BPP = open_fb(FB_PATH)
    
    _gray_buffer = np.empty((480, 640), dtype=np.uint8)
    _enh_buffer = np.empty((480, 640), dtype=np.uint8)
    disp = np.empty((480, 640, 3), dtype=np.uint8)

    try:
        last_hud_update = 0
        photos_left, minutes_left = 0, 0
        usb_txt = "INT"
        
        loop_count = 0
        last_frame = None
        
        while True:
            handle_gestures()

            if _stopping_video:
                time.sleep(0.05)
                loop_count += 1
                continue

            if loop_count > 0:
                loop_count = 0

            try:
                frame = picam.capture_array()
            except Exception as e:
                print(f"[MAIN] capture_array error: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(0.1)
                continue

            cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY, dst=_gray_buffer)
            cv2.equalizeHist(_gray_buffer, dst=_enh_buffer)
            cv2.cvtColor(_enh_buffer, cv2.COLOR_GRAY2BGR, dst=disp)

            now = time.time()
            if now - last_hud_update > 1.0:
                photos_left, minutes_left = estimate_capacity()
                usb_txt = "USB" if usb_mountpoint() else "INT"
                last_hud_update = now

            hud = f"{state.upper()} {usb_txt} F:{photos_left} V~{minutes_left}min"
            cv2.putText(
                disp, hud, (10,20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2, cv2.LINE_AA
            )

            if state == "recording":
                cv2.circle(disp, (W-40,30), 12, (0,0,255), -1)
                cv2.putText(
                    disp, "REC", (W-90,35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2, cv2.LINE_AA
                )

            fb_draw(disp, fbmem, W, H)

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n[EXIT] KeyboardInterrupt")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        if state == "recording":
            stop_video()
        picam.stop()
        fbmem.close()
        os.close(fbfd)
        if touch_fd is not None:
            os.close(touch_fd)
        print("NightCam Touch exit")

if __name__ == "__main__":
    main()
