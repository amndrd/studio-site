# Generates the paper / screen textures used on the plans table and the desk.
# usage: python -I papiers.py <out_dir> <fonts_dir>
import math, os, random, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import numpy as np

out, fonts = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
R = random.Random(7)


def font(name, size):
    return ImageFont.truetype(os.path.join(fonts, name), size)


MONO = 'jetbrains-mono-latin-400-normal.woff2'
MONO5 = 'jetbrains-mono-latin-500-normal.woff2'
SANS = 'inter-latin-500-normal.woff2'
SERIF = 'instrument-serif-latin-400-italic.woff2'


def fnt(name, size):
    try:
        return font(name, size)
    except Exception:
        return ImageFont.load_default()


def paper_base(w, h, color, grain=10, stains=2):
    a = np.zeros((h, w, 3), np.float32)
    a[:] = color
    n = np.random.default_rng(R.randint(0, 9999)).normal(0, grain, (h, w, 1))
    a += n
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    # soft blotches
    for _ in range(stains):
        m = Image.new('L', (w, h), 0)
        d = ImageDraw.Draw(m)
        cx, cy, r = R.randint(0, w), R.randint(0, h), R.randint(w // 10, w // 4)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=R.randint(14, 30))
        m = m.filter(ImageFilter.GaussianBlur(r / 2))
        dark = Image.new('RGB', (w, h), (90, 70, 40))
        img = Image.composite(dark, img, m)
    return img


def wobble_line(d, p0, p1, fill, width, amp=1.2):
    n = max(2, int(math.dist(p0, p1) / 12))
    pts = []
    for i in range(n + 1):
        t = i / n
        x = p0[0] + (p1[0] - p0[0]) * t + R.uniform(-amp, amp)
        y = p0[1] + (p1[1] - p0[1]) * t + R.uniform(-amp, amp)
        pts.append((x, y))
    d.line(pts, fill=fill, width=width, joint='curve')


def scribble(d, x, y, w, fill, width=3, lines=1, h=26):
    for li in range(lines):
        yy = y + li * h * 1.5
        xx = x
        lw = w * R.uniform(0.55, 1.0)
        pts = []
        while xx < x + lw:
            pts.append((xx, yy + R.uniform(-h * .35, h * .35)))
            xx += R.uniform(6, 14)
        if len(pts) > 1:
            d.line(pts, fill=fill, width=width, joint='curve')


def dims(d, x0, y0, x1, y1, col, f, label):
    d.line([(x0, y0), (x1, y1)], fill=col, width=2)
    for (x, y) in [(x0, y0), (x1, y1)]:
        d.line([(x - 8, y + 8), (x + 8, y - 8)], fill=col, width=2)
    d.text(((x0 + x1) / 2, (y0 + y1) / 2 - 26), label, fill=col, font=f, anchor='mm')


def title_block(d, w, h, col, f, fs, title, ref):
    bx, by = w - 640, h - 210
    d.rectangle([bx, by, w - 60, h - 60], outline=col, width=3)
    d.line([(bx, by + 60), (w - 60, by + 60)], fill=col, width=2)
    d.line([(bx + 380, by + 60), (bx + 380, h - 60)], fill=col, width=2)
    d.text((bx + 20, by + 14), title, fill=col, font=f)
    d.text((bx + 20, by + 80), 'ÉCH. 1:50', fill=col, font=fs)
    d.text((bx + 20, by + 112), 'DESS. A.D.', fill=col, font=fs)
    d.text((bx + 400, by + 80), ref, fill=col, font=fs)
    d.text((bx + 400, by + 112), 'FEUILLE 2/7', fill=col, font=fs)


def frame(d, w, h, col):
    d.rectangle([40, 40, w - 40, h - 40], outline=col, width=4)
    d.rectangle([60, 60, w - 60, h - 60], outline=col, width=2)


# ---------- blueprints ----------
def blueprint_floorplan(name, seed):
    R.seed(seed)
    w, h = 2048, 1448
    img = paper_base(w, h, (28, 72, 140), grain=7, stains=3)
    d = ImageDraw.Draw(img)
    col = (214, 228, 250)
    faint = (90, 130, 190)
    for x in range(60, w - 60, 48):
        d.line([(x, 60), (x, h - 60)], fill=faint, width=1)
    for y in range(60, h - 60, 48):
        d.line([(60, y), (w - 60, y)], fill=faint, width=1)
    frame(d, w, h, col)
    f, fs = fnt(MONO5, 34), fnt(MONO, 24)
    # rooms
    x0, y0 = 200, 180
    rooms = []
    xs = [x0, x0 + R.randint(380, 520), x0 + R.randint(820, 980), 1500]
    ys = [y0, y0 + R.randint(380, 480), 1080]
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            rooms.append((xs[i], ys[j], xs[i + 1], ys[j + 1]))
    for r in rooms:
        d.rectangle(r, outline=col, width=9)
    # doors (arcs)
    for r in rooms[:4]:
        cx, cy = r[0] + 90, r[3]
        d.rectangle([cx - 4, cy - 6, cx + 80, cy + 6], fill=(28, 72, 140))
        d.arc([cx - 80, cy - 80, cx + 80, cy + 80], 270, 360, fill=col, width=3)
    # big circle (the fan) on one wall
    cx, cy = xs[-1], (ys[0] + ys[-1]) // 2
    d.ellipse([cx - 120, cy - 120, cx + 120, cy + 120], outline=col, width=4)
    for k in range(7):
        a = k * 2 * math.pi / 7
        d.line([(cx, cy), (cx + 110 * math.cos(a), cy + 110 * math.sin(a))], fill=col, width=3)
    dims(d, xs[0], ys[-1] + 70, xs[-1], ys[-1] + 70, col, fs, f'{(xs[-1]-xs[0])/100:.2f} m')
    dims(d, xs[0] - 70, ys[0], xs[0] - 70, ys[-1], col, fs, '')
    for r in rooms:
        d.text(((r[0] + r[2]) / 2, (r[1] + r[3]) / 2), R.choice(['ATELIER', 'STOCK', 'LABO', 'SERRE', 'BUREAU', 'TECH.', 'ARCHIVES']), fill=col, font=f, anchor='mm')
    title_block(d, w, h, col, f, fs, 'NIVEAU -2 · PLAN', f'REF. B-{seed:03d}')
    img.save(os.path.join(out, name), quality=92)


def blueprint_mechanical(name, seed):
    R.seed(seed)
    w, h = 2048, 1448
    img = paper_base(w, h, (24, 64, 128), grain=7, stains=3)
    d = ImageDraw.Draw(img)
    col = (214, 228, 250)
    frame(d, w, h, col)
    f, fs = fnt(MONO5, 34), fnt(MONO, 24)
    # front view of a fan / gear
    cx, cy, rr = 640, 680, 420
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=col, width=6)
    d.ellipse([cx - rr + 40, cy - rr + 40, cx + rr - 40, cy + rr - 40], outline=col, width=2)
    d.ellipse([cx - 70, cy - 70, cx + 70, cy + 70], outline=col, width=5)
    nb = R.choice([5, 6, 7, 8])
    for k in range(nb):
        a = k * 2 * math.pi / nb
        pts = []
        for t in np.linspace(0, 1, 12):
            rad = 80 + t * (rr - 70)
            ang = a + 0.35 * t + 0.18
            pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
        for t in np.linspace(1, 0, 12):
            rad = 80 + t * (rr - 70)
            ang = a + 0.35 * t - 0.18 - 0.25 * t
            pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
        d.line(pts + [pts[0]], fill=col, width=3)
    d.line([(cx - rr - 60, cy), (cx + rr + 60, cy)], fill=col, width=1)
    d.line([(cx, cy - rr - 60), (cx, cy + rr + 60)], fill=col, width=1)
    dims(d, cx - rr, cy + rr + 80, cx + rr, cy + rr + 80, col, fs, 'Ø 5 500')
    # side section
    sx = 1300
    d.rectangle([sx, cy - rr, sx + 260, cy + rr], outline=col, width=5)
    d.rectangle([sx + 90, cy - 70, sx + 230, cy + 70], outline=col, width=4)
    for k in range(-3, 4):
        d.line([(sx + 20, cy + k * 110), (sx + 240, cy + k * 110 + 30)], fill=col, width=2)
    dims(d, sx, cy - rr - 60, sx + 260, cy - rr - 60, col, fs, '1 200')
    title_block(d, w, h, col, f, fs, 'VENTILATION · V-01', f'REF. M-{seed:03d}')
    img.save(os.path.join(out, name), quality=92)


