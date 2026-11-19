# Layout and key legends of the desk keyboard (modelled after an Apple keyboard with numeric keypad, French AZERTY).
# Writes textures-bureau/clavier-touches.json (key outlines in mm, read by blender/objets-poste.py)
# and textures-bureau/clavier-legendes.png (legends, mapped on the key tops by a planar projection).
# usage: python -I clavier_magic.py
import json, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'textures-bureau')
W, D = 418.7, 114.9          # body, mm
U = 18.6                     # key pitch, mm
GAP = 3.0                    # aluminium web between caps, mm
X0 = (W - 22 * U) / 2        # main block 14.5 u, nav 3 u, keypad 4 u, two 0.25 u gaps
Y0 = (D - 5.65 * U) / 2
PPM = 10                     # texture pixels per mm

keys = []


def key(x, y, w, h, leg, kind='c'):
    """x, y, w, h in units from the front-left corner of the key area."""
    a, b = X0 + x * U + GAP / 2, Y0 + y * U + GAP / 2
    c, d = X0 + (x + w) * U - GAP / 2, Y0 + (y + h) * U - GAP / 2
    keys.append(dict(poly=[[a, b], [c, b], [c, d], [a, d]], leg=leg, kind=kind))


def row(y, x, h, items):
    for w, leg, kind in items:
        if leg is not None:
            key(x, y, w, h, leg, kind)
        x += w


FN_Y, FN_H = 5.1, 0.55
# main block
row(FN_Y, 0, FN_H, [(1.25, 'esc', 'f')] + [(13.25 / 12, f'F{i}', 'f') for i in range(1, 13)])
row(4, 0, 1, [(1, '#|@', 'd')] + [(1, f'{a}|{b}', 'd') for a, b in zip('1234567890°_', '&é"\'(§è!çà)-')] + [(1.5, '⌫', 'wr')])
row(3, 0, 1, [(1.25, '⇥', 'wl')] + [(1, ch, 'c') for ch in 'AZERTYUIOP'] + [(1, '¨|^', 'd'), (1, '*|$', 'd')])
row(2, 0, 1, [(1.5, '⇪', 'wl')] + [(1, ch, 'c') for ch in 'QSDFGHJKLM'] + [(1, '%|ù', 'd'), (1, '£|`', 'd')])
row(1, 0, 1, [(1.25, '⇧', 'wl'), (1, '>|<', 'd')] + [(1, ch, 'c') for ch in 'WXCVBN'] + [(1, '?|,', 'd'), (1, '.|;', 'd'), (1, '/|:', 'd'), (1, '+|=', 'd'), (2.25, '⇧', 'wr')])
row(0, 0, 1, [(1.25, 'ctrl|⌃', 'm'), (1.25, 'alt|⌥', 'm'), (1.5, 'cmd|⌘', 'm'), (6.0, '', 'c'), (1.5, 'cmd|⌘', 'mr'), (1.25, 'alt|⌥', 'mr'), (1.75, 'ctrl|⌃', 'mr')])
# ISO return, L-shaped (top 1.25 u, bottom 1 u)
g = GAP / 2
keys.append(dict(poly=[[X0 + 13.5 * U + g, Y0 + 2 * U + g], [X0 + 14.5 * U - g, Y0 + 2 * U + g], [X0 + 14.5 * U - g, Y0 + 4 * U - g],
                       [X0 + 13.25 * U + g, Y0 + 4 * U - g], [X0 + 13.25 * U + g, Y0 + 3 * U + g], [X0 + 13.5 * U + g, Y0 + 3 * U + g]], leg='⏎', kind='wr'))
