# Covers and spines of the three books under the desk lamp, redrawn by hand after the originals (no scanned image):
#   Kernighan & Ritchie, The C Programming Language, 2nd ed. (Prentice Hall, 1988): white, huge blue C, red ANSI stamp.
#   Josef Albers, Interaction of Color, 50th anniversary ed. (Yale, 2013): white, stacked bars in reds and pinks.
#   Josef Müller-Brockmann, Grid Systems in Graphic Design (Niggli): vermilion, white 4 x 8 grid, titles in English and German.
# Covers are portrait (spine on the left); spines are horizontal strips (book top on the left), read lying flat.
# usage: python -I textures_livres.py <hero_dir>   -> hero/outils/textures-bureau/livres/
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

H = os.path.abspath(sys.argv[1])
OUT = os.path.join(H, 'outils', 'textures-bureau', 'livres')
os.makedirs(OUT, exist_ok=True)
NP = np.random.default_rng(3)
PX = 6                                          # pixels per millimetre
F_TIMES = '/System/Library/Fonts/Times.ttc'
F_FUT = '/System/Library/Fonts/Supplemental/Futura.ttc'
F_HELV = '/System/Library/Fonts/HelveticaNeue.ttc'
F_BASK = '/System/Library/Fonts/Supplemental/Baskerville.ttc'


def fnt(path, size, idx=0):
    try:
        return ImageFont.truetype(path, size, index=idx)
    except OSError:
        return ImageFont.truetype(F_HELV, size)


def wear(im, amount=0.06, edge=0.1):
    """A used book: soft grime, slightly rubbed edges."""
    a = np.asarray(im.convert('RGB')).astype(np.float32)
    h, w = a.shape[:2]
    n = NP.normal(0, 1, (h // 90 + 2, w // 90 + 2)).astype(np.float32)
    n = np.asarray(Image.fromarray(n).resize((w, h), Image.BICUBIC))
    a *= (1 - amount * 0.25 * np.clip(n, 0, 2) * 0.5)[..., None]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy))
    a = a * (1 - edge * np.clip(1 - d / 10, 0, 1))[..., None] + 30 * edge * np.clip(1 - d / 6, 0, 1)[..., None]
    a += NP.normal(0, 2.0, a.shape)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def spine_line(sp, parts, x0, x1):
    """Lays out (text, font path, index, size, colour, gap after) along a spine, shrinking every size to fit [x0, x1]."""
    d = ImageDraw.Draw(sp)
    y = sp.height / 2

    def width(k):
        return sum(d.textlength(t, font=fnt(p, max(8, int(sz * k)), i)) + g * k for t, p, i, sz, c, g in parts)
    k = min(1.0, (x1 - x0) / width(1.0))
    x = x0
    for t, p, i, sz, c, g in parts:
        f = fnt(p, max(8, int(sz * k)), i)
        d.text((x, y), t, font=f, fill=c, anchor='lm')
        x += d.textlength(t, font=f) + g * k


def text_fit(d, xy, s, f, fill, anchor='mm', sx=1.0, img=None):
    """Text drawn on its own layer and stretched horizontally by sx (condensed / expanded faces)."""
    if sx == 1.0:
        d.text(xy, s, font=f, fill=fill, anchor=anchor)
        return
    l, t, r, b = d.textbbox((0, 0), s, font=f)
    tmp = Image.new('L', (r - l + 20, b - t + 20), 0)
    ImageDraw.Draw(tmp).text((10 - l, 10 - t), s, font=f, fill=255)
    tmp = tmp.resize((int(tmp.width * sx), tmp.height), Image.LANCZOS)
    x, y = xy
    if anchor == 'mm':
        x, y = x - tmp.width // 2, y - tmp.height // 2
    col = Image.new('RGB', tmp.size, fill)
    img.paste(col, (int(x), int(y)), tmp)


