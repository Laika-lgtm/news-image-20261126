#!/usr/bin/env python3
"""Render the news-image-20261126 round-2 front page (1024x1024 PNG).

Draws a one-page newspaper: masthead, region colour bar, 3 hero scenes,
10 medium scenes, DATE CHECK box, world map with 13 numbered pins,
numbered list 14-36, UTC strip and footer. All scenes are drawn
illustrations (PIL primitives), not photographs. Deterministic: no
randomness, no time, no network.
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
MARGIN = 12
CW = W - 2 * MARGIN

CREAM = (247, 242, 231)
PAPER = (255, 255, 255)
INK = (17, 17, 17)
GREY = (90, 90, 90)
LIGHT_GREY = (120, 118, 110)
RED = (176, 30, 30)
DARK_RED = (139, 26, 26)
NAVY = (27, 42, 74)
NAVY_DARK = (22, 35, 63)
GOLD = (201, 162, 39)
BORDER = (216, 210, 192)
SEA = (217, 228, 230)
LAND = (169, 188, 160)

BADGE_FILL = {
    "OFFICIAL": (20, 83, 45),
    "CONFIRMED": (27, 42, 74),
    "REPORTED": (71, 85, 105),
    "CLAIM": (185, 28, 28),
    "ONGOING": (146, 64, 14),
}

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
_FONTS = {}


def font(size, bold=False, serif=False):
    key = (size, bold, serif)
    if key in _FONTS:
        return _FONTS[key]
    if serif:
        name = "DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf"
    else:
        name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    path = os.path.join(FONT_DIR, name)
    try:
        f = ImageFont.truetype(path, size)
    except OSError:
        f = ImageFont.load_default()
    _FONTS[key] = f
    return f


def wrap(draw, s, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = s.split()
    if not words:
        return [""]
    lines = []
    cur = words[0]
    for word in words[1:]:
        trial = cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


def wrap_max(draw, s, fnt, max_w, max_lines):
    """Wrap to at most max_lines; truncate the last line with an ellipsis."""
    lines = wrap(draw, s, fnt, max_w)
    if len(lines) <= max_lines:
        return lines
    lines = lines[:max_lines]
    last = lines[-1]
    while last and draw.textlength(last + "…", font=fnt) > max_w:
        last = last.rsplit(" ", 1)[0] if " " in last else last[:-1]
    lines[-1] = last + "…"
    return lines


def draw_lines(draw, x, y, lines, fnt, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def badge(draw, x, y, text, fill):
    """Small status badge; returns its width."""
    fnt = font(9, bold=True)
    tw = draw.textlength(text, font=fnt)
    w = int(tw) + 10
    h = 14
    draw.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=fill)
    draw.text((x + 5, y + 2), text, font=fnt, fill=(255, 255, 255))
    return w


def chip(draw, x, y, text, box_w):
    """White stat chip right-aligned inside a scene of width box_w."""
    fnt = font(10, bold=True)
    tw = draw.textlength(text, font=fnt)
    w = int(tw) + 12
    draw.rounded_rectangle(
        [x + box_w - w - 6, y, x + box_w - 6, y + 16], radius=3,
        fill=(255, 255, 255), outline=RED, width=1)
    draw.text((x + box_w - w, y + 2), text, font=fnt, fill=RED)
    return w


def number_circle(draw, x, y, n, d=22):
    draw.ellipse([x, y, x + d, y + d], fill=RED, outline=(255, 255, 255), width=2)
    fnt = font(12, bold=True)
    s = str(n)
    tw = draw.textlength(s, font=fnt)
    draw.text((x + (d - tw) / 2, y + 3), s, font=fnt, fill=(255, 255, 255))


# ---------------------------------------------------------------- scenes
# Each scene draws into box (x, y, w, h) on draw. Flat, print-style
# illustrations. All coordinates are integers and deterministic.

def scene_parade(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 38, 66))
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(18, 24, 46))
    for bx, bw, bh in ((8, 34, 30), (52, 22, 44), (88, 40, 26), (140, 26, 50),
                        (180, 34, 34), (228, 24, 46), (268, 36, 28)):
        d.rectangle([x + bx, y + h - 26 - bh, x + bx + bw, y + h - 26],
                    fill=(12, 16, 34))
    for cx, cy, col in ((70, 52, (214, 48, 49)), (160, 40, (37, 99, 235)),
                         (250, 56, (217, 160, 32))):
        d.ellipse([x + cx - 20, y + cy - 16, x + cx + 20, y + cy + 16], fill=col)
        d.line([x + cx, y + cy + 16, x + cx, y + h - 26], fill=(200, 200, 200), width=1)
    for rx in range(12, w, 26):
        d.line([x + rx, y + 6, x + rx - 5, y + 18], fill=(180, 190, 220), width=1)


def scene_mumbai(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 34, 58))
    for sx in (30, 90, 150, 210, 270, 310):
        d.ellipse([x + sx, y + 10, x + sx + 2, y + 12], fill=(255, 255, 255))
    d.rectangle([x + w // 2 - 46, y + 34, x + w // 2 + 46, y + h - 30],
                fill=(176, 150, 110))
    d.pieslice([x + w // 2 - 46, y + 2, x + w // 2 + 46, y + 66],
               start=180, end=360, fill=(176, 150, 110))
    d.rectangle([x + w // 2 - 20, y + 66, x + w // 2 + 20, y + h - 30],
                fill=(24, 34, 58))
    d.pieslice([x + w // 2 - 20, y + 46, x + w // 2 + 20, y + 86],
               start=180, end=360, fill=(24, 34, 58))
    for cx in (60, 130, 200, 270):
        d.rectangle([x + cx - 4, y + h - 26, x + cx + 4, y + h - 12],
                    fill=(240, 230, 200))
        d.ellipse([x + cx - 5, y + h - 36, x + cx + 5, y + h - 24],
                  fill=(255, 196, 66))


def scene_chess(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 214, 170))
    sq = min(w, h) // 8
    bx = x + (w - sq * 8) // 2
    by = y + (h - sq * 8) // 2
    for r in range(8):
        for c in range(8):
            if (r + c) % 2 == 0:
                d.rectangle([bx + c * sq, by + r * sq,
                             bx + (c + 1) * sq, by + (r + 1) * sq],
                            fill=(146, 110, 72))
    for (cc, rr, col, out) in ((2, 5, (255, 255, 255), (60, 60, 60)),
                               (5, 2, (30, 30, 30), (0, 0, 0))):
        cx = bx + cc * sq + sq // 2
        cy = by + rr * sq + sq // 2
        rad = sq // 2 - 2
        d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=col,
                  outline=out, width=2)
        d.polygon([(cx - rad, cy - rad // 2), (cx, cy - rad - 3),
                   (cx + rad, cy - rad // 2)], fill=col, outline=out)


def scene_fire(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(52, 24, 18))
    d.polygon([(x + 30, y + h - 30), (x + 70, y + 20), (x + 100, y + h - 30)],
              fill=(234, 88, 12))
    d.polygon([(x + 90, y + h - 30), (x + 130, y + 8), (x + 170, y + h - 30)],
              fill=(220, 38, 38))
    d.polygon([(x + 120, y + h - 30), (x + 150, y + 30), (x + 180, y + h - 30)],
              fill=(250, 204, 21))
    d.ellipse([x + 40, y + 8, x + 90, y + 30], fill=(120, 120, 120))
    d.ellipse([x + 110, y + 2, x + 160, y + 22], fill=(100, 100, 100))
    d.rectangle([x + 20, y + h - 34, x + 130, y + h - 18], fill=(20, 20, 20))
    d.rectangle([x + 130, y + h - 30, x + 165, y + h - 18], fill=(40, 40, 40))
    d.rectangle([x + 140, y + h - 28, x + 158, y + h - 20], fill=(180, 220, 240))
    for wx in (40, 90, 150):
        d.ellipse([x + wx - 7, y + h - 16, x + wx + 7, y + h - 2], fill=(0, 0, 0),
                  outline=(200, 200, 200), width=1)


def scene_refinery(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(64, 38, 66))
    d.rectangle([x, y + h - 34, x + w, y + h], fill=(30, 20, 34))
    for bx, bw, bh in ((16, 14, 58), (44, 18, 76), (76, 12, 50), (120, 16, 66)):
        d.rectangle([x + bx, y + h - 34 - bh, x + bx + bw, y + h - 34],
                    fill=(24, 24, 30))
        d.ellipse([x + bx + 2, y + h - 40 - bh, x + bx + bw - 2, y + h - 28 - bh],
                  fill=(250, 160, 40))
    d.rectangle([x + 150, y + 30, x + 158, y + h - 34], fill=(24, 24, 30))
    d.polygon([(x + 146, y + 30), (x + 162, y + 30), (x + 154, y + 14)],
              fill=(250, 120, 30))
    d.ellipse([x + 168, y + 10, x + 196, y + 26], fill=(150, 150, 150))
    d.line([x, y + h - 34, x + w, y + h - 34], fill=(90, 90, 90), width=2)


def scene_island(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(135, 190, 220))
    d.ellipse([x + 150, y + 10, x + 166, y + 26], fill=(255, 240, 160))
    d.rectangle([x, y + h - 34, x + w, y + h], fill=(40, 110, 160))
    d.polygon([(x + 30, y + h - 34), (x + 100, y + h - 58), (x + 170, y + h - 34)],
              fill=(46, 125, 70))
    d.rectangle([x + 118, y + h - 66, x + 124, y + h - 34], fill=(101, 67, 50))
    for dx, dy in ((-26, -12), (8, -14), (-18, -22), (16, -22)):
        d.line([x + 121, y + h - 66, x + 121 + dx, y + h - 66 + dy],
               fill=(34, 100, 60), width=3)
    for fx, col in ((36, (0, 47, 108)), (66, (0, 82, 165))):
        d.rectangle([x + fx, y + 8, x + fx + 2, y + 34], fill=(120, 90, 60))
        d.rectangle([x + fx + 2, y + 8, x + fx + 26, y + 22], fill=col)


def scene_tariffs(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 238, 228))
    d.line([x + 14, y + h - 16, x + w - 14, y + h - 16], fill=(60, 60, 60), width=2)
    for i, (bh, col, lab) in enumerate(((26, (37, 99, 235), "15%"),
                                        (44, (217, 119, 6), "20%"),
                                        (62, (185, 28, 28), "40%"))):
        bx = x + 30 + i * 56
        d.rectangle([bx, y + h - 16 - bh, bx + 34, y + h - 16], fill=col)
        fnt = font(11, bold=True)
        d.text((bx + 4, y + h - 34 - bh), lab, font=fnt, fill=INK)
    fnt = font(12, bold=True)
    d.text((x + 14, y + 6), "$  TARIFFS", font=fnt, fill=INK)


def scene_factory(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 230, 208))
    d.rectangle([x + 18, y + h - 44, x + w - 18, y + h - 14], fill=(120, 90, 70))
    for i in range(4):
        bx = x + 24 + i * 42
        d.polygon([(bx, y + h - 44), (bx + 20, y + h - 62),
                   (bx + 40, y + h - 44)], fill=(90, 66, 50))
    d.rectangle([x + 30, y + h - 38, x + 52, y + h - 24], fill=(180, 220, 240))
    d.rectangle([x + 66, y + h - 38, x + 88, y + h - 24], fill=(180, 220, 240))
    d.polygon([(x + w - 62, y + h - 20), (x + w - 30, y + h - 52),
               (x + w - 30, y + h - 40), (x + w - 50, y + h - 20)],
              fill=(22, 163, 74))
    d.polygon([(x + w - 30, y + h - 52), (x + w - 18, y + h - 40),
               (x + w - 30, y + h - 40)], fill=(22, 163, 74))


def scene_rocket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(10, 12, 26))
    for sx, sy in ((20, 14), (60, 30), (120, 10), (170, 26), (90, 44), (150, 48)):
        d.ellipse([x + sx, y + sy, x + sx + 3, y + sy + 3], fill=(255, 255, 255))
    d.ellipse([x - 40, y + h - 30, x + w + 40, y + h + 60], fill=(37, 99, 235))
    d.ellipse([x - 20, y + h - 22, x + w + 20, y + h + 40], fill=(96, 165, 250))
    cx = x + w // 2
    d.polygon([(cx - 12, y + 26), (cx, y + 8), (cx + 12, y + 26)], fill=(185, 28, 28))
    d.rectangle([cx - 12, y + 26, cx + 12, y + h - 46], fill=(240, 240, 240))
    d.rectangle([cx - 12, y + 44, cx + 12, y + 56], fill=(185, 28, 28))
    d.ellipse([cx - 6, y + 34, cx + 6, y + 46], fill=(135, 190, 220),
              outline=(60, 60, 60), width=1)
    d.polygon([(cx - 12, y + h - 46), (cx - 22, y + h - 30), (cx - 12, y + h - 36)],
              fill=(185, 28, 28))
    d.polygon([(cx + 12, y + h - 46), (cx + 22, y + h - 30), (cx + 12, y + h - 36)],
              fill=(185, 28, 28))
    d.polygon([(cx - 7, y + h - 46), (cx, y + h - 22), (cx + 7, y + h - 46)],
              fill=(250, 160, 40))
    d.polygon([(cx - 4, y + h - 46), (cx, y + h - 30), (cx + 4, y + h - 46)],
              fill=(250, 204, 21))


def scene_leak(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(228, 228, 222))
    d.rectangle([x + 24, y + 10, x + 96, y + h - 10], fill=(255, 255, 255),
                outline=(150, 150, 150), width=1)
    for i, lw in enumerate((56, 60, 44, 58, 30)):
        d.rectangle([x + 32, y + 22 + i * 12, x + 32 + lw, y + 26 + i * 12],
                    fill=(120, 120, 120))
    d.rectangle([x + 108, y + 22, x + 188, y + 44], outline=RED, width=3)
    fnt = font(13, bold=True)
    d.text((x + 116, y + 25), "LEAKED", font=fnt, fill=RED)
    for i, bh in enumerate((18, 30, 24, 40)):
        bx = x + 112 + i * 20
        d.rectangle([bx, y + h - 16 - bh, bx + 12, y + h - 16], fill=(27, 42, 74))
    d.line([x + 108, y + h - 16, x + 192, y + h - 16], fill=(60, 60, 60), width=1)


def scene_storm(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(58, 74, 96))
    d.ellipse([x + 30, y + 8, x + 110, y + 44], fill=(160, 170, 180))
    d.ellipse([x + 80, y + 2, x + 160, y + 40], fill=(140, 150, 160))
    d.ellipse([x + 120, y + 12, x + 180, y + 46], fill=(160, 170, 180))
    d.polygon([(x + 100, y + 44), (x + 88, y + 66), (x + 98, y + 66),
               (x + 84, y + 88), (x + 108, y + 60), (x + 98, y + 60),
               (x + 112, y + 44)], fill=(250, 204, 21))
    for rx in range(16, w, 22):
        d.line([x + rx, y + 56, x + rx - 4, y + 72], fill=(180, 200, 220), width=1)
        d.line([x + rx, y + 76, x + rx - 4, y + 92], fill=(180, 200, 220), width=1)
    d.arc([x + 14, y + h - 26, x + 54, y + h - 2], start=180, end=360,
          fill=(200, 210, 220), width=2)


def scene_europe(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(0, 51, 153))
    cx, cy, r = x + w // 2, y + h // 2 - 4, 30
    for i in range(12):
        a = math.pi * 2 * i / 12 - math.pi / 2
        sx, sy = cx + int(r * math.cos(a)), cy + int(r * math.sin(a))
        d.polygon([(sx, sy - 5), (sx + 2, sy - 1), (sx + 5, sy), (sx + 2, sy + 2),
                   (sx, sy + 5), (sx - 2, sy + 2), (sx - 5, sy), (sx - 2, sy - 1)],
                  fill=(255, 204, 0))
    d.rectangle([x, y + h - 18, x + w, y + h], fill=(20, 20, 40))
    for bx, bw, bh in ((20, 30, 12), (70, 22, 16), (120, 34, 10), (160, 24, 14)):
        d.rectangle([x + bx, y + h - 18 - bh, x + bx + bw, y + h - 18],
                    fill=(40, 40, 60))


def scene_fx(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 238, 228))
    for gy in (16, 34, 52, 70):
        d.line([x + 12, y + gy, x + w - 12, y + gy], fill=(210, 208, 196), width=1)
    pts = [(x + 16, y + 18), (x + 52, y + 26), (x + 88, y + 24),
           (x + 124, y + 44), (x + 160, y + 52), (x + 184, y + 78)]
    d.line(pts, fill=(185, 28, 28), width=3, joint="curve")
    for px, py in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(185, 28, 28))
    fnt = font(13, bold=True)
    d.text((x + 14, y + h - 20), "$", font=fnt, fill=INK)
    d.text((x + w - 26, y + h - 20), "₦", font=fnt, fill=INK)


SCENES = {
    "parade": scene_parade,
    "mumbai": scene_mumbai,
    "chess": scene_chess,
    "fire": scene_fire,
    "refinery": scene_refinery,
    "island": scene_island,
    "tariffs": scene_tariffs,
    "factory": scene_factory,
    "rocket": scene_rocket,
    "leak": scene_leak,
    "storm": scene_storm,
    "europe": scene_europe,
    "fx": scene_fx,
}

DESIGN_W, DESIGN_H = 320, 112


def draw_scene_box(img, name, x, y, w, h):
    """Render a scene at its 320x112 design size, then scale it into the
    target box. Guarantees no scene ever paints outside its box."""
    tmp = Image.new("RGB", (DESIGN_W, DESIGN_H))
    td = ImageDraw.Draw(tmp)
    SCENES[name](td, 0, 0, DESIGN_W, DESIGN_H)
    if (w, h) != (DESIGN_W, DESIGN_H):
        tmp = tmp.resize((w, h), Image.LANCZOS)
    img.paste(tmp, (x, y))


# ---------------------------------------------------------------- layout

REGION_COLORS = {
    "NORTH AMERICA": "#1B2A4A",
    "SOUTH ASIA": "#D97706",
    "EUROPE": "#2563EB",
    "MIDDLE EAST": "#0F766E",
    "AFRICA": "#C2410C",
    "EAST ASIA": "#B91C1C",
    "OCEANIA": "#15803D",
    "SOUTH AMERICA": "#7E22CE",
    "WORLD": "#475569",
}


def hex2rgb(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


CONTINENTS = [
    [(-168, 66), (-150, 70), (-130, 71), (-115, 73), (-100, 74), (-90, 80),
     (-80, 76), (-70, 70), (-60, 60), (-55, 52), (-60, 46), (-68, 44),
     (-74, 40), (-76, 36), (-80, 32), (-81, 26), (-84, 30), (-90, 21),
     (-95, 18), (-92, 15), (-86, 13), (-82, 9), (-78, 8), (-84, 10),
     (-90, 14), (-95, 16), (-100, 18), (-105, 21), (-110, 24), (-114, 29),
     (-120, 34), (-124, 42), (-124, 49), (-132, 56), (-145, 60), (-158, 58),
     (-165, 60)],
    [(-55, 60), (-45, 60), (-40, 64), (-32, 68), (-22, 70), (-20, 74),
     (-30, 76), (-45, 77), (-58, 74), (-60, 68)],
    [(-79, 9), (-74, 11), (-64, 10), (-54, 6), (-50, 0), (-44, -3),
     (-35, -8), (-38, -15), (-41, -23), (-48, -28), (-56, -35), (-64, -41),
     (-68, -50), (-70, -54), (-73, -48), (-73, -38), (-71, -30), (-70, -20),
     (-76, -14), (-80, -6), (-81, 0)],
    [(-17, 15), (-13, 27), (-6, 33), (0, 36), (10, 37), (20, 32), (30, 31),
     (34, 28), (37, 22), (40, 15), (44, 11), (48, 11), (51, 12), (46, 4),
     (42, -2), (40, -10), (36, -18), (32, -26), (27, -33), (20, -35),
     (16, -28), (12, -18), (9, -1), (9, 4), (-8, 5), (-13, 9), (-16, 12)],
    [(-10, 36), (-9, 43), (-2, 48), (2, 51), (6, 54), (8, 57), (12, 56),
     (18, 56), (21, 55), (24, 59), (28, 61), (30, 64), (32, 70), (38, 68),
     (46, 68), (54, 69), (62, 70), (70, 72), (78, 73), (88, 75), (100, 76),
     (112, 74), (124, 73), (135, 72), (146, 72), (158, 70), (170, 67),
     (178, 65), (170, 61), (162, 57), (158, 53), (150, 59), (142, 50),
     (140, 40), (134, 34), (130, 32), (127, 35), (124, 38), (121, 32),
     (118, 26), (110, 21), (108, 12), (105, 9), (101, 7), (98, 12),
     (95, 16), (92, 21), (89, 22), (86, 20), (81, 15), (78, 8), (75, 12),
     (73, 18), (70, 21), (66, 25), (61, 25), (57, 26), (54, 27), (51, 29),
     (49, 30), (45, 29), (42, 27), (39, 24), (38, 21), (35, 28), (33, 31),
     (30, 36), (27, 37), (24, 36), (21, 39), (19, 41), (15, 44), (12, 44),
     (8, 44), (4, 44), (0, 40), (-2, 37), (-6, 36)],
    [(113, -22), (114, -30), (115, -34), (122, -34), (129, -32), (134, -33),
     (137, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27),
     (150, -23), (146, -19), (142, -11), (137, -12), (132, -12), (127, -14),
     (122, -17), (118, -20)],
    [(109, 1), (113, 4), (117, 6), (119, 1), (117, -3), (112, -3), (109, -1)],
    [(95, 5), (98, 3), (101, 0), (104, -3), (106, -6), (103, -5), (99, 0),
     (96, 4)],
    [(105, -6), (110, -7), (114, -8), (114, -9), (106, -8)],
    [(131, -1), (136, -2), (141, -3), (146, -6), (147, -9), (142, -8),
     (136, -6), (131, -3)],
    [(130, 31), (132, 33), (135, 34), (137, 35), (139, 36), (141, 39),
     (141, 42), (143, 44), (141, 45), (139, 41), (137, 38), (134, 35),
     (131, 33)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
     (-2, 50)],
    [(167, -45), (170, -42), (174, -39), (176, -38), (174, -41), (170, -43),
     (167, -46)],
]


def project(lon, lat, mx, my, mw, mh):
    """Equirectangular: lon -180..180, lat 85..-60."""
    px = mx + (lon + 180.0) / 360.0 * mw
    py = my + (85.0 - lat) / 145.0 * mh
    return (px, py)


def repel(points, min_d, iters=8):
    """Push overlapping points apart; deterministic fixed-order passes."""
    pts = [list(p) for p in points]
    for _ in range(iters):
        moved = False
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                dx = pts[j][0] - pts[i][0]
                dy = pts[j][1] - pts[i][1]
                d = math.hypot(dx, dy)
                if d < min_d:
                    if d < 0.01:
                        dx, dy, d = 1.0, 0.0, 1.0
                    push = (min_d - d) / 2.0
                    ux, uy = dx / d, dy / d
                    pts[i][0] -= ux * push
                    pts[i][1] -= uy * push
                    pts[j][0] += ux * push
                    pts[j][1] += uy * push
                    moved = True
        if not moved:
            break
    return [(p[0], p[1]) for p in pts]


def draw_masthead(d, meta):
    d.rectangle([0, 0, W, 5], fill=RED)
    title_f = font(40, bold=True, serif=True)
    d.text((MARGIN, 8), meta["title"], font=title_f, fill=INK)
    date_f = font(19, bold=True)
    dw = d.textlength(meta["date"], font=date_f)
    d.text((W - MARGIN - dw, 17), meta["date"], font=date_f, fill=NAVY)
    d.line([MARGIN, 52, W - MARGIN, 52], fill=NAVY, width=2)
    stat_f = font(15, bold=True)
    d.text((MARGIN, 57), meta["stat"], font=stat_f, fill=RED)
    cyc_f = font(13, bold=True)
    cw = d.textlength(meta["cycle"], font=cyc_f)
    d.text((W - MARGIN - cw, 59), meta["cycle"], font=cyc_f, fill=RED)


def draw_region_bar(d, regions, y):
    seg_w = CW // len(regions)
    x = MARGIN
    fnt = font(11, bold=True)
    for i, reg in enumerate(regions):
        w = CW - seg_w * (len(regions) - 1) if i == len(regions) - 1 else seg_w
        d.rectangle([x, y, x + w, y + 24], fill=hex2rgb(reg["color"]))
        label = "%s %d" % (reg["label"], reg["count"])
        tw = d.textlength(label, font=fnt)
        d.text((x + (w - tw) / 2, y + 5), label, font=fnt, fill=(255, 255, 255))
        x += w


def draw_hero(img, d, story, x, y):
    w, h = 330, 218
    d.rectangle([x, y, x + w, y + h], fill=PAPER, outline=BORDER, width=1)
    draw_scene_box(img, story["scene"], x + 1, y + 1, w - 2, 112)
    number_circle(d, x + 7, y + 7, story["n"])
    chip(d, x + 1, y + 112 - 22, story["chip"], w - 2)
    hl_f = font(21, bold=True, serif=True)
    hl = wrap_max(d, story["headline"], hl_f, w - 16, 2)
    draw_lines(d, x + 8, y + 118, hl, hl_f, INK, 23)
    dk_f = font(12)
    dk = wrap_max(d, story["deck"], dk_f, w - 16, 2)
    assert "…" not in "".join(hl + dk), "truncated hero text: %s" % story["n"]
    draw_lines(d, x + 8, y + 166, dk, dk_f, (50, 50, 50), 15)
    ft_f = font(9, bold=True)
    d.text((x + 8, y + 200), "%s · %s" % (story["region"], story["field"].upper()),
           font=ft_f, fill=GREY)
    src_f = font(9, bold=True)
    sw = d.textlength(story["source"], font=src_f)
    bw = badge(d, x + w - 8 - 62, y + 197, story["badge"],
               BADGE_FILL[story["badge"]])
    d.text((x + w - 8 - 62 - sw - 6, y + 200), story["source"], font=src_f,
           fill=INK)


def draw_medium(img, d, story, x, y):
    w, h = 196, 112
    d.rectangle([x, y, x + w, y + h], fill=PAPER, outline=BORDER, width=1)
    draw_scene_box(img, story["scene"], x + 1, y + 1, w - 2, 42)
    number_circle(d, x + 5, y + 5, story["n"], d=16)
    tag_f = font(8, bold=True)
    tag = story["region"]
    tw = d.textlength(tag, font=tag_f)
    tx = x + w - int(tw) - 12
    d.rectangle([tx, y + 1, x + w - 1, y + 15],
                fill=hex2rgb(REGION_COLORS[story["region"]]))
    d.text((tx + 4, y + 3), tag, font=tag_f, fill=(255, 255, 255))
    hl_f = font(13, bold=True)
    hl = wrap_max(d, story["headline"], hl_f, w - 10, 2)
    draw_lines(d, x + 5, y + 46, hl, hl_f, INK, 15)
    dk_f = font(10)
    dk = wrap_max(d, story["deck"], dk_f, w - 10, 2)
    assert "…" not in "".join(hl + dk), "truncated medium text: %s" % story["n"]
    draw_lines(d, x + 5, y + 76, dk, dk_f, (60, 60, 60), 11)
    src_f = font(9, bold=True)
    d.text((x + 5, y + 99), story["source"], font=src_f, fill=INK)
    badge(d, x + w - 8 - 60, y + 96, story["badge"], BADGE_FILL[story["badge"]])


def draw_datecheck(d, data, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=PAPER, outline=RED, width=2)
    t_f = font(13, bold=True)
    d.text((x + 10, y + 8), "DATE CHECK — READ THIS FIRST", font=t_f, fill=RED)
    i_f = font(10)
    intro = ("Every story above was first reported in the 25–26 Nov news cycle.",
             "These are NOT today's news:")
    draw_lines(d, x + 10, y + 30, list(intro), i_f, INK, 13)
    it_f = font(10)
    x_f = font(10, bold=True)
    col_w = (w - 20) // 2
    for i, item in enumerate(data["date_check"]):
        cx = x + 10 + (i // 5) * col_w
        cy = y + 62 + (i % 5) * 15
        d.text((cx, cy), "×", font=x_f, fill=RED)
        d.text((cx + 12, cy), item, font=it_f, fill=INK)
    ny_f = font(10, bold=True)
    ny = wrap_max(d, data["not_yet"], ny_f, w - 20, 2)
    draw_lines(d, x + 10, y + h - 34, ny, ny_f, RED, 13)


def draw_map(d, pins, x, y, w, h):
    t_f = font(12, bold=True)
    d.text((x, y), "WHERE IT HAPPENED — 13 STORIES PINNED", font=t_f, fill=NAVY)
    mx, my, mw, mh = x, y + 18, w, h - 18
    d.rectangle([mx, my, mx + mw, my + mh], fill=SEA)
    for poly in CONTINENTS:
        pts = [project(lon, lat, mx, my, mw, mh) for lon, lat in poly]
        d.polygon(pts, fill=LAND)
    true_pts = [project(p["lon"], p["lat"], mx, my, mw, mh) for p in pins]
    disp_pts = repel(true_pts, 18)
    for (tx, ty), (px, py), pin in zip(true_pts, disp_pts, pins):
        if math.hypot(px - tx, py - ty) > 4:
            d.line([tx, ty, px, py], fill=RED, width=1)
    for (px, py), pin in zip(disp_pts, pins):
        r = 8
        d.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                  outline=(255, 255, 255), width=2)
        n_f = font(9, bold=True)
        s = str(pin["n"])
        tw = d.textlength(s, font=n_f)
        d.text((px - tw / 2, py - 6), s, font=n_f, fill=(255, 255, 255))


def draw_also_on(d, listed, y):
    t_f = font(14, bold=True)
    d.text((MARGIN, y), "ALSO ON — THURSDAY 26 NOVEMBER", font=t_f, fill=NAVY)
    d.line([MARGIN, y + 20, W - MARGIN, y + 20], fill=NAVY, width=1)
    row_f = font(11)
    num_f = font(11, bold=True)
    src_f = font(10, bold=True)
    col1_x, col2_x = MARGIN, 516
    col_w = 492
    for i, item in enumerate(listed):
        cx = col1_x if i < 12 else col2_x
        cy = y + 26 + (i % 12) * 15
        num = "%d." % item["n"]
        d.text((cx, cy), num, font=num_f, fill=RED)
        nx = cx + d.textlength(num, font=num_f) + 4
        head = item["headline"]
        hw = d.textlength(head, font=row_f)
        d.text((nx, cy), head, font=row_f, fill=INK)
        d.text((nx + hw + 4, cy + 1), "— " + item["source"], font=src_f,
               fill=DARK_RED)
    return y + 26 + 12 * 15


def draw_utc(d, utc, y):
    d.rectangle([MARGIN, y, W - MARGIN, y + 32], fill=NAVY)
    lab_f = font(11, bold=True)
    lab = "THE DAY IN UTC"
    d.text((MARGIN + 8, y + 3), lab, font=lab_f, fill=GOLD)
    lw = d.textlength(lab, font=lab_f)
    e_f = font(11)
    off = MARGIN + 8 + lw + 10
    line1 = " · ".join(utc[:3])
    line2 = " · ".join(utc[3:])
    d.text((off, y + 3), line1, font=e_f, fill=(255, 255, 255))
    d.text((off, y + 17), line2, font=e_f, fill=(255, 255, 255))


def draw_footer(d, data, y):
    fields = "FIELDS: " + " · ".join(data["meta"]["fields"])
    lines = [
        ("HOW SURE:  REPORTED = carried by the day's wires · CLAIM = one "
         "side's account · OFFICIAL = from the institution itself · "
         "CONFIRMED = confirmed by the named wire · ONGOING = still to "
         "happen", 9),
        ("Every story here was first reported in the news cycle of Thursday "
         "26 November 2026. Sources are named on each story. Scenes are "
         "drawn illustrations, not photographs.", 10),
        (fields + "  ·  news-image-20261126", 9),
    ]
    cy = y
    for text, size in lines:
        fnt = font(size)
        d.text((MARGIN, cy), text, font=fnt, fill=GREY)
        cy += 11
    return cy


def render(data):
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    meta = data["meta"]
    draw_masthead(d, meta)
    draw_region_bar(d, meta["regions"], 76)
    for i, story in enumerate(data["heroes"]):
        draw_hero(img, d, story, MARGIN + i * 335, 104)
    for r in range(2):
        for c in range(5):
            story = data["medium"][r * 5 + c]
            draw_medium(img, d, story, MARGIN + c * 201, 326 + r * 116)
    draw_datecheck(d, data, MARGIN, 558, 492, 178)
    draw_map(d, data["pins"], 508, 558, 504, 178)
    end_y = draw_also_on(d, data["listed"], 740)
    assert end_y <= 948, "ALSO ON overflow: %d" % end_y
    draw_utc(d, data["utc"], 950)
    end_y = draw_footer(d, data, 986)
    assert end_y <= 1024, "footer overflow: %d" % end_y
    return img


def check_data(data):
    stories = data["heroes"] + data["medium"] + data["listed"]
    assert len(stories) == 36, len(stories)
    regions = {s["region"] for s in stories}
    fields = {s["field"] for s in stories}
    sources = {s["source"] for s in stories}
    region_counts = {}
    for s in stories:
        region_counts[s["region"]] = region_counts.get(s["region"], 0) + 1
    for reg in data["meta"]["regions"]:
        key = {"N. AMERICA": "NORTH AMERICA", "S. ASIA": "SOUTH ASIA",
               "EUROPE": "EUROPE", "M. EAST": "MIDDLE EAST",
               "AFRICA": "AFRICA", "E. ASIA": "EAST ASIA",
               "OCEANIA": "OCEANIA", "S. AMERICA": "SOUTH AMERICA",
               "WORLD": "WORLD"}[reg["label"]]
        assert region_counts.get(key, 0) == reg["count"], (key, reg["count"])
    assert len(regions) == 9, regions
    assert len(fields) == 15, fields
    assert len(sources) == 20, sources
    assert len(data["pins"]) == 13
    assert len(data["date_check"]) == 10
    assert len(data["utc"]) == 6
    print("check: 36 stories, 9 regions, 15 fields, 20 sources, "
          "13 pins, 10 date-check, 6 utc — OK")
    print("regions:", sorted(region_counts.items()))
    print("fields:", sorted(fields))
    print("sources:", sorted(sources))


def main():
    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as f:
        data = json.load(f)
    check_data(data)
    img = render(data)
    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG")
    size = os.path.getsize(out)
    print("wrote %s (%d bytes)" % (out, size))
    assert size <= 1024 * 1024, "entry.png over 1 MiB"
    return 0


if __name__ == "__main__":
    sys.exit(main())
