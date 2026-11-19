# Textures of the desk papers: the documents of two fictional clients of the studio, printed on paper and annotated by hand.
#   Printed: captures of papiers-contenus/pages (documents.py + capture.sh: Halde plan A2, section A3, site map, materials
#   board, quote; Ombelle homepage, mobile screens, brand guidelines, code), multiplied onto a paper grain, with red pencil,
#   pen and highlighter notes. Handwritten: two tracing overlays, meeting notes, to-do card, post-its.
#   Photo prints of the fictional renders (papiers-contenus/img, blender/rendus-fictifs.sh). No image of the desk or the lab.
# usage: python -I textures_papiers.py <hero_dir>   -> hero/outils/textures-bureau/papiers/
import math, os, random, re, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

H = os.path.abspath(sys.argv[1])
ROOT = os.path.dirname(H)
OUT = os.path.join(H, 'outils', 'textures-bureau', 'papiers')
os.makedirs(OUT, exist_ok=True)
R = random.Random(15)
NP = np.random.default_rng(15)
POL = os.path.join(ROOT, 'plan-du-site', 'polices')
F_NOTE = '/System/Library/Fonts/Noteworthy.ttc'
F_MARK = '/System/Library/Fonts/MarkerFelt.ttc'
F_HELV = '/System/Library/Fonts/HelveticaNeue.ttc'
F_MONO = '/System/Library/Fonts/Menlo.ttc'


def font(path, size, index=0):
    return ImageFont.truetype(path, size, index=index)


def inter(size, w=500):
    return ImageFont.truetype(os.path.join(POL, f'inter-latin-{w}-normal.woff2'), size)


def serif(size, italic=True):
    return ImageFont.truetype(os.path.join(POL, f'instrument-serif-latin-400-{"italic" if italic else "normal"}.woff2'), size)


