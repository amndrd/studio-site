# Architectural drawings of the fictional project "Halde, galerie & café" (Vesper & Morel architectes, Lyon 7e),
# drawn as SVG in millimetres on the sheet: ground-floor plan 1:50 (A2) and section AA 1:50 (A3).
# Imported by documents.py, which wraps them in HTML pages for the capture.
import math

INK = '#151515'
FONT = "font-family:'Helvetica Neue',Helvetica,Arial,sans-serif"


class Svg:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.e = []

    def add(self, s):
        self.e.append(s)

    def line(self, x1, y1, x2, y2, w=0.18, c=INK, dash=None, cap='butt'):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.add(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{c}" stroke-width="{w}"{d} stroke-linecap="{cap}"/>')

    def rect(self, x, y, w, h, sw=0.18, fill='none', c=INK, dash=None, extra=''):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.add(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}" stroke="{c}" stroke-width="{sw}"{d} {extra}/>')

    def poly(self, pts, sw=0.18, fill='none', c=INK, close=True, dash=None):
        p = ' '.join(f'{x:.2f},{y:.2f}' for x, y in pts)
        d = f' stroke-dasharray="{dash}"' if dash else ''
        tag = 'polygon' if close else 'polyline'
        self.add(f'<{tag} points="{p}" fill="{fill}" stroke="{c}" stroke-width="{sw}"{d} stroke-linejoin="miter"/>')

    def circle(self, cx, cy, r, sw=0.18, fill='none', c=INK, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.add(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{fill}" stroke="{c}" stroke-width="{sw}"{d}/>')

    def path(self, d, sw=0.18, fill='none', c=INK, dash=None):
        da = f' stroke-dasharray="{dash}"' if dash else ''
        self.add(f'<path d="{d}" fill="{fill}" stroke="{c}" stroke-width="{sw}"{da}/>')

    def text(self, x, y, s, size=2.5, weight=400, anchor='start', rot=0, c=INK, ls=0, font=FONT, italic=False):
        t = f' transform="rotate({rot} {x:.2f} {y:.2f})"' if rot else ''
        st = ' font-style="italic"' if italic else ''
        self.add(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{c}" letter-spacing="{ls}" style="{font}"{st}{t}>{s}</text>')

    def svg(self):
        defs = ('<defs>'
                '<pattern id="hatch" width="1.2" height="1.2" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="1.2" stroke="#151515" stroke-width="0.22"/></pattern>'
                '<pattern id="hatchl" width="2" height="2" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="2" stroke="#555" stroke-width="0.12"/></pattern>'
                '<pattern id="earth" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)"><line x1="0" y1="0" x2="0" y2="4" stroke="#333" stroke-width="0.15"/><line x1="2" y1="0" x2="2" y2="1.4" stroke="#333" stroke-width="0.15"/></pattern>'
                '<pattern id="beton" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="1" cy="1.5" r="0.25" fill="#333"/><circle cx="4" cy="3.6" r="0.35" fill="none" stroke="#333" stroke-width="0.12"/><circle cx="2.4" cy="5" r="0.18" fill="#333"/><path d="M4.6 0.6 l0.7 0.5 l-0.8 0.3z" fill="none" stroke="#333" stroke-width="0.1"/></pattern>'
                '<pattern id="isol" width="3" height="2" patternUnits="userSpaceOnUse"><path d="M0 1 Q0.75 0 1.5 1 T3 1" fill="none" stroke="#333" stroke-width="0.12"/></pattern>'
                '<pattern id="bois" width="3" height="1.2" patternUnits="userSpaceOnUse"><line x1="0" y1="0.6" x2="3" y2="0.6" stroke="#444" stroke-width="0.1"/></pattern>'
                '</defs>')
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="100%" height="100%">{defs}{"".join(self.e)}</svg>'


def dim_chain(S, pts, y, horiz=True, off=0.0, size=2.2, labels=None):
    """Dimension chain: ticks at 45°, values in metres (2 decimals) above the line."""
    k = 20.0
    if horiz:
        S.line(pts[0][0], y, pts[-1][0], y, 0.13)
        for i, (x, v) in enumerate(pts):
            S.line(x - 0.9, y + 0.9, x + 0.9, y - 0.9, 0.3)
            S.line(x, y - 2.2, x, y + 1.5, 0.1)
        for i in range(len(pts) - 1):
            a, b = pts[i][0], pts[i + 1][0]
            val = labels[i] if labels else f'{(b - a) / k:.2f}'.replace('.', ',')
            S.text((a + b) / 2, y - 0.9, val, size, anchor='middle')
    else:
        S.line(y, pts[0][0], y, pts[-1][0], 0.13)
        for x, v in pts:
            S.line(y - 0.9, x + 0.9, y + 0.9, x - 0.9, 0.3)
            S.line(y - 1.5, x, y + 2.2, x, 0.1)
        for i in range(len(pts) - 1):
            a, b = pts[i][0], pts[i + 1][0]
            val = labels[i] if labels else f'{(b - a) / k:.2f}'.replace('.', ',')
            S.text(y - 0.9, (a + b) / 2, val, size, anchor='middle', rot=-90)


def door(S, X, Y, hinge, w, ang0, sweep=90, sw=0.18):
    """Door leaf + swing arc. hinge in mm, w leaf width mm, ang0 direction of the closed leaf (deg)."""
    hx, hy = hinge
    a0 = math.radians(ang0)
    a1 = math.radians(ang0 + sweep)
    ex, ey = hx + w * math.cos(a1), hy + w * math.sin(a1)
    sx, sy = hx + w * math.cos(a0), hy + w * math.sin(a0)
    S.line(hx, hy, ex, ey, 0.3)
    large = 0
    sweep_flag = 1 if sweep > 0 else 0
    S.path(f'M{sx:.2f} {sy:.2f} A{w:.2f} {w:.2f} 0 {large} {sweep_flag} {ex:.2f} {ey:.2f}', 0.1)


def chair(S, cx, cy, ang):
    a = math.radians(ang)
    c, s = math.cos(a), math.sin(a)
    pts = [(-4.2, -4.2), (4.2, -4.2), (4.2, 4.2), (-4.2, 4.2)]
    S.poly([(cx + x * c - y * s, cy + x * s + y * c) for x, y in pts], 0.12)
    S.line(cx + -4.2 * c - 4.6 * s, cy + -4.2 * s + 4.6 * c, cx + 4.2 * c - 4.6 * s, cy + 4.2 * s + 4.6 * c, 0.35)


def plan_rdc():
    """Halde, ground floor, 1:50 on A2 (594 x 420 mm)."""
    S = Svg(594, 420)
    k = 20.0
    ox, oy = 86.0, 80.0
    X = lambda m: ox + m * k
    Y = lambda m: oy + m * k
    S.rect(10, 10, 574, 400, 0.5)
    S.line(516, 10, 516, 410, 0.35)                                               # right strip: legend and title block
    L, W, t = 21.0, 12.0, 0.4
    # existing walls (hatched poché) with openings
    S.add(f'<path d="M{X(0)} {Y(0)} H{X(L)} V{Y(W)} H{X(0)} Z M{X(t)} {Y(t)} V{Y(W - t)} H{X(L - t)} V{Y(t)} Z" fill="url(#hatch)" fill-rule="evenodd" stroke="{INK}" stroke-width="0.5"/>')
    gaps_s = [(1.0, 4.6), (6.4, 9.4), (12.0, 14.0), (16.6, 20.0)]                 # street facade (south)
    for a, b in gaps_s:
        S.rect(X(a), Y(W - t) - 0.3, (b - a) * k, t * k + 0.6, 0, '#fff', '#fff')
        S.line(X(a), Y(W - t), X(a), Y(W), 0.5)
        S.line(X(b), Y(W - t), X(b), Y(W), 0.5)
        if (a, b) != (12.0, 14.0):
            for f in (0.35, 0.5, 0.65):                                            # glazing
                S.line(X(a), Y(W - t + t * f), X(b), Y(W - t + t * f), 0.13 if f != 0.5 else 0.22)
            S.line(X(a), Y(W) + 4, X(b), Y(W) + 4, 0.1, dash='1.2 0.8')            # sill outside
    door(S, X, Y, (X(12.0), Y(W - t)), 1.0 * k, 0, -90)
    door(S, X, Y, (X(14.0), Y(W - t)), 1.0 * k, 180, 90)
    for a, b in ((18.4, 19.9),):                                                   # delivery door, north
        S.rect(X(a), Y(0) - 0.3, (b - a) * k, t * k + 0.6, 0, '#fff', '#fff')
        S.line(X(a), Y(0), X(a), Y(t), 0.5)
        S.line(X(b), Y(0), X(b), Y(t), 0.5)
        door(S, X, Y, (X(a), Y(t)), (b - a) * k, 0, 90)
    for a, b in ((7.0, 9.0), (13.0, 15.0)):                                        # high windows, north (dashed)
        S.line(X(a), Y(t / 2), X(b), Y(t / 2), 0.15, dash='2 1')
    # structural grid and steel columns
    ax = [0.2, 5.4, 10.5, 15.6, 20.8]
    ay = [0.2, 6.0, 11.8]
    for i, a in enumerate(ax):
        S.line(X(a), Y(-2.2), X(a), Y(W + 1.0), 0.1, '#555', '3 1 0.6 1')
        S.circle(X(a), Y(-2.9), 3.2, 0.2, '#fff')
        S.text(X(a), Y(-2.9) + 1.3, 'ABCDE'[i], 3.6, 500, 'middle')
    for j, a in enumerate(ay):
        S.line(X(-3.0), Y(a), X(L + 0.5), Y(a), 0.1, '#555', '3 1 0.6 1')
        S.circle(X(-3.6), Y(a), 3.2, 0.2, '#fff')
        S.text(X(-3.6), Y(a) + 1.3, str(j + 1), 3.6, 500, 'middle')
    for a in ax[1:-1]:
        S.rect(X(a) - 3, Y(6.0) - 3, 6, 6, 0.3, INK)
    # new partitions (solid black)
    part = [(0.4, 2.6, 5.2, 2.7), (5.1, 0.4, 5.2, 2.7), (3.6, 0.4, 3.7, 2.6), (12.0, 0.4, 12.1, 4.6), (12.1, 3.0, 20.6, 3.1), (15.0, 0.4, 15.1, 3.0),
            (1.8, 0.4, 1.9, 1.8)]
    for x0, y0, x1, y1 in part:
        S.rect(X(x0), Y(y0), (x1 - x0) * k, (y1 - y0) * k, 0.25, INK)
    S.rect(X(12.0) - 0.2, Y(1.1), 2.4, 0.9 * k, 0, '#fff', '#fff')
    door(S, X, Y, (X(12.1), Y(1.1)), 0.9 * k, 90, -90)
    S.rect(X(16.6), Y(3.0) - 0.2, 0.9 * k, 2.4, 0, '#fff', '#fff')
    door(S, X, Y, (X(16.6), Y(3.1)), 0.9 * k, 0, 90)
    S.rect(X(2.4), Y(2.6) - 0.2, 0.9 * k, 2.4, 0, '#fff', '#fff')
    door(S, X, Y, (X(2.4), Y(2.7)), 0.9 * k, 0, 90)
    S.rect(X(4.0), Y(2.6) - 0.2, 0.8 * k, 2.4, 0, '#fff', '#fff')
    door(S, X, Y, (X(4.0), Y(2.7)), 0.8 * k, 0, 90)
    # demolished wall (dashed grey)
    S.rect(X(7.8), Y(4.2), 0.25 * k, 4.4 * k, 0.15, 'none', '#777', '1.5 1')
    # sanitary fittings
    for cx in (0.95, 2.85):
        S.add(f'<ellipse cx="{X(cx):.2f}" cy="{Y(0.95):.2f}" rx="3.6" ry="5" fill="none" stroke="{INK}" stroke-width="0.15"/>')
        S.rect(X(cx) - 4.4, Y(0.4), 8.8, 3.2, 0.15)
    S.rect(X(0.5), Y(2.0), 0.5 * k, 0.45 * k, 0.15)
    S.add(f'<ellipse cx="{X(0.75):.2f}" cy="{Y(2.24):.2f}" rx="3.2" ry="2.4" fill="none" stroke="{INK}" stroke-width="0.12"/>')
    S.circle(X(1.0), Y(1.6), 1.5 * k / 2 * 0.98, 0.08, dash='0.8 0.8')            # turning circle (PMR)
    # stair to the mezzanine (18 risers) and mezzanine outline above
    sx0, sx1, sy0, sy1 = 6.0, 10.5, 0.5, 1.6
    S.rect(X(sx0), Y(sy0), (sx1 - sx0) * k, (sy1 - sy0) * k, 0.2)
    for i in range(1, 18):
        x = X(sx0) + (sx1 - sx0) * k * i / 18
        S.line(x, Y(sy0), x, Y(sy1), 0.12)
    S.line(X(sx0) + 2, Y(1.05), X(sx1) - 3, Y(1.05), 0.15)
    S.poly([(X(sx1) - 3, Y(1.05) - 1), (X(sx1) - 1, Y(1.05)), (X(sx1) - 3, Y(1.05) + 1)], 0.15, INK)
    S.line(X(8.9), Y(sy0), X(9.4), Y(sy1), 0.25)                                    # cut line of the stair
    S.text(X(sx0) + 2, Y(sy1) + 3.2, 'montée 18 × 17,8 / 25', 2.0)
    S.rect(X(5.6), Y(0.4), 6.4 * k, 3.6 * k, 0.15, dash='2.5 1')
    S.text(X(8.8), Y(3.6), 'mezzanine (au-dessus)', 2.0, anchor='middle', italic=True, c='#444')
    # kitchen
    S.rect(X(15.1), Y(0.4), 5.5 * k, 0.65 * k, 0.15, 'url(#hatchl)')
    S.rect(X(19.95), Y(1.05), 0.65 * k, 1.95 * k, 0.15, 'url(#hatchl)')
    for i in range(4):
        S.circle(X(16.0) + (i % 2) * 7, Y(0.62) + (i // 2) * 5.2 - 2, 2.0, 0.12)
    S.rect(X(17.6), Y(0.45), 1.6 * k, 0.5 * k, 0.12)
    S.rect(X(17.7), Y(0.5), 0.7 * k, 0.4 * k, 0.1)
    S.rect(X(18.45), Y(0.5), 0.7 * k, 0.4 * k, 0.1)
    S.rect(X(15.4), Y(1.6), 1.8 * k, 0.9 * k, 0.12)
    S.text(X(16.3), Y(2.15), 'îlot', 1.8, anchor='middle')
    # shelving in the store room
    S.rect(X(12.3), Y(0.5), 2.5 * k, 0.45 * k, 0.12)
    S.rect(X(12.3), Y(0.5), 0.45 * k, 2.3 * k, 0.12)
    # bar counter (L) and back bar
    S.poly([(X(13.0), Y(3.7)), (X(17.2), Y(3.7)), (X(17.2), Y(5.6)), (X(16.5), Y(5.6)), (X(16.5), Y(4.4)), (X(13.0), Y(4.4))], 0.3, 'url(#hatchl)')
    S.rect(X(13.0), Y(3.15), 4.6 * k, 0.4 * k, 0.15)
    S.text(X(14.8), Y(4.12), 'COMPTOIR', 1.9, 500, 'middle')
    for i in range(5):
        S.circle(X(13.5) + i * 14, Y(4.95), 2.2, 0.12)
    # café tables
    for (cx, cy) in ((13.3, 7.0), (15.3, 7.0), (17.3, 7.0), (13.3, 9.3), (15.3, 9.3), (17.3, 9.3)):
        S.circle(X(cx), Y(cy), 0.38 * k, 0.15)
        for ang in (0, 90, 180, 270):
            a = math.radians(ang)
            chair(S, X(cx) + 13 * math.cos(a), Y(cy) + 13 * math.sin(a), ang + 90)
    S.rect(X(20.0), Y(4.4), 0.6 * k, 6.6 * k, 0.15)                                # banquette
    for cy in (5.2, 6.8, 8.4, 10.0):
        S.rect(X(19.1), Y(cy) - 6, 0.6 * k, 0.6 * k, 0.12)
    # gallery: free-standing picture walls, plinths, picture rail
    S.rect(X(3.2), Y(5.0), 0.15 * k, 3.6 * k, 0.25, INK)
    S.rect(X(8.6), Y(6.4), 3.0 * k, 0.15 * k, 0.25, INK)
    for (cx, cy) in ((5.6, 9.2), (7.0, 9.2), (6.3, 4.6)):
        S.rect(X(cx) - 6, Y(cy) - 6, 12, 12, 0.15, 'url(#hatchl)')
    S.line(X(0.5), Y(3.0), X(0.5), Y(11.5), 0.12, dash='0.8 0.8')
    S.rect(X(10.0), Y(10.0), 2.0 * k, 0.6 * k, 0.2)                                # reception desk
    S.text(X(11.0), Y(10.38), 'accueil', 1.8, anchor='middle')
    # room labels
    rooms = [('GALERIE', '138,4 m²', 6.0, 7.2), ('CAFÉ', '74,2 m²', 15.4, 8.2), ('CUISINE', '14,6 m²', 18.2, 2.2), ('RÉSERVE', '7,5 m²', 13.6, 2.2),
             ('SANITAIRES', '8,3 m²', 1.8, 3.4), ('LOC. TECH.', '3,2 m²', 4.4, 1.5)]
    for n, a, cx, cy in rooms:
        big = n in ('GALERIE', 'CAFÉ')
        S.text(X(cx), Y(cy), n, 4.0 if big else 2.4, 600, 'middle', ls=0.3)
        S.text(X(cx), Y(cy) + (4.6 if big else 3.0), a, 2.6 if big else 2.0, anchor='middle')
        if big:
            S.text(X(cx), Y(cy) + 8.4, 'sol : béton ciré · HSP 6,20', 2.0, anchor='middle', c='#333')
    # section line A-A
    for yy in (-1.6, W + 1.6):
        S.line(X(11.0), Y(yy) - 3, X(11.0), Y(yy) + 3, 0.6)
        S.poly([(X(11.0), Y(yy)), (X(11.0) - 6, Y(yy)), (X(11.0) - 3.4, Y(yy) - 2.2)], 0.2, INK)
        S.text(X(11.0) + 2, Y(yy) + 1.4, 'A', 3.6, 600)
    S.line(X(11.0), Y(-1.0), X(11.0), Y(W + 1.0), 0.15, dash='6 1.2 1 1.2')
    # dimension chains (bottom and left; the axis bubbles take the top)
    dim_chain(S, [(X(v), 0) for v in [0, 1.0, 4.6, 6.4, 9.4, 12.0, 14.0, 16.6, 20.0, L]], Y(W + 2.8))
    dim_chain(S, [(X(0), 0), (X(L), 0)], Y(W + 4.0))
    dim_chain(S, [(Y(v), 0) for v in [0, 2.6, 6.0, W]], X(-1.6), horiz=False)
    dim_chain(S, [(Y(0), 0), (Y(W), 0)], X(-2.6), horiz=False)
    # right strip: north, legend, scale, notes, revisions, title block
    cx = 550
    S.circle(cx, 36, 9, 0.25)
    S.poly([(cx, 23), (cx - 3.4, 40), (cx, 36.5), (cx + 3.4, 40)], 0.2, INK)
    S.text(cx, 52, 'N', 3.6, 600, 'middle')
    x0 = 521
    S.text(x0, 66, 'LÉGENDE', 2.4, 600, ls=0.3)
    items = [('url(#hatch)', 'Maçonnerie existante'), (INK, 'Cloison neuve 98/48'), ('none', 'Élément démoli')]
    for i, (fi, lab) in enumerate(items):
        y = 71 + i * 7
        S.rect(x0, y, 8, 4, 0.2, fi, dash='1 0.6' if fi == 'none' else None)
        S.text(x0 + 11, y + 3.2, lab, 2.0)
    S.text(x0, 101, 'ÉCHELLE 1:50', 2.4, 600, ls=0.3)
    for i in range(5):
        S.rect(x0 + i * 10, 104, 10, 1.8, 0.15, INK if i % 2 == 0 else '#fff')
    for i, v in enumerate(('0', '0,5', '1', '1,5', '2', '2,5 m')):
        S.text(x0 + i * 10, 110.5, v, 1.8, anchor='middle')
    S.text(x0, 124, 'NOTES', 2.4, 600, ls=0.3)
    notes = ['1. Cotes en mètres,', '    à vérifier sur site.', '2. ±0,00 = dalle finie RDC.', '3. Portique acier conservé,', '    poteaux HEB 300 à protéger.',
             '4. Accès PMR par l’entrée', '    principale, ressaut ≤ 2 cm.', '5. Mobilier café indicatif.', '6. Voir coupe AA (A-102).']
    for i, n in enumerate(notes):
        S.text(x0, 130 + i * 4.4, n, 1.95)
    ry = 214
    S.line(516, ry, 584, ry, 0.35)
    S.text(x0, ry + 5, 'IND.  DATE           MODIFICATION', 1.8, 600)
    S.text(x0, ry + 11, 'A     28.10.2026  Première diffusion', 1.8)
    S.text(x0, ry + 16, 'B     12.11.2026  Comptoir agrandi,', 1.8)
    S.text(x0, ry + 20, '                         cimaise déplacée', 1.8)
    ty = 242
    S.line(516, ty, 584, ty, 0.5)
    S.rect(x0, ty + 5, 9, 9, 0.35, INK)
    S.text(x0 + 4.5, ty + 11.7, 'V', 6, 600, 'middle', c='#fff')
    S.text(x0 + 12, ty + 9, 'VESPER &amp;', 3.4, 700, ls=0.5)
    S.text(x0 + 12, ty + 13.4, 'MOREL', 3.4, 700, ls=0.5)
    S.text(x0, ty + 20, 'architectes', 2.0)
    S.text(x0, ty + 24, '12 quai de la Halde, 69007 Lyon', 1.8)
    S.line(516, ty + 29, 584, ty + 29, 0.2)
    S.text(x0, ty + 37, 'HALDE', 5.0, 700, ls=0.8)
    S.text(x0, ty + 42.5, 'galerie &amp; café', 2.8)
    S.text(x0, ty + 47.5, 'Réhabilitation d’une halle', 1.9)
    S.text(x0, ty + 51.5, 'Maître d’ouvrage : SAS Halde', 1.9)
    S.line(516, ty + 56, 584, ty + 56, 0.2)
    S.text(x0, ty + 63, 'PLAN DU', 3.0, 600, ls=0.3)
    S.text(x0, ty + 67.5, 'REZ-DE-CHAUSSÉE', 3.0, 600, ls=0.3)
    S.text(x0, ty + 73, 'Phase APD · 1:50 · A2', 2.0)
    S.line(516, ty + 78, 584, ty + 78, 0.2)
    S.text(x0, ty + 84, 'Dessiné C.M. · Vérifié L.V.', 1.9)
    S.text(x0, ty + 88, 'Date 12.11.2026', 1.9)
    S.text(x0, ty + 92, 'HAL_APD_A101_B.dwg', 1.7, c='#444')
    S.line(516, ty + 97, 584, ty + 97, 0.2)
    S.text(x0, ty + 103, 'N° PLAN', 1.9)
    S.text(x0, ty + 116, 'A-101', 9, 700)
    S.line(560, ty + 97, 560, 410, 0.2)
    S.text(563, ty + 103, 'INDICE', 1.9)
    S.text(572, ty + 116, 'B', 9, 700, 'middle')
    S.line(516, ty + 122, 584, ty + 122, 0.2)
    S.text(x0, ty + 130, 'Ce document est la propriété de', 1.6, c='#555')
    S.text(x0, ty + 133.5, 'Vesper &amp; Morel. Reproduction interdite.', 1.6, c='#555')
    S.text(x0, ty + 140, 'Format A2 · 594 × 420', 1.6, c='#555')
    S.text(x0, ty + 152, 'Visa', 1.8)
    S.rect(x0, ty + 154, 58, 10, 0.15)
    return S.svg()


def coupe_aa():
    """Halde, section AA, 1:50 on A3 (420 x 297 mm)."""
    S = Svg(420, 297)
    k = 20.0
    ox, gy = 70.0, 214.0
    X = lambda m: ox + m * k
    Z = lambda m: gy - m * k
    S.rect(10, 10, 400, 277, 0.5)
    W = 12.0
    # earth and slab
    S.rect(X(-2.2), Z(0) + 5, (W + 4.4) * k, 18, 0, 'url(#earth)', 'none')
    S.line(X(-2.6), Z(0), X(W + 2.6), Z(0), 0.5)
    S.rect(X(0.4), Z(0), (W - 0.8) * k, 5, 0.3, 'url(#beton)')
    for x0 in (0, W - 0.6):                                                       # footings
        S.rect(X(x0) - 4, Z(0) + 5, 0.6 * k + 8, 9, 0.3, 'url(#beton)')
    # walls cut (hatched), parapets
    for x0 in (0, W - 0.4):
        S.rect(X(x0), Z(6.6), 0.4 * k, 6.6 * k, 0.5, 'url(#hatch)')
    # sawtooth roof: teeth of 2.4 m (vertical glazed face to the north = left)
    tooth = 2.4
    x = 0.4
    pts = [(X(0.4), Z(6.2))]
    while x < W - 0.4 - 0.01:
        x1 = min(x + tooth, W - 0.4)
        pts += [(X(x), Z(8.2)), (X(x1), Z(6.2))]
        S.rect(X(x) - 0.4, Z(8.2), 0.8, 2.0 * k, 0.15, '#cfd8dc')                # glazing (cut)
        S.line(X(x), Z(8.2), X(x1), Z(6.2), 0.15)
        x = x1
    S.poly(pts + [(X(W - 0.4), Z(6.2))], 0.5, close=False)
    for i in range(len(pts) - 1):                                                  # insulated deck (thickness)
        (ax_, ay_), (bx_, by_) = pts[i], pts[i + 1]
        if ay_ != by_:
            S.poly([(ax_, ay_), (bx_, by_), (bx_, by_ + 3.2), (ax_, ay_ + 3.2)], 0.15, 'url(#isol)')
    # steel trusses beyond (light)
    for i in range(5):
        x0 = 0.4 + i * tooth
        S.line(X(x0), Z(6.2), X(x0 + tooth), Z(6.2), 0.25, '#555')
        S.line(X(x0), Z(6.2), X(x0 + tooth / 2), Z(5.7), 0.12, '#666')
        S.line(X(x0 + tooth / 2), Z(5.7), X(x0 + tooth), Z(6.2), 0.12, '#666')
    S.rect(X(6.0) - 1.5, Z(6.2), 3, 6.2 * k, 0.25, 'none', '#444')                 # column beyond
    # mezzanine (cut) with railing
    S.rect(X(0.4), Z(3.2), 3.6 * k, 0.32 * k, 0.4, 'url(#bois)')
    S.line(X(4.0), Z(3.2), X(4.0), Z(4.2), 0.3)
    S.line(X(0.4), Z(4.2), X(4.0), Z(4.2), 0.3)
    for i in range(1, 9):
        S.line(X(0.4) + i * 8, Z(3.2), X(0.4) + i * 8, Z(4.2), 0.1)
    # stair beyond, seen end-on (steps as horizontal lines)
    S.rect(X(0.5), Z(3.2), 1.1 * k, 3.2 * k, 0.2, 'none', '#444')
    for i in range(1, 18):
        S.line(X(0.5), Z(i * 0.178), X(1.6), Z(i * 0.178), 0.1, '#555')
    # windows in the south wall (elevation beyond), counter and tables (light)
    S.rect(X(W - 0.4) - 0.6, Z(3.4), 1.2, 3.4 * k, 0.2, '#e8eef0')
    S.rect(X(6.6), Z(1.1), 2.2 * k, 1.1 * k, 0.15, 'none', '#555')
    S.text(X(7.7), Z(0.45), 'comptoir', 1.9, anchor='middle', c='#555')
    for cx in (9.3, 10.6):
        S.line(X(cx) - 7.6, Z(0.75), X(cx) + 7.6, Z(0.75), 0.2, '#555')
        S.line(X(cx), Z(0.75), X(cx), Z(0), 0.15, '#555')
    # level marks
    for v, lab in ((0, '±0,00'), (3.2, '+3,20'), (6.2, '+6,20'), (8.2, '+8,20')):
        S.line(X(-1.8), Z(v), X(-0.2), Z(v), 0.15)
        S.poly([(X(-1.2), Z(v)), (X(-1.2) - 1.6, Z(v) - 2.4), (X(-1.2) + 1.6, Z(v) - 2.4)], 0.15, INK)
        S.text(X(-1.2) - 3, Z(v) - 3.4, lab, 2.4, 500, 'end')
    # dimension stacks
    dim_chain(S, [(Z(0), 0), (Z(3.2), 0), (Z(6.2), 0), (Z(8.2), 0)][::-1], X(W + 1.6), horiz=False,
              labels=['2,00', '3,00', '3,20'])
    dim_chain(S, [(X(0), 0), (X(W), 0)], Z(-1.6) + 8, labels=['12,00'])
    # material callouts
    calls = [((X(7.0), Z(7.3)), (X(9.0), Z(9.6)), 'Toiture shed : bac acier isolé 160 mm, vitrage nord feuilleté 44.2'),
             ((X(2.0), Z(3.05)), (X(1.0), Z(5.0) - 2), 'Mezzanine : plancher bois 22 mm sur solives acier'),
             ((X(5.0), Z(0) + 2.5), (X(3.0), Z(-2.6) + 12), 'Dalle existante, ragréage + béton ciré 3 mm'),
             ((X(W - 0.2), Z(5.0)), (X(W + 2.2), Z(5.0)), 'Mur existant, enduit chaux')]
    for (ax_, ay_), (bx_, by_), lab in calls:
        S.circle(ax_, ay_, 0.6, 0.1, INK)
        S.line(ax_, ay_, bx_, by_, 0.12)
        S.line(bx_, by_, bx_ + 4, by_, 0.12)
        S.text(bx_ + 5, by_ + 0.8, lab, 2.1)
    # title
    S.text(30, 32, 'COUPE AA', 5.4, 700, ls=0.6)
    S.text(30, 39, 'Échelle 1:50', 2.6)
    tb = (264, 258, 138, 22)
    S.rect(*tb, 0.4)
    S.text(tb[0] + 3, tb[1] + 7, 'VESPER &amp; MOREL · HALDE — galerie &amp; café', 2.6, 600)
    S.text(tb[0] + 3, tb[1] + 13, 'Coupe AA · APD · 1:50 · A3 · 12.11.2026', 2.2)
    S.text(tb[0] + 3, tb[1] + 18.5, 'N° A-102 · Indice B', 2.2)
    return S.svg()
