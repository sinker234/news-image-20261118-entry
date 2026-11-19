#!/usr/bin/env python3
"""Render entry.png: 'The World in a Day' - the world news of Wednesday
18 November 2026 in one 1024x1024 infographic poster.

Everything is drawn in code with PIL (no external images), so the picture
is fully our own work. Stories chosen from the day's reporting (Reuters,
AP, AFP, The Straits Times, Dawn, Business Recorder, Outlook India):

  TOP   Trump lands in Shenzhen, greeted by Xi; a first-ever
        Trump-Xi-Putin trilateral summit is set for Thursday at APEC.
  GULF  Iran strikes US bases in Kuwait and Bahrain after the US hit
        Qeshm Island; tankers are hit in the Strait of Hormuz.
  WAR   Ukraine hits the Kerch Bridge a second day running - part of
        the road span collapses, Zelensky confirms.
  HEALTH The US loses its measles-free status after 26 years, PAHO says.
  TECH  Nvidia posts a record $115.8B quarter; its board rejects
        ousted CEO Jensen Huang's offer to return.
  PLUS  Democrat Peltola wins Alaska's Senate seat - Democrats take a
        56-44 majority; Israel opens a new operation in central Gaza;
        a Russian military plane crashes in Siberia, 19 killed.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


# palette - broadsheet cream, ink, wire-service red, navy
CREAM = (248, 244, 234)
INK = (20, 24, 29)
RED = (179, 32, 44)
NAVY = (27, 58, 120)
WHITE = (255, 255, 255)
GREY = (52, 58, 66)

img = Image.new("RGB", (W, H), CREAM)
d = ImageDraw.Draw(img)


def wrap(text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def text_block(x, y, text, fnt, fill, max_w, leading=1.18):
    for line in wrap(text, fnt, max_w):
        d.text((x, y), line, font=fnt, fill=fill)
        y += int(fnt.size * leading)
    return y


# ---------------------------------------------------------------- icons
def _bezier(p0, p1, p2, p3, n=14):
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        x = u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]
        pts.append((x, y))
    return pts


def _flame_pts(cx, cy, s):
    tip = (cx + s * 0.18, cy - s)
    pts = []
    pts += _bezier(tip, (cx - s * 0.62, cy - s * 0.42),
                   (cx - s * 0.58, cy + s * 0.28), (cx - s * 0.34, cy + s * 0.72))
    pts += _bezier((cx - s * 0.34, cy + s * 0.72), (cx - s * 0.12, cy + s * 1.0),
                   (cx + s * 0.30, cy + s * 1.0), (cx + s * 0.46, cy + s * 0.66))
    pts += _bezier((cx + s * 0.46, cy + s * 0.66), (cx + s * 0.66, cy + s * 0.30),
                   (cx + s * 0.34, cy - s * 0.02), (cx + s * 0.16, cy + s * 0.30))
    pts += _bezier((cx + s * 0.16, cy + s * 0.30), (cx + s * 0.05, cy - s * 0.10),
                   (cx + s * 0.30, cy - s * 0.55), tip)
    return pts


def icon_flame(cx, cy, s, col):
    d.polygon(_flame_pts(cx, cy, s), fill=col)
    d.polygon(_flame_pts(cx, cy + s * 0.34, s * 0.52), fill=(255, 176, 66))


def icon_missile(cx, cy, s, col):
    """A rocket streaking up-right with a flame tail."""
    d.line([cx - s, cy + s, cx + s * 0.55, cy - s * 0.55], fill=col, width=10)
    d.polygon([(cx + s * 0.55, cy - s * 0.55), (cx + s * 0.95, cy - s * 0.30),
               (cx + s * 0.75, cy - s * 0.05)], fill=col)
    d.polygon(_flame_pts(cx - s * 0.72, cy + s * 0.72, s * 0.42), fill=(255, 176, 66))
    for i, r in enumerate((6, 10, 14)):
        d.arc([cx - s - r, cy + s - r, cx - s + r, cy + s + r],
              start=90, end=270, fill=col, width=3)


def icon_bridge(cx, cy, s, col):
    """A suspension bridge with a broken, sagging middle span."""
    d.line([cx - s, cy - int(s * 0.55), cx - s, cy + int(s * 0.5)], fill=col, width=8)
    d.line([cx + s, cy - int(s * 0.55), cx + s, cy + int(s * 0.5)], fill=col, width=8)
    # left deck solid, middle span sagging down, right deck solid
    d.line([cx - s, cy + int(s * 0.15), cx - int(s * 0.30), cy + int(s * 0.15)],
           fill=col, width=9)
    d.line([cx - int(s * 0.30), cy + int(s * 0.15), cx, cy + int(s * 0.62)],
           fill=col, width=9)
    d.line([cx, cy + int(s * 0.62), cx + int(s * 0.30), cy + int(s * 0.15)],
           fill=col, width=9)
    d.line([cx + int(s * 0.30), cy + int(s * 0.15), cx + s, cy + int(s * 0.15)],
           fill=col, width=9)
    for x in (cx - int(s * 0.62), cx + int(s * 0.62)):
        d.line([x, cy - int(s * 0.35), x, cy + int(s * 0.15)], fill=col, width=4)
    # small flame at the break point, below the sag
    icon_flame(cx, cy + int(s * 0.42), int(s * 0.26), RED)


def icon_virus(cx, cy, s, col):
    """A spiky virus ball with a red cross over it."""
    d.ellipse([cx - int(s * 0.55), cy - int(s * 0.55), cx + int(s * 0.55),
               cy + int(s * 0.55)], fill=col)
    for i in range(10):
        a = i * math.pi / 5
        x1 = cx + int(s * 0.55 * math.cos(a))
        y1 = cy + int(s * 0.55 * math.sin(a))
        x2 = cx + int(s * 0.95 * math.cos(a))
        y2 = cy + int(s * 0.95 * math.sin(a))
        d.line([x1, y1, x2, y2], fill=col, width=7)
        d.ellipse([x2 - 6, y2 - 6, x2 + 6, y2 + 6], fill=col)
    # red cross badge bottom-right
    bx, by, r = cx + int(s * 0.55), cy + int(s * 0.55), int(s * 0.42)
    d.ellipse([bx - r, by - r, bx + r, by + r], fill=RED)
    d.rectangle([bx - int(r * 0.55), by - int(r * 0.18), bx + int(r * 0.55),
                 by + int(r * 0.18)], fill=WHITE)
    d.rectangle([bx - int(r * 0.18), by - int(r * 0.55), bx + int(r * 0.18),
                 by + int(r * 0.55)], fill=WHITE)


def icon_chip(cx, cy, s, col):
    """A computer chip with pins."""
    d.rectangle([cx - int(s * 0.55), cy - int(s * 0.55), cx + int(s * 0.55),
                 cy + int(s * 0.55)], fill=col)
    d.rectangle([cx - int(s * 0.30), cy - int(s * 0.30), cx + int(s * 0.30),
                 cy + int(s * 0.30)], fill=(255, 176, 66))
    for i in range(-1, 2):
        off = i * int(s * 0.42)
        d.line([cx + off, cy - int(s * 0.55), cx + off, cy - int(s * 0.85)],
               fill=col, width=6)
        d.line([cx + off, cy + int(s * 0.55), cx + off, cy + int(s * 0.85)],
               fill=col, width=6)
        d.line([cx - int(s * 0.55), cy + off, cx - int(s * 0.85), cy + off],
               fill=col, width=6)
        d.line([cx + int(s * 0.55), cy + off, cx + int(s * 0.85), cy + off],
               fill=col, width=6)


def icon_flags(x, y, w):
    """Three stylised flags stacked: US, China, Russia (each w x 34)."""
    fh, gap = 34, 9
    for i in range(6):
        d.rectangle([x, y + i * fh // 6, x + w, y + (i + 1) * fh // 6],
                    fill=(178, 34, 52) if i % 2 == 0 else (245, 245, 245))
    d.rectangle([x, y, x + w * 0.42, y + fh // 2], fill=(60, 59, 110))
    d.rectangle([x, y, x + w, y + fh], outline=INK, width=3)
    y2 = y + fh + gap
    d.rectangle([x, y2, x + w, y2 + fh], fill=(222, 41, 16))
    cx, cy, r = x + 22, y2 + fh // 2, 10
    star = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        star.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(star, fill=(255, 222, 0))
    d.rectangle([x, y2, x + w, y2 + fh], outline=INK, width=3)
    y3 = y2 + fh + gap
    d.rectangle([x, y3, x + w, y3 + fh // 3], fill=(245, 245, 245))
    d.rectangle([x, y3 + fh // 3, x + w, y3 + 2 * fh // 3], fill=(0, 57, 166))
    d.rectangle([x, y3 + 2 * fh // 3, x + w, y3 + fh], fill=(213, 43, 30))
    d.rectangle([x, y3, x + w, y3 + fh], outline=INK, width=3)


# ---------------------------------------------------------------- masthead
MX = 36  # page margin
d.line([MX, 30, W - MX, 30], fill=INK, width=3)
f_title = font(SERIF_B, 64)
t = "THE WORLD IN A DAY"
d.text(((W - d.textlength(t, font=f_title)) / 2, 40), t, font=f_title, fill=INK)
d.line([MX, 122, W - MX, 122], fill=INK, width=3)

# date bar - the day, unmissable
d.rectangle([MX, 134, W - MX, 192], fill=INK)
f_date = font(SANS_B, 37)
t = "WEDNESDAY · 18 NOVEMBER 2026"
d.text(((W - d.textlength(t, font=f_date)) / 2, 145), t, font=f_date, fill=CREAM)

# ---------------------------------------------------------------- hero
HY, HH = 208, 238
d.rectangle([MX, HY, W - MX, HY + HH], fill=(233, 238, 247))
d.rectangle([MX, HY, MX + 10, HY + HH], fill=NAVY)
hx = MX + 34
f_kick = font(SANS_B, 23)
d.text((hx, HY + 18), "TOP STORY · SHENZHEN, CHINA", font=f_kick, fill=RED)
# hero headline: shrink until the widest line fits the space left of the flags
hero_lines = ["Trump Lands in China for", "First-Ever Three-Power Summit"]
hero_size = 49
while hero_size > 30:
    f_hero = font(SERIF_B, hero_size)
    if max(d.textlength(l, font=f_hero) for l in hero_lines) <= 745:
        break
    hero_size -= 1
f_hero = font(SERIF_B, hero_size)
d.text((hx, HY + 52), hero_lines[0], font=f_hero, fill=INK)
d.text((hx, HY + 108), hero_lines[1], font=f_hero, fill=INK)
f_sub = font(SANS, 24)
text_block(hx, HY + 172,
           "Xi greets him at the airport; he meets Xi and Putin "
           "on Thursday at the APEC summit.",
           f_sub, GREY, 640)
icon_flags(W - MX - 158, HY + 56, 136)

# ---------------------------------------------------------------- panels
panels = [
    ("THE GULF · WAR WIDENS", (163, 22, 33), (249, 232, 234),
     "Iran Strikes US Bases in Kuwait and Bahrain",
     "After the US hit Qeshm Island; tankers struck in the Strait of Hormuz.",
     icon_missile),
    ("UKRAINE · KERCH BRIDGE", (43, 58, 143), (233, 235, 247),
     "Kerch Bridge Hit Again — Span Collapses",
     "A second day of strikes; Zelensky confirms the damage.",
     icon_bridge),
    ("HEALTH · UNITED STATES", (14, 122, 95), (226, 242, 236),
     "US Loses Measles-Free Status After 26 Years",
     "Measles spread unchecked for over a year.",
     icon_virus),
    ("TECH · CHIP GIANT", (194, 81, 10), (251, 238, 226),
     "Nvidia's Record $115.8B Quarter",
     "Board says no to ousted chief Huang's offer to return.",
     icon_chip),
]

PW = (W - 2 * MX - 16) // 2
PH = 216
rows_y = [458, 690]
f_pk = font(SANS_B, 20)
f_ph = font(SERIF_B, 30)
f_ps = font(SANS, 20)

for i, (kick, accent, tint, head, sub, icon) in enumerate(panels):
    px = MX + (i % 2) * (PW + 16)
    py = rows_y[i // 2]
    d.rectangle([px, py, px + PW, py + PH], fill=tint)
    d.rectangle([px, py, px + PW, py + 7], fill=accent)
    tx = px + 22
    d.text((tx, py + 18), kick, font=f_pk, fill=accent)
    yy = text_block(tx, py + 48, head, f_ph, INK, PW - 142, leading=1.12)
    text_block(tx, yy + 4, sub, f_ps, GREY, PW - 142, leading=1.15)
    icx, icy = px + PW - 62, py + PH // 2 + 8
    if icon is icon_missile:
        icon(icx, icy, 42, accent)
    elif icon is icon_bridge:
        icon(icx, icy, 46, accent)
    elif icon is icon_virus:
        icon(icx, icy, 40, accent)
    else:
        icon(icx, icy, 42, accent)

# ---------------------------------------------------------------- ticker
TY = 922
d.rectangle([MX, TY, W - MX, 1002], fill=INK)
f_tk = font(SANS_B, 20)
d.text((MX + 20, TY + 9), "ALSO TODAY", font=f_tk, fill=(255, 176, 66))
text_block(MX + 20, TY + 36,
           "Peltola wins Alaska Senate seat — Democrats take a 56–44 "
           "majority · Israel opens a new Gaza operation · Russian "
           "military plane crashes in Siberia, 19 killed",
           font(SANS, 19), CREAM, W - 2 * MX - 40, leading=1.12)

img.save(OUT, optimize=True)
print(OUT, os.path.getsize(OUT), "bytes")
