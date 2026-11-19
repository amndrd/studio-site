# Textures for the decor around the desk (step 10, 16/11): label-maker labels for the cartons (same white tape, black
# print as the storage contents), the black ink print of a shipping carton (this side up, fragile, keep dry, the
# corrugated board stamp) and a parcel label from a fictional sender (Ombelle, the speaker client of the papers).
# Writes hero/outils/textures-bureau/autour/.
# usage: python -I textures_autour.py <hero_dir>
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

H = sys.argv[1]
OUT = os.path.join(H, 'outils', 'textures-bureau', 'autour')
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(23)
F_NARROW = '/System/Library/Fonts/Supplemental/Arial Narrow Bold.ttf'
F_BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
F_HELV = '/System/Library/Fonts/HelveticaNeue.ttc'
F_MONO = '/System/Library/Fonts/Menlo.ttc'


def font(path, size, index=0):
    return ImageFont.truetype(path, size, index=index)


def grime(w, h, amount, scale=8):
    n = rng.normal(0, 1, (h // scale + 1, w // scale + 1))
    n = np.asarray(Image.fromarray(((n - n.min()) / (np.ptp(n) + 1e-6) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)).astype(np.float32) / 255
    return np.clip(1 - amount * np.clip(n - 0.45, 0, 1) * 1.8 + rng.normal(0, 1, (h, w)) * 0.03, 0.6, 1.05)


def save(im, name, dirt=0.2):
    a = np.asarray(im.convert('RGB')).astype(np.float32) * grime(im.width, im.height, dirt)[..., None]
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(os.path.join(OUT, name), optimize=True)


# ------------------------------------------------------------------ label-maker labels for the cartons
WORDS = {'emballages': 'EMBALLAGES', 'archives-23': 'ARCHIVES 2023', 'ombelle-protos': 'OMBELLE · PROTOS',
         'halde-echantillons': 'HALDE · ÉCHANTILLONS', 'cables': 'CÂBLES', 'lampes': 'LAMPES', 'ecrans': 'CARTONS ÉCRANS',
         'maquettes': 'MAQUETTES', 'tirages-a2': 'TIRAGES A2', 'studio': 'STUDIO · DIVERS'}
for slug, word in WORDS.items():
    w, h = 900, 150
    im = Image.new('RGB', (w, h), (234, 233, 228))
    d = ImageDraw.Draw(im)
    f = font(F_NARROW, 96)
    while d.textlength(word, font=f) > w - 60:
        f = font(F_NARROW, f.size - 4)
    tw = d.textlength(word, font=f)
    d.text(((w - tw) / 2, (h - f.size) / 2 - 6), word, font=f, fill=(22, 22, 22))
    save(im, f'etiquette-{slug}.png', 0.22)


# ------------------------------------------------------------------ the ink print of a shipping carton (RGBA, black ink)
def ink(d, xy, txt, f, fill=(20, 18, 16, 235)):
    d.text(xy, txt, font=f, fill=fill)


W, Hh = 1200, 600
im = Image.new('RGBA', (W, Hh), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
INK = (24, 20, 17, 230)
# this side up: two arrows over a bar
x0, y0 = 70, 90
for k in range(2):
    x = x0 + k * 90
    d.polygon([(x + 35, y0), (x + 70, y0 + 60), (x + 50, y0 + 60), (x + 50, y0 + 170), (x + 20, y0 + 170), (x + 20, y0 + 60), (x, y0 + 60)], fill=INK)
d.rectangle([x0 - 10, y0 + 190, x0 + 170, y0 + 212], fill=INK)
d.rectangle([x0 - 30, y0 - 30, x0 + 190, y0 + 240], outline=INK, width=8)
# fragile: a stemmed glass
gx, gy = 340, 60
d.rectangle([gx, gy, gx + 220, gy + 270], outline=INK, width=8)
d.polygon([(gx + 60, gy + 40), (gx + 160, gy + 40), (gx + 150, gy + 120), (gx + 120, gy + 150), (gx + 100, gy + 150), (gx + 70, gy + 120)], fill=INK)
d.rectangle([gx + 104, gy + 150, gx + 116, gy + 215], fill=INK)
d.rectangle([gx + 75, gy + 215, gx + 145, gy + 228], fill=INK)
d.line([(gx + 100, gy + 40), (gx + 115, gy + 75), (gx + 98, gy + 95)], fill=(0, 0, 0, 0), width=7)
# keep dry: umbrella and drops
ux, uy = 620, 60
d.rectangle([ux, uy, ux + 220, uy + 270], outline=INK, width=8)
d.pieslice([ux + 30, uy + 70, ux + 190, uy + 230], 180, 360, fill=INK)
d.rectangle([ux + 106, uy + 150, ux + 114, uy + 225], fill=INK)
d.arc([ux + 86, uy + 205, ux + 114, uy + 240], 0, 180, fill=INK, width=8)
for (px, py) in ((ux + 45, uy + 35), (ux + 110, uy + 22), (ux + 170, uy + 38)):
    d.polygon([(px, py), (px + 9, py + 20), (px - 9, py + 20)], fill=INK)
    d.ellipse([px - 9, py + 13, px + 9, py + 31], fill=INK)
# the box maker's round stamp
cx, cy, r = 1010, 190, 150
d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=8)
d.ellipse([cx - r + 26, cy - r + 26, cx + r - 26, cy + r - 26], outline=INK, width=4)
f1, f2 = font(F_BOLD, 34), font(F_BOLD, 26)
for txt, yy, ff in (('CARTON', cy - 70, f1), ('DOUBLE', cy - 28, f1), ('CANNELURE', cy + 10, f1), ('BC · 32 ECT', cy + 52, f2)):
    tw = d.textlength(txt, font=ff)
    ink(d, (cx - tw / 2, yy), txt, ff, INK)
f3 = font(F_NARROW, 64)
ink(d, (60, 400), 'HAUT  ·  FRAGILE  ·  CRAINT L’HUMIDITÉ', f3, INK)
ink(d, (60, 480), 'MAX. 25 KG  ·  60 × 40 × 40 CM', font(F_NARROW, 54), INK)
a = np.asarray(im).astype(np.float32)
a[..., 3] *= np.clip(grime(W, Hh, 0.45, 5), 0, 1)                  # worn ink, absorbed by the board
Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(os.path.join(OUT, 'carton-pictos.png'), optimize=True)

# ------------------------------------------------------------------ parcel label (10 x 15 cm), fictional sender and carrier
w, h = 1000, 1500
im = Image.new('RGB', (w, h), (240, 239, 234))
d = ImageDraw.Draw(im)
fb, fr, fm = font(F_BOLD, 46), font(F_HELV, 38), font(F_MONO, 34)
d.rectangle([20, 20, w - 20, h - 20], outline=(20, 20, 20), width=6)
d.text((50, 50), 'COURSIER NORD · EXPRESS 24H', font=font(F_BOLD, 40), fill=(20, 20, 20))
d.line([(20, 120), (w - 20, 120)], fill=(20, 20, 20), width=5)
d.text((50, 150), 'EXPÉDITEUR', font=font(F_BOLD, 30), fill=(20, 20, 20))
for i, line in enumerate(['Ombelle Audio', '9 rue des Tanneurs', '69007 Lyon']):
    d.text((50, 195 + i * 48), line, font=fr, fill=(20, 20, 20))
d.line([(20, 360), (w - 20, 360)], fill=(20, 20, 20), width=5)
d.text((50, 390), 'DESTINATAIRE', font=font(F_BOLD, 30), fill=(20, 20, 20))
for i, line in enumerate(['STUDIO', 'Niveau −2, accès quai B', '69002 Lyon']):
    d.text((50, 440 + i * 62), line, font=font(F_BOLD, 54) if i == 0 else font(F_HELV, 46), fill=(20, 20, 20))
d.line([(20, 660), (w - 20, 660)], fill=(20, 20, 20), width=5)
d.text((50, 690), 'COLIS 2 / 4', font=font(F_BOLD, 80), fill=(20, 20, 20))
d.text((600, 705), '7,4 kg', font=font(F_BOLD, 64), fill=(20, 20, 20))
d.text((50, 800), 'Prototypes enceintes · fragile', font=fr, fill=(20, 20, 20))
# barcode (interleaved bars) and its number
code = '7 41 0393 2817 5562'
bx0, by0 = 70, 900
x = bx0
r2 = np.random.default_rng(5)
while x < w - 90:
    bw = int(r2.choice([4, 4, 8, 12]))
    if r2.random() > 0.42:
        d.rectangle([x, by0, x + bw - 1, by0 + 330], fill=(15, 15, 15))
    x += bw
d.text((90, by0 + 345), code, font=font(F_MONO, 50), fill=(20, 20, 20))
d.text((50, h - 110), 'CN 7410 3932 FR   ·   16.11.2026', font=fm, fill=(20, 20, 20))
save(im, 'etiquette-colis.png', 0.15)
print('ok', len(os.listdir(OUT)))

