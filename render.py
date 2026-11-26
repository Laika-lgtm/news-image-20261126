"""Render the news-image-20261126 front page as a single 1024x1024 PNG.

Reads stories.json (same directory), draws every element with PIL, writes
entry.png next to this file. Deterministic: no randomness, no timestamps,
no network. Run:  python3 render.py
"""
import json
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

PAPER = (250, 246, 238)
CARD = (255, 255, 255)
INK = (26, 26, 26)
GREY = (104, 100, 92)
RED = (185, 28, 28)
RED_DK = (150, 20, 20)
NAVY = (30, 58, 95)
NAVY_DK = (20, 42, 72)
GOLD = (176, 141, 44)
LINE = (203, 195, 178)
SKY = (214, 232, 244)
SKY_DK = (178, 205, 228)
GREEN = (31, 122, 63)
MAP_BG = (226, 236, 242)
MAP_LAND = (196, 204, 190)


def _font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def font_serif_b(size):
    return _font("/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf", size)


def font_serif(size):
    return _font("/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf", size)


def font_sans_b(size):
    return _font("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)


def font_sans(size):
    return _font("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)


def wrap(draw, text, font, max_w):
    """Greedy word wrap to a list of lines fitting max_w pixels."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_box(draw, x, y, text, font, fill, max_w, leading, max_lines=None):
    """Draw wrapped text; return y just below the last line."""
    lines = wrap(draw, text, font, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def chip(draw, x, y, text, font, fg, bg, pad_x=6, pad_y=3, outline=None):
    """Draw a rounded text chip; return its right edge."""
    w = int(draw.textlength(text, font=font)) + pad_x * 2
    h = font.size + pad_y * 2
    draw.rounded_rectangle([x, y, x + w, y + h], radius=4, fill=bg,
                           outline=outline, width=1 if outline else 0)
    draw.text((x + pad_x, y + pad_y), text, font=font, fill=fg)
    return x + w


# ---------------------------------------------------------------- scenes
def _sky(draw, x, y, w, h, top, bot):
    for i in range(h):
        t = i / max(1, h - 1)
        c = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
        draw.line([(x, y + i), (x + w, y + i)], fill=c)


def scene_parade(draw, x, y, w, h):
    _sky(draw, x, y, w, h, (120, 130, 145), (70, 80, 95))
    # rain
    for i in range(14):
        rx = x + 8 + (i * 23) % max(8, w - 16)
        ry = y + 4 + (i * 17) % max(8, h - 40)
        draw.line([(rx, ry), (rx - 4, ry + 10)], fill=(200, 210, 220), width=2)
    # buildings
    for i, f in enumerate((0.28, 0.44, 0.36, 0.50, 0.32)):
        bh = h * f
        bx = x + 6 + i * (w // 5)
        draw.rectangle([bx, y + h - bh, bx + w // 5 - 8, y + h], fill=(52, 58, 66))
    # grounded balloons, low and sagging
    for fx, fy, col in ((0.22, 0.62, RED), (0.52, 0.55, (42, 92, 150)),
                        (0.80, 0.66, GOLD)):
        bx, by = x + w * fx, y + h * fy
        r = min(16, h * 0.16)
        draw.ellipse([bx - r, by - r, bx + r, by + r], fill=col)
        draw.line([(bx, by + r), (bx, y + h - h * 0.25)],
                  fill=(230, 230, 230), width=1)


def scene_memorial(draw, x, y, w, h):
    _sky(draw, x, y, w, h, (28, 36, 58), (58, 52, 70))
    # stars
    for fx, fy in ((0.06, 0.08), (0.20, 0.18), (0.35, 0.07), (0.55, 0.15),
                   (0.75, 0.08), (0.92, 0.20)):
        draw.ellipse([x + w * fx, y + h * fy, x + w * fx + 2, y + h * fy + 2],
                     fill=(240, 230, 180))
    # skyline + arch (Gateway of India)
    sky_h = h * 0.28
    draw.rectangle([x, y + h - sky_h, x + w, y + h], fill=(18, 20, 32))
    ax, ay = x + w // 2, y + h - sky_h
    ah = h * 0.45
    draw.arc([ax - 26, ay - ah, ax + 26, ay + 6], 180, 360,
             fill=(210, 190, 140), width=4)
    draw.rectangle([ax - 30, ay - ah * 0.3, ax - 22, ay + 2],
                   fill=(210, 190, 140))
    draw.rectangle([ax + 22, ay - ah * 0.3, ax + 30, ay + 2],
                   fill=(210, 190, 140))
    # three candles
    ch = h * 0.18
    for cx in (x + 26, x + w // 2 - 52, x + w - 40):
        draw.rectangle([cx, y + h - ch - 6, cx + 8, y + h - 6],
                       fill=(240, 235, 220))
        draw.ellipse([cx + 1, y + h - ch - 12, cx + 7, y + h - ch - 3],
                     fill=(255, 190, 60))


def scene_chess(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(238, 226, 200))
    s = min(w, h) / 8.0
    ox, oy = x + (w - s * 8) / 2, y + (h - s * 8) / 2
    for r in range(8):
        for c in range(8):
            if (r + c) % 2 == 0:
                draw.rectangle([ox + c * s, oy + r * s,
                                ox + (c + 1) * s, oy + (r + 1) * s],
                               fill=(96, 74, 52))
    # two kings facing off
    for kx, col in ((ox + 2.2 * s, (250, 250, 250)), (ox + 5.2 * s, (30, 30, 30))):
        ky = oy + 3.0 * s
        draw.ellipse([kx, ky, kx + 1.6 * s, ky + 1.6 * s], fill=col,
                     outline=(120, 120, 120), width=1)
        draw.rectangle([kx + 0.55 * s, ky - 0.5 * s, kx + 1.05 * s, ky],
                       fill=col)
        draw.line([(kx + 0.8 * s, ky - 0.7 * s), (kx + 0.8 * s, ky - 0.3 * s)],
                  fill=col, width=2)
        draw.line([(kx + 0.6 * s, ky - 0.5 * s), (kx + 1.0 * s, ky - 0.5 * s)],
                  fill=col, width=2)


def scene_storm(draw, x, y, w, h):
    _sky(draw, x, y, w, h, (90, 100, 115), (60, 68, 82))
    # clouds
    for cx, cy, cw in ((x + 10, y + 8, 60), (x + w * 0.45, y + 2, 80),
                       (x + w * 0.7, y + 14, 55)):
        draw.ellipse([cx, cy, cx + cw, cy + 26], fill=(70, 76, 88))
        draw.ellipse([cx + 12, cy - 8, cx + cw - 10, cy + 16], fill=(88, 94, 106))
    # lightning
    lx, ly = x + w * 0.62, y + 30
    draw.polygon([(lx, ly), (lx - 10, ly + 26), (lx - 2, ly + 26),
                  (lx - 12, ly + 52), (lx + 8, ly + 20), (lx, ly + 20)],
                 fill=(255, 220, 80))
    # rain
    for i in range(16):
        rx = x + 6 + (i * 19) % max(8, w - 12)
        ry = y + 44 + (i * 13) % max(6, h - 50)
        draw.line([(rx, ry), (rx - 3, ry + 10)], fill=(190, 200, 212), width=2)


def scene_council(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(24, 48, 92))
    cx, cy, r = x + w / 2, y + h / 2 + 4, min(w, h) * 0.36
    for k in range(12):
        a = math.pi * 2 * k / 12 - math.pi / 2
        sx, sy = cx + r * math.cos(a), cy + r * math.sin(a)
        draw.polygon([(sx, sy - 5), (sx + 1.6, sy - 1.6), (sx + 5, sy),
                      (sx + 1.6, sy + 1.6), (sx, sy + 5), (sx - 1.6, sy + 1.6),
                      (sx - 5, sy), (sx - 1.6, sy - 1.6)], fill=(255, 210, 60))
    # building base
    draw.rectangle([x, y + h - 12, x + w, y + h], fill=(16, 32, 64))


def scene_market_up(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(232, 245, 234))
    base = y + h - 12
    vals = (0.30, 0.45, 0.38, 0.62, 0.55, 0.82, 0.95)
    bw = w / (len(vals) * 1.6)
    for i, v in enumerate(vals):
        bx = x + 8 + i * (w - 16) / len(vals)
        bh = v * (h - 26)
        draw.rectangle([bx, base - bh, bx + bw, base], fill=GREEN)
    # arrow
    ax0, ay0 = x + 10, base - 0.30 * (h - 26) - 8
    ax1, ay1 = x + w - 12, base - 0.95 * (h - 26) - 4
    draw.line([(ax0, ay0), (ax1, ay1)], fill=RED_DK, width=3)
    draw.polygon([(ax1, ay1), (ax1 - 12, ay1 + 2), (ax1 - 2, ay1 + 12)],
                 fill=RED_DK)


def scene_market_down(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(247, 232, 232))
    base = y + h - 12
    vals = (0.95, 0.80, 0.86, 0.60, 0.66, 0.42, 0.28)
    for i, v in enumerate(vals):
        bx = x + 8 + i * (w - 16) / len(vals)
        bh = v * (h - 26)
        draw.rectangle([bx, base - bh, bx + (w - 16) / len(vals) * 0.6, base],
                       fill=RED)
    ax0, ay0 = x + 10, base - 0.95 * (h - 26) - 4
    ax1, ay1 = x + w - 12, base - 0.28 * (h - 26) - 4
    draw.line([(ax0, ay0), (ax1, ay1)], fill=RED_DK, width=3)
    draw.polygon([(ax1, ay1), (ax1 - 12, ay1 - 2), (ax1 - 2, ay1 - 12)],
                 fill=RED_DK)


def scene_tube(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(240, 238, 232))
    cx, cy, r = x + w / 2, y + h / 2, min(w, h) * 0.36
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=RED, width=7)
    draw.rectangle([x + 6, cy - 9, x + w - 6, cy + 9], fill=NAVY)
    draw.rectangle([cx - r - 4, cy - 4, cx + r + 4, cy + 4], fill=(255, 255, 255))


def scene_guitar(draw, x, y, w, h):
    _sky(draw, x, y, w, h, (52, 40, 48), (30, 24, 30))
    # body
    cx, cy = x + w * 0.42, y + h * 0.62
    r = min(26, h * 0.30)
    draw.ellipse([cx - r, cy - r * 0.7, cx + r, cy + r * 0.85],
                 fill=(150, 80, 40))
    draw.ellipse([cx - r * 0.55, cy - r * 1.3, cx + r * 0.6, cy - r * 0.25],
                 fill=(150, 80, 40))
    draw.ellipse([cx - r * 0.28, cy - r * 0.15, cx + r * 0.28, cy + r * 0.4],
                 fill=(20, 16, 16))
    # neck + head
    nt = y + 2
    nb = cy - r * 0.9
    if nb > nt + 2:
        draw.rectangle([cx - 3, nt, cx + 5, nb], fill=(90, 60, 36))
        draw.rectangle([cx - 6, nt, cx + 8, nt + 8], fill=(60, 40, 26))
    # strings
    for k in range(3):
        draw.line([(cx - 4 + k * 4, nt + 4), (cx - 4 + k * 4, cy + r * 0.7)],
                  fill=(220, 210, 190), width=1)


def scene_phone(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(226, 238, 246))
    px, py = x + w / 2 - 22, y + 6
    draw.rounded_rectangle([px, py, px + 44, py + h - 12], radius=7,
                           fill=(24, 32, 44))
    draw.rectangle([px + 4, py + 8, px + 40, py + h - 22], fill=(60, 140, 90))
    f = font_sans_b(30 if h >= 80 else 18)
    rtxt = "₹"
    tw = draw.textlength(rtxt, font=f)
    draw.text((px + 22 - tw / 2, py + h // 2 - f.size // 2 - 2), rtxt, font=f,
              fill=(255, 255, 255))
    draw.ellipse([px + 18, py + h - 18, px + 26, py + h - 10],
                 fill=(200, 200, 200))


def scene_cricket(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(46, 125, 62))
    # pitch
    draw.rectangle([x + w * 0.30, y, x + w * 0.70, y + h], fill=(196, 164, 110))
    # stumps
    for k in range(3):
        sx = x + w * 0.42 + k * 7
        draw.line([(sx, y + 8), (sx, y + 24)], fill=(240, 220, 160), width=3)
    # bat
    draw.line([(x + w * 0.60, y + h - 12), (x + w * 0.52, y + h * 0.42)],
              fill=(222, 190, 130), width=9)
    # ball
    draw.ellipse([x + w * 0.72, y + h * 0.30, x + w * 0.72 + 12,
                  y + h * 0.30 + 12], fill=RED)
    draw.arc([x + w * 0.72, y + h * 0.30, x + w * 0.72 + 12,
              y + h * 0.30 + 12], 40, 200, fill=(255, 255, 255), width=1)


def scene_shield(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(226, 236, 246))
    cx, cy = x + w / 2, y + h / 2
    draw.polygon([(cx, cy - 30), (cx + 26, cy - 18), (cx + 26, cy + 6),
                  (cx, cy + 32), (cx - 26, cy + 6), (cx - 26, cy - 18)],
                 fill=NAVY)
    draw.line([(cx - 12, cy + 2), (cx - 3, cy + 12), (cx + 14, cy - 10)],
              fill=(120, 220, 140), width=4)
    # lock
    draw.rectangle([x + w - 34, y + h - 30, x + w - 12, y + h - 12],
                   fill=(70, 70, 70))
    draw.arc([x + w - 30, y + h - 40, x + w - 16, y + h - 26], 180, 360,
             fill=(70, 70, 70), width=3)


def scene_moon(draw, x, y, w, h):
    _sky(draw, x, y, w, h, (16, 22, 44), (40, 44, 72))
    for sx, sy in ((10, 8), (34, 20), (66, 6), (96, 16), (130, 8), (160, 22)):
        draw.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2], fill=(240, 240, 220))
    cx, cy, r = x + w / 2, y + h / 2, min(w, h) * 0.34
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(238, 230, 200))
    for mx, my, mr in ((-0.4, -0.3, 0.12), (0.3, 0.2, 0.16), (-0.1, 0.45, 0.10),
                       (0.45, -0.35, 0.08)):
        draw.ellipse([cx + mx * r - mr * r, cy + my * r - mr * r,
                      cx + mx * r + mr * r, cy + my * r + mr * r],
                     fill=(210, 200, 170))
    # rooftops
    draw.rectangle([x, y + h - 12, x + w, y + h], fill=(12, 14, 26))


def scene_siren(draw, x, y, w, h):
    _sky(draw, x, y, w, h, (214, 232, 244), (178, 205, 228))
    # road
    draw.rectangle([x, y + h - 8, x + w, y + h], fill=(90, 90, 96))
    # ambulance van body
    bx0, by0 = x + w * 0.30, y + h * 0.18
    bx1, by1 = x + w * 0.72, y + h * 0.78
    draw.rectangle([bx0, by0, bx1, by1], fill=(255, 255, 255),
                   outline=(120, 120, 120))
    # cab + windshield
    draw.rectangle([bx1, y + h * 0.38, x + w * 0.80, by1],
                   fill=(255, 255, 255), outline=(120, 120, 120))
    draw.polygon([(bx1 + 2, y + h * 0.42), (x + w * 0.79, y + h * 0.42),
                  (x + w * 0.79, y + h * 0.58), (bx1 + 2, y + h * 0.58)],
                 fill=(140, 190, 220))
    # light bar
    draw.rectangle([x + w * 0.42, by0 - 5, x + w * 0.50, by0], fill=RED)
    draw.rectangle([x + w * 0.52, by0 - 5, x + w * 0.60, by0],
                   fill=(40, 90, 200))
    # red cross on van side
    cx = x + w * 0.51
    cy = y + h * 0.48
    draw.rectangle([cx - 2, cy - 7, cx + 2, cy + 7], fill=RED)
    draw.rectangle([cx - 7, cy - 2, cx + 7, cy + 2], fill=RED)
    # wheels
    for wx in (x + w * 0.38, x + w * 0.74):
        draw.ellipse([wx - 5, y + h - 13, wx + 5, y + h - 3],
                     fill=(30, 30, 30))


def scene_missile(draw, x, y, w, h):
    _sky(draw, x, y, w, h, (16, 22, 44), (40, 44, 72))
    for sx, sy in ((8, 6), (30, 14), (70, 5), (120, 10), (160, 6),
                   (185, 14)):
        draw.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2],
                     fill=(240, 240, 220))
    cy = y + h * 0.5
    # flame + smoke trailing left
    draw.polygon([(x + w * 0.30, cy - 4), (x + w * 0.30, cy + 4),
                  (x + w * 0.12, cy)], fill=(255, 170, 40))
    draw.polygon([(x + w * 0.34, cy - 3), (x + w * 0.34, cy + 3),
                  (x + w * 0.20, cy)], fill=(255, 220, 90))
    for sx, sy, r in ((0.16, 0.30, 3), (0.10, 0.62, 2), (0.06, 0.45, 2)):
        draw.ellipse([x + w * sx - r, y + h * sy - r, x + w * sx + r,
                      y + h * sy + r], fill=(150, 150, 150))
    # body
    draw.rectangle([x + w * 0.34, cy - 6, x + w * 0.74, cy + 6],
                   fill=(225, 225, 225))
    # nose cone
    draw.polygon([(x + w * 0.74, cy - 6), (x + w * 0.74, cy + 6),
                  (x + w * 0.90, cy)], fill=(200, 60, 60))
    # fins
    draw.polygon([(x + w * 0.36, cy - 6), (x + w * 0.30, cy - 13),
                  (x + w * 0.44, cy - 6)], fill=(180, 180, 180))
    draw.polygon([(x + w * 0.36, cy + 6), (x + w * 0.30, cy + 13),
                  (x + w * 0.44, cy + 6)], fill=(180, 180, 180))


SCENES = {"parade": scene_parade, "memorial": scene_memorial,
          "chess": scene_chess, "storm": scene_storm,
          "council": scene_council, "market_up": scene_market_up,
          "tube": scene_tube, "guitar": scene_guitar,
          "phone": scene_phone, "cricket": scene_cricket,
          "shield": scene_shield, "market_down": scene_market_down,
          "moon": scene_moon, "siren": scene_siren,
          "missile": scene_missile}

# ---------------------------------------------------------------- map
CONTINENTS = {
    "north_america": [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73),
                      (-75, 62), (-70, 44), (-80, 26), (-90, 21), (-97, 16),
                      (-105, 20), (-117, 32), (-125, 40), (-125, 49),
                      (-140, 60), (-168, 66)],
    "south_america": [(-80, 10), (-60, 5), (-50, 0), (-40, -5), (-35, -8),
                      (-40, -20), (-48, -28), (-58, -38), (-65, -45),
                      (-70, -55), (-73, -40), (-72, -20), (-77, -5), (-80, 10)],
    "europe": [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57),
               (10, 59), (18, 56), (21, 55), (24, 60), (30, 70), (40, 68),
               (45, 60), (40, 50), (30, 46), (28, 41), (23, 36), (19, 40),
               (12, 44), (3, 43), (-2, 37), (-10, 36)],
    "africa": [(-6, 35), (10, 37), (20, 32), (32, 31), (35, 28), (40, 15),
               (48, 11), (51, 10), (44, 0), (40, -10), (35, -20), (32, -29),
               (25, -34), (18, -32), (12, -18), (8, 4), (-8, 5), (-15, 11),
               (-17, 15), (-6, 35)],
    "asia": [(40, 68), (60, 70), (80, 73), (110, 76), (140, 72), (170, 66),
             (178, 65), (170, 60), (160, 55), (150, 45), (140, 40),
             (130, 35), (127, 35), (122, 30), (120, 25), (110, 20),
             (105, 10), (100, 8), (95, 15), (90, 22), (85, 20), (80, 15),
             (77, 8), (72, 20), (66, 25), (60, 25), (55, 26), (50, 29),
             (48, 30), (44, 29), (40, 36), (40, 68)],
    "australia": [(113, -22), (114, -30), (115, -35), (120, -34), (129, -32),
                  (132, -32), (135, -35), (137, -38), (140, -38), (142, -37),
                  (146, -39), (150, -37), (153, -32), (153, -27), (150, -22),
                  (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
                  (132, -12), (130, -13), (126, -14), (122, -17), (118, -20),
                  (113, -22)],
}


def draw_map(draw, x, y, w, h, pins):
    draw.rectangle([x, y, x + w, y + h], fill=MAP_BG)
    lon0, lon1, lat0, lat1 = -170.0, 190.0, 78.0, -58.0

    def proj(lon, lat):
        px = x + (lon - lon0) / (lon1 - lon0) * w
        py = y + (lat0 - lat) / (lat0 - lat1) * h
        return (px, py)

    for poly in CONTINENTS.values():
        draw.polygon([proj(lon, lat) for lon, lat in poly], fill=MAP_LAND,
                     outline=(255, 255, 255))
    # small islands: UK, Japan, New Zealand
    for lon, lat, r in ((-2, 54, 3), (138, 37, 3), (172, -41, 3)):
        px, py = proj(lon, lat)
        draw.ellipse([px - r, py - r, px + r, py + r], fill=MAP_LAND)
    f_num = font_sans_b(8)
    for pin in pins:
        px, py = proj(pin["lon"], pin["lat"])
        draw.ellipse([px - 6, py - 6, px + 6, py + 6], fill=RED,
                     outline=(255, 255, 255), width=1)
        label = str(pin["pin"])
        tw = draw.textlength(label, font=f_num)
        draw.text((px - tw / 2, py - 4), label, font=f_num,
                  fill=(255, 255, 255))


# ---------------------------------------------------------------- build
def build():
    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as fh:
        data = json.load(fh)

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead
    d.rectangle([0, 0, W, 6], fill=RED)
    f_title = font_serif_b(46)
    d.text((16, 14), data["masthead_title"], font=f_title, fill=INK)
    f_date = font_sans_b(20)
    date_txt = data["date"]
    d.text((W - 16 - d.textlength(date_txt, font=f_date), 22), date_txt,
           font=f_date, fill=NAVY)
    f_claim = font_sans_b(14)
    d.text((16, 68), data["masthead_claim"], font=f_claim, fill=RED_DK)
    d.line([(16, 92), (W - 16, 92)], fill=INK, width=2)

    # ---- ticker
    d.rectangle([0, 94, W, 122], fill=NAVY)
    f_tick = font_sans_b(13)
    tick = data["ticker"]
    d.text(((W - d.textlength(tick, font=f_tick)) / 2, 102), tick,
           font=f_tick, fill=(255, 255, 255))

    # ---- heroes
    hy, hh = 126, 228
    hw = 325
    hx = [16, 349, 682]
    f_h_head = font_sans_b(19)
    f_h_deck = font_sans(12)
    f_meta = font_sans_b(10)
    f_tag = font_sans_b(10)
    for card, x in zip(data["heroes"], hx):
        d.rectangle([x, hy, x + hw, hy + hh], fill=CARD, outline=LINE, width=1)
        SCENES[card["scene"]](d, x + 1, hy + 1, hw - 2, 112)
        # number badge on scene
        badge = str(card["id"])
        d.ellipse([x + 8, hy + 8, x + 28, hy + 28], fill=RED)
        tw = d.textlength(badge, font=f_tag)
        d.text((x + 18 - tw / 2, hy + 12), badge, font=f_tag,
               fill=(255, 255, 255))
        # stat chip on scene, bottom right
        f_stat = font_sans_b(11)
        sw = d.textlength(card["stat"], font=f_stat) + 12
        d.rounded_rectangle([x + hw - sw - 8, hy + 112 - 24, x + hw - 8,
                             hy + 112 - 6], radius=4, fill=(255, 255, 255))
        d.text((x + hw - sw - 2, hy + 112 - 22), card["stat"], font=f_stat,
               fill=RED_DK)
        ty = hy + 120
        ty = text_box(d, x + 10, ty, card["headline"], f_h_head, INK,
                      hw - 20, 22, max_lines=2)
        ty = text_box(d, x + 10, ty + 2, card["deck"], f_h_deck, (60, 58, 52),
                      hw - 20, 15, max_lines=2)
        meta = "%s · %s" % (card["region"], card["field"])
        d.text((x + 10, hy + hh - 16), meta, font=f_meta, fill=GREY)
        tag = card["tag"]
        tw = d.textlength(tag, font=f_tag) + 10
        d.rounded_rectangle([x + hw - tw - 8, hy + hh - 18, x + hw - 8,
                             hy + hh - 4], radius=3, fill=NAVY)
        d.text((x + hw - tw - 3, hy + hh - 16), tag, font=f_tag,
               fill=(255, 255, 255))

    # ---- stat strip
    sy, sh = 360, 34
    stats = data["stat_strip"]
    gap = 6
    sw = (W - 32 - gap * (len(stats) - 1)) // len(stats)
    f_stat2 = font_sans_b(11)
    for i, s in enumerate(stats):
        x = 16 + i * (sw + gap)
        d.rectangle([x, sy, x + sw, sy + sh], fill=CARD, outline=LINE, width=1)
        lines = wrap(d, s, f_stat2, sw - 10)
        ly = sy + (sh - len(lines) * 13) // 2
        for line in lines:
            lw = d.textlength(line, font=f_stat2)
            d.text((x + (sw - lw) / 2, ly), line, font=f_stat2, fill=RED_DK)
            ly += 13

    # ---- region bar
    f_reg = font_sans_b(13)
    reg = data["region_bar"]
    d.text(((W - d.textlength(reg, font=f_reg)) / 2, 400), reg, font=f_reg,
           fill=NAVY)

    # ---- featured grid (5 cols x 2 rows)
    fy, fh = 420, 110
    f_f_head = font_sans_b(13)
    f_f_deck = font_sans(10)
    f_f_tag = font_sans_b(9)
    cols, rows = 5, 2
    gapx, gapy = 6, 8
    fw = (W - 32 - gapx * (cols - 1)) // cols
    for idx, card in enumerate(data["featured"]):
        r, c = divmod(idx, cols)
        x = 16 + c * (fw + gapx)
        yy = fy + r * (fh + gapy)
        d.rectangle([x, yy, x + fw, yy + fh], fill=CARD, outline=LINE, width=1)
        SCENES[card["scene"]](d, x + 1, yy + 1, fw - 2, 36)
        # number badge + region chip on scene
        badge = str(card["id"])
        d.ellipse([x + 6, yy + 6, x + 22, yy + 22], fill=RED)
        tw = d.textlength(badge, font=f_f_tag)
        d.text((x + 14 - tw / 2, yy + 9), badge, font=f_f_tag,
               fill=(255, 255, 255))
        reg_txt = card["region"]
        rw = d.textlength(reg_txt, font=f_f_tag) + 8
        d.rounded_rectangle([x + fw - rw - 5, yy + 6, x + fw - 5, yy + 20],
                            radius=3, fill=NAVY)
        d.text((x + fw - rw - 1, yy + 8), reg_txt, font=f_f_tag,
               fill=(255, 255, 255))
        ty = yy + 40
        ty = text_box(d, x + 7, ty, card["headline"], f_f_head, INK,
                      fw - 14, 15, max_lines=2)
        ty = text_box(d, x + 7, ty + 1, card["deck"], f_f_deck, (60, 58, 52),
                      fw - 14, 12, max_lines=2)
        # stat line at bottom
        d.text((x + 7, yy + fh - 13), card["stat"], font=f_f_tag, fill=RED_DK)

    # ---- date check + map
    dy, dh = 652, 150
    d.rectangle([16, dy, 516, dy + dh], fill=(255, 252, 240), outline=RED,
                width=1)
    f_dc_t = font_sans_b(13)
    d.text((26, dy + 8), data["date_check_title"], font=f_dc_t, fill=RED_DK)
    f_dc_i = font_sans(10)
    iy = text_box(d, 26, dy + 26, data["date_check_intro"], f_dc_i, INK,
                  480, 12, max_lines=2)
    f_dc = font_sans(8)
    ex = data["date_check"]
    col_w = 160
    for i, item in enumerate(ex):
        col = i // 7
        row = i % 7
        ex_x = 26 + col * col_w
        ex_y = iy + 2 + row * 11
        d.text((ex_x, ex_y), "✕ " + item, font=f_dc, fill=(90, 40, 40))
    f_ny = font_sans_b(9)
    ny = data["not_yet"]
    text_box(d, 26, dy + dh - 24, ny, f_ny, NAVY, 480, 11, max_lines=2)

    # map
    mx, mw = 524, 484
    d.rectangle([mx, dy, mx + mw, dy + dh], fill=CARD, outline=LINE, width=1)
    f_map_t = font_sans_b(11)
    d.text((mx + 10, dy + 6), "WHERE IT HAPPENED — 12 STORIES PINNED",
           font=f_map_t, fill=NAVY)
    draw_map(d, mx + 8, dy + 24, mw - 16, dh - 32, data["map_pins"])

    # ---- also on
    ay = 808
    f_ao_t = font_sans_b(13)
    d.text((16, ay), "ALSO ON — THURSDAY 26 NOVEMBER", font=f_ao_t, fill=INK)
    d.line([(16, ay + 18), (W - 16, ay + 18)], fill=LINE, width=1)
    f_ao = font_sans(11)
    f_ao_r = font_sans_b(10)
    items = data["also_on"]
    rows = 11
    for i, item in enumerate(items):
        col = i // rows
        row = i % rows
        ax = 16 + col * 500
        ayy = ay + 24 + row * 12
        d.text((ax, ayy), "•", font=f_ao, fill=RED)
        head = item["headline"]
        max_hw = 500 - 14 - d.textlength(item["region"], font=f_ao_r) - 12
        while d.textlength(head, font=f_ao) > max_hw and len(head) > 10:
            head = head[:-4] + "…"
        d.text((ax + 12, ayy), head, font=f_ao, fill=INK)
        rw = d.textlength(item["region"], font=f_ao_r)
        d.text((ax + 500 - rw - 4, ayy), item["region"], font=f_ao_r,
               fill=GREY)

    # ---- timeline
    ty = 952
    d.rectangle([0, ty, W, ty + 32], fill=NAVY_DK)
    f_tl_t = font_sans_b(11)
    d.text((16, ty + 9), data["timeline_title"], font=f_tl_t,
           fill=(255, 210, 60))
    f_tl = font_sans(9)
    parts = ["%s  %s" % (t, txt) for t, txt in data["timeline"]]
    line1 = "  ·  ".join(parts[:4])
    line2 = "  ·  ".join(parts[4:])
    # two-line timeline, right of the title block
    tx = 150
    d.text((tx, ty + 3), line1, font=f_tl, fill=(255, 255, 255))
    d.text((tx, ty + 17), line2, font=f_tl, fill=(255, 255, 255))

    # ---- footer
    f_leg = font_sans(10)
    leg = data["legend"]
    d.text((16, 990), leg, font=f_leg, fill=GREY)
    f_foot = font_sans(10)
    d.text((16, 1004), data["footer"], font=f_foot, fill=GREY)

    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG")
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    build()