# ---------- white technical drawings ----------
def tech_drawing(name, seed):
    R.seed(seed)
    w, h = 2048, 1448
    img = paper_base(w, h, (236, 232, 222), grain=6, stains=2)
    d = ImageDraw.Draw(img)
    col = (40, 40, 46)
    light = (150, 150, 155)
    frame(d, w, h, col)
    f, fs = fnt(MONO5, 32), fnt(MONO, 22)
    # elevation: a section through a vaulted room
    bx, by, bw, bh = 220, 260, 1100, 760
    d.line([(bx, by + bh), (bx + bw, by + bh)], fill=col, width=6)
    d.arc([bx, by, bx + bw, by + bh * 1.6], 180, 360, fill=col, width=6)
    d.arc([bx + 40, by + 40, bx + bw - 40, by + bh * 1.6 - 40], 180, 360, fill=col, width=2)
    for k in range(1, 9):
        x = bx + k * bw / 9
        wobble_line(d, (x, by + bh), (x, by + bh - R.randint(60, 300)), light, 2, 0.6)
    # hatch ground
    for x in range(bx - 80, bx + bw + 80, 26):
        d.line([(x, by + bh + 10), (x + 30, by + bh + 50)], fill=light, width=2)
    dims(d, bx, by + bh + 110, bx + bw, by + bh + 110, col, fs, '9 000')
    # detail circles
    for i in range(3):
        cx, cy = 1500 + (i % 2) * 220, 330 + i * 230
        d.ellipse([cx - 90, cy - 90, cx + 90, cy + 90], outline=col, width=3)
        d.text((cx, cy), f'D{i+1}', fill=col, font=f, anchor='mm')
        wobble_line(d, (cx - 90, cy), (bx + bw - R.randint(50, 400), by + R.randint(100, 600)), light, 2)
    # notes
    for i in range(6):
        scribble(d, 1420, 900 + i * 40, 420, (70, 70, 80), 2, 1, 14)
    title_block(d, w, h, col, f, fs, 'COUPE A-A', f'REF. T-{seed:03d}')
    img.save(os.path.join(out, name), quality=92)