# navigation cluster
row(FN_Y, 14.75, FN_H, [(1, 'F13', 'f'), (1, 'F14', 'f'), (1, 'F15', 'f')])
row(4, 14.75, 1, [(1, 'fn', 'f'), (1, '↖', 's'), (1, '⇞', 's')])
row(3, 14.75, 1, [(1, '⌦', 's'), (1, '↘', 's'), (1, '⇟', 's')])
row(1, 15.75, 1, [(1, '▲', 'a')])
row(0, 14.75, 1, [(1, '◀', 'a'), (1, '▼', 'a'), (1, '▶', 'a')])
# numeric keypad
row(FN_Y, 18, FN_H, [(1, f'F{i}', 'f') for i in range(16, 20)])
row(4, 18, 1, [(1, '⌧', 's'), (1, '=', 'c'), (1, '/', 'c'), (1, '*', 'c')])
row(3, 18, 1, [(1, '7', 'c'), (1, '8', 'c'), (1, '9', 'c'), (1, '−', 'c')])
row(2, 18, 1, [(1, '4', 'c'), (1, '5', 'c'), (1, '6', 'c'), (1, '+', 'c')])
row(1, 18, 1, [(1, '1', 'c'), (1, '2', 'c'), (1, '3', 'c')])
key(21, 0, 1, 2, '⌤', 'wr')
row(0, 18, 1, [(2, '0', 'c'), (1, ',', 'c')])

# ------------------------------------------------------------------ legends texture
BG, FG = (30, 30, 32), (198, 198, 196)
F_TXT = '/System/Library/Fonts/SFNS.ttf'
F_SYM = '/System/Library/Fonts/Apple Symbols.ttf'
im = Image.new('RGB', (int(W * PPM), int(D * PPM)), BG)
dr = ImageDraw.Draw(im)
FONTS = {}


def font(size, sym=False):
    k = (size, sym)
    if k not in FONTS:
        FONTS[k] = ImageFont.truetype(F_SYM if sym else F_TXT, size)
    return FONTS[k]


def has_glyph(f, ch):
    """False when the font draws its .notdef box for ch."""
    try:
        m = f.getmask(ch)
        return m.getbbox() is not None and bytes(m) != bytes(f.getmask('\U000F0001'))
    except Exception:
        return False


ALT = {'⇥': 'tab', '⇞': 'pg ↑', '⇟': 'pg ↓', '⌤': 'enter', '⌧': 'clear', '↖': 'home', '↘': 'end', '⌦': 'del ⌦'}


def text(x, y, s, size, anchor='mm'):
    """x, y in mm (y from the front edge). Falls back to Apple Symbols, then to a word."""
    for sym in (False, True):
        f = font(size, sym)
        if all(has_glyph(f, ch) for ch in s if not ch.isspace()):
            break
    else:
        s, f = ALT.get(s, s), font(int(size * 0.62))
    dr.text((x * PPM, (D - y) * PPM), s, fill=FG, font=f, anchor=anchor)


for k in keys:
    xs = [p[0] for p in k['poly']]
    ys = [p[1] for p in k['poly']]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    leg, kind = k['leg'], k['kind']
    if not leg:
        continue
    if kind == 'c':
        text(cx, cy, leg, 42)
    elif kind == 'd':
        top, bot = leg.split('|')
        text(cx, cy + 2.6, top, 30)
        text(cx, cy - 2.9, bot, 30)
    elif kind == 'f':
        text(cx, cy - 0.3, leg, 20)
    elif kind == 's':
        text(cx, cy, leg, 34)
    elif kind == 'a':
        text(cx, cy, leg, 22)
    elif kind in ('wl', 'wr'):
        if kind == 'wl':
            text(x0 + 2.0, y0 + 2.0, leg, 34, 'ls')
        else:
            text(x1 - 2.0, y0 + 2.0, leg, 34, 'rs')
    elif kind in ('m', 'mr'):
        word, sym = leg.split('|')
        if kind == 'm':
            text(x1 - 2.0, y1 - 4.2, sym, 30, 'rm')
            text(x0 + 2.0, y0 + 2.0, word, 24, 'ls')
        else:
            text(x0 + 2.0, y1 - 4.2, sym, 30, 'lm')
            text(x1 - 2.0, y0 + 2.0, word, 24, 'rs')

os.makedirs(OUT, exist_ok=True)
im.save(os.path.join(OUT, 'clavier-legendes.png'), optimize=True)
json.dump(dict(W=W, D=D, keys=keys), open(os.path.join(OUT, 'clavier-touches.json'), 'w'), ensure_ascii=False, indent=0)
print('keys', len(keys), im.size)
