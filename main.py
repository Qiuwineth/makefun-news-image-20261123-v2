#!/usr/bin/env python3
"""THE WORLD ON MONDAY - one-image summary of Monday 23 November 2026.

Pure standard-library procedural newspaper front page. Draws a dense,
fully illustrated front page (lead COP31 collapse, Hormuz, Dymer,
Cikande, EU-Indonesia pact, Nvidia chips, Nepal, cricket, markets)
into a 1024x1024 RGB buffer and writes it as entry.png.
"""
import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
PAPER = (246, 240, 221)
PAPER2 = (251, 247, 234)
INK = (24, 20, 14)
RED = (178, 44, 34)
DARKRED = (122, 26, 20)
BLUE = (30, 74, 120)
SKY = (126, 178, 222)
SEA = (38, 96, 148)
GREEN = (44, 122, 62)
LAND = (86, 148, 74)
ORANGE = (224, 116, 32)
FLAME = (244, 164, 40)
GOLD = (198, 156, 34)
GREY = (110, 104, 92)
LGREY = (206, 198, 178)
WHITE = (255, 255, 255)
BLACK = (10, 10, 10)
BROWN = (120, 78, 44)
SAND = (232, 214, 168)

BUF = bytearray(W * H * 3)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        BUF[i] = c[0]
        BUF[i + 1] = c[1]
        BUF[i + 2] = c[2]


def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            px(xx, yy, c)


def frame(x, y, w, h, c, t=2):
    rect(x, y, w, t, c)
    rect(x, y + h - t, w, t, c)
    rect(x, y, t, h, c)
    rect(x + w - t, y, t, h, c)


def line(x0, y0, x1, y1, c, t=1):
    dx = x1 - x0
    dy = y1 - y0
    steps = max(abs(dx), abs(dy), 1)
    r = t // 2
    for i in range(steps + 1):
        x = x0 + dx * i // steps
        y = y0 + dy * i // steps
        rect(x - r, y - r, t, t, c)


