#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Draws the port's icon, tools/release/avsp.png (256x256): a hunter's targeting triangle over a
dark jungle, with a claw slash — arithmetic only, so the releases ship no artwork from the game.
Rebuild it with:

    python3 tools/release/make-icon.py

Each shape is rasterised with one bit per pixel at SS-times the final size, then averaged down, which
is what gives the edges their smoothness.
"""

import math
import os
import struct
import zlib

W = H = 256
SS = 3
SW = W * SS

JUNGLE_TOP = (3, 9, 7)         # night jungle, above
JUNGLE_BOTTOM = (14, 32, 18)   # and below
GLOW = (26, 74, 34)            # a warm green light behind the centre
LASER = (168, 255, 132)        # the targeting triangle's bright lines and dots
LASER_DIM = (46, 120, 62)      # their glow
RING = (96, 205, 96)           # the targeting ring
CLAW = (156, 44, 32)           # the claw slash
INK = (2, 6, 4)                # the outline

CX, CY = 128, 132


def mask_from_spans(rows):
    m = [0] * SW
    for y, spans in rows.items():
        ys = range(max(0, y * SS), min(SW, (y + 1) * SS))
        bits = 0
        for x0, x1 in spans:
            xa, xb = max(0, int(x0 * SS)), min(SW, int(x1 * SS))
            if xb > xa:
                bits |= ((1 << (xb - xa)) - 1) << xa
        for yy in ys:
            m[yy] |= bits
    return m


def polygon(points):
    spans = {}
    ys = [p[1] for p in points]
    for y in range(int(min(ys)), int(max(ys)) + 1):
        yc = y + 0.5
        xs = []
        for i in range(len(points)):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % len(points)]
            if (y0 <= yc < y1) or (y1 <= yc < y0):
                xs.append(x0 + (yc - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        spans[y] = [(xs[i], xs[i + 1]) for i in range(0, len(xs) - 1, 2)]
    return mask_from_spans(spans)


def ellipse(cx, cy, rx, ry):
    spans = {}
    for y in range(int(cy - ry), int(cy + ry) + 1):
        dy = (y + 0.5 - cy) / ry
        if abs(dy) >= 1:
            continue
        dx = rx * (1 - dy * dy) ** 0.5
        spans[y] = [(cx - dx, cx + dx)]
    return mask_from_spans(spans)


def bar(p0, p1, w):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    length = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / length * w / 2.0, dx / length * w / 2.0
    return polygon([(p0[0] + nx, p0[1] + ny), (p1[0] + nx, p1[1] + ny),
                    (p1[0] - nx, p1[1] - ny), (p0[0] - nx, p0[1] - ny)])


def union(*masks):
    out = [0] * SW
    for m in masks:
        for y in range(SW):
            out[y] |= m[y]
    return out


def intersect(a, b):
    return [a[y] & b[y] for y in range(SW)]


def spread(mask, r):
    out = mask[:]
    for dy in range(-r, r + 1):
        for y in range(SW):
            sy = y + dy
            if 0 <= sy < SW:
                out[y] |= mask[sy]
    for y in range(SW):
        row = out[y]
        acc = 0
        for dx in range(-r, r + 1):
            acc |= row << dx if dx > 0 else row >> -dx
        out[y] = acc & ((1 << SW) - 1)
    return out


def minus(a, b):
    return [a[y] & ~b[y] for y in range(SW)]


def coverage(mask):
    cov = [[0.0] * W for _ in range(H)]
    group = (1 << SS) - 1
    for y in range(H):
        rows = mask[y * SS:(y + 1) * SS]
        for x in range(W):
            sh = x * SS
            n = 0
            for row in rows:
                n += bin((row >> sh) & group).count("1")
            cov[y][x] = n / float(SS * SS)
    return cov


# --- the shapes -----------------------------------------------------------------------------------

def triangle_vertices(radius):
    """The three aiming points, an equilateral triangle pointing down."""
    out = []
    for i in range(3):
        a = math.radians(-90 + 120 * i)
        out.append((CX + radius * math.cos(a), CY + radius * math.sin(a)))
    return out


def reticle(radius, line_w, dot_r):
    a, b, c = triangle_vertices(radius)
    lines = union(bar(a, b, line_w), bar(b, c, line_w), bar(c, a, line_w))
    dots = union(ellipse(a[0], a[1], dot_r, dot_r),
                 ellipse(b[0], b[1], dot_r, dot_r),
                 ellipse(c[0], c[1], dot_r, dot_r))
    return union(lines, dots)


def ring(cx, cy, outer, inner):
    return minus(ellipse(cx, cy, outer, outer), ellipse(cx, cy, inner, inner))


def background():
    img = [[[0.0] * 3 for _ in range(W)] for _ in range(H)]
    for y in range(H):
        t = y / float(H - 1)
        base = [JUNGLE_TOP[i] + (JUNGLE_BOTTOM[i] - JUNGLE_TOP[i]) * t for i in range(3)]
        for x in range(W):
            d = (((x - CX) ** 2 + (y - CY) ** 2) ** 0.5) / 175.0
            glow = max(0.0, 1.0 - d) ** 2
            img[y][x] = [base[i] + (GLOW[i] - base[i]) * glow * 0.6 for i in range(3)]
    return img


def over(img, cov, colour):
    for y in range(H):
        for x in range(W):
            a = cov[y][x]
            if a:
                px = img[y][x]
                img[y][x] = [px[i] + (colour[i] - px[i]) * a for i in range(3)]


def main():
    aim = reticle(84, 5, 13)
    target_ring = ring(CX, CY, 101, 97)
    slash = union(bar((6, 206), (54, 146), 9), bar((26, 222), (74, 162), 9))
    slash = intersect(slash, ellipse(CX, CY, 126, 126))
    outline = minus(spread(union(aim, target_ring), 7), spread(union(aim, target_ring), 3))
    glow = minus(spread(aim, 12), spread(aim, 4))

    img = background()
    over(img, coverage(slash), CLAW)
    over(img, coverage(glow), LASER_DIM)
    over(img, coverage(outline), INK)
    over(img, coverage(target_ring), RING)
    over(img, coverage(aim), LASER)

    rows = []
    for y in range(H):
        row = bytearray()
        for x in range(W):
            for i in range(3):
                row.append(max(0, min(255, int(img[y][x][i] + 0.5))))
        rows.append(row)

    raw = b"".join(b"\x00" + bytes(r) for r in rows)

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "avsp.png")
    with open(out, "wb") as f:
        f.write(png)
    print("wrote %s (%d bytes)" % (out, len(png)))


if __name__ == "__main__":
    main()
