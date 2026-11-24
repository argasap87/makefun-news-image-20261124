#!/usr/bin/env python3
"""Rebuild entry.png for make.fun news-image-20261124.

A newspaper front page for Tuesday 24 November 2026: a dated masthead,
one AI-generated hero photograph of a cracked globe over a glowing
horizon, and eight numbered story rows, each with a coloured disc, a
small geometric pictogram, a bold headline and one verified fact line.

The eight stories are baked into STORIES below (headline + deck line).
The picture is assembled only from assets/hero.webp and the Pillow
drawing primitives in this file, so re-running it is deterministic:
same input bytes, same output bytes. Run with `python3 draw.py`
from the repository root; it writes entry.png (and out/entry.png).
"""

from __future__ import annotations

import math
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
HERO_PATH = ROOT / "assets" / "hero.webp"
OUT_PATH = ROOT / "entry.png"

CANVAS = 1024
MASTHEAD_H = 116          # dark banner at the top
RULE_H = 4                # red rule under the masthead
HERO_H = 292              # hero photograph band
ROW_COUNT = 8

# Palette -----------------------------------------------------------------
INK = (8, 12, 24)         # page background, near-black navy
MASTHEAD_BG = (46, 16, 12)  # deep oxblood banner
RULE = (214, 48, 32)      # signal red rule
AMBER = (240, 178, 74)    # masthead dateline
PAPER = (244, 246, 248)   # headline white
DECK = (176, 186, 198)    # deck-line grey
DIVIDER = (52, 62, 78)    # hairline between rows
ROW_A = (13, 20, 36)      # alternating row tints
ROW_B = (17, 26, 44)

# One accent colour per story, reused for its disc and pictogram.
ACCENTS = [
    (64, 224, 200),   # 1 teal
    (240, 74, 66),    # 2 red
    (96, 165, 250),   # 3 blue
    (245, 183, 84),   # 4 amber
    (240, 74, 66),    # 5 red
    (96, 165, 250),   # 6 blue
    (140, 210, 90),   # 7 green
    (245, 183, 84),   # 8 amber
]

STORIES = [
    ("HUANG IS BACK AT NVIDIA",
     "Reinstated 12 days after resigning; shares close up 31%"),
    ("US BLACKLISTS MEGASPEED",
     "Singapore firm at centre of Nvidia spy scandal put on Entity List"),
    ("ZELENSKY SEEKS FOUR-WAY TALKS",
     "Urges Ukraine, Russia, US and Europe to meet 'as soon as possible'"),
    ("UKRAINE SAYS IT SANK RUSSIAN SHIP",
     "Seven sea drones sank the corvette Merkury off Benghazi"),
    ("24 KILLED IN INDONESIA FACTORY FIRE",
     "Blaze at Milkita candy plant in Banten; 24 dead, about 30 missing"),
    ("KOREA SCRAMBLES JETS",
     "Russian planes near Ulleung island; shelter alert lifted in 3 minutes"),
    ("COP31 TALKS STALL IN TURKIYE",
     "Climate summit deadlocked on fossil fuels and finance"),
    ("TRUMP WARNS IRAN OF 'TRAUMATIC' OUTCOME",
     "Warns of consequences if no nuclear deal; Iran warns on US blockade"),
]

MASTHEAD_TITLE = "ONE TUESDAY, EIGHT FAULT LINES"
MASTHEAD_DATE = "TUESDAY  24  NOVEMBER  2026  \u00b7  AS REPORTED"


# Fonts -------------------------------------------------------------------
def _font(bold: bool, size: int) -> ImageFont.FreeTypeFont:
    """Pick a DejaVu face, falling back to Pillow's built-in bitmap font."""
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    for base in ("/usr/share/fonts/truetype/dejavu",
                 "/usr/share/fonts/truetype/liberation"):
        path = os.path.join(base, name)
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _fit(draw: ImageDraw.ImageDraw, text: str, bold: bool,
         start: int, limit: int) -> ImageFont.FreeTypeFont:
    """Largest font size (down from `start`) that fits `text` in `limit` px."""
    size = start
    while size > 10:
        font = _font(bold, size)
        if draw.textlength(text, font=font) <= limit:
            return font
        size -= 1
    return _font(bold, 10)


# Pictograms ---------------------------------------------------------------
# Every glyph is drawn from scratch with plain PIL shapes inside a
# 44x44 box whose top-left corner is (x, y). One glyph per story.
def _glyph_chip(d: ImageDraw.ImageDraw, x: int, y: int, c) -> None:
    d.rectangle([x + 10, y + 10, x + 34, y + 34], outline=c, width=4)
    d.rectangle([x + 18, y + 18, x + 26, y + 26], fill=c)
    for px in (14, 22, 30):
        d.line([x + px, y + 2, x + px, y + 10], fill=c, width=3)
        d.line([x + px, y + 34, x + px, y + 42], fill=c, width=3)
        d.line([x + 2, y + px, x + 10, y + px], fill=c, width=3)
        d.line([x + 34, y + px, x + 42, y + px], fill=c, width=3)


def _glyph_ban(d: ImageDraw.ImageDraw, x: int, y: int, c) -> None:
    d.ellipse([x + 4, y + 4, x + 40, y + 40], outline=c, width=5)
    d.line([x + 10, y + 34, x + 34, y + 10], fill=c, width=5)


def _glyph_talks(d: ImageDraw.ImageDraw, x: int, y: int, c) -> None:
    d.rounded_rectangle([x + 4, y + 6, x + 28, y + 26], radius=5,
                        outline=c, width=4)
    d.rounded_rectangle([x + 18, y + 20, x + 40, y + 38], radius=5,
                        outline=c, width=4)
    d.polygon([(x + 10, y + 26), (x + 10, y + 34), (x + 18, y + 26)], fill=c)