# ------------------------------------------------------------------ Kernighan & Ritchie
def knr():
    W, Hh = 178 * PX, 235 * PX
    im = Image.new('RGB', (W, Hh), (248, 247, 243))
    d = ImageDraw.Draw(im)
    BLUE, RED, BLK = (62, 86, 170), (206, 42, 36), (22, 22, 24)
    CBLUE = (96, 122, 214)
    text_fit(d, (W / 2, 0.055 * Hh), 'SECOND EDITION', fnt(F_TIMES, 62), RED, sx=0.92, img=im)
    for y, c, t in ((0.088, BLUE, 7), (0.1, BLK, 3)):
        d.rectangle((0.02 * W, y * Hh, 0.98 * W, y * Hh + t), fill=c)
    text_fit(d, (W / 2, 0.155 * Hh), 'THE', fnt(F_TIMES, 170), BLK, sx=0.82, img=im)
    d.rectangle((0.02 * W, 0.205 * Hh, 0.98 * W, 0.205 * Hh + 3), fill=BLK)
    fc = fnt(F_FUT, 620, 4)
    text_fit(d, (0.43 * W, 0.395 * Hh), 'C', fc, CBLUE, sx=1.0, img=im)
    st = Image.new('RGBA', (360, 260), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    sd.rectangle((8, 8, 352, 252), outline=RED + (255,), width=9)
    sd.text((180, 70), 'ANSI', font=fnt(F_FUT, 82, 4), fill=RED + (255,), anchor='mm')
    sd.text((180, 172), 'C', font=fnt(F_FUT, 150, 4), fill=RED + (255,), anchor='mm')
    st = st.rotate(16, expand=True, resample=Image.BICUBIC)
    im.paste(st, (int(0.62 * W), int(0.3 * Hh)), st)
    d.rectangle((0.02 * W, 0.585 * Hh, 0.98 * W, 0.585 * Hh + 3), fill=BLK)
    text_fit(d, (W / 2, 0.635 * Hh), 'PROGRAMMING', fnt(F_TIMES, 150), BLK, sx=0.74, img=im)
    text_fit(d, (W / 2, 0.705 * Hh), 'LANGUAGE', fnt(F_TIMES, 150), BLK, sx=0.74, img=im)
    for y, c, t in ((0.75, BLK, 3), (0.758, BLUE, 7)):
        d.rectangle((0.02 * W, y * Hh, 0.98 * W, y * Hh + t), fill=c)
    text_fit(d, (W / 2, 0.83 * Hh), 'BRIAN W. KERNIGHAN', fnt(F_TIMES, 70), BLUE, sx=0.86, img=im)
    text_fit(d, (W / 2, 0.875 * Hh), 'DENNIS M. RITCHIE', fnt(F_TIMES, 70), BLUE, sx=0.86, img=im)
    d.text((W / 2, 0.955 * Hh), 'PRENTICE HALL SOFTWARE SERIES', font=fnt(F_HELV, 24), fill=BLK, anchor='mm')
    wear(im, 0.05, 0.12).save(os.path.join(OUT, 'knr-couverture.png'))
    sp = Image.new('RGB', (Hh, 14 * PX), (248, 247, 243))
    d = ImageDraw.Draw(sp)
    y = sp.height / 2
    spine_line(sp, [('KERNIGHAN · RITCHIE', F_TIMES, 0, 36, BLUE, 60), ('THE', F_TIMES, 0, 42, BLK, 12), ('C', F_FUT, 4, 58, CBLUE, 12),
                    ('PROGRAMMING LANGUAGE', F_TIMES, 0, 42, BLK, 50), ('SECOND EDITION', F_TIMES, 0, 26, RED, 0)], 50, Hh - 130)
    d.rectangle((Hh - 100, 16, Hh - 44, sp.height - 16), outline=BLK, width=3)
    d.text((Hh - 72, y), 'PH', font=fnt(F_HELV, 26, 1), fill=BLK, anchor='mm')
    wear(sp, 0.05, 0.2).save(os.path.join(OUT, 'knr-tranche.png'))


# ------------------------------------------------------------------ Albers
def albers():
    W, Hh = 165 * PX, 235 * PX
    im = Image.new('RGB', (W, Hh), (248, 247, 244))
    d = ImageDraw.Draw(im)
    d.text((0.1 * W, 0.068 * Hh), 'Josef Albers', font=fnt(F_HELV, 46, 1), fill=(96, 96, 96), anchor='lm')
    d.text((0.43 * W, 0.066 * Hh), 'Interaction of Color', font=fnt(F_BASK, 52), fill=(96, 96, 96), anchor='lm')
    d.text((0.43 * W, 0.092 * Hh), '50th Anniversary Edition', font=fnt(F_BASK, 30, 1), fill=(110, 110, 110), anchor='lm')
    bars = [((240, 138, 118), 0.17, 0.18, 0.86, -2.0), ((232, 86, 60), 0.255, 0.2, 0.84, 1.5), ((226, 98, 106), 0.345, 0.25, 0.83, -0.8),
            ((196, 40, 46), 0.425, 0.09, 0.62, 1.8), ((240, 134, 150), 0.505, 0.33, 0.92, -2.2), ((184, 92, 120), 0.585, 0.32, 0.93, 0.6),
            ((238, 88, 50), 0.665, 0.24, 0.81, -0.5), ((196, 24, 74), 0.75, 0.2, 0.8, 1.8)]
    for col, y, x0, x1, rot in bars:
        bar = Image.new('RGBA', (int((x1 - x0) * W), int(0.072 * Hh)), col + (255,))
        bar = bar.rotate(rot, expand=True, resample=Image.BICUBIC)
        im.paste(bar, (int(x0 * W), int(y * Hh)), bar)
    wear(im, 0.04, 0.1).save(os.path.join(OUT, 'albers-couverture.png'))
    sp = Image.new('RGB', (Hh, 17 * PX), (248, 247, 244))
    d = ImageDraw.Draw(sp)
    y = sp.height / 2
    d.text((70, y), 'Josef Albers', font=fnt(F_HELV, 40, 1), fill=(96, 96, 96), anchor='lm')
    d.text((420, y), 'Interaction of Color', font=fnt(F_BASK, 48), fill=(80, 80, 80), anchor='lm')
    d.rectangle((1000, y - 18, 1060, y + 18), fill=(232, 86, 60))
    d.text((Hh - 90, y), 'Yale', font=fnt(F_BASK, 38), fill=(80, 80, 80), anchor='mm')
    wear(sp, 0.04, 0.2).save(os.path.join(OUT, 'albers-tranche.png'))


# ------------------------------------------------------------------ Müller-Brockmann
def grid():
    W, Hh = 210 * PX, 300 * PX
    V = (230, 70, 44)
    im = Image.new('RGB', (W, Hh), V)
    d = ImageDraw.Draw(im)
    m, cols, rows = 0.06, 4, 8
    gx = [m * W + i * (1 - 2 * m) * W / cols for i in range(cols + 1)]
    gy = [m * Hh + j * (1 - 2 * m) * Hh / rows for j in range(rows + 1)]
    for x in gx:
        d.line((x, gy[0], x, gy[-1]), fill=(246, 176, 160), width=3)
    for y in gy:
        d.line((gx[0], y, gx[-1], y), fill=(246, 176, 160), width=3)
    BLK = (24, 18, 16)
    d.text((gx[2] + 14, gy[0] + 26), 'Josef Müller-Brockmann', font=fnt(F_HELV, 30), fill=BLK, anchor='lm')
    d.text((gx[0] + 14, gy[1] + 50), 'Grid systems', font=fnt(F_HELV, 70, 1), fill=BLK, anchor='lm')
    d.text((gx[0] + 14, gy[1] + 116), 'in graphic design', font=fnt(F_HELV, 30), fill=BLK, anchor='lm')
    for k, ln in enumerate(['A visual communication manual', 'for graphic designers,', 'typographers and three', 'dimensional designers']):
        d.text((gx[2] + 14, gy[1] + 30 + k * 34), ln, font=fnt(F_HELV, 26), fill=BLK, anchor='lm')
    d.text((gx[0] + 14, gy[2] + 50), 'Raster systeme', font=fnt(F_HELV, 70, 1), fill=BLK, anchor='lm')
    d.text((gx[0] + 14, gy[2] + 116), 'für die visuelle Gestaltung', font=fnt(F_HELV, 30), fill=BLK, anchor='lm')
    for k, ln in enumerate(['Ein Handbuch für Grafiker,', 'Typografen und', 'Ausstellungsgestalter']):
        d.text((gx[2] + 14, gy[2] + 30 + k * 34), ln, font=fnt(F_HELV, 26), fill=BLK, anchor='lm')
    d.text((gx[3] + 14, gy[7] + 60), 'Niggli', font=fnt(F_HELV, 34, 1), fill=BLK, anchor='lm')
    wear(im, 0.05, 0.14).save(os.path.join(OUT, 'grid-couverture.png'))
    sp = Image.new('RGB', (Hh, 22 * PX), V)
    d = ImageDraw.Draw(sp)
    y = sp.height / 2
    spine_line(sp, [('Josef Müller-Brockmann', F_HELV, 0, 40, BLK, 60), ('Grid systems in graphic design', F_HELV, 1, 46, BLK, 40),
                    ('Raster systeme für die visuelle Gestaltung', F_HELV, 1, 46, BLK, 0)], 80, Hh - 220)
    d.text((Hh - 120, y), 'Niggli', font=fnt(F_HELV, 40, 1), fill=BLK, anchor='mm')
    wear(sp, 0.05, 0.22).save(os.path.join(OUT, 'grid-tranche.png'))


for fn in (knr, albers, grid):
    fn()
    print(fn.__name__)