def wireframe(name, seed):
    R.seed(seed)
    w, h = 1448, 2048
    img = paper_base(w, h, (240, 238, 232), grain=5, stains=1)
    d = ImageDraw.Draw(img)
    ink = (30, 30, 36)
    grey = (170, 170, 175)
    f, fs = fnt(SANS, 34), fnt(MONO, 22)
    # three phone frames
    for i in range(2):
        px, py, pw, ph = 120 + i * 640, 160, 540, 1080
        d.rounded_rectangle([px, py, px + pw, py + ph], 60, outline=ink, width=6)
        d.rounded_rectangle([px + 190, py + 24, px + 350, py + 52], 14, fill=ink)
        y = py + 110
        d.rectangle([px + 40, y, px + pw - 40, y + 260], outline=ink, width=3)
        d.line([(px + 40, y), (px + pw - 40, y + 260)], fill=grey, width=2)
        d.line([(px + pw - 40, y), (px + 40, y + 260)], fill=grey, width=2)
        y += 300
        for k in range(5):
            d.rectangle([px + 40, y, px + 120, y + 80], outline=ink, width=3)
            d.line([(px + 150, y + 20), (px + pw - 60 - R.randint(0, 160), y + 20)], fill=ink, width=6)
            d.line([(px + 150, y + 56), (px + pw - 160 - R.randint(0, 120), y + 56)], fill=grey, width=5)
            y += 110
        d.rounded_rectangle([px + 40, py + ph - 120, px + pw - 40, py + ph - 50], 30, fill=ink)
    # arrow between
    wobble_line(d, (660, 700), (760, 700), (200, 60, 50), 5)
    d.polygon([(760, 685), (790, 700), (760, 715)], fill=(200, 60, 50))
    # notes in red
    for i in range(5):
        scribble(d, 140, 1340 + i * 70, 1100, (190, 50, 45) if i == 0 else ink, 3, 1, 22)
    d.text((140, 1290), 'PARCOURS · V2', fill=ink, font=f)
    # site layout bottom
    d.rectangle([140, 1720, 1300, 1950], outline=ink, width=3)
    for k in range(4):
        d.rectangle([170 + k * 280, 1750, 400 + k * 280, 1920], outline=grey, width=3)
    img.save(os.path.join(out, name), quality=92)


