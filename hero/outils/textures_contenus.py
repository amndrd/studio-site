# Textures for the storage contents: label-maker labels, numbered archive labels, book spines,
# hanging-file tabs, paper-ream wrapper, printer screen. Writes hero/outils/textures-bureau/contenus/.
# usage: python -I textures_contenus.py <hero_dir>
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

H = sys.argv[1]
OUT = os.path.join(H, 'outils', 'textures-bureau', 'contenus')
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(11)
F_NARROW = '/System/Library/Fonts/Supplemental/Arial Narrow Bold.ttf'
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


# ------------------------------------------------------------------ label-maker labels (white tape, black print)
WORDS = {'archives-24': 'ARCHIVES 2024', 'archives-25': 'ARCHIVES 2025', 'factures': 'FACTURES', 'contrats': 'CONTRATS',
         'croquis': 'CROQUIS', 'projets-af': 'PROJETS A–F', 'projets-gm': 'PROJETS G–M', 'cables-usbc': 'CÂBLES USB-C',
         'cables-video': 'HDMI / DP', 'adaptateurs': 'ADAPTATEURS', 'disques': 'DISQUES', 'sauvegardes': 'SAUVEGARDES',
         'papier-a4': 'PAPIER A4', 'papier-a3': 'PAPIER A3', 'echantillons': 'ÉCHANTILLONS', 'manuels': 'MANUELS',
         'chargeurs': 'CHARGEURS', 'revues': 'REVUES', 'tirages': 'TIRAGES', 'reseau': 'RÉSEAU', 'divers': 'DIVERS',
         'cles': 'CLÉS USB', 'devis': 'DEVIS', 'notices': 'NOTICES'}
for slug, word in WORDS.items():
    w, h = 900, 150
    im = Image.new('RGB', (w, h), (234, 233, 228))
    d = ImageDraw.Draw(im)
    f = font(F_NARROW, 96)
    tw = d.textlength(word, font=f)
    d.text(((w - tw) / 2, 20), word, font=f, fill=(22, 22, 22))
    save(im, f'etiquette-{slug}.png', 0.22)

# ------------------------------------------------------------------ numbered archive labels (card in a holder)
for n in range(1, 13):
    w, h = 600, 420
    im = Image.new('RGB', (w, h), (236, 235, 230))
    d = ImageDraw.Draw(im)
    d.text((w - 40, h / 2 + 10), f'{n:02d}', font=font(F_HELV, 250, 1), fill=(20, 20, 20), anchor='rm')
    sf = font(F_NARROW, 34)
    for k, line in enumerate(['PROJETS', f'20{19 + (n + 1) // 2}', 'A' if n % 2 else 'B']):
        d.text((40, 70 + k * 52), line, font=sf, fill=(40, 40, 40))
    d.line((40, h - 70, w - 40, h - 70), fill=(60, 60, 60), width=3)
    save(im, f'numero-{n:02d}.png', 0.18)

# ------------------------------------------------------------------ book spines (fictional titles and imprints)
TITLES = ['Grilles', 'Systèmes de signes', 'Interfaces', 'Typographie appliquée', 'Lumière et matière', 'Forme',
          'Archives du plan', 'Structures légères', 'Code & image', 'Couleur', 'Espaces', 'Le détail', 'Objets ordinaires',
          'Prototypes', 'Échelles', 'Tracés', 'Modulaire', 'Signal', 'Volumes', 'Contraste', 'Béton', 'Écrans', 'Mesures', 'Atlas']
AUTHORS = ['M. Varenne', 'L. Okafor', 'S. Brandt', 'J. Ito', 'A. Moreau', 'K. Lindqvist', 'R. Duval', 'E. Novak']
PAL = [((0.86, 0.85, 0.81), (30, 30, 30)), ((0.05, 0.05, 0.055), (232, 230, 224)), ((0.62, 0.06, 0.05), (240, 236, 228)),
       ((0.85, 0.36, 0.08), (20, 20, 20)), ((0.03, 0.13, 0.55), (238, 238, 236)), ((0.5, 0.51, 0.5), (20, 20, 20)),
       ((0.86, 0.72, 0.12), (22, 22, 22)), ((0.08, 0.2, 0.15), (230, 228, 220)), ((0.55, 0.42, 0.28), (24, 22, 20)),
       ((0.78, 0.55, 0.55), (30, 26, 26)), ((0.2, 0.2, 0.22), (226, 160, 60)), ((0.92, 0.91, 0.88), (190, 40, 30))]
