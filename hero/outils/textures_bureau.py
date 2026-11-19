# Textures for the desk prototypes: embossed labels, cable tape, floor marking tape (four colour palettes), perforated sheet.
# usage: python -I textures_bureau.py <hero_dir>   (writes hero/outils/textures-bureau/)
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

H = sys.argv[1]
OUT = os.path.join(H, 'outils', 'textures-bureau')
os.makedirs(OUT, exist_ok=True)
FONT = '/System/Library/Fonts/Supplemental/Arial Narrow Bold.ttf'
rng = np.random.default_rng(7)

PALETTES = {
    'blanc': dict(tape=(232, 231, 225), ink=(24, 24, 24), floor=(226, 226, 220), cable=(225, 225, 220)),
    'noir': dict(tape=(26, 26, 28), ink=(232, 232, 226), floor=(226, 226, 220), cable=(24, 24, 26)),
    'jaune': dict(tape=(226, 182, 24), ink=(22, 20, 16), floor=(222, 178, 22), cable=(226, 182, 24), hazard=True),
    'bleu': dict(tape=(36, 86, 168), ink=(236, 238, 240), floor=(40, 92, 176), cable=(36, 86, 168)),
}
WORDS = ['ARCHIVES 26', 'CÂBLES', 'PROTOS', 'SERVEUR 02', 'DISQUES', 'NE PAS JETER']


def grime(w, h, amount):
    n = rng.normal(0, 1, (h // 8 + 1, w // 8 + 1))
    n = np.asarray(Image.fromarray(((n - n.min()) / (np.ptp(n) + 1e-6) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)).astype(np.float32) / 255
    fine = rng.normal(0, 1, (h, w)) * 0.04
    return np.clip(1 - amount * np.clip(n - 0.45, 0, 1) * 1.8 + fine, 0.6, 1.05)


def label(word, pal, path):
    w, h = 900, 150
    col = Image.new('RGB', (w, h), pal['tape'])
    hgt = Image.new('L', (w, h), 0)
    f = ImageFont.truetype(FONT, 104)
    for im, fill in ((col, pal['ink']), (hgt, 255)):
        d = ImageDraw.Draw(im)
        tw = d.textlength(word, font=f)
        d.text(((w - tw) / 2, 14), word, font=f, fill=fill)
    a = np.asarray(col).astype(np.float32) * grime(w, h, 0.25)[..., None]
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(path + '.png')
    hgt.filter(ImageFilter.GaussianBlur(2.2)).save(path + '-relief.png')


def floor_tape(pal, path):
    w, h = 1200, 120
    if pal.get('hazard'):
        im = Image.new('RGB', (w, h), pal['floor'])
        d = ImageDraw.Draw(im)
        for x in range(-h, w + h, 90):
            d.polygon([(x, 0), (x + 45, 0), (x + 45 + h, h), (x + h, h)], fill=(22, 22, 20))
    else:
        im = Image.new('RGB', (w, h), pal['floor'])
    a = np.asarray(im).astype(np.float32) * grime(w, h, 0.55)[..., None]
    alpha = np.ones((h, w), np.float32)
    edge = (rng.random(w) < 0.06)
    for x in np.where(edge)[0]:
        alpha[: rng.integers(3, 12), x: x + rng.integers(4, 30)] = 0
    for x in np.where(rng.random(w) < 0.05)[0]:
        alpha[h - rng.integers(3, 12):, x: x + rng.integers(4, 30)] = 0
    rgba = np.dstack([np.clip(a, 0, 255), alpha * 255]).astype(np.uint8)
    Image.fromarray(rgba, 'RGBA').save(path + '.png')


def cable_tape(pal, path):
    w, h = 400, 200
    a = np.ones((h, w, 3), np.float32) * np.array(pal['cable'], np.float32)
    a *= grime(w, h, 0.35)[..., None]
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(path + '.png')


for name, pal in PALETTES.items():
    for i, wd in enumerate(WORDS):
        label(wd, pal, os.path.join(OUT, f'etiquette-{name}-{i}'))
    floor_tape(pal, os.path.join(OUT, f'marquage-{name}'))
    cable_tape(pal, os.path.join(OUT, f'scotch-{name}'))

# perforated sheet (round holes, staggered), alpha
n, pitch, r = 1024, 64, 19
im = Image.new('L', (n, n), 255)
d = ImageDraw.Draw(im)
for j in range(0, n // pitch + 1):
    for i in range(0, n // pitch + 1):
        cx = i * pitch + (pitch // 2 if j % 2 else 0)
        cy = j * pitch
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=0)
im.save(os.path.join(OUT, 'perfore-alpha.png'))
print('ok', len(os.listdir(OUT)))