def site_wireframe(name, seed):
    R.seed(seed)
    w, h = 2048, 1448
    img = paper_base(w, h, (238, 236, 230), grain=5, stains=1)
    d = ImageDraw.Draw(img)
    ink = (34, 34, 40)
    grey = (165, 165, 172)
    f = fnt(SANS, 40)
    d.rectangle([120, 120, w - 120, h - 120], outline=ink, width=5)
    d.rectangle([120, 120, w - 120, 210], outline=ink, width=3)
    for k in range(5):
        d.line([(1100 + k * 150, 165), (1200 + k * 150, 165)], fill=ink, width=6)
    d.rectangle([180, 270, 1100, 760], outline=ink, width=4)
    d.text((220, 320), 'HERO', fill=ink, font=f)
    scribble(d, 220, 420, 700, ink, 4, 3, 30)
    d.rounded_rectangle([220, 640, 470, 710], 30, fill=ink)
    d.rectangle([1160, 270, w - 180, 760], outline=grey, width=4)
    d.line([(1160, 270), (w - 180, 760)], fill=grey, width=2)
    d.line([(w - 180, 270), (1160, 760)], fill=grey, width=2)
    for k in range(3):
        x = 180 + k * 580
        d.rectangle([x, 820, x + 520, 1240], outline=ink, width=4)
        scribble(d, x + 30, 1100, 440, grey, 4, 2, 24)
    wobble_line(d, (1500, 900), (1900, 560), (195, 55, 45), 5)
    d.ellipse([1880, 520, 1960, 600], outline=(195, 55, 45), width=5)
    img.save(os.path.join(out, name), quality=92)


def topo_map(name, seed):
    R.seed(seed)
    w, h = 2048, 1448
    img = paper_base(w, h, (226, 214, 186), grain=7, stains=4)
    a = np.asarray(img).astype(np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    z = np.zeros_like(xx)
    rng = np.random.default_rng(seed)
    for _ in range(7):
        cx, cy, s, amp = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(150, 500), rng.uniform(-1, 1)
        z += amp * np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * s * s))
    lines = np.abs(((z * 18) % 1.0) - 0.5) < 0.035
    a[lines] = a[lines] * 0.55 + np.array([120, 80, 50]) * 0.45
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    for _ in range(6):
        x, y = R.randint(0, w), R.randint(0, h)
        pts = [(x, y)]
        for _ in range(30):
            x += R.randint(-30, 90)
            y += R.randint(-60, 60)
            pts.append((x, y))
        d.line(pts, fill=(170, 60, 50), width=5, joint='curve')
    for _ in range(14):
        x, y = R.randint(200, w - 200), R.randint(200, h - 200)
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=(30, 30, 30))
    d.rectangle([40, 40, w - 40, h - 40], outline=(80, 60, 40), width=4)
    img.save(os.path.join(out, name), quality=92)