def circle(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        dy = yy - cy
        rem = r * r - dy * dy
        if rem < 0:
            continue
        half = int(rem ** 0.5)
        for xx in range(cx - half, cx + half + 1):
            px(xx, yy, c)


def ring(cx, cy, r, c, t=2):
    for yy in range(cy - r - t, cy + r + t + 1):
        for xx in range(cx - r - t, cx + r + t + 1):
            d2 = (xx - cx) ** 2 + (yy - cy) ** 2
            if (r - t) ** 2 <= d2 <= (r + t) ** 2:
                px(xx, yy, c)


def poly(points, c):
    ys = [p[1] for p in points]
    for yy in range(min(ys), max(ys) + 1):
        xs = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= yy < y1) or (y1 <= yy < y0):
                xs.append(x0 + (yy - y0) * (x1 - x0) // (y1 - y0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            for xx in range(xs[i], xs[i + 1] + 1):
                px(xx, yy, c)


def tri(x0, y0, x1, y1, x2, y2, c):
    poly([(x0, y0), (x1, y1), (x2, y2)], c)


# ---------------------------------------------------------------- font 5x7
FONT = {
    "A": (14, 17, 17, 31, 17, 17, 17), "B": (30, 17, 17, 30, 17, 17, 30),
    "C": (14, 17, 16, 16, 16, 17, 14), "D": (28, 18, 17, 17, 17, 18, 28),
    "E": (31, 16, 16, 30, 16, 16, 31), "F": (31, 16, 16, 30, 16, 16, 16),
    "G": (14, 17, 16, 23, 17, 17, 15), "H": (17, 17, 17, 31, 17, 17, 17),
    "I": (14, 4, 4, 4, 4, 4, 14), "J": (15, 2, 2, 2, 2, 18, 12),
    "K": (17, 18, 20, 24, 20, 18, 17), "L": (16, 16, 16, 16, 16, 16, 31),
    "M": (17, 27, 21, 21, 17, 17, 17), "N": (17, 25, 21, 19, 17, 17, 17),
    "O": (14, 17, 17, 17, 17, 17, 14), "P": (30, 17, 17, 30, 16, 16, 16),
    "Q": (14, 17, 17, 17, 21, 18, 13), "R": (30, 17, 17, 30, 20, 18, 17),
    "S": (15, 16, 16, 14, 1, 1, 30), "T": (31, 4, 4, 4, 4, 4, 4),
    "U": (17, 17, 17, 17, 17, 17, 14), "V": (17, 17, 17, 17, 17, 10, 4),
    "W": (17, 17, 17, 21, 21, 21, 10), "X": (17, 10, 4, 4, 4, 10, 17),
    "Y": (17, 10, 4, 4, 4, 4, 4), "Z": (31, 1, 2, 4, 8, 16, 31),
    "0": (14, 17, 19, 21, 25, 17, 14), "1": (4, 12, 4, 4, 4, 4, 14),
    "2": (14, 17, 1, 6, 8, 16, 31), "3": (14, 17, 1, 6, 1, 17, 14),
    "4": (2, 6, 10, 18, 31, 2, 2), "5": (31, 16, 30, 1, 1, 17, 14),
    "6": (6, 8, 16, 30, 17, 17, 14), "7": (31, 1, 2, 4, 8, 8, 8),
    "8": (14, 17, 17, 14, 17, 17, 14), "9": (14, 17, 17, 15, 1, 2, 12),
    " ": (0, 0, 0, 0, 0, 0, 0), ".": (0, 0, 0, 0, 0, 12, 12),
    ",": (0, 0, 0, 0, 12, 4, 8), "'": (4, 4, 8, 0, 0, 0, 0),
    "-": (0, 0, 0, 14, 0, 0, 0), ":": (0, 12, 12, 0, 12, 12, 0),
    ";": (0, 12, 12, 0, 12, 4, 8), "!": (4, 4, 4, 4, 4, 0, 4),
    "?": (14, 17, 1, 6, 4, 0, 4), "$": (4, 15, 20, 14, 5, 30, 4),
    "%": (25, 26, 2, 4, 8, 21, 19), "&": (12, 18, 20, 8, 21, 18, 13),
    "/": (1, 2, 2, 4, 8, 8, 16), "(": (2, 4, 8, 8, 8, 4, 2),
    ")": (8, 4, 2, 2, 2, 4, 8), "+": (0, 4, 4, 14, 4, 4, 0),
    "*": (0, 4, 21, 14, 21, 4, 0), "•": (0, 0, 14, 14, 14, 0, 0),
    "—": (0, 0, 0, 31, 0, 0, 0),
}


def text_w(s, scale):
    if not s:
        return 0
    return len(s) * 6 * scale - scale


def text(x, y, s, scale, c):
    for ch in s.upper():
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits & (16 >> col):
                    rect(x + col * scale, y + row * scale, scale, scale, c)
        x += 6 * scale
    return x


def text_c(cx, y, s, scale, c):
    return text(cx - text_w(s, scale) // 2, y, s, scale, c)


def text_r(xright, y, s, scale, c):
    return text(xright - text_w(s, scale), y, s, scale, c)


def wrap(s, scale, maxw):
    words = s.split()
    lines = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(trial, scale) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def block(x, y, s, scale, c, maxw, gap=5):
    for ln in wrap(s, scale, maxw):
        text(x, y, ln, scale, c)
        y += 7 * scale + gap
    return y


# ---------------------------------------------------------------- scenes
def globe(cx, cy, r):
    circle(cx, cy, r, SKY)
    # continents: blobby green circles clipped by the disc
    blobs = [(-0.45, -0.35, 0.30), (-0.15, -0.55, 0.22), (0.30, -0.30, 0.26),
             (0.55, 0.05, 0.20), (0.05, 0.15, 0.30), (-0.50, 0.30, 0.24),
             (0.35, 0.55, 0.18), (-0.10, 0.62, 0.15)]
    for fx, fy, fr in blobs:
        bx, by, br = cx + int(fx * r), cy + int(fy * r), int(fr * r)
        for yy in range(by - br, by + br + 1):
            for xx in range(bx - br, bx + br + 1):
                if (xx - bx) ** 2 + (yy - by) ** 2 <= br * br and \
                        (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    px(xx, yy, LAND)
    # polar cap
    for yy in range(cy - r, cy - r + r // 4):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                px(xx, yy, WHITE)
    ring(cx, cy, r, BLUE, 3)
    # the crack: jagged dark split down the middle
    pts = [(cx - 6, cy - r + 6), (cx + 10, cy - r // 2), (cx - 8, cy - 4),
           (cx + 12, cy + r // 3), (cx - 4, cy + 2 * r // 3),
           (cx + 6, cy + r - 8)]
    for i in range(len(pts) - 1):
        line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], DARKRED, 5)
    line(cx + 10, cy - r // 2, cx + 34, cy - r // 3, DARKRED, 3)
    line(cx - 8, cy - 4, cx - 32, cy + 8, DARKRED, 3)


def thermometer(x, y, h):
    rect(x, y, 12, h, WHITE)
    frame(x, y, 12, h, INK, 2)
    rect(x + 3, y + h // 3, 6, h - h // 3, RED)
    circle(x + 6, y + h + 8, 13, RED)
    ring(x + 6, y + h + 8, 13, INK, 2)
    for i in range(5):
        rect(x + 14, y + 6 + i * (h // 5), 7, 2, INK)


def crossed_banner(x, y, w, label):
    rect(x, y, w, 34, INK)
    text_c(x + w // 2, y + 7, label, 3, WHITE)
    line(x + 4, y + 30, x + w - 4, y + 4, RED, 5)
    line(x + 4, y + 4, x + w - 4, y + 30, RED, 5)


def flame(x, y, s, c1=ORANGE, c2=FLAME):
    tri(x, y, x + s // 2, y - s, x + s, y, c1)
    tri(x + s // 4, y, x + s // 2, y - 3 * s // 5, x + 3 * s // 4, y, c2)
    tri(x + 2 * s // 5, y, x + s // 2, y - s // 3, x + 3 * s // 5, y, RED)


def smoke(x, y, n=4, r=13):
    for i in range(n):
        circle(x + i * r, y - i * r // 2, r - i, GREY)
        circle(x + i * r + 4, y - i * r // 2 - 4, r - i - 3, LGREY)


def tanker(x, y, w):
    # sea
    rect(x, y + 66, w, 26, SEA)
    for i in range(6):
        line(x + 8 + i * (w // 6), y + 76, x + 26 + i * (w // 6), y + 76,
             WHITE, 2)
    # hull
    poly([(x + 6, y + 44), (x + w - 6, y + 44), (x + w - 26, y + 68),
          (x + 26, y + 68)], DARKRED)
    rect(x + 6, y + 40, w - 12, 6, INK)
    # containers
    cols = [RED, BLUE, GREEN, ORANGE, GOLD, BLUE]
    for i in range(6):
        rect(x + 16 + i * ((w - 90) // 6), y + 22, (w - 90) // 6 - 3, 18,
             cols[i])
    # bridge tower
    rect(x + w - 62, y + 6, 34, 36, WHITE)
    frame(x + w - 62, y + 6, 34, 36, INK, 2)
    rect(x + w - 56, y + 12, 8, 7, SKY)
    rect(x + w - 44, y + 12, 8, 7, SKY)
    # fire at the stern + smoke
    flame(x + 14, y + 40, 30)
    flame(x + 40, y + 40, 20)
    smoke(x + 24, y + 22, 3, 9)
    # incoming missile with dashed trail
    for i in range(5):
        rect(x + w - 128 + i * 14, y + 2 + i * 4, 8, 3, GREY)
    tri(x + w - 52, y + 24, x + w - 38, y + 16, x + w - 42, y + 30, INK)
    flame(x + w - 60, y + 26, 12)


def drone(x, y, s=3):
    rect(x - 4 * s, y - s, 8 * s, 2 * s, INK)
    rect(x - s, y - 4 * s, 2 * s, 8 * s, INK)
    for dx, dy in ((-5, -5), (5, -5), (-5, 5), (5, 5)):
        line(x, y, x + dx * s, y + dy * s, INK, s)
        rect(x + dx * s - 3 * s, y + dy * s - s, 6 * s, s, GREY)
    circle(x, y, 2 * s, RED)


def dymer_block(x, y, w, h):
    floors = 5
    fh = h // floors
    # left standing part
    rect(x, y, w * 2 // 5, h, SAND)
    frame(x, y, w * 2 // 5, h, INK, 2)
    # right standing part
    rect(x + w * 3 // 5, y, w - w * 3 // 5, h, SAND)
    frame(x + w * 3 // 5, y, w - w * 3 // 5, h, INK, 2)
    for side_x, side_w in ((x, w * 2 // 5), (x + w * 3 // 5, w - w * 3 // 5)):
        for f in range(floors):
            for wx in range(side_x + 8, side_x + side_w - 10, 16):
                rect(wx, y + 6 + f * fh, 9, fh - 11, BLUE)
    # collapsed middle: broken slabs leaning into the gap
    poly([(x + w * 2 // 5, y + 4), (x + w * 3 // 5, y + h // 3),
          (x + w * 3 // 5, y + 12), (x + w * 2 // 5, y + h // 4)], BROWN)
    poly([(x + w * 2 // 5, y + h // 2), (x + w * 3 // 5, y + h - 6),
          (x + w * 2 // 5, y + h - 6)], GREY)
    # rubble pile
    tri(x + w // 3, y + h, x + w // 2, y + h - 22, x + 2 * w // 3, y + h, GREY)
    tri(x + w // 2 - 8, y + h, x + w // 2 + 8, y + h - 30,
        x + 2 * w // 3 + 10, y + h, BROWN)
    rect(x, y + h, w, 4, INK)
    smoke(x + w // 2, y + 8, 3, 9)
    drone(x + 30, y - 6, 2)


def factory(x, y, w, h):
    # main hall with sawtooth roof
    rect(x, y + 22, w, h - 22, (196, 178, 150))
    frame(x, y + 22, w, h - 22, INK, 2)
    for i in range(4):
        tri(x + i * w // 4, y + 22, x + i * w // 4 + w // 8, y + 4,
            x + (i + 1) * w // 4, y + 22, BROWN)
    # windows
    for wx in range(x + 10, x + w - 16, 22):
        rect(wx, y + 34, 13, 16, SKY)
    # chimney
    rect(x + w - 34, y - 16, 16, 40, BROWN)
    rect(x + w - 37, y - 20, 22, 6, INK)
    # big fire along the roofline
    for fx in range(x + 12, x + w - 30, 34):
        flame(fx, y + 24, 30)
    flame(x + w // 2, y + 22, 42)
    smoke(x + w - 30, y - 6, 4, 10)
    smoke(x + 26, y + 6, 3, 8)
    rect(x, y + h, w, 4, INK)


def flag_eu(x, y, w, h):
    rect(x, y, w, h, BLUE)
    frame(x, y, w, h, INK, 2)
    cx, cy, r = x + w // 2, y + h // 2, h // 3
    for i in range(8):
        import math
        sx = cx + int(r * math.cos(i * math.pi / 4))
        sy = cy + int(r * math.sin(i * math.pi / 4))
        circle(sx, sy, 3, GOLD)


def flag_id(x, y, w, h):
    rect(x, y, w, h // 2, RED)
    rect(x, y + h // 2, w, h - h // 2, WHITE)
    frame(x, y, w, h, INK, 2)


def flag_in(x, y, w, h):
    rect(x, y, w, h // 3, ORANGE)
    rect(x, y + h // 3, w, h // 3, WHITE)
    rect(x, y + 2 * h // 3, w, h - 2 * h // 3, GREEN)
    frame(x, y, w, h, INK, 2)
    circle(x + w // 2, y + h // 2, 4, BLUE)


def flag_np(x, y, w, h):
    # Nepal's double pennant, simplified
    poly([(x, y), (x + w, y + h // 3), (x + w // 2, y + h // 2),
          (x + w, y + 2 * h // 3), (x, y + h)], BLUE)
    poly([(x + 3, y + 4), (x + w - 8, y + h // 3), (x + w // 2 - 2, y + h // 2),
          (x + w - 8, y + 2 * h // 3), (x + 3, y + h - 4)], RED)
    circle(x + 14, y + h // 3, 4, WHITE)
    circle(x + 14, y + 2 * h // 3, 4, WHITE)


def chip(x, y, s):
    rect(x, y, s, s, INK)
    rect(x + s // 5, y + s // 5, 3 * s // 5, 3 * s // 5, GREY)
    frame(x + s // 5, y + s // 5, 3 * s // 5, 3 * s // 5, GOLD, 3)
    text_c(x + s // 2, y + s // 2 - 10, "AI", 3, GOLD)
    pin = s // 9
    for i in range(5):
        off = y + pin + i * (s - 2 * pin) // 4
        rect(x - 10, off, 10, 4, GOLD)
        rect(x + s, off, 10, 4, GOLD)
        offx = x + pin + i * (s - 2 * pin) // 4
        rect(offx, y - 10, 4, 10, GOLD)
        rect(offx, y + s, 4, 10, GOLD)
    # route dots sneaking off to the right
    for i in range(4):
        circle(x + s + 18 + i * 13, y + s // 2 - i * 7, 3, RED)


def mountains(x, y, w, h):
    tri(x, y + h, x + w // 3, y, x + 2 * w // 3, y + h, GREY)
    tri(x + w // 3, y + h, x + 2 * w // 3, y + 6, x + w, y + h, (88, 84, 78))
    tri(x + w // 3 - 13, y + h // 4, x + w // 3, y, x + w // 3 + 13, y + h // 4,
        WHITE)
    tri(x + 2 * w // 3 - 12, y + h // 4 + 5, x + 2 * w // 3, y + 6,
        x + 2 * w // 3 + 12, y + h // 4 + 5, WHITE)
    rect(x, y + h, w, 3, INK)


def cricket(x, y, w, h):
    rect(x, y, w, h, GREEN)
    frame(x, y, w, h, INK, 2)
    text_c(x + w // 2, y + 5, "720/9", 3, WHITE)
    text_c(x + w // 2, y + h - 15, "DECLARED", 2, GOLD)
    # bat and ball
    line(x + 14, y + h - 6, x + 30, y + h - 20, SAND, 5)
    rect(x + 27, y + h - 30, 7, 13, BROWN)
    circle(x + w - 18, y + h - 12, 6, RED)
    ring(x + w - 18, y + h - 12, 6, WHITE, 1)


def panel(x, y, w, h, kicker, kc, headline, body, ill, ill_h,
          head_scale=3):
    rect(x, y, w, h, PAPER2)
    frame(x, y, w, h, INK, 2)
    rect(x, y, w, 24, kc)
    text(x + 8, y + 5, kicker, 2, WHITE)
    yy = y + 32
    for ln in headline:
        text(x + 8, yy, ln, head_scale, INK)
        yy += 7 * head_scale + 4
    ill(x + 10, yy + 2, w - 20)
    yy += ill_h + 8
    line(x + 8, yy - 3, x + w - 8, yy - 3, LGREY, 2)
    block(x + 8, yy + 2, body, 2, INK, w - 16, 4)


# ---------------------------------------------------------------- layout
def compose():
    rect(0, 0, W, H, PAPER)
    frame(8, 8, W - 16, H - 16, INK, 3)
    frame(15, 15, W - 30, H - 30, INK, 1)

    # masthead
    text(28, 26, "EST. TODAY • VOL. I — NO. 23", 2, GREY)
    text_r(996, 26, "PRICE: ONE DAY OF NEWS", 2, GREY)
    text_c(512, 44, "THE WORLD ON MONDAY", 8, INK)
    text_c(512, 108, "MONDAY 23 NOVEMBER 2026 • LATE EDITION", 3, RED)
    rect(24, 132, 976, 5, INK)
    rect(24, 141, 976, 2, INK)

    # ---- lead: COP31 collapse
    lx, ly, lw, lh = 24, 152, 976, 268
    rect(lx, ly, lw, lh, PAPER2)
    frame(lx, ly, lw, lh, INK, 2)
    globe(215, 258, 86)
    thermometer(336, 192, 104)
    text_c(342, 330, "1.5C", 3, RED)
    crossed_banner(48, 360, 380, "FOSSIL FUELS")
    text_c(238, 404, "44H INTO OVERTIME, NO DEAL", 2, INK)
    tx = 452
    text(tx, 164, "COP31 • ANTALYA, TURKIYE", 3, RED)
    text(tx, 192, "CLIMATE TALKS", 6, INK)
    text(tx, 240, "COLLAPSE", 6, INK)
    rect(tx, 288, 300, 4, RED)
    text(tx, 300, "NO DEAL IN ANTALYA", 3, INK)
    block(tx, 332, "THE FINAL PACT NEVER MENTIONED FOSSIL FUELS — THE "
                   "WORDS WERE CUT DESPITE 100+ NATIONS BACKING A "
                   "PHASE-OUT. THE EU WALKED OUT AND AMERICA STAYED "
                   "AWAY. ONE CONSOLATION: 90+ COUNTRIES PLEDGED TO "
                   "ELECTRIFY.", 2, INK, 532, 4)

    # ---- row 2: three war/disaster panels
    py = 436
    panel(24, py, 317, 256, "WAR • THE GULF", RED,
          ["HORMUZ ON FIRE", "TANKERS HIT"],
          "TWO TANKERS STRUCK NEAR THE STRAIT. MISSILES FLEW AT "
          "RIYADH; A BAHRAIN BASE WAS HIT.",
          lambda X, Y, Wd: tanker(X, Y, Wd), 92)
    panel(353, py, 317, 256, "WAR • UKRAINE", BLUE,
          ["14 MISSING IN", "THE DYMER RUBBLE"],
          "A RUSSIAN DRONE LEVELS A FIVE-STOREY BLOCK NEAR KYIV. "
          "14 PEOPLE UNACCOUNTED FOR.",
          lambda X, Y, Wd: dymer_block(X + 20, Y + 18, Wd - 40, 70), 92)
    panel(682, py, 317, 256, "INDONESIA • DISASTER", ORANGE,
          ["CIKANDE FACTORY", "INFERNO"],
          "FIRE GUTS A BANTEN CANDY FACTORY. 24 BODY BAGS OUT; "
          "ABOUT 50 OF 300 WORKERS MISSING.",
          lambda X, Y, Wd: factory(X + 10, Y + 24, Wd - 20, 62), 92)

    # ---- row 3: four panels
    qy = 704
    panel(24, qy, 235, 216, "TRADE • EU DEAL", GREEN,
          ["730M PEOPLE,", "ONE MARKET"],
          "INDONESIA AND THE EU SIGN THEIR BIGGEST PACT AFTER 10 "
          "YEARS OF TALKS.",
          lambda X, Y, Wd: (flag_eu(X + 2, Y + 2, 100, 44),
                            flag_id(X + 113, Y + 2, 100, 44)), 48)
    panel(271, qy, 235, 216, "TECH • US-CHINA", INK,
          ["$12BN CHIP", "PIPELINE"],
          "TOP NVIDIA CHIPS REACHED CHINA VIA SINGAPORE; CEO "
          "OUSTED.",
          lambda X, Y, Wd: chip(X + 82, Y, 48), 48)
    panel(518, qy, 235, 216, "ASIA • DIPLOMACY", BLUE,
          ["BALEN'S BIG", "DELHI DAY"],
          "NEPAL'S PM MAKES HIS FIRST FOREIGN TRIP: A SUMMIT "
          "WITH MODI.",
          lambda X, Y, Wd: (mountains(X, Y + 6, 128, 40),
                            flag_in(X + 138, Y + 4, 34, 22),
                            flag_np(X + 182, Y + 2, 30, 40)), 48)
    panel(765, qy, 235, 216, "SPORT • CRICKET", GREEN,
          ["720! INDIA'S", "RUN MOUNTAIN"],
          "WELLINGTON RECORD: RAHUL 136, PANT 128. NZ TRAIL "
          "BY 233.",
          lambda X, Y, Wd: cricket(X, Y, Wd, 48), 48)

    # ---- markets strip
    my = 926
    rect(24, my, 976, 46, PAPER2)
    frame(24, my, 976, 46, INK, 2)
    rect(24, my, 128, 46, RED)
    text_c(88, my + 8, "MARKETS", 2, WHITE)
    text_c(88, my + 26, "IN SHOCK", 2, WHITE)
    text(168, my + 6, "AI ROUT: NASDAQ -5.28% • S&P -3.70% • CHIPS -10.7%",
         2, INK)
    text(168, my + 25, "BTC $55,130 LOW THEN $60,934 • GOLD $3,502 -9.4% "
                       "• BRENT $92.57", 2, INK)

    # ---- footer nuggets
    text_c(512, 978, "ALSO TODAY: THOUSANDS MARCH IN LISBON OVER THE "
                     "COST OF LIVING", 2, GREY)
    text_c(512, 994, "RUSSIAN CARGO SHIP STILL ABLAZE OFF FINLAND "
                     "AFTER A DRONE ATTACK", 2, GREY)


# ---------------------------------------------------------------- png out
def png_bytes():
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw += BUF[yy * W * 3:(yy + 1) * W * 3]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
            chunk(b"IEND", b""))


def main():
    compose()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or \
        os.path.dirname(os.path.abspath(__file__))
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(png_bytes())


if __name__ == "__main__":
    main()