def _glyph_ship(d: ImageDraw.ImageDraw, x: int, y: int, c) -> None:
    d.polygon([(x + 6, y + 26), (x + 38, y + 26), (x + 30, y + 40),
               (x + 14, y + 40)], fill=c)
    d.line([x + 22, y + 6, x + 22, y + 26], fill=c, width=4)
    d.polygon([(x + 22, y + 8), (x + 34, y + 20), (x + 22, y + 20)], fill=c)


def _glyph_fire(d: ImageDraw.ImageDraw, x: int, y: int, c) -> None:
    cx, cy = x + 22, y + 22
    pts = []
    for i in range(16):
        ang = math.pi * i / 8
        r = 20 if i % 2 == 0 else 8
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    d.polygon(pts, fill=c)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=INK)


def _glyph_jet(d: ImageDraw.ImageDraw, x: int, y: int, c) -> None:
    d.polygon([(x + 22, y + 2), (x + 30, y + 24), (x + 40, y + 30),
               (x + 26, y + 32), (x + 22, y + 42), (x + 18, y + 32),
               (x + 4, y + 30), (x + 14, y + 24)], fill=c)


def _glyph_globe(d: ImageDraw.ImageDraw, x: int, y: int, c) -> None:
    d.ellipse([x + 4, y + 4, x + 40, y + 40], outline=c, width=4)
    d.ellipse([x + 16, y + 4, x + 28, y + 40], outline=c, width=3)
    d.line([x + 4, y + 22, x + 40, y + 22], fill=c, width=3)
    d.arc([x + 4, y + 10, x + 40, y + 34], 200, 340, fill=c, width=3)


def _glyph_warn(d: ImageDraw.ImageDraw, x: int, y: int, c) -> None:
    d.polygon([(x + 22, y + 4), (x + 42, y + 38), (x + 2, y + 38)], fill=c)
    d.rectangle([x + 20, y + 16, x + 24, y + 28], fill=INK)
    d.ellipse([x + 19, y + 31, x + 25, y + 37], fill=INK)


GLYPHS = [_glyph_chip, _glyph_ban, _glyph_talks, _glyph_ship,
          _glyph_fire, _glyph_jet, _glyph_globe, _glyph_warn]


# Layout --------------------------------------------------------------------
def build() -> Image.Image:
    page = Image.new("RGB", (CANVAS, CANVAS), INK)
    d = ImageDraw.Draw(page)

    # --- Masthead ------------------------------------------------------
    d.rectangle([0, 0, CANVAS, MASTHEAD_H], fill=MASTHEAD_BG)
    title_font = _fit(d, MASTHEAD_TITLE, True, 58, CANVAS - 48)
    d.text((24, 14), MASTHEAD_TITLE, font=title_font, fill=PAPER)
    date_font = _fit(d, MASTHEAD_DATE, True, 34, CANVAS - 48)
    d.text((24, 72), MASTHEAD_DATE, font=date_font, fill=AMBER)
    d.rectangle([0, MASTHEAD_H, CANVAS, MASTHEAD_H + RULE_H], fill=RULE)

    # --- Hero photograph ----------------------------------------------
    # Centre-crop the 2:1 hero to the band, then paste it edge to edge.
    hero = Image.open(HERO_PATH).convert("RGB")
    hw, hh = hero.size
    target_ratio = CANVAS / HERO_H
    src_ratio = hw / hh
    if src_ratio > target_ratio:  # too wide: trim the sides
        crop_w = int(hh * target_ratio)
        left = (hw - crop_w) // 2
        hero = hero.crop((left, 0, left + crop_w, hh))
    else:  # too tall: trim top and bottom
        crop_h = int(hw / target_ratio)
        top = (hh - crop_h) // 2
        hero = hero.crop((0, top, hw, top + crop_h))
    hero = hero.resize((CANVAS, HERO_H), Image.LANCZOS)
    page.paste(hero, (0, MASTHEAD_H + RULE_H))

    # --- Story rows -----------------------------------------------------
    rows_top = MASTHEAD_H + RULE_H + HERO_H
    row_h = (CANVAS - rows_top) // ROW_COUNT
    text_x = 148
    text_w = CANVAS - text_x - 24
    for i, (headline, deck) in enumerate(STORIES):
        top = rows_top + i * row_h
        d.rectangle([0, top, CANVAS, top + row_h],
                    fill=ROW_A if i % 2 == 0 else ROW_B)
        if i:
            d.line([0, top, CANVAS, top], fill=DIVIDER, width=1)

        accent = ACCENTS[i]
        # Number disc.
        cx, cy, r = 38, top + row_h // 2, 24
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=accent)
        num_font = _font(True, 30)
        num = str(i + 1)
        nw = d.textlength(num, font=num_font)
        nh = num_font.getbbox(num)[3]
        d.text((cx - nw / 2, cy - nh / 2 - 2), num, font=num_font, fill=INK)

        # Pictogram.
        GLYPHS[i](d, 78, top + (row_h - 44) // 2, accent)

        # Headline + deck line.
        head_font = _fit(d, headline, True, 31, text_w)
        d.text((text_x, top + 9), headline, font=head_font, fill=PAPER)
        deck_font = _fit(d, deck, False, 22, text_w)
        d.text((text_x, top + row_h - 30), deck, font=deck_font, fill=DECK)

    return page


def main() -> None:
    page = build()
    page.save(OUT_PATH, format="PNG")
    out_dir = ROOT / "out"
    out_dir.mkdir(exist_ok=True)
    page.save(out_dir / "entry.png", format="PNG")
    print(f"wrote {OUT_PATH} ({OUT_PATH.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