def graph_sketch(name, seed):
    R.seed(seed)
    w, h = 1448, 2048
    img = paper_base(w, h, (242, 240, 234), grain=4, stains=1)
    d = ImageDraw.Draw(img)
    g = (190, 205, 220)
    for x in range(0, w, 40):
        d.line([(x, 0), (x, h)], fill=g, width=1)
    for y in range(0, h, 40):
        d.line([(0, y), (w, y)], fill=g, width=1)
    ink = (36, 40, 70)
    # a sketched box object in perspective
    cx, cy = 720, 700
    pts = [(cx - 300, cy), (cx, cy - 150), (cx + 300, cy), (cx, cy + 150)]
    for i in range(4):
        wobble_line(d, pts[i], pts[(i + 1) % 4], ink, 4, 2.5)
        wobble_line(d, pts[i], (pts[i][0], pts[i][1] + 320), ink, 4, 2.5)
    for i in range(3):
        wobble_line(d, (pts[i][0], pts[i][1] + 320), (pts[i + 1][0], pts[i + 1][1] + 320), ink, 4, 2.5)
    d.ellipse([cx - 90, cy - 50, cx + 90, cy + 50], outline=ink, width=4)
    for i in range(10):
        scribble(d, 140, 1260 + i * 60, 1150, ink, 3, 1, 20)
    wobble_line(d, (1000, 500), (1200, 330), (190, 50, 45), 5)
    d.text((1060, 260), '?', fill=(190, 50, 45), font=fnt(SERIF, 120))
    img.save(os.path.join(out, name), quality=92)


def code_listing(name, seed):
    R.seed(seed)
    w, h = 1448, 2048
    img = paper_base(w, h, (244, 242, 236), grain=4, stains=1)
    d = ImageDraw.Draw(img)
    f = fnt(MONO, 30)
    words = ['const', 'scene', 'camera', 'render', 'await', 'load', 'fan', 'light', 'mesh', 'return', 'if', 'for', 'export', 'function', 'uniform', 'vec3', 'float', 'mix', 'time', 'speed']
    y = 120
    ind = 0
    for i in range(54):
        if R.random() < 0.15:
            ind = max(0, ind + R.choice([-1, 1]))
        line = ' '.join(R.choice(words) for _ in range(R.randint(2, 7)))
        d.text((110 + ind * 60, y), f'{i+1:>3}  ' + line, fill=(40, 40, 50), font=f)
        y += 34
    # red pen marks
    for _ in range(4):
        yy = R.randint(160, 1900)
        wobble_line(d, (100, yy), (1300, yy + R.randint(-6, 6)), (195, 50, 45), 4)
    d.ellipse([900, 600, 1250, 720], outline=(195, 50, 45), width=5)
    img.save(os.path.join(out, name), quality=92)


def sticky(name, color, seed):
    R.seed(seed)
    w = h = 512
    img = paper_base(w, h, color, grain=5, stains=0)
    d = ImageDraw.Draw(img)
    for i in range(R.randint(2, 4)):
        scribble(d, 50, 110 + i * 90, 400, (40, 40, 60), 6, 1, 26)
    img.save(os.path.join(out, name), quality=92)


def photo(name, seed):
    R.seed(seed)
    w, h = 1024, 1220
    img = Image.new('RGB', (w, h), (240, 238, 232))
    rng = np.random.default_rng(seed)
    pw, ph = 900, 900
    yy, xx = np.mgrid[0:ph, 0:pw].astype(np.float32)
    base = np.zeros((ph, pw, 3), np.float32)
    c1 = np.array(R.choice([(40, 50, 60), (70, 60, 40), (30, 45, 40)]), np.float32)
    c2 = np.array(R.choice([(200, 190, 160), (160, 180, 190), (210, 170, 120)]), np.float32)
    t = np.clip((yy / ph) * 0.8 + rng.normal(0, .02, (ph, pw)), 0, 1)[..., None]
    base = c1 * (1 - t) + c2 * t
    # silhouettes of a structure
    for _ in range(5):
        x0 = rng.uniform(0, pw); wd = rng.uniform(40, 200); ht = rng.uniform(200, 700)
        base[int(ph - ht):, int(x0):int(x0 + wd)] *= 0.35
    base += rng.normal(0, 8, base.shape)
    ph_img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))
    img.paste(ph_img, (62, 62))
    d = ImageDraw.Draw(img)
    scribble(d, 90, 1060, 600, (40, 40, 60), 5, 1, 24)
    img.save(os.path.join(out, name), quality=92)


