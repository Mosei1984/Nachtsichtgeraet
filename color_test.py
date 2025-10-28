#!/usr/bin/env python3
# Farb-Test für Display

import os, fcntl, mmap, struct
import numpy as np

FB_PATH = "/dev/fb1"
FBIOGET_VSCREENINFO = 0x4600

# Framebuffer öffnen
fd = os.open(FB_PATH, os.O_RDWR)
raw = fcntl.ioctl(fd, FBIOGET_VSCREENINFO, b"\x00"*160)
xres, yres = struct.unpack_from("2I", raw, 0)
fbsize = xres * yres * 2
mm = mmap.mmap(fd, fbsize, mmap.MAP_SHARED, mmap.PROT_WRITE | mmap.PROT_READ, 0)

print(f"Display: {xres}x{yres}")

# Test-Farben (RGB565 format)
# Format: RRRRR GGGGGG BBBBB
colors = {
    'ROT':   0b1111100000000000,  # R=31, G=0, B=0
    'GRÜN':  0b0000011111100000,  # R=0, G=63, B=0
    'BLAU':  0b0000000000011111,  # R=0, G=0, B=31
    'WEISS': 0b1111111111111111,  # R=31, G=63, B=31
    'SCHWARZ': 0b0000000000000000
}

# Display in 5 vertikale Streifen teilen
stripe_width = xres // 5
color_names = list(colors.keys())

buffer = np.zeros((yres, xres), dtype=np.uint16)

for i, name in enumerate(color_names):
    x_start = i * stripe_width
    x_end = (i + 1) * stripe_width if i < 4 else xres
    buffer[:, x_start:x_end] = colors[name]

mm.seek(0)
mm.write(buffer.tobytes())

print(f"\nFarb-Streifen angezeigt (von links nach rechts):")
for name in color_names:
    print(f"  {name}")
print("\nWelche Farben sehen Sie tatsächlich?")

input("Drücken Sie Enter zum Beenden...")

mm.close()
os.close(fd)