# ------------------------------------------------------------------ paper and ink
def paper(w, h, col=(238, 237, 232), grain=5.0, edge=0.04):
    a = np.ones((h, w, 3), np.float32) * np.array(col, np.float32)
    n = NP.normal(0, 1, (h // 6 + 1, w // 6 + 1)).astype(np.float32)
    n = np.asarray(Image.fromarray(((n - n.min()) / (np.ptp(n) + 1e-6) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)).astype(np.float32) / 255 - 0.5
    a += (n * grain * 1.6 + NP.normal(0, grain * 0.35, (h, w)).astype(np.float32))[..., None]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.minimum(np.minimum(xx, w - xx) / w, np.minimum(yy, h - yy) / h)
    a *= (1 - edge * np.clip(1 - d / 0.03, 0, 1))[..., None]
    return a


class Sheet:
    """A paper base and an ink layer per colour; strokes are drawn on the ink layers, then composited."""

    def __init__(self, w, h, col=(238, 237, 232), transparent=False, grain=5.0):
        self.w, self.h = w, h
        self.base = None if transparent else paper(w, h, col, grain)
        self.layers = {}

    def ink(self, color=(28, 28, 32)):
        if color not in self.layers:
            self.layers[color] = Image.new('L', (self.w, self.h), 0)
        return self.layers[color]

    def draw(self, color=(28, 28, 32)):
        return ImageDraw.Draw(self.ink(color))

    def paste(self, im, xy, color=None):
        """Pastes an RGB image (print) onto the paper."""
        self.prints = getattr(self, 'prints', [])
        self.prints.append((im.convert('RGB'), xy))

    def save(self, name, blur=0.6, opacity=None):
        if self.base is None:      # tracing overlay: RGBA, ink only
            rgb = np.zeros((self.h, self.w, 3), np.float32)
            alpha = np.zeros((self.h, self.w), np.float32)
            for col, lay in self.layers.items():
                a = np.asarray(lay.filter(ImageFilter.GaussianBlur(blur))).astype(np.float32) / 255
                rgb = rgb * (1 - a[..., None]) + np.array(col, np.float32) * a[..., None]
                alpha = np.maximum(alpha, a)
            out = np.dstack([rgb, alpha * 255])
            Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGBA').save(os.path.join(OUT, name), optimize=True)
            return
        a = self.base.copy()
        for im, (x, y) in getattr(self, 'prints', []):
            p = np.asarray(im).astype(np.float32)
            ph, pw = p.shape[:2]
            a[y:y + ph, x:x + pw] = p * 0.93 + a[y:y + ph, x:x + pw] * 0.07
        for col, lay in self.layers.items():
            al = np.asarray(lay.filter(ImageFilter.GaussianBlur(blur))).astype(np.float32) / 255
            if opacity:
                al *= opacity.get(col, 1.0)
            if col in MULTIPLY:          # highlighter: multiplies
                a = a * (1 - al[..., None]) + a * (np.array(col, np.float32) / 255) * al[..., None]
            else:
                a = a * (1 - al[..., None]) + np.array(col, np.float32) * al[..., None]
        Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(os.path.join(OUT, name), optimize=True)


BLACK, PENCIL, BLUE, RED = (24, 24, 28), (88, 88, 92), (32, 56, 140), (170, 36, 30)
YELLOW, GREEN = (250, 236, 90), (150, 230, 140)
MULTIPLY = {YELLOW, GREEN}


def hline(d, p0, p1, w=3, j=1.2, over=0.0, passes=1, rng=R):
    """Hand-drawn line: jittered polyline with a slight overshoot."""
    (x0, y0), (x1, y1) = p0, p1
    L = math.hypot(x1 - x0, y1 - y0) + 1e-6
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    for _ in range(passes):
        o0, o1 = rng.uniform(-over, over) * L * 0.04, rng.uniform(0, over) * L * 0.06
        n = max(2, int(L / 45))
        bow = rng.uniform(-1, 1) * j * 1.5
        pts = []
        for i in range(n + 1):
            t = i / n
            x = x0 - ux * o0 + (x1 - x0 + ux * (o0 + o1)) * t
            y = y0 - uy * o0 + (y1 - y0 + uy * (o0 + o1)) * t
            s = math.sin(math.pi * t) * bow
            pts.append((x - uy * s + rng.gauss(0, j * 0.4), y + ux * s + rng.gauss(0, j * 0.4)))
        d.line(pts, fill=255, width=w, joint='curve')


def hrect(d, x0, y0, x1, y1, w=3, j=1.2, over=0.6, cross=False):
    for p, q in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        hline(d, p, q, w, j, over)
    if cross:
        hline(d, (x0, y0), (x1, y1), max(1, w - 1), j)
        hline(d, (x1, y0), (x0, y1), max(1, w - 1), j)


def hcircle(d, cx, cy, r, w=3, j=1.0, turns=1.08):
    n = int(40 + r / 4)
    ph = R.uniform(0, 6.28)
    pts = [(cx + (r + R.gauss(0, j)) * math.cos(ph + 2 * math.pi * turns * i / n), cy + (r + R.gauss(0, j)) * math.sin(ph + 2 * math.pi * turns * i / n)) for i in range(n + 1)]
    d.line(pts, fill=255, width=w, joint='curve')


def harrow(d, p0, p1, w=3):
    hline(d, p0, p1, w, 1.4)
    a = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    for s in (-1, 1):
        hline(d, p1, (p1[0] - 26 * math.cos(a + s * 0.45), p1[1] - 26 * math.sin(a + s * 0.45)), w, 0.6)


def write(sh, color, text, xy, size, fnt=F_NOTE, rot=None, idx=0, anchor='la'):
    """Handwritten (or typed) text drawn on the ink layer, with a small random tilt."""
    f = font(fnt, size, idx) if isinstance(fnt, str) else fnt
    tmp = Image.new('L', (int(f.getlength(text)) + 40, int(size * 1.8) + 20), 0)
    ImageDraw.Draw(tmp).text((20, 10), text, font=f, fill=255)
    rot = R.uniform(-2.5, 2.5) if rot is None else rot
    tmp = tmp.rotate(rot, expand=True, resample=Image.BICUBIC)
    x, y = xy
    if anchor == 'mm':
        x, y = x - tmp.width // 2, y - tmp.height // 2
    lay = sh.ink(color)
    region = lay.crop((x, y, x + tmp.width, y + tmp.height))
    lay.paste(Image.fromarray(np.maximum(np.asarray(region), np.asarray(tmp))), (x, y))


def typed(sh, color, text, xy, f, anchor='la'):
    sh.draw(color).text(xy, text, font=f, fill=255, anchor=anchor)


def highlight(sh, x0, y, x1, h=34, color=YELLOW):
    d = sh.draw(color)
    pts = [(x0, y + R.uniform(-2, 2)), (x1, y + R.uniform(-3, 3)), (x1, y + h), (x0, y + h + R.uniform(-2, 2))]
    d.polygon(pts, fill=200)


def edges(path, size, lo=4, hi=14):
    """Outline drawing of a render: gradient magnitude of the blurred luminance (ink = 0..255)."""
    im = Image.open(path).convert('L')
    im.thumbnail(size, Image.LANCZOS)
    a = np.asarray(im.filter(ImageFilter.GaussianBlur(1.1))).astype(np.float32)
    gx = np.abs(np.diff(a, axis=1, prepend=a[:, :1]))
    gy = np.abs(np.diff(a, axis=0, prepend=a[:1]))
    g = np.clip((np.hypot(gx, gy) - lo) / hi, 0, 1)
    return Image.fromarray((g * 255).astype(np.uint8))


def stamp(sh, color, ink, xy, gain=1.0):
    lay = sh.ink(color)
    x, y = xy
    region = np.asarray(lay.crop((x, y, x + ink.width, y + ink.height))).astype(np.float32)
    lay.paste(Image.fromarray(np.maximum(region, np.asarray(ink).astype(np.float32) * gain).clip(0, 255).astype(np.uint8)), (x, y))


def ruled(sh, top, step, x0=0, x1=None, color=(160, 190, 225), margin=None):
    d = sh.draw(color)
    for y in range(top, sh.h - 40, step):
        d.line((x0, y, x1 or sh.w, y), fill=170, width=2)
    if margin:
        sh.draw((225, 120, 120)).line((margin, 0, margin, sh.h), fill=170, width=2)


def dots(sh, step=48, color=(170, 170, 176)):
    d = sh.draw(color)
    for y in range(step, sh.h, step):
        for x in range(step, sh.w, step):
            d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=200)


def rouleau():
    sh = Sheet(1024, 512, (236, 236, 230), grain=4.0)
    d = sh.draw((150, 160, 175))
    for k in range(6):
        y = R.randint(40, 470)
        d.line((0, y, 1024, y + R.randint(-4, 4)), fill=90, width=2)
    sh.save('rouleau-exterieur.png', 1.0)
    b = Image.new('RGB', (512, 512), (226, 226, 220))
    d2 = ImageDraw.Draw(b)
    for k in range(40):
        r = 250 - k * 6
        d2.ellipse((256 - r, 256 - r, 256 + r, 256 + r), outline=(190 - k % 3 * 10,) * 3, width=2)
    b.save(os.path.join(OUT, 'rouleau-bout.png'))



CAP = os.path.join(H, 'outils', 'papiers-contenus', 'captures')
IMGF = os.path.join(H, 'outils', 'papiers-contenus', 'img')


def imprime(name, col=(242, 241, 236), toner=1.0):
    """A capture printed on paper: the paper grain shows through, the toner is slightly uneven."""
    im = Image.open(os.path.join(CAP, name + '.png')).convert('RGB')
    w, h = im.size
    sh = Sheet(w, h, col, grain=4.0)
    a = np.asarray(im.filter(ImageFilter.GaussianBlur(0.5))).astype(np.float32) / 255
    ink = 1 - a
    var = 1 - 0.025 * np.clip(NP.normal(0, 1, (h // 160 + 2, w // 160 + 2)), -2, 2)
    var = np.asarray(Image.fromarray(var.astype(np.float32)).resize((w, h), Image.BICUBIC))
    sh.base = np.clip(sh.base * (1 - ink * toner * var[..., None]), 0, 255)   # multiply: the ink darkens the paper
    return sh


def P(sh, u, v):
    return int(u * sh.w), int(v * sh.h)


def S_(sh, base=1240):
    return sh.w / base


# ------------------------------------------------------------------ printed and annotated
def plan_rdc():
    sh = imprime('plan-rdc')
    k = S_(sh, 1240)
    r = sh.draw(RED)
    cx, cy = P(sh, 2189 / 3368, 930 / 2382)
    hcircle(r, cx, cy, int(300 * k / 2.7), int(7 * k / 2.7), 4)
    write(sh, RED, '+ 60 cm ?', (cx + int(330 * k / 2.7), cy + int(120 * k / 2.7)), int(86 * k / 2.7))
    harrow(r, (cx + int(320 * k / 2.7), cy + int(150 * k / 2.7)), (cx + int(200 * k / 2.7), cy + int(60 * k / 2.7)), int(6 * k / 2.7))
    b = sh.draw(BLUE)
    x, y = P(sh, 880 / 3368, 1160 / 2382)
    write(sh, BLUE, 'cimaise mobile ok', (x - 200, y + 260), int(70 * k / 2.7))
    hline(b, (x - 200, y + 360), (x + 340, y + 352), 5, 1.2)
    write(sh, PENCIL, 'lumière nord : sheds', P(sh, 0.3, 0.07), int(66 * k / 2.7))
    sh.save('halde-plan-a2.png', 0.6)


def coupe_aa():
    sh = imprime('coupe-aa')
    write(sh, PENCIL, 'sous ferme : 5,70 ?', P(sh, 0.5, 0.36), 70)
    harrow(sh.draw(PENCIL), P(sh, 0.5, 0.39), P(sh, 0.42, 0.33), 6)
    hcircle(sh.draw(RED), *P(sh, 0.2, 0.51), 120, 6, 3)
    sh.save('halde-coupe-a3.png', 0.6)


def sitemap():
    sh = imprime('halde-sitemap')
    r = sh.draw(RED)
    for u in (0.135, 0.268, 0.528):
        x, y = P(sh, u, 0.24)
        hline(r, (x, y), (x + 22, y + 26), 7, 0.4)
        hline(r, (x + 22, y + 26), (x + 64, y - 36), 7, 0.4)
    hcircle(sh.draw(BLUE), *P(sh, 0.423, 0.285), 165, 6, 3)
    write(sh, BLUE, 'priorité lot 1', P(sh, 0.36, 0.48), 74)
    sh.save('halde-sitemap-a3.png', 0.5)


def materiaux():
    sh = imprime('halde-materiaux')
    write(sh, PENCIL, 'terrazzo : échantillon reçu', P(sh, 0.06, 0.88), 66)
    sh.save('halde-materiaux-a3.png', 0.5)


def devis():
    sh = imprime('devis', (246, 246, 243))
    write(sh, PENCIL, 'v2 : visite 3D en option ?', P(sh, 0.08, 0.8), 52)
    sh.save('halde-devis-a4.png', 0.5)


def accueil():
    sh = imprime('ombelle-accueil', (246, 246, 243))
    r = sh.draw(RED)
    hcircle(r, *P(sh, 0.21, 0.215), 250, 7, 4)
    write(sh, RED, 'plus grand !', P(sh, 0.3, 0.085), 84)
    harrow(r, P(sh, 0.62, 0.47), P(sh, 0.52, 0.53), 7)
    write(sh, RED, 'recadrer serré', P(sh, 0.6, 0.43), 84)
    x0, y0 = P(sh, 0.245, 0.342)                                  # the « Écouter un extrait » button
    hline(r, (x0, y0), (x0 + 215, y0 - 4), 6, 0.6)
    write(sh, RED, 'à retirer', (x0 + 230, y0 - 50), 70)
    sh.save('ombelle-accueil-a3.png', 0.5)


def mobile():
    sh = imprime('ombelle-mobile', (246, 246, 243))
    write(sh, PENCIL, 'ok pour la v3', P(sh, 0.07, 0.94), 64)
    sh.save('ombelle-mobile-a4.png', 0.5)


def charte():
    sh = imprime('ombelle-charte', (246, 246, 243))
    sh.save('ombelle-charte-a4.png', 0.5)


def code():
    sh = imprime('code', (247, 247, 244))
    for line in (20, 21, 37, 44):
        y = int(sh.h * (56 + (line - 1) * 12.31) / 842)            # line pitch of the printed listing (7.6 px x 1.62)
        highlight(sh, int(sh.w * 0.12), y, int(sh.w * 0.82), int(sh.h * 11 / 842))
    write(sh, BLUE, 'dispose() !', P(sh, 0.66, 0.52), 64)
    harrow(sh.draw(BLUE), P(sh, 0.65, 0.55), P(sh, 0.55, 0.6), 5)
    write(sh, BLUE, 'debounce ?', P(sh, 0.68, 0.79), 64)
    sh.save('ombelle-code-a4.png', 0.4)


# ------------------------------------------------------------------ handwritten
def calque_halde():
    W, Hh = 2480, 1754
    sh = Sheet(W, Hh, transparent=True)
    p = sh.draw(PENCIL)
    hrect(p, 260, 240, 2220, 1500, 6, 2.5)
    hrect(p, 1240, 240, 1260, 760, 5, 1)
    hrect(p, 1420, 560, 2000, 650, 5, 1.5)
    for k in range(10):
        hline(sh.draw(RED), (1430 + k * 58, 650), (1480 + k * 58, 560), 4, 0.6)
    for x in range(1450, 2150, 230):
        for y in (900, 1180):
            hcircle(p, x, y, 70, 4, 1.5)
            for dx, dy in ((0, -110), (0, 110), (-110, 0), (110, 0)):
                hrect(p, x + dx - 30, y + dy - 30, x + dx + 30, y + dy + 30, 3, 0.8)
    hrect(p, 2100, 700, 2190, 1460, 5, 1.5)
    write(sh, BLUE, 'variante 2 : banquette continue', (1300, 1540), 70)
    write(sh, RED, 'comptoir + 60', (1500, 430), 66)
    write(sh, PENCIL, '32 places', (1800, 1340), 60)
    for k in range(3):
        hcircle(p, 520 + k * 300, 1120, 26, 3, 0.6)
    write(sh, PENCIL, 'socles', (480, 1220), 56)
    sh.save('calque-halde.png', 0.8)


def calque_enceinte():
    W, Hh = 1240, 1754
    sh = Sheet(W, Hh, transparent=True)
    e = edges(os.path.join(IMGF, 'ombelle-sauge.png'), (1000, 1100), 4, 13)
    stamp(sh, BLACK, e, (90, 380), 1.6)
    notes = [('plateau chêne 12', (700, 330), (560, 520)), ('rayon 18', (860, 760), (850, 900)), ('tissu laine', (120, 260), (380, 760)),
             ('bouton laiton Ø 32', (700, 200), (640, 470))]
    for t, xy, tip in notes:
        write(sh, BLUE, t, xy, 54)
        hline(sh.draw(BLUE), (xy[0] + 20, xy[1] + 70), tip, 3, 1)
    write(sh, BLACK, 'One — face 3/4', (90, 110), 70, F_MARK)
    sh.save('calque-enceinte.png', 0.7)


def notes_reunion():
    sh = Sheet(1240, 1754, (246, 246, 242), grain=3.0)
    ruled(sh, 260, 66, margin=150)
    write(sh, BLACK, 'Halde — réunion du 14/11', (180, 110), 62)
    lines = ['- visite 3D : mode guidé d’abord', '- photos des expos : le 20/11', '- billetterie : API à confirmer', '- palette béton / chêne / laiton',
             '- comptoir : +60 cm, revoir plan', '- mise en ligne visée : mars', '- devis 118 : ok sur le principe']
    for k, t in enumerate(lines):
        write(sh, BLUE, t, (180, 250 + k * 132), 50)
    hcircle(sh.draw(RED), 560, 250 + 5 * 132 + 40, 330, 4, 3)
    sh.save('notes-halde.png', 0.5)


def fiche():
    sh = Sheet(1480, 1050, (246, 245, 240), grain=3.0)
    ruled(sh, 190, 72, margin=150)
    write(sh, BLACK, 'Semaine 47', (190, 60), 64, F_MARK)
    items = [('x', 'Ombelle : GLB sous 4 Mo'), ('', 'Ombelle : photos teinte Encre'), ('x', 'Halde : plans A2 à jour'), ('', 'Halde : relancer devis 118'),
             ('', 'facturer acompte Ombelle'), ('', 'tester visite 3D sur mobile'), ('x', 'commander papier calque')]
    for k, (c, t) in enumerate(items):
        y = 175 + k * 72
        hrect(sh.draw(BLACK), 190, y + 18, 226, y + 54, 3, 0.6, 0.2)
        if c:
            hline(sh.draw(BLUE), (194, y + 36), (208, y + 52), 4, 0.3)
            hline(sh.draw(BLUE), (208, y + 52), (236, y + 8), 4, 0.3)
        write(sh, BLUE if c else BLACK, t, (250, y), 46)
    sh.save('fiche-semaine.png', 0.5)


F_BRAD = '/System/Library/Fonts/Supplemental/Bradley Hand Bold.ttf'


def postits():
    """Sticky notes written with a ballpoint: small handwriting (x-height about 4 mm on a 76 mm note), drifting baseline,
    a word crossed out, an underline, a drawn arrow or tick. Two hands: Noteworthy (light) and Bradley Hand."""
    cols = {'jaune': (246, 226, 120), 'vert': (176, 222, 164), 'rose': (246, 176, 198), 'bleu': (156, 202, 238)}
    notes = {
        # on the Ombelle homepage printout
        'jaune': (F_NOTE, BLUE, ['Accueil v4', '– hero en 4:5', '– titre + grand', '– retirer « écouter »', 'voir Léa jeudi'], {'underline': 0, 'tick': 4, 'strike': None}),
        # on the folded configurator code
        'rose': (F_BRAD, BLACK, ['configurateur :', 'dispose() au', 'changement de teinte', 'fuite mémoire ?'], {'underline': None, 'arrow': 3, 'strike': None}),
        'vert': (F_NOTE, BLACK, ['GLB < 4 Mo', 'draco + ktx2', 'tester iPhone 12', 'et Safari 17'], {'underline': 0, 'strike': 3}),
        'bleu': (F_BRAD, BLUE, ['RDV Ombelle 10h', 'apporter', 'échantillons tissu', '+ devis v2'], {'underline': 0, 'strike': None}),
    }
    for k, c in cols.items():
        sh = Sheet(600, 600, c, grain=4.0)
        fnt_, ink, lines, marks = notes[k]
        size = 40 if fnt_ == F_NOTE else 33
        y = 72
        x0 = 52
        for n, t in enumerate(lines):
            x = x0 + (34 if t.startswith('–') or n == len(lines) - 1 and marks.get('arrow') == n else 0) + R.randint(-4, 4)
            rot = R.uniform(-2.2, 1.2) + n * 0.4
            write(sh, ink, t, (x, int(y)), size, fnt_, rot=rot)
            f = font(fnt_, size)
            wpx = int(f.getlength(t))
            l_, top, r_, bot = f.getbbox(t)                      # real glyph box (these fonts have a tall line height)
            base = int(y) + 10 + bot                                # write() draws the text 10 px under its anchor
            mid = int(y) + 10 + (top + bot) // 2
            if marks.get('underline') == n:
                hline(sh.draw(ink), (x + 18, base + 7), (x + 18 + wpx, base + 3), 3, 0.8)
            if marks.get('strike') == n:
                hline(sh.draw(ink), (x + 16, mid + 2), (x + 26 + wpx, mid - 3), 3, 0.6)
            if marks.get('tick') == n:
                d = sh.draw(ink)
                tx = x + wpx + 46
                hline(d, (tx, int(y) + 40), (tx + 12, int(y) + 56), 4, 0.3)
                hline(d, (tx + 12, int(y) + 56), (tx + 40, int(y) + 14), 4, 0.3)
            if marks.get('arrow') == n:
                harrow(sh.draw(ink), (x0, int(y) + 36), (x - 6, int(y) + 36), 3)
            y += size * 1.55 + R.uniform(-3, 5)
        sh.save(f'postit-{k}.png', 0.55, opacity={ink: 0.92})


def tirages():
    for name, size in (('halde-maquette', (1500, 1000)), ('ombelle-trio', (1500, 1000)), ('ombelle-sauge', (1000, 1300))):
        im = Image.open(os.path.join(IMGF, name + '.png')).convert('RGB')
        W, Hh = size
        b = 40
        iw, ih = W - 2 * b, Hh - 2 * b
        r = max(iw / im.width, ih / im.height)
        im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
        im = im.crop(((im.width - iw) // 2, (im.height - ih) // 2, (im.width - iw) // 2 + iw, (im.height - ih) // 2 + ih))
        out = Image.new('RGB', (W, Hh), (242, 242, 238))
        out.paste(im, (b, b))
        out.save(os.path.join(OUT, f'tirage-{name}.png'), optimize=True)



for fn in (plan_rdc, coupe_aa, sitemap, materiaux, devis, accueil, mobile, charte, code, calque_halde, calque_enceinte, notes_reunion, fiche,
           postits, tirages, rouleau):
    fn()
    print(fn.__name__, flush=True)
print('ok', len(os.listdir(OUT)))