def kraft(name, seed):
    R.seed(seed)
    img = paper_base(1448, 2048, (176, 140, 98), grain=9, stains=3)
    d = ImageDraw.Draw(img)
    d.text((140, 180), 'CONFIDENTIEL', fill=(120, 40, 35), font=fnt(MONO5, 90))
    d.rectangle([120, 160, 820, 290], outline=(120, 40, 35), width=6)
    for i in range(5):
        scribble(d, 140, 420 + i * 60, 900, (60, 45, 35), 4, 1, 20)
    img.save(os.path.join(out, name), quality=92)


# ---------- screens ----------
def screen_terminal(name, seed, color=(110, 255, 150), bg=(4, 14, 8)):
    R.seed(seed)
    w, h = 1024, 768
    img = Image.new('RGB', (w, h), bg)
    d = ImageDraw.Draw(img)
    f = fnt(MONO, 24)
    y = 30
    for i in range(24):
        txt = R.choice(['> build scene --lab', 'compiling shaders ........ ok', 'fan.rpm = 420', 'load assets 74/74', 'net: link up 1Gb', 'temp 21.4 C  hum 48%', '[ok] sensors', 'deploy staging', 'render 1920x1080', '$ git commit -m "v2"'])
        if R.random() < .3:
            txt = ''.join(R.choice('0123456789ABCDEF ') for _ in range(R.randint(10, 40)))
        d.text((40, y), txt, fill=color, font=f)
        y += 30
    d.rectangle([40, y + 4, 56, y + 30], fill=color)
    # scanlines
    a = np.asarray(img).astype(np.float32)
    a[::3] *= 0.65
    img = Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
    glow = img.filter(ImageFilter.GaussianBlur(6))
    img = ImageChops.add(img, glow, scale=1.6)
    img.save(os.path.join(out, name), quality=92)


def screen_graph(name, seed):
    R.seed(seed)
    w, h = 1024, 768
    img = Image.new('RGB', (w, h), (6, 10, 14))
    d = ImageDraw.Draw(img)
    c = (90, 200, 255)
    for x in range(0, w, 64):
        d.line([(x, 0), (x, h)], fill=(18, 34, 46), width=1)
    for y in range(0, h, 64):
        d.line([(0, y), (w, y)], fill=(18, 34, 46), width=1)
    for k, col in enumerate([(90, 200, 255), (255, 170, 80)]):
        pts = []
        v = h * (0.4 + 0.2 * k)
        for x in range(0, w, 8):
            v += R.uniform(-14, 14)
            v = min(max(v, 80), h - 80)
            pts.append((x, v))
        d.line(pts, fill=col, width=3)
    d.text((30, 24), 'FLUX · SALLE V-01', fill=c, font=fnt(MONO5, 28))
    img = ImageChops.add(img, img.filter(ImageFilter.GaussianBlur(5)), scale=1.4)
    img.save(os.path.join(out, name), quality=92)


def screen_ui(name, seed):
    R.seed(seed)
    w, h = 1280, 800
    img = Image.new('RGB', (w, h), (16, 17, 20))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 220, h], fill=(24, 25, 30))
    for i in range(8):
        d.rounded_rectangle([24, 90 + i * 60, 196, 126 + i * 60], 8, fill=(40, 42, 50) if i else (230, 120, 60))
    for i in range(3):
        x = 260 + i * 330
        d.rounded_rectangle([x, 60, x + 300, 300], 18, fill=(30, 32, 38))
        d.text((x + 24, 84), R.choice(['Projets', 'Rendus', 'Build', 'Visiteurs']), fill=(200, 200, 210), font=fnt(SANS, 26))
        d.text((x + 24, 150), str(R.randint(12, 980)), fill=(240, 240, 245), font=fnt(SANS, 64))
    d.rounded_rectangle([260, 330, w - 40, h - 40], 18, fill=(30, 32, 38))
    pts = [(300 + k * 30, 700 - 300 * abs(math.sin(k / 5)) - R.randint(0, 60)) for k in range(30)]
    d.line(pts, fill=(230, 120, 60), width=5)
    img.save(os.path.join(out, name), quality=92)


