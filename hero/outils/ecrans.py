# Contemporary screen contents and tracing-paper plans for the v2 lab.
# usage: python -I ecrans.py <out_dir> <fonts_dir> <renders_dir>
import math, os, random, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

out, fonts, renders = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
R = random.Random(3)


def F(name, size):
    return ImageFont.truetype(os.path.join(fonts, name), size)


MONO = 'jetbrains-mono-latin-400-normal.woff2'
SANS = 'inter-latin-500-normal.woff2'
SANS4 = 'inter-latin-400-normal.woff2'
SANS6 = 'inter-latin-600-normal.woff2'

BG, PANEL, LINE = (18, 19, 22), (26, 27, 31), (40, 42, 48)
ACC = (255, 122, 69)
SYN = [(197, 134, 192), (86, 156, 214), (206, 145, 120), (78, 201, 176), (220, 220, 170), (156, 220, 254), (212, 212, 212)]


def code_editor(name):
    w, h = 2560, 1440
    im = Image.new('RGB', (w, h), BG)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 72, h], fill=(14, 15, 17))
    d.rectangle([72, 0, 520, h], fill=PANEL)
    f, fs = F(MONO, 26), F(SANS4, 24)
    for i, n in enumerate(['src', '  scene', '    labo.ts', '    fan.ts', '    lights.ts', '  ui', '    hotspots.tsx', '    menu.tsx', 'public', '  models', 'package.json', 'astro.config.mjs']):
        d.text((100, 80 + i * 44), n, fill=(200, 200, 205) if i != 3 else (255, 255, 255), font=fs)
    d.rectangle([520, 0, w, 56], fill=(22, 23, 26))
    for i, t in enumerate(['fan.ts', 'lights.ts', 'hotspots.tsx']):
        d.rectangle([520 + i * 260, 0, 520 + (i + 1) * 260 - 2, 56], fill=BG if i == 0 else (22, 23, 26))
        d.text((548 + i * 260, 14), t, fill=(230, 230, 230) if i == 0 else (140, 140, 150), font=fs)
    y = 90
    ind = 0
    for i in range(36):
        d.text((560, y), f'{i + 1:>3}', fill=(90, 92, 100), font=f)
        x = 660 + ind * 34
        for _ in range(R.randint(1, 6)):
            wd = R.randint(40, 220)
            d.rounded_rectangle([x, y + 8, x + wd, y + 26], 4, fill=R.choice(SYN))
            x += wd + 18
            if x > 2300:
                break
        if R.random() < .25:
            ind = max(0, min(4, ind + R.choice([-1, 1])))
        y += 36
    d.rectangle([2160, 56, w, h], fill=(22, 23, 26))
    d.rectangle([520, h - 300, 2160, h], fill=(14, 15, 17))
    d.text((548, h - 286), 'TERMINAL', fill=(140, 140, 150), font=fs)
    for i in range(6):
        d.text((548, h - 240 + i * 36), R.choice(['> astro dev', '  ready in 412 ms', '  ➜ local: http://localhost:4321', '✓ 74 modèles optimisés (meshopt + ktx2)', '✓ build 1.8 s']), fill=(170, 220, 170), font=f)
    im.save(os.path.join(out, name), quality=92)


def design_tool(name):
    w, h = 2560, 1440
    im = Image.new('RGB', (w, h), (30, 30, 30))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w, 64], fill=(44, 44, 44))
    d.rectangle([0, 64, 300, h], fill=(44, 44, 44))
    d.rectangle([w - 340, 64, w, h], fill=(44, 44, 44))
    fs = F(SANS4, 22)
    for i in range(14):
        d.text((24, 96 + i * 40), R.choice(['Frame', 'Hero', 'Zones', 'Menu', 'Card', 'Mobile', 'Button']), fill=(200, 200, 200), font=fs)
    for i in range(3):
        x0 = 420 + i * 640
        d.rectangle([x0, 160, x0 + 560, 1260], fill=(245, 245, 245))
        d.rectangle([x0, 160, x0 + 560, 520], fill=(18, 20, 24) if i != 1 else (235, 230, 222))
        d.ellipse([x0 + 200, 260, x0 + 360, 420], outline=(240, 240, 240) if i != 1 else (40, 40, 40), width=6)
        for k in range(5):
            d.rectangle([x0 + 40, 580 + k * 120, x0 + 40 + R.randint(200, 460), 610 + k * 120], fill=(200, 200, 205))
        d.rounded_rectangle([x0 + 40, 1160, x0 + 260, 1220], 30, fill=ACC)
        d.text((x0, 124), ['Hero · desktop', 'Projet · cas', 'Contact'][i], fill=(180, 180, 180), font=fs)
    d.rectangle([1060, 150, 1630, 1270], outline=(24, 160, 251), width=4)
    for i in range(10):
        d.rectangle([w - 310, 110 + i * 70, w - 40, 140 + i * 70], fill=(60, 60, 60))
    im.save(os.path.join(out, name), quality=92)


