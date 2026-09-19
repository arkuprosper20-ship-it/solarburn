#!/usr/bin/env python3
"""
tools/gen_favicon.py
====================
Rasterises the SuryaDrishti favicon mark into PNG + ICO assets with no
third-party dependencies (pure stdlib: zlib + struct).

The mark is redrawn procedurally at 64x64 design units and scaled, so every
exported size stays crisp instead of being a blurry upscale.

Outputs (into frontend/dashboard/):
  favicon.ico              16 + 32 + 48 (PNG payloads, Vista+)
  favicon-16x16.png
  favicon-32x32.png
  apple-touch-icon.png     180x180
  icon-192.png
  icon-512.png

Usage:
  py tools/gen_favicon.py
"""

import math
import os
import struct
import zlib

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                       "frontend", "dashboard")

# ---------------------------------------------------------------------------
# Colour helpers (all colours carry straight alpha in 0..1)
# ---------------------------------------------------------------------------
def hx(s, a=1.0):
    s = s.lstrip("#")
    return (int(s[0:2], 16) / 255.0, int(s[2:4], 16) / 255.0,
            int(s[4:6], 16) / 255.0, a)


BG        = hx("05060f")
EDGE      = hx("00d4ff", 0.28)
STAR      = hx("ffffff", 0.65)
CORONA1   = hx("ff8c00", 0.13)
CORONA2   = hx("ffb300", 0.16)
SPIKE_A   = hx("ffb703", 0.95)
SPIKE_B   = hx("ffd54a", 0.80)
DISK_EDGE = hx("fff3c4", 0.55)
AR_DARK   = hx("7c2d12", 0.50)
AR_DARK2  = hx("7c2d12", 0.42)
RING_A    = hx("00d4ff", 0.95)
RING_B    = hx("0084ff", 0.95)
RING_FAINT= hx("00d4ff", 0.35)
SAT       = hx("00d4ff")
SAT_HALO  = hx("00d4ff", 0.50)

DISK_STOPS = [
    (0.00, hx("fffbe8")),
    (0.30, hx("ffd54a")),
    (0.62, hx("ff9e00")),
    (1.00, hx("c2410c")),
]


def clampi(v):
    if v <= 0.0:
        return 0
    if v >= 255.0:
        return 255
    return int(v + 0.5)


