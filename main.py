#!/usr/bin/env python3
"""Draw the world news of Wednesday 18 November 2026 as one broadsheet poster.

Writes entry.png (1024x1024, under 1 MiB) to /output, or to the directory
named by MAKEFUN_OUTPUT_DIR when that variable is set. No network, no
randomness, no clock: two runs write byte-identical files.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 28
RIGHT = W - MARGIN

PAPER = (247, 243, 232)
INK = (18, 18, 22)
BLACK_BAR = (16, 16, 20)
AMBER = (245, 176, 65)
RED = (178, 34, 34)
NAVY = (31, 58, 147)
GREEN = (15, 118, 90)
ORANGE = (196, 94, 12)

SERIF_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
]
SANS_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]
SANS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]


def load_font(paths, size):
    """First usable font file, else Pillow's built-in bitmap font."""
    for path in paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default(size)


def wrap_text(draw, text, font, width):
    """Greedy word wrap; returns a list of lines that fit inside width."""
    lines = []
    current = ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=font) <= width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_lines(draw, lines, x, y, font, fill, leading):
    """Draw wrapped lines top to bottom; returns the y below the last line."""
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def star_points(cx, cy, outer, inner, points=5):
    """Vertices of a regular star centred on (cx, cy)."""
    pts = []
    for i in range(points * 2):
        radius = outer if i % 2 == 0 else inner
        angle = -math.pi / 2 + i * math.pi / points
        pts.append((cx + radius * math.cos(angle),
                    cy + radius * math.sin(angle)))
    return pts


def flag_usa(draw, x, y, w, h):
    stripe = h / 13.0
    for i in range(13):
        colour = (178, 34, 34) if i % 2 == 0 else (255, 255, 255)
        draw.rectangle([x, y + i * stripe, x + w, y + (i + 1) * stripe],
                       fill=colour)
    canton_w, canton_h = w * 0.42, stripe * 7
    draw.rectangle([x, y, x + canton_w, y + canton_h], fill=(60, 59, 110))
    for row in range(4):
        for col in range(5):
            cx = x + 8 + col * (canton_w - 12) / 4
            cy = y + 7 + row * (canton_h - 12) / 3
            draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(255, 255, 255))
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=2)


def flag_china(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    draw.polygon(star_points(x + w * 0.16, y + h * 0.30, h * 0.26, h * 0.10),
                 fill=(255, 222, 0))
    for fx, fy in [(0.36, 0.14), (0.44, 0.26),
                   (0.44, 0.44), (0.36, 0.56)]:
        draw.polygon(star_points(x + w * fx, y + h * fy, h * 0.09, h * 0.04),
                     fill=(255, 222, 0))
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=2)


def flag_russia(draw, x, y, w, h):
    for i, colour in enumerate([(255, 255, 255), (0, 57, 166), (213, 0, 50)]):
        draw.rectangle([x, y + i * h / 3, x + w, y + (i + 1) * h / 3],
                       fill=colour)
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=2)


def icon_missile(draw, cx, cy, size):
    """A missile streaking up to the right, with a flame at its tail."""
    s = size / 2.0
    draw.line([cx - s, cy + s * 0.6, cx + s * 0.7, cy - s * 0.7],
              fill=RED, width=9)
    draw.polygon([(cx + s * 0.7, cy - s * 0.7), (cx + s * 0.25, cy - s * 0.55),
                  (cx + s * 0.55, cy - s * 0.25)], fill=RED)
    draw.ellipse([cx - s - 6, cy + s * 0.6 - 6, cx - s + 14, cy + s * 0.6 + 14],
                 fill=(245, 176, 65))
    draw.ellipse([cx - s - 1, cy + s * 0.6 - 1, cx - s + 9, cy + s * 0.6 + 9],
                 fill=(255, 230, 120))
    draw.arc([cx - s * 1.3, cy + s * 0.1, cx - s * 0.5, cy + s * 0.9],
             start=200, end=340, fill=RED, width=4)