def viewport3d(name):
    w, h = 2560, 1440
    im = Image.new('RGB', (w, h), (40, 40, 42))
    d = ImageDraw.Draw(im)
    for x in range(-2000, 4000, 80):
        d.line([(x, h), (w / 2 + (x - w / 2) * 0.25, h * 0.45)], fill=(52, 52, 55), width=2)
    for k in range(14):
        y = h * 0.45 + (h * 0.55) * (k / 14) ** 1.6
        d.line([(0, y), (w, y)], fill=(52, 52, 55), width=2)
    cx, cy, r = w * 0.5, h * 0.42, 420
    d.ellipse([cx - r - 40, cy - r - 40, cx + r + 40, cy + r + 40], outline=(230, 230, 230), width=4)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(160, 160, 160), width=2)
    for k in range(10):
        a = 2 * math.pi * k / 10
        pts = []
        for t in [i / 12 for i in range(13)]:
            rr = 80 + t * (r - 80)
            ang = a + 0.5 * t
            pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
        pts2 = []
        for t in [i / 12 for i in range(12, -1, -1)]:
            rr = 80 + t * (r - 80)
            ang = a + 0.5 * t + 0.22 + 0.1 * t
            pts2.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
        d.line(pts + pts2 + [pts[0]], fill=(255, 160, 90) if k == 0 else (210, 210, 210), width=3)
    d.ellipse([cx - 80, cy - 80, cx + 80, cy + 80], outline=(230, 230, 230), width=4)
    d.rectangle([0, 0, w, 56], fill=(30, 30, 32))
    d.rectangle([w - 420, 56, w, h], fill=(34, 34, 36))
    fs = F(SANS4, 22)
    for i, t in enumerate(['Ventilateur V-02', '  pales ×10', '  moyeu', '  carénage', 'Lumières', 'Caméras', 'Brume']):
        d.text((w - 390, 90 + i * 40), t, fill=(210, 210, 210), font=fs)
    im.save(os.path.join(out, name), quality=92)


def dashboard(name):
    w, h = 2560, 1440
    im = Image.new('RGB', (w, h), (12, 13, 16))
    d = ImageDraw.Draw(im)
    f1, f2 = F(SANS4, 26), F(SANS6, 72)
    for i in range(4):
        x = 80 + i * 610
        d.rounded_rectangle([x, 80, x + 570, 330], 18, fill=(22, 23, 28))
        d.text((x + 36, 110), ['Requêtes / min', 'Temps de réponse', 'Disponibilité', 'Déploiements'][i], fill=(150, 150, 160), font=f1)
        d.text((x + 36, 180), ['2 418', '86 ms', '99,98 %', '14'][i], fill=(240, 240, 245), font=f2)
    d.rounded_rectangle([80, 380, 1640, 1360], 18, fill=(22, 23, 28))
    for k, col in enumerate([(90, 170, 255), ACC]):
        pts, v = [], 900 - 150 * k
        for x in range(120, 1600, 14):
            v += R.uniform(-22, 22)
            v = min(max(v, 480), 1300)
            pts.append((x, v))
        d.line(pts, fill=col, width=4)
    d.rounded_rectangle([1700, 380, 2480, 1360], 18, fill=(22, 23, 28))
    for i in range(12):
        d.rectangle([1740, 430 + i * 74, 1740 + R.randint(160, 680), 470 + i * 74], fill=(40, 120, 90) if i % 4 else (160, 70, 50))
    im.save(os.path.join(out, name), quality=92)


def terminal(name):
    w, h = 2560, 1440
    im = Image.new('RGB', (w, h), (10, 11, 12))
    d = ImageDraw.Draw(im)
    f = F(MONO, 30)
    y = 60
    for i in range(36):
        t = R.choice(['$ ssh labo@rack-02', 'load average: 0.42 0.38 0.35', '● nginx.service  active (running)', '● api.service    active (running)',
                      'GET /api/projets 200 12ms', 'POST /api/contact 201 31ms', 'backup ok · 2026-11-14 03:00', 'disk /data 41 % used', '$ docker ps', 'web  api  db  queue  — up 12 days'])
        d.text((60, y), t, fill=(200, 220, 200) if not t.startswith('$') else (255, 255, 255), font=f)
        y += 38
    im.save(os.path.join(out, name), quality=92)


