#!/usr/bin/env python3
"""Build entry.png for make.fun news-image-20261124.

Layout (1024x1024, dark news-poster style):
  - top banner: title + date (TUESDAY 24 NOVEMBER 2026)
  - centre: AI-generated dynamic-horizon hero art (no text in it)
  - bottom: eight story rows, each with a number chip, a small
    hand-drawn PIL icon, a bold headline and one short fact line.

All eight stories were verified against real reporting of 24 Nov 2026
(NYT, Guardian, France 24, Al Jazeera, Reuters-derived digests).

Run: python3 draw.py  -> writes entry.png next to this file.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

BG = (8, 13, 18)
BANNER_BG = (26, 5, 5)
AMBER = (255, 179, 71)
RED = (255, 69, 58)
WHITE = (245, 245, 240)
FADE = (196, 208, 216)
ROW_A = (16, 24, 32)
ROW_B = (11, 17, 24)
LINE = (48, 60, 72)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def banner(draw):
    draw.rectangle([0, 0, W, 124], fill=BANNER_BG)
    draw.rectangle([0, 124, W, 128], fill=RED)
    title = font(FONT_BOLD, 46)
    date = font(FONT_BOLD, 32)
    draw.text((32, 10), "ONE TUESDAY, EIGHT FAULT LINES", font=title, fill=WHITE)
    draw.text((32, 70), "TUESDAY  24  NOVEMBER  2026  ·  AS REPORTED", font=date, fill=AMBER)


def hero(base):
    """Crop a band of the wide hero art and paste it."""
    art = Image.open(os.path.join(HERE, "assets", "hero.webp")).convert("RGB")
    # Wide art 2240x1120; take a 1024x280 band through the middle.
    top = (art.height - 560) // 2
    band = art.crop((0, top, art.width, top + 560))
    band = band.resize((W, 280), Image.LANCZOS)
    base.paste(band, (0, 128))


def star(draw, cx, cy, r, colour, points=8):
    pts = []
    for i in range(points * 2):
        ang = math.pi * i / points - math.pi / 2
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(pts, fill=colour)


def icon(draw, kind, x, y, s, colour):
    """Draw a simple bold icon inside a square of side s at (x, y)."""
    cx, cy = x + s // 2, y + s // 2
    if kind == "chip":  # microchip: square with pins
        draw.rectangle([x + 10, y + 10, x + s - 10, y + s - 10], fill=colour)
        draw.rectangle([cx - 7, cy - 7, cx + 7, cy + 7], fill=BG)
        for px in (x + 16, cx, x + s - 16):
            draw.line([(px, y + 2), (px, y + 10)], fill=colour, width=4)
            draw.line([(px, y + s - 10), (px, y + s - 2)], fill=colour, width=4)
        for py in (y + 16, cy, y + s - 16):
            draw.line([(x + 2, py), (x + 10, py)], fill=colour, width=4)
            draw.line([(x + s - 10, py), (x + s - 2, py)], fill=colour, width=4)
    elif kind == "ban":  # blacklist: circle with slash
        draw.ellipse([x + 4, y + 4, x + s - 4, y + s - 4], outline=colour, width=6)
        draw.line([(x + 12, y + s - 12), (x + s - 12, y + 12)], fill=colour, width=6)
    elif kind == "talks":  # peace talks: two speech bubbles
        draw.rectangle([x + 4, y + 8, x + s - 16, y + 30], fill=colour)
        draw.polygon([(x + 12, y + 30), (x + 20, y + 42), (x + 24, y + 30)], fill=colour)
        draw.rectangle([x + 16, y + 26, x + s - 4, y + 46], outline=colour, width=4)
    elif kind == "ship":  # warship at sea
        draw.polygon([(x + 6, y + s - 14), (x + s - 6, y + s - 14),
                      (x + s - 14, y + s - 34), (x + 14, y + s - 34)],
                     fill=colour)
        draw.rectangle([cx - 8, y + 8, cx + 8, y + s - 34], fill=colour)
        draw.line([(cx, y + 8), (cx + 10, y - 2)], fill=RED, width=4)
    elif kind == "flame":  # factory fire
        star(draw, cx, cy, s // 2 - 2, colour, 8)
        draw.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=BG)
    elif kind == "jet":  # fighter jet
        draw.polygon([(cx, y + 2), (cx + 10, y + s - 10), (cx, y + s - 22),
                      (cx - 10, y + s - 10)], fill=colour)
        draw.polygon([(x + 4, y + s - 16), (cx, y + s - 30), (cx, y + s - 14)],
                     fill=colour)
        draw.polygon([(x + s - 4, y + s - 16), (cx, y + s - 30), (cx, y + s - 14)],
                     fill=colour)
    elif kind == "leaf":  # climate talks: leaf / globe
        draw.ellipse([x + 4, y + 4, x + s - 4, y + s - 4], outline=colour, width=5)
        draw.line([(x + 8, cy), (x + s - 8, cy)], fill=colour, width=4)
        draw.arc([x + 14, y + 4, x + s - 14, y + s - 4], 270, 90, fill=colour, width=4)
    elif kind == "warn":  # warning triangle
        draw.polygon([(cx, y + 4), (x + s - 4, y + s - 6), (x + 4, y + s - 6)],
                     fill=colour)
        draw.rectangle([cx - 3, y + 18, cx + 3, y + 34], fill=BG)
        draw.ellipse([cx - 3, y + 38, cx + 3, y + 44], fill=BG)


STORIES = [
    # (icon, chip colour, headline, fact line)
    ("chip", (94, 234, 212),
     "HUANG IS BACK AT NVIDIA",
     "Shares surge 31% as Jensen Huang returns as CEO"),
    ("ban", (255, 69, 58),
     "US BLACKLISTS MEGASPEED",
     "Singapore firm at centre of Nvidia spy scandal put on Entity List"),
    ("talks", (96, 165, 250),
     "ZELENSKY SEEKS FOUR-WAY TALKS",
     "Urges Ukraine, Russia, US and Europe to meet 'as soon as possible'"),
    ("ship", (255, 179, 71),
     "UKRAINE SAYS IT SANK RUSSIAN SHIP",
     "Zelensky: drone strike sank a Russian warship off Libya"),
    ("flame", (255, 69, 58),
     "24 KILLED IN INDONESIA FACTORY FIRE",
     "Blaze rips through a candy factory; rescuers search for missing"),
    ("jet", (96, 165, 250),
     "KOREA SCRAMBLES JETS",
     "Russian aircraft enter South Korea's air defence zone; islanders shelter"),
    ("leaf", (163, 230, 53),
     "COP31 TALKS STALL IN TURKIYE",
     "Climate summit deadlocked on fossil fuels and finance"),
    ("warn", (255, 179, 71),
     "TRUMP WARNS IRAN OF 'TRAUMATIC' OUTCOME",
     "Warns of consequences if no nuclear deal; Iran warns on US blockade"),
]


def rows(draw):
    y0 = 408
    rh = 77
    head = font(FONT_BOLD, 27)
    fact = font(FONT_REG, 19)
    chip = font(FONT_BOLD, 28)
    for i, (kind, colour, headline, factline) in enumerate(STORIES):
        y = y0 + i * rh
        draw.rectangle([0, y, W, y + rh], fill=ROW_A if i % 2 == 0 else ROW_B)
        draw.rectangle([0, y, W, y + 1], fill=LINE)
        # number chip
        draw.ellipse([16, y + 15, 62, y + 61], fill=colour)
        num = str(i + 1)
        tw = draw.textlength(num, font=chip)
        draw.text((39 - tw / 2, y + 17), num, font=chip, fill=(10, 10, 10))
        # icon
        icon(draw, kind, 78, y + 13, 50, colour)
        # text
        draw.text((142, y + 6), headline, font=head, fill=WHITE)
        draw.text((142, y + 40), factline, font=fact, fill=FADE)


def main():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    banner(draw)
    hero(img)
    rows(ImageDraw.Draw(img))
    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    print(out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