spines = []
for k, title in enumerate(TITLES):
    bg, ink = PAL[k % len(PAL)]
    bgc = tuple(int(c * 255) for c in bg)
    w, h = 180, 1200
    im = Image.new('RGB', (w, h), bgc)
    d = ImageDraw.Draw(im)
    style = k % 4
    if style == 1:
        d.rectangle((0, 36, w, 92), fill=ink)
    if style == 3:
        d.rectangle((0, h - 330, w, h), fill=tuple(255 - c // 3 for c in bgc))
    txt = Image.new('RGBA', (h, w), (0, 0, 0, 0))
    td = ImageDraw.Draw(txt)
    ft = font(F_HELV, 74 if len(title) < 14 else 60, 1)
    td.text((130, w / 2), title.upper() if style in (0, 2) else title, font=ft, fill=ink + (255,), anchor='lm')
    td.text((h - 330 if style != 3 else h - 300, w / 2), AUTHORS[k % len(AUTHORS)], font=font(F_HELV, 40), fill=(ink if style != 3 else (30, 30, 30)) + (255,), anchor='lm')
    rot = txt.rotate(-90, expand=True)
    im.paste(rot, (0, 0), rot)
    mark = [(w / 2 - 22, h - 80), (w / 2 + 22, h - 80), (w / 2, h - 118)] if k % 3 == 0 else None
    if mark:
        d.polygon(mark, fill=ink)
    elif k % 3 == 1:
        d.ellipse((w / 2 - 20, h - 120, w / 2 + 20, h - 80), outline=ink, width=6)
    else:
        d.rectangle((w / 2 - 18, h - 118, w / 2 + 18, h - 82), fill=ink)
    save(im, f'tranche-{k:02d}.png', 0.12)
    spines.append(dict(file=f'tranche-{k:02d}.png', color=bg, title=title))
json.dump(spines, open(os.path.join(OUT, 'tranches.json'), 'w'), ensure_ascii=False, indent=1)

# ------------------------------------------------------------------ hanging-file tabs
for k, word in enumerate(['CLIENTS', 'FACTURES', 'DEVIS', 'CONTRATS', '2025', '2024', 'ADMIN', 'BANQUE', 'NOTICES', 'DIVERS']):
    im = Image.new('RGB', (360, 110), (238, 238, 234))
    d = ImageDraw.Draw(im)
    d.text((180, 58), word, font=font(F_NARROW, 58), fill=(28, 28, 28), anchor='mm')
    save(im, f'onglet-{k}.png', 0.1)

# ------------------------------------------------------------------ paper ream wrapper (fictional brand)
im = Image.new('RGB', (1200, 260), (238, 238, 234))
d = ImageDraw.Draw(im)
d.rectangle((0, 0, 1200, 46), fill=(52, 70, 96))
d.rectangle((0, 214, 1200, 260), fill=(52, 70, 96))
d.text((60, 130), 'A4', font=font(F_HELV, 110, 1), fill=(30, 30, 30), anchor='lm')
d.text((250, 105), '80 g/m²', font=font(F_HELV, 52), fill=(40, 40, 40), anchor='lm')
d.text((250, 160), '500 feuilles · blanc', font=font(F_HELV, 40), fill=(70, 70, 70), anchor='lm')
d.text((1140, 130), 'papier de bureau', font=font(F_HELV, 44, 1), fill=(52, 70, 96), anchor='rm')
save(im, 'ramette.png', 0.08)

# ------------------------------------------------------------------ printer status screen
im = Image.new('RGB', (480, 270), (14, 16, 18))
d = ImageDraw.Draw(im)
d.text((240, 110), 'Prête', font=font(F_HELV, 64), fill=(220, 224, 228), anchor='mm')
d.text((240, 180), 'Wi-Fi · toner 64 %', font=font(F_HELV, 30), fill=(140, 146, 152), anchor='mm')
d.rectangle((40, 220, 440, 230), fill=(50, 54, 58))
d.rectangle((40, 220, 296, 230), fill=(170, 176, 182))
im.save(os.path.join(OUT, 'ecran-imprimante.png'))

# ------------------------------------------------------------------ labels added for the retained mix (own noise seed, the others stay identical)
rng = np.random.default_rng(12)
for slug, word in {'admin': 'ADMIN', 'banque': 'BANQUE', 'clients': 'CLIENTS'}.items():
    w, h = 900, 150
    im = Image.new('RGB', (w, h), (234, 233, 228))
    d = ImageDraw.Draw(im)
    f = font(F_NARROW, 96)
    d.text(((w - d.textlength(word, font=f)) / 2, 20), word, font=f, fill=(22, 22, 22))
    save(im, f'etiquette-{slug}.png', 0.22)
print('ok', len(os.listdir(OUT)))