def icon_bridge(draw, cx, cy, size):
    """A bridge deck snapped in the middle, with a spark at the break."""
    s = size / 2.0
    draw.rectangle([cx - s, cy - s * 0.7, cx - s + 8, cy + s * 0.7],
                   fill=NAVY)
    draw.rectangle([cx + s - 8, cy - s * 0.7, cx + s, cy + s * 0.7],
                   fill=NAVY)
    draw.line([cx - s, cy, cx - s * 0.15, cy], fill=NAVY, width=8)
    draw.line([cx + s * 0.15, cy, cx + s, cy], fill=NAVY, width=8)
    draw.line([cx - s * 0.15, cy, cx, cy + s * 0.35], fill=NAVY, width=6)
    draw.line([cx + s * 0.15, cy, cx, cy + s * 0.35], fill=NAVY, width=6)
    draw.polygon([(cx - 6, cy + s * 0.35), (cx + 6, cy + s * 0.35),
                  (cx, cy + s * 0.62)], fill=(245, 130, 32))
    draw.line([cx - s * 0.5, cy - s * 0.45, cx - s * 0.5, cy - s * 0.15],
              fill=NAVY, width=4)
    draw.line([cx + s * 0.5, cy - s * 0.45, cx + s * 0.5, cy - s * 0.15],
              fill=NAVY, width=4)


def icon_virus(draw, cx, cy, size):
    """A spiked virus blob with a red-cross badge."""
    r = size * 0.28
    for k in range(8):
        angle = k * math.pi / 4
        x1, y1 = cx + r * math.cos(angle), cy + r * math.sin(angle)
        x2, y2 = cx + (r + 13) * math.cos(angle), cy + (r + 13) * math.sin(angle)
        draw.line([x1, y1, x2, y2], fill=GREEN, width=7)
        draw.ellipse([x2 - 4, y2 - 4, x2 + 4, y2 + 4], fill=GREEN)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GREEN)
    bx, by, br = cx + r * 0.7, cy + r * 0.7, 17
    draw.ellipse([bx - br, by - br, bx + br, by + br], fill=RED)
    draw.rectangle([bx - 3, by - 10, bx + 3, by + 10], fill=(255, 255, 255))
    draw.rectangle([bx - 10, by - 3, bx + 10, by + 3], fill=(255, 255, 255))


def icon_chip(draw, cx, cy, size):
    """A processor chip: square body, pins on four sides, amber core."""
    s = size / 2.0
    body = size * 0.56
    for k in range(3):
        off = -body / 3 + k * body / 3
        draw.line([cx + off, cy - s, cx + off, cy - body / 2], fill=ORANGE,
                  width=6)
        draw.line([cx + off, cy + body / 2, cx + off, cy + s], fill=ORANGE,
                  width=6)
        draw.line([cx - s, cy + off, cx - body / 2, cy + off], fill=ORANGE,
                  width=6)
        draw.line([cx + body / 2, cy + off, cx + s, cy + off], fill=ORANGE,
                  width=6)
    draw.rectangle([cx - body / 2, cy - body / 2, cx + body / 2, cy + body / 2],
                   fill=ORANGE)
    core = body * 0.45
    draw.rectangle([cx - core, cy - core, cx + core, cy + core],
                   fill=AMBER)