blueprint_floorplan('plan-bleu-1.jpg', 11)
blueprint_floorplan('plan-bleu-2.jpg', 23)
blueprint_mechanical('plan-bleu-ventilo.jpg', 5)
blueprint_mechanical('plan-bleu-meca.jpg', 41)
tech_drawing('plan-coupe-1.jpg', 3)
tech_drawing('plan-coupe-2.jpg', 17)
wireframe('maquette-appli.jpg', 8)
site_wireframe('maquette-site.jpg', 9)
site_wireframe('maquette-site-2.jpg', 31)
topo_map('carte-1.jpg', 12)
topo_map('carte-2.jpg', 44)
graph_sketch('croquis-1.jpg', 2)
graph_sketch('croquis-2.jpg', 19)
code_listing('listing-1.jpg', 4)
kraft('dossier-kraft.jpg', 6)
sticky('postit-jaune.jpg', (240, 214, 90), 1)
sticky('postit-rose.jpg', (238, 150, 160), 2)
sticky('postit-bleu.jpg', (140, 200, 230), 3)
sticky('postit-orange.jpg', (240, 160, 80), 4)
photo('photo-1.jpg', 1)
photo('photo-2.jpg', 2)
photo('photo-3.jpg', 3)
screen_terminal('ecran-terminal-vert.jpg', 1)
screen_terminal('ecran-terminal-ambre.jpg', 2, (255, 176, 70), (16, 8, 2))
screen_graph('ecran-graphe.jpg', 3)
screen_ui('ecran-interface.jpg', 4)
print('ok', len(os.listdir(out)))


def chalkboard(name, seed):
    R.seed(seed)
    w, h = 2048, 1300
    img = paper_base(w, h, (34, 46, 40), grain=6, stains=5)
    d = ImageDraw.Draw(img)
    chalk = (215, 220, 210)
    cx, cy, rr = 520, 600, 330
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=chalk, width=6)
    for k in range(7):
        a = k * 2 * math.pi / 7
        wobble_line(d, (cx, cy), (cx + rr * 0.9 * math.cos(a + .3), cy + rr * 0.9 * math.sin(a + .3)), chalk, 5, 2)
    for i in range(3):
        bx = 1000 + i * 300
        d.rectangle([bx, 300, bx + 220, 460], outline=chalk, width=5)
        if i < 2:
            wobble_line(d, (bx + 225, 380), (bx + 295, 380), chalk, 5, 1.5)
    for i in range(7):
        scribble(d, 1000, 620 + i * 70, 860, chalk, 4, 1, 22)
    d.text((1000, 150), 'V-01 → V-02 ?', fill=chalk, font=fnt(SERIF, 90))
    img = img.filter(ImageFilter.GaussianBlur(0.6))
    img.save(os.path.join(out, name), quality=92)


def cork(name, seed):
    R.seed(seed)
    w, h = 2048, 1300
    a = np.zeros((h, w, 3), np.float32)
    rng = np.random.default_rng(seed)
    a[:] = (150, 104, 62)
    a += rng.normal(0, 22, (h, w, 1))
    for _ in range(9000):
        x, y = rng.integers(0, w), rng.integers(0, h)
        a[max(0, y - 2):y + 2, max(0, x - 2):x + 2] *= rng.uniform(0.6, 1.2)
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
    img.save(os.path.join(out, name), quality=92)


def pegboard(name):
    w, h = 1024, 1024
    img = Image.new('RGB', (w, h), (120, 92, 64))
    a = np.asarray(img).astype(np.float32) + np.random.default_rng(1).normal(0, 6, (h, w, 1))
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    for x in range(16, w, 32):
        for y in range(16, h, 32):
            d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(18, 14, 10))
    img.save(os.path.join(out, name), quality=92)


chalkboard('tableau-noir.jpg', 3)
cork('liege.jpg', 5)
pegboard('perfore.jpg')
print('ok+', len(os.listdir(out)))