class Canvas:
    """Tiny RGBA canvas with source-over compositing and box downsampling."""

    def __init__(self, size):
        self.size = size
        self.px = [0.0] * (size * size * 4)

    # -- compositing ------------------------------------------------------
    def blend(self, x, y, col):
        if x < 0 or y < 0 or x >= self.size or y >= self.size:
            return
        sa = col[3]
        if sa <= 0.0:
            return
        if sa > 1.0:
            sa = 1.0
        i = (y * self.size + x) * 4
        px = self.px
        da = px[i + 3]
        oa = sa + da * (1.0 - sa)
        if oa <= 0.0:
            return
        inv = da * (1.0 - sa)
        px[i]     = (col[0] * sa + px[i]     * inv) / oa
        px[i + 1] = (col[1] * sa + px[i + 1] * inv) / oa
        px[i + 2] = (col[2] * sa + px[i + 2] * inv) / oa
        px[i + 3] = oa

    # -- primitives -------------------------------------------------------
    def disc(self, cx, cy, r, col, soft=1.0):
        """Filled circle with a soft 1px-ish edge for antialiasing."""
        if r <= 0:
            return
        x0, x1 = int(math.floor(cx - r - 1)), int(math.ceil(cx + r + 1))
        y0, y1 = int(math.floor(cy - r - 1)), int(math.ceil(cy + r + 1))
        for y in range(y0, y1 + 1):
            dy = y + 0.5 - cy
            for x in range(x0, x1 + 1):
                dx = x + 0.5 - cx
                d = math.hypot(dx, dy)
                if d <= r - soft:
                    a = col[3]
                elif d >= r + soft:
                    continue
                else:
                    a = col[3] * (1.0 - (d - (r - soft)) / (2.0 * soft))
                if a > 0:
                    self.blend(x, y, (col[0], col[1], col[2], a))
    def round_rect(self, x0, y0, x1, y1, r, col):
        for y in range(int(math.floor(y0)), int(math.ceil(y1))):
            for x in range(int(math.floor(x0)), int(math.ceil(x1))):
                cx, cy = x + 0.5, y + 0.5
                if cx < x0 or cx > x1 or cy < y0 or cy > y1:
                    continue
                dx = max(x0 + r - cx, 0.0, cx - (x1 - r))
                dy = max(y0 + r - cy, 0.0, cy - (y1 - r))
                if math.hypot(dx, dy) <= r + 0.5:
                    self.blend(x, y, col)

    def rect_outline(self, x0, y0, x1, y1, r, w, col):
        for y in range(int(math.floor(y0 - w)), int(math.ceil(y1 + w))):
            for x in range(int(math.floor(x0 - w)), int(math.ceil(x1 + w))):
                cx, cy = x + 0.5, y + 0.5
                dx = max(x0 + r - cx, 0.0, cx - (x1 - r))
                dy = max(y0 + r - cy, 0.0, cy - (y1 - r))
                if abs(math.hypot(dx, dy) - r) <= w * 0.5:
                    self.blend(x, y, col)

    def line(self, x0, y0, x1, y1, w, col):
        """Round-capped line: walk the segment stamping discs."""
        length = math.hypot(x1 - x0, y1 - y0)
        steps = max(2, int(length * 2.5))
        r = w * 0.5
        for i in range(steps + 1):
            t = i / float(steps)
            self.disc(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, r, col, soft=0.5)

    def ellipse_outline(self, cx, cy, rx, ry, rot, w, col):
        """Rotated ellipse outline, stamped parametrically."""
        steps = max(90, int((rx + ry) * 6))
        r = w * 0.5
        cr, sr = math.cos(rot), math.sin(rot)
        for i in range(steps + 1):
            t = 2.0 * math.pi * i / steps
            ex, ey = rx * math.cos(t), ry * math.sin(t)
            self.disc(cx + ex * cr - ey * sr, cy + ex * sr + ey * cr, r, col,
                      soft=0.45)

    def gradient_disc(self, cx, cy, r, stops):
        """Radial gradient disc (stop offset 0 = centre)."""
        x0, x1 = int(math.floor(cx - r - 1)), int(math.ceil(cx + r + 1))
        y0, y1 = int(math.floor(cy - r - 1)), int(math.ceil(cy + r + 1))
        for y in range(y0, y1 + 1):
            dy = y + 0.5 - cy
            for x in range(x0, x1 + 1):
                dx = x + 0.5 - cx
                d = math.hypot(dx, dy) / r
                if d > 1.0:
                    continue
                col = sample_stops(stops, d)
                edge = 1.0 if d < 0.985 else (1.0 - (d - 0.985) / 0.015)
                if edge > 0:
                    self.blend(x, y, (col[0], col[1], col[2], col[3] * edge))

    def downsample(self, factor):
        n = self.size // factor
        out = Canvas(n)
        area = float(factor * factor)
        for y in range(n):
            for x in range(n):
                r = g = b = a = 0.0
                for sy in range(factor):
                    base = ((y * factor + sy) * self.size + x * factor) * 4
                    for sx in range(factor):
                        i = base + sx * 4
                        r += self.px[i]; g += self.px[i + 1]
                        b += self.px[i + 2]; a += self.px[i + 3]
                o = (y * n + x) * 4
                out.px[o]     = r / area
                out.px[o + 1] = g / area
                out.px[o + 2] = b / area
                out.px[o + 3] = a / area
        return out

    def to_rgba_bytes(self):
        buf = bytearray(self.size * self.size * 4)
        for i in range(0, len(self.px), 4):
            buf[i]     = clampi(self.px[i] * 255.0)
            buf[i + 1] = clampi(self.px[i + 1] * 255.0)
            buf[i + 2] = clampi(self.px[i + 2] * 255.0)
            buf[i + 3] = clampi(self.px[i + 3] * 255.0)
        return bytes(buf)


# ---------------------------------------------------------------------------
# The mark, drawn in 64x64 design units
# ---------------------------------------------------------------------------
def draw_mark(S):
    """Render the mark into an S x S canvas (64 design units scaled to S)."""
    c = Canvas(S)
    u = S / 64.0                       # one design unit in pixels

    def P(v):
        return v * u

    pad = P(0.6)
    c.round_rect(pad, pad, S - pad, S - pad, P(14), BG)
    c.rect_outline(pad, pad, S - pad, S - pad, P(14), P(1.2), EDGE)

    for (sx, sy, sr, sa) in ((14, 13, 0.9, 0.75), (50, 17, 0.7, 0.55),
                             (47, 50, 0.8, 0.60), (13, 47, 0.6, 0.50)):
        col = (STAR[0], STAR[1], STAR[2], sa)
        c.disc(P(sx), P(sy), P(sr), col, soft=P(0.55))

    c.disc(P(32), P(32), P(21), CORONA1, soft=P(1.6))
    c.disc(P(32), P(32), P(17), CORONA2, soft=P(1.6))

    # eight flare spikes: primary (axis-aligned) then secondary (diagonal)
    for (x0, y0, x1, y1) in ((32, 3.5, 32, 10.5), (32, 53.5, 32, 60.5),
                             (3.5, 32, 10.5, 32), (53.5, 32, 60.5, 32)):
        c.line(P(x0), P(y0), P(x1), P(y1), P(2.4), SPIKE_A)
    for (x0, y0, x1, y1) in ((11.8, 11.8, 16.7, 16.7), (52.2, 11.8, 47.3, 16.7),
                             (11.8, 52.2, 16.7, 47.3), (52.2, 52.2, 47.3, 47.3)):
        c.line(P(x0), P(y0), P(x1), P(y1), P(1.9), SPIKE_B)

    # solar disk with radial gradient (offsets shifted toward upper-left light)
    dx, dy = P(-0.20), P(-0.20)
    c.gradient_disc(P(32) + dx * 0.0, P(32) + dy * 0.0, P(13), DISK_STOPS)
    c.disc(P(27.5), P(28), P(3.1), AR_DARK, soft=P(0.7))
    c.disc(P(36.5), P(35.5), P(2.2), AR_DARK2, soft=P(0.6))
    c.ellipse_outline(P(32), P(32), P(13), P(13), 0.0, P(0.9), DISK_EDGE)

    # Aditya-L1 halo orbit at L1
    c.ellipse_outline(P(32), P(32), P(25), P(8.6), math.radians(-28), P(1.7), RING_A)
    c.ellipse_outline(P(32), P(32), P(25), P(8.6), math.radians(32), P(0.7), RING_FAINT)
    c.disc(P(52.6), P(20.5), P(4.4), SAT_HALO, soft=P(0.5))
    c.disc(P(52.6), P(20.5), P(2.5), SAT, soft=P(0.45))

    return c