def story_panel(draw, box, rule_colour, bg, kicker, kicker_colour,
                headline, deck, icon):
    """One of the four small story panels: rule, kicker, headline, deck, icon."""
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], fill=bg)
    draw.rectangle([x0, y0, x1, y0 + 6], fill=rule_colour)
    kick_font = load_font(SANS_BOLD, 22)
    head_font = load_font(SERIF_BOLD, 31)
    deck_font = load_font(SANS, 21)
    text_x = x0 + 20
    text_w = 340
    draw.text((text_x, y0 + 18), kicker, font=kick_font, fill=kicker_colour)
    head_lines = wrap_text(draw, headline, head_font, text_w)
    y = draw_lines(draw, head_lines, text_x, y0 + 48, head_font, INK, 36)
    deck_lines = wrap_text(draw, deck, deck_font, text_w)
    draw_lines(draw, deck_lines, text_x, y + 4, deck_font, (60, 60, 66), 25)
    icon(draw, x1 - 58, (y0 + y1) / 2 + 8, 96)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # Masthead.
    draw.rectangle([MARGIN, 16, RIGHT, 19], fill=INK)
    title_font = load_font(SERIF_BOLD, 62)
    title = "THE WORLD IN A DAY"
    tw = draw.textlength(title, font=title_font)
    draw.text(((W - tw) / 2, 30), title, font=title_font, fill=INK)
    draw.rectangle([MARGIN, 112, RIGHT, 114], fill=INK)

    # Date bar.
    draw.rectangle([MARGIN, 124, RIGHT, 186], fill=BLACK_BAR)
    date_font = load_font(SANS_BOLD, 38)
    date = "WEDNESDAY \u00b7 18 NOVEMBER 2026"
    dw = draw.textlength(date, font=date_font)
    draw.text(((W - dw) / 2, 136), date, font=date_font, fill=(255, 255, 255))

    # Hero panel: the Shenzhen summit.
    draw.rectangle([MARGIN, 198, RIGHT, 430], fill=(226, 232, 244))
    draw.rectangle([MARGIN, 198, MARGIN + 10, 430], fill=NAVY)
    kick_font = load_font(SANS_BOLD, 23)
    draw.text((MARGIN + 28, 212), "TOP STORY \u00b7 SHENZHEN, CHINA",
              font=kick_font, fill=RED)
    hero_font = load_font(SERIF_BOLD, 36)
    hero_lines = wrap_text(draw, "Trump Lands in China for First-Ever "
                           "Three-Power Summit", hero_font, 700)
    hero_end = draw_lines(draw, hero_lines, MARGIN + 28, 244, hero_font,
                          INK, 44)
    deck_font = load_font(SANS, 24)
    hero_deck = wrap_text(draw, "Xi greets him at the airport; he meets Xi "
                          "and Putin on Thursday at the APEC summit.",
                          deck_font, 700)
    draw_lines(draw, hero_deck, MARGIN + 28, hero_end + 10, deck_font,
               (52, 52, 58), 30)
    flag_w, flag_h, flag_gap = 168, 52, 16
    flag_x = RIGHT - 28 - flag_w
    flag_y = 224
    flag_usa(draw, flag_x, flag_y, flag_w, flag_h)
    flag_china(draw, flag_x, flag_y + flag_h + flag_gap, flag_w, flag_h)
    flag_russia(draw, flag_x, flag_y + 2 * (flag_h + flag_gap), flag_w, flag_h)

    # Middle row: the Gulf and Ukraine.
    story_panel(draw, (MARGIN, 442, 500, 656), RED, (250, 232, 234),
                "THE GULF \u00b7 WAR WIDENS", RED,
                "Iran Strikes US Bases in Kuwait and Bahrain",
                "US hit Qeshm Island first; tankers struck in Hormuz.",
                icon_missile)
    story_panel(draw, (524, 442, RIGHT, 656), NAVY, (232, 234, 248),
                "UKRAINE \u00b7 KERCH BRIDGE", NAVY,
                "Kerch Bridge Hit Again \u2014 Span Collapses",
                "Second day of strikes; Zelensky confirms it.",
                icon_bridge)

    # Bottom row: health and tech.
    story_panel(draw, (MARGIN, 668, 500, 882), GREEN, (226, 242, 236),
                "HEALTH \u00b7 UNITED STATES", GREEN,
                "US Loses Measles-Free Status",
                "PAHO confirms the loss after 26 years.",
                icon_virus)
    story_panel(draw, (524, 668, RIGHT, 882), ORANGE, (251, 238, 224),
                "TECH \u00b7 CHIP GIANT", ORANGE,
                "Nvidia's Record $115.8B Quarter",
                "Board says no to ousted chief Huang's offer to return.",
                icon_chip)

    # Ticker: the rest of the day.
    draw.rectangle([MARGIN, 894, RIGHT, 996], fill=BLACK_BAR)
    label_font = load_font(SANS_BOLD, 24)
    draw.text((MARGIN + 20, 904), "ALSO TODAY", font=label_font, fill=AMBER)
    tick_font = load_font(SANS, 22)
    tick_lines = wrap_text(draw, "Peltola wins Alaska Senate seat \u2014 "
                           "Democrats take a 56\u201344 majority \u00b7 Israel "
                           "opens a new Gaza operation \u00b7 Russian military "
                           "plane crashes in Siberia, 19 killed",
                           tick_font, RIGHT - MARGIN - 40)
    draw_lines(draw, tick_lines, MARGIN + 20, 934, tick_font,
               (255, 255, 255), 27)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    img.save(os.path.join(out_dir, "entry.png"), format="PNG")


if __name__ == "__main__":
    main()
