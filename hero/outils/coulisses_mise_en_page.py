# Behind the scenes (17/11, pistes A and C retained): the captures of blender/rendus-coulisses.sh (_bruts/coulisses)
# filed into one structured folder, hero/bureau/coulisses/, without any text on the images:
#   A-interface/      the Blender window as it is: wireframe, clay, material preview, render, the material's nodes;
#   C-decomposition/  the same view without interface: wireframe (as a light drawing on the black of the site), clay,
#                     material preview, render (studio grade), the four stages in bands, a diagonal cut wireframe / render;
# each in site-16-9/ (A 2880 x 1620, C 3840 x 2160) and instagram-4-5/ (1080 x 1350), one folder per view.
# usage: python -I coulisses_mise_en_page.py <hero_dir>
import os, sys
import numpy as np
from PIL import Image, ImageDraw

H = os.path.abspath(sys.argv[1])
RAW = os.path.join(H, 'outils', 'blender', '_bruts', 'coulisses')
OUT = os.path.join(H, 'bureau', 'coulisses')
BG = (13, 13, 15)
VUES = [('ensemble', '1-ensemble'), ('poste', '2-le-poste'), ('arriere', '3-derriere-le-bureau'), ('dessus', '4-le-dessus-du-bureau'),
        ('lampe', '5-la-lampe'), ('cables', '6-les-cables')]
A_ST = ['1-fil-de-fer', '2-argile', '3-materiaux', '4-rendu', '5-noeuds']
C_ST = ['1-fil-de-fer', '2-argile', '3-materiaux', '4-rendu']
FMTS = [('169', 'site-16-9'), ('45', 'instagram-4-5')]
SIZE = {('A', '169'): (2880, 1620), ('A', '45'): (1080, 1350), ('C', '169'): (3840, 2160), ('C', '45'): (1080, 1350)}
DONE = []


def save(im, *p):
    path = os.path.join(OUT, *p)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.convert('RGB').save(path, optimize=True)
    DONE.append(path)


def fit(im, w, h):
    """Scaled to cover w x h, centred crop."""
    r = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def grade(im, vig=0.22, start=0.4, ell=0.8, grain=0.012, floor=0.4, seed=1):
    """The studio grade of the prototypes (finition.py): vignette and grain, for the final render only."""
    a = np.asarray(im.convert('RGB')).astype(np.float32) / 255.0
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 * ell + ((yy - h / 2) / (h / 2)) ** 2 * ell)
    a *= (1.0 - vig * np.clip(r - start, 0, None) ** 1.6)[..., None]
    g = np.random.default_rng(seed).normal(0, grain, (h, w, 1)).astype(np.float32)
    a += g * (floor + (1 - floor) * np.sqrt(np.clip(a.mean(axis=2, keepdims=True), 0, 1)))
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))


def trait(im):
    """The wireframe as a drawing: Blender draws dark lines on a dark grey; the grey becomes the black of the site and the
    lines turn light (the darker a line, the lighter it gets)."""
    a = np.asarray(im.convert('RGB')).astype(np.float32).mean(axis=2) / 255.0
    bg = float(np.median(a))
    k = np.clip(1.0 - a / max(bg, 1e-3), 0, 1) ** 0.8
    out = np.array(BG, np.float32)[None, None, :] + k[..., None] * (np.array((226, 224, 218), np.float32) - np.array(BG, np.float32))[None, None, :]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def bands(ims):
    """The four stages side by side in bands of the same image, thin light separators, no text."""
    W, Hh = ims[0].size
    c = Image.new('RGB', (W, Hh))
    n = len(ims)
    for k, im in enumerate(ims):
        x0, x1 = round(W * k / n), round(W * (k + 1) / n)
        c.paste(im.crop((x0, 0, x1, Hh)), (x0, 0))
    d = ImageDraw.Draw(c, 'RGBA')
    wl = max(2, round(3 * max(W, Hh) / 3840))
    for k in range(1, n):
        x = round(W * k / n)
        d.line((x, 0, x, Hh), fill=(240, 238, 232, 200), width=wl)
    return c


def diagonal(a, b):
    """Wireframe on the upper left, render on the lower right, cut along a diagonal, no text."""
    W, Hh = a.size
    mask = Image.new('L', (W, Hh), 0)
    ImageDraw.Draw(mask).polygon([(W * 0.62, 0), (W, 0), (W, Hh), (W * 0.38, Hh)], fill=255)
    c = Image.composite(b, a, mask)
    d = ImageDraw.Draw(c, 'RGBA')
    d.line((W * 0.62, 0, W * 0.38, Hh), fill=(240, 238, 232, 220), width=max(2, round(4 * max(W, Hh) / 3840)))
    return c


def piste_a():
    for vue, dossier in VUES:
        for fmt, fd in FMTS:
            sfx = '' if fmt == '169' else '-45'
            for st in A_ST:
                p = os.path.join(RAW, f'ui-{vue}-{st}{sfx}.png')
                if os.path.exists(p):
                    save(fit(Image.open(p).convert('RGB'), *SIZE[('A', fmt)]), 'A-interface', fd, dossier, f'{st}.png')


def piste_c():
    for vue, dossier in VUES:
        for fmt, fd in FMTS:
            ims = []
            for st in C_ST:
                p = os.path.join(RAW, f'net-{vue}-{fmt}-{st}.png')
                if not os.path.exists(p):
                    break
                im = Image.open(p).convert('RGB')
                im = trait(im) if st == '1-fil-de-fer' else (grade(im) if st == '4-rendu' else im)
                ims.append(fit(im, *SIZE[('C', fmt)]))
            if len(ims) < 4:
                continue
            for st, im in zip(C_ST, ims):
                save(im, 'C-decomposition', fd, dossier, f'{st}.png')
            save(bands(ims), 'C-decomposition', fd, dossier, '5-les-quatre-etapes.png')
            save(diagonal(ims[0], ims[3]), 'C-decomposition', fd, dossier, '6-diagonale.png')


piste_a()
piste_c()
print(len(DONE), 'images dans', os.path.relpath(OUT, H))