def app_screen(name, kind, w=1200, h=1600):
    im = Image.new('RGB', (w, h), (248, 246, 242) if kind != 'dark' else (16, 17, 20))
    d = ImageDraw.Draw(im)
    f1, f2, f3 = F(SANS6, 64), F(SANS4, 34), F(SANS, 30)
    ink = (20, 20, 22) if kind != 'dark' else (240, 240, 240)
    if kind == 'menu':
        d.text((70, 90), 'Trattoria Sofia', fill=ink, font=f1)
        d.text((70, 180), 'Carte · Midi', fill=(120, 120, 120), font=f2)
        for i in range(6):
            y = 300 + i * 200
            d.rounded_rectangle([70, y, 250, y + 160], 20, fill=[(196, 120, 80), (120, 150, 90), (210, 180, 120), (160, 80, 60), (90, 120, 150), (200, 150, 90)][i])
            d.text((290, y + 20), R.choice(['Burrata', 'Risotto', 'Tagliata', 'Tiramisù', 'Linguine', 'Carpaccio']), fill=ink, font=f3)
            d.text((290, y + 70), f'{R.randint(9, 24)},00 €', fill=(120, 120, 120), font=f2)
    elif kind == 'booking':
        d.text((70, 90), 'Réserver', fill=ink, font=f1)
        for r_ in range(5):
            for c in range(7):
                x, y = 70 + c * 150, 260 + r_ * 150
                on = R.random() < .3
                d.rounded_rectangle([x, y, x + 120, y + 120], 24, fill=ACC if on else (232, 230, 226))
        d.rounded_rectangle([70, 1420, w - 70, 1520], 50, fill=(20, 20, 22))
    else:
        d.text((70, 90), 'Projets', fill=ink, font=f1)
        for i in range(4):
            y = 260 + i * 320
            d.rounded_rectangle([70, y, w - 70, y + 280], 30, fill=(32, 33, 38))
            d.rectangle([110, y + 40, 520, y + 240], fill=(60, 64, 72))
    im.save(os.path.join(out, name), quality=92)


def tracing(name, seed):
    """Plan drawing on transparent tracing paper (RGBA)."""
    rr = random.Random(seed)
    w, h = 2048, 1448
    im = Image.new('RGBA', (w, h), (248, 248, 244, 120))
    d = ImageDraw.Draw(im)
    ink = (30, 32, 40, 255)
    x0, y0 = 200, 180
    for _ in range(9):
        a, b = rr.randint(150, 1700), rr.randint(150, 1100)
        d.rectangle([a, b, a + rr.randint(150, 500), b + rr.randint(120, 400)], outline=ink, width=rr.choice([7, 12]))
    for _ in range(14):
        a, b = rr.randint(100, 1900), rr.randint(100, 1300)
        d.line([(a, b), (a + rr.randint(-400, 400), b + rr.randint(-300, 300))], fill=(30, 32, 40, 230), width=5)
    cx, cy = rr.randint(500, 1500), rr.randint(400, 1000)
    d.ellipse([cx - 160, cy - 160, cx + 160, cy + 160], outline=(220, 70, 40, 255), width=10)
    d.text((240, h - 160), f'CALQUE {seed:02d}', fill=ink, font=F(MONO, 40))
    im.save(os.path.join(out, name))


def prints_from_renders(prefix):
    srcs = [p for p in sorted(os.listdir(renders)) if p.endswith('.png')]
    n = 0
    for p in srcs:
        im = Image.open(os.path.join(renders, p)).convert('RGB')
        w, h = im.size
        crop = im.crop((w // 6, h // 6, w // 6 + int(h * 0.7), h // 6 + int(h * 0.7) * 3 // 4)).resize((800, 600))
        card = Image.new('RGB', (860, 720), (245, 244, 240))
        card.paste(crop, (30, 30))
        card.save(os.path.join(out, f'{prefix}-{n:02d}.jpg'), quality=88)
        n += 1
        if n >= 8:
            break


code_editor('ecran-code.jpg')
design_tool('ecran-design.jpg')
viewport3d('ecran-3d.jpg')
dashboard('ecran-dashboard.jpg')
terminal('ecran-terminal-serveur.jpg')
app_screen('tablette-menu.jpg', 'menu')
app_screen('tablette-reservation.jpg', 'booking')
app_screen('telephone-projets.jpg', 'dark', 900, 1900)
for s in range(4):
    tracing(f'calque-{s}.png', s + 1)
prints_from_renders('tirage')
print('ok', len(os.listdir(out)))