def render(size, max_scale=6):
    """Return a Canvas holding the mark at exactly `size` x `size`.

    Small sizes are drawn at a multiple of the target and box-downsampled,
    which is what keeps 16px/32px tabs legible.
    """
    k = 1
    while size * k < 256 and k < max_scale:
        k += 1
    base = draw_mark(size * k)
    return base if k == 1 else base.downsample(k)


# ---------------------------------------------------------------------------
# Encoders
# ---------------------------------------------------------------------------
def png_bytes(canvas):
    rgba = canvas.to_rgba_bytes()
    n = canvas.size
    raw = bytearray()
    stride = n * 4
    for y in range(n):
        raw.append(0)                                  # filter type 0
        raw += rgba[y * stride:(y + 1) * stride]

    def chunk(tag, data):
        body = tag + data
        return (struct.pack(">I", len(data)) + body +
                struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", n, n, 8, 6, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
            chunk(b"IEND", b""))


def ico_bytes(entries):
    """entries: list of (size, png_payload) — PNG-compressed ICO (Vista+)."""
    count = len(entries)
    header = struct.pack("<HHH", 0, 1, count)
    offset = 6 + 16 * count
    directory, blobs = bytearray(), bytearray()
    for size, payload in entries:
        dim = 0 if size >= 256 else size
        directory += struct.pack("<BBBBHHII", dim, dim, 0, 0, 1, 32,
                                 len(payload), offset)
        blobs += payload
        offset += len(payload)
    return bytes(header + directory + blobs)
    if v <= 0.0:
        return 0
    if v >= 255.0:
        return 255
    return int(v + 0.5)


def sample_stops(stops, t):
    if t <= stops[0][0]:
        return stops[0][1]
    for i in range(1, len(stops)):
        t0, c0 = stops[i - 1]
        t1, c1 = stops[i]
        if t <= t1:
            f = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
            return (c0[0] + (c1[0] - c0[0]) * f,
                    c0[1] + (c1[1] - c0[1]) * f,
                    c0[2] + (c1[2] - c0[2]) * f,
                    c0[3] + (c1[3] - c0[3]) * f)
    return stops[-1][1]


def main():
    out = os.path.normpath(OUT_DIR)
    os.makedirs(out, exist_ok=True)

    targets = [
        ("favicon-16x16.png",    16),
        ("favicon-32x32.png",    32),
        ("apple-touch-icon.png", 180),
        ("icon-192.png",         192),
        ("icon-512.png",         512),
    ]

    written = []
    for name, size in targets:
        canvas = render(size)
        data = png_bytes(canvas)
        path = os.path.join(out, name)
        with open(path, "wb") as fh:
            fh.write(data)
        written.append((name, size, len(data)))

    # Multi-resolution .ico for legacy tabs / bookmarks / Windows shortcuts
    ico_entries = []
    for size in (16, 32, 48):
        ico_entries.append((size, png_bytes(render(size))))
    ico_path = os.path.join(out, "favicon.ico")
    with open(ico_path, "wb") as fh:
        fh.write(ico_bytes(ico_entries))
    written.append(("favicon.ico", 48, os.path.getsize(ico_path)))

    print("SuryaDrishti favicon assets written to:", out)
    for name, size, nbytes in written:
        print("  %-22s %3dx%-3d  %7d bytes" % (name, size, size, nbytes))


if __name__ == "__main__":
    main()

