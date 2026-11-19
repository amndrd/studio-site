# Packaging prints of the desk objects, as real pages (HTML/CSS/SVG) captured like the documents and the screens:
#   three soda cans of invented brands (no real trademark on a public site) and the stamp of an invented café on the
#   kraft sleeve of the takeaway cup. Sizes are the printed areas of the Sketchfab models, 10 px per mm:
#     slim can 25 cl (Soda Cans 3D pack, "Long", scaled to 134 mm): 180.6 x 116.5 mm  -> 1806 x 1165
#     standard can 33 cl ("Short", scaled to 115 mm):                  204.5 x 95.6 mm   -> 2045 x 956
#     cup sleeve (Paper Cup Unperfect, cup 110 mm high):                273 x 42 mm       -> 2730 x 420
#   Left to right = around the can, the front panel in the middle (x 50 %); top of the page = top of the can.
#   Ampère (energy drink, slim can), Nord (sparkling yerba maté, 33 cl), Minuit (energy drink without sugar, slim can),
#   Pente (specialty coffee roaster, Lyon 1er: the sleeve stamp).
# Writes pages/emb-*.html; capture-emballages.sh screenshots them (transparent background) into captures/.
# usage: python -I emballages.py
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PAGES = os.path.join(HERE, 'pages')
os.makedirs(PAGES, exist_ok=True)

BASE = """
@font-face{font-family:Inter;font-weight:400;src:url(../polices/inter-latin-400-normal.woff2)}
@font-face{font-family:Inter;font-weight:500;src:url(../polices/inter-latin-500-normal.woff2)}
@font-face{font-family:Inter;font-weight:600;src:url(../polices/inter-latin-600-normal.woff2)}
@font-face{font-family:Inter;font-weight:700;src:url(../polices/inter-latin-700-normal.woff2)}
@font-face{font-family:Serif;font-style:normal;src:url(../polices/instrument-serif-latin-400-normal.woff2)}
@font-face{font-family:Serif;font-style:italic;src:url(../polices/instrument-serif-latin-400-italic.woff2)}
@font-face{font-family:Mono;font-weight:400;src:url(../polices/jetbrains-mono-latin-400-normal.woff2)}
@font-face{font-family:Mono;font-weight:500;src:url(../polices/jetbrains-mono-latin-500-normal.woff2)}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:transparent;font-family:Inter,sans-serif;-webkit-font-smoothing:antialiased}
body{overflow:hidden;position:relative}
.abs{position:absolute}
.cond{font-family:'Avenir Next Condensed';font-weight:800}
.din{font-family:'DIN Condensed';font-weight:700}
.futura{font-family:Futura;font-weight:700}
.mono{font-family:Mono}
table.nut{border-collapse:collapse;width:100%}
table.nut td{padding:4px 0;border-bottom:1.5px solid currentColor}
table.nut td:last-child{text-align:right}
table.nut tr.sub td:first-child{padding-left:16px}
"""


def page(name, w, h, body, css=''):
    doc = (f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>{BASE}'
           f'body{{width:{w}px;height:{h}px}}{css}</style></head><body>{body}</body></html>')
    open(os.path.join(PAGES, name + '.html'), 'w', encoding='utf-8').write(doc)


# ------------------------------------------------------------------ EAN-13 barcode (valid check digit)
L = ['0001101', '0011001', '0010011', '0111101', '0100011', '0110001', '0101111', '0111011', '0110111', '0001011']
G = ['0100111', '0110011', '0011011', '0100001', '0011101', '0111001', '0000101', '0010001', '0001001', '0010111']
R = ['1110010', '1100110', '1101100', '1000010', '1011100', '1001110', '1010000', '1000100', '1001000', '1110100']
PAR = ['LLLLLL', 'LLGLGG', 'LLGGLG', 'LLGGGL', 'LGLLGG', 'LGGLLG', 'LGGGLL', 'LGLGLG', 'LGLGGL', 'LGGLGL']


def ean13(d12, color, mod=2.6, h=150):
    s = sum(int(c) * (3 if i % 2 else 1) for i, c in enumerate(d12))
    code = d12 + str((10 - s % 10) % 10)
    bits = '101' + ''.join((L if PAR[int(code[0])][i] == 'L' else G)[int(c)] for i, c in enumerate(code[1:7])) + '01010' + ''.join(R[int(c)] for c in code[7:]) + '101'
    guards = set(range(0, 3)) | set(range(45, 50)) | set(range(92, 95))
    q = 11 * mod
    W = q * 2 + 95 * mod
    rects = ''.join(f'<rect x="{q + i * mod:.2f}" y="0" width="{mod:.2f}" height="{h + (5 * mod if i in guards else 0):.1f}"/>' for i, b in enumerate(bits) if b == '1')
    fs = 9.5 * mod                                       # digits sit between the guard bars, as printed
    y = h + fs * 0.95
    txt = (f'<text x="{q - 2 * mod}" y="{y:.1f}" text-anchor="end">{code[0]}</text>'
           f'<text x="{q + 5 * mod:.1f}" y="{y:.1f}" textLength="{39 * mod:.1f}" lengthAdjust="spacing">{code[1:7]}</text>'
           f'<text x="{q + 51 * mod:.1f}" y="{y:.1f}" textLength="{39 * mod:.1f}" lengthAdjust="spacing">{code[7:]}</text>')
    return (f'<svg width="{W:.0f}" height="{h + fs * 1.15:.0f}" viewBox="0 0 {W:.1f} {h + fs * 1.15:.1f}" fill="{color}" '
            f'style="font-family:Inter;font-size:{fs:.1f}px">{rects}{txt}</svg>')


def infotri(color):
    """Sorting guidance box (can + recycling bin), as printed on French packaging."""
    return f"""<svg width="300" height="104" viewBox="0 0 300 104" fill="none" stroke="{color}" stroke-width="3">
<rect x="2" y="2" width="296" height="100" rx="12"/>
<g transform="translate(22,18)"><path d="M6 4h28l-2 6v44l2 6H6l2-6V10z"/><path d="M10 0h20"/></g>
<g transform="translate(78,20)"><path d="M0 8h44M6 8l4 52h24l4-52M16 0h12v8"/><path d="M14 22v28M22 22v28M30 22v28"/></g>
<text x="140" y="42" fill="{color}" stroke="none" style="font:700 22px Inter">CANETTE</text>
<text x="140" y="70" fill="{color}" stroke="none" style="font:500 18px Inter">à recycler</text>
<text x="140" y="92" fill="{color}" stroke="none" style="font:400 14px Inter">triercestdonner.fr</text></svg>"""


def nutrition(rows, color, title='Valeurs nutritionnelles moyennes', per='pour 100 ml'):
    tr = ''.join(f'<tr class="{"sub" if r[0].startswith("dont") else ""}"><td>{r[0]}</td><td>{r[1]}</td></tr>' for r in rows)
    return (f'<div style="color:{color};font-size:21px;line-height:1.15"><div style="display:flex;justify-content:space-between;font-weight:700;'
            f'border-bottom:3px solid {color};padding-bottom:5px;margin-bottom:2px"><span>{title}</span><span>{per}</span></div>'
            f'<table class="nut">{tr}</table></div>')


# ------------------------------------------------------------------ the three cans
# A camera sees about a third of the can: the front panel is x 600..1200 (slim) or 680..1360 (33 cl); the legal panels
# go around the back (x 40..560 and 1250..1770 on the slim can, the seam at x 0). Above and below the print, the page is
# transparent: bare aluminium on the can.
def ampere():
    W, H = 1806, 1165
    blue, white = '#1F2FD6', '#FFFFFF'
    back = f"""
<div class="abs" style="left:50px;top:190px;width:500px;color:{white};font-size:19px;line-height:1.3">
 <div style="font-weight:700;font-size:21px;letter-spacing:.5px">BOISSON ÉNERGISANTE AROMATISÉE</div>
 <p style="margin-top:8px"><b>Ingrédients :</b> eau gazéifiée, sucre, acidifiant : acide citrique, correcteur d’acidité : citrates de sodium,
 taurine (0,4 %), caféine (0,032 %), arômes naturels, vitamines (niacine, acide pantothénique, B6, B12), colorant : caramel ordinaire.</p>
 <p style="margin-top:10px;font-weight:700">Teneur élevée en caféine. Déconseillé aux enfants et aux femmes enceintes ou allaitantes (32 mg / 100 ml).</p>
 <div style="margin-top:14px">{nutrition([('Énergie', '194 kJ / 46 kcal'), ('Matières grasses', '0 g'), ('dont acides gras saturés', '0 g'),
      ('Glucides', '11 g'), ('dont sucres', '11 g'), ('Protéines', '0 g'), ('Sel', '0,10 g'), ('Niacine', '8,0 mg (50 %*)'), ('Vitamine B6', '0,8 mg (57 %*)'),
      ('Vitamine B12', '0,8 µg (32 %*)')], white)}
 <div style="font-size:15px;margin-top:6px">*VNR : valeurs nutritionnelles de référence. Une canette (250 ml) contient 80 mg de caféine.</div></div>
</div>
<div class="abs" style="left:1260px;top:190px;width:500px;color:{white};font-size:18px;line-height:1.35">
 <div style="display:flex;gap:26px;align-items:flex-end">
  <div><div class="din" style="font-size:132px;line-height:.85">32</div><div style="font-size:20px;line-height:1.25;margin-top:6px">mg de caféine<br>pour 100 ml</div></div>
  <div style="background:{white};padding:10px 8px 4px;border-radius:4px">{ean13('376014520093', blue, 1.7, 110)}</div></div>
 <div style="margin-top:26px">{infotri(white)}</div>
 <p style="margin-top:18px">À conserver au frais, à l’abri de la lumière. Ne pas consommer plus de 2 canettes par jour.
 À consommer de préférence avant fin : voir le fond de la canette.</p>
 <p style="margin-top:10px">Ampère SAS · 18 rue Bichat, 69002 Lyon · ampere-energie.fr</p>
</div>"""
    front = f"""
<div class="abs cond" style="left:640px;top:150px;height:930px;writing-mode:vertical-rl;transform:rotate(180deg);font-size:262px;line-height:.78;color:{white};letter-spacing:-4px;text-align:center">AMPÈRE</div>
<div class="abs" style="left:900px;top:196px;width:290px;color:{white}">
 <div class="mono" style="font-size:20px;letter-spacing:2px">N° 01 — ORIGINAL</div>
 <div style="font-size:42px;font-weight:700;line-height:1.04;margin-top:18px">Boisson<br>énergisante</div>
 <div style="font-size:23px;margin-top:14px;line-height:1.3">taurine · caféine<br>vitamines B</div>
 <svg style="margin-top:70px;display:block" width="112" height="112" viewBox="0 0 120 120" fill="none" stroke="{white}" stroke-width="7">
  <circle cx="60" cy="60" r="52"/><path d="M60 18v50M30 68h60M40 82h40M50 96h20" stroke-width="6"/></svg>
 <div class="din" style="margin-top:240px;font-size:66px;line-height:1">25 cl</div>
 <div style="font-size:19px;margin-top:6px">Conçu à Lyon</div>
</div>"""
    bands = f"""
<div class="abs" style="left:0;right:0;top:118px;bottom:66px;background:{blue}"></div>
<div class="abs" style="left:0;right:0;top:136px;height:2px;background:{white}"></div>
<div class="abs" style="left:0;right:0;bottom:86px;height:2px;background:{white}"></div>
<div class="abs mono" style="left:24px;right:24px;bottom:96px;display:flex;justify-content:space-between;font-size:18px;letter-spacing:3px;color:{white}">
 <span>AMPÈRE — ÉNERGIE</span><span>LYON · FRANCE</span><span></span><span></span><span>A = C / s</span><span>N° 01</span></div>"""
    page('emb-ampere', W, H, bands + back + front)


def nord():
    W, H = 2045, 956
    cream, green, mustard = '#ECE5D2', '#1E3A2B', '#B8862A'
    compass = f"""<svg width="96" height="96" viewBox="0 0 150 150" fill="none" stroke="{green}" stroke-width="5">
<circle cx="75" cy="75" r="68"/><path d="M75 14 L89 75 L75 136 L61 75 Z" fill="{green}" stroke="none"/><path d="M75 75 L89 75 L75 136 Z" fill="{cream}" stroke="none"/>
<path d="M75 75 L89 75 L75 136 L61 75" stroke-width="3"/></svg>"""
    front = f"""
<div class="abs" style="left:{W // 2}px;top:96px;transform:translateX(-50%);text-align:center;color:{green};width:660px">
 <div style="display:flex;justify-content:center">{compass}</div>
 <div style="font-size:21px;letter-spacing:8px;font-weight:600;margin-top:14px;padding-left:8px">MATÉ PÉTILLANT</div>
 <div style="font-family:Serif;font-style:italic;font-size:300px;line-height:.86;margin-top:2px;letter-spacing:-5px">Nord</div>
 <div style="width:400px;height:2px;background:{green};margin:20px auto 16px"></div>
 <div style="font-size:24px;line-height:1.35">Infusion de yerba maté, citron,<br>une pointe de sucre de canne</div>
 <div style="font-size:21px;margin-top:16px;letter-spacing:2px"><b>33 CL</b> · 20 mg de caféine / 100 ml</div>
</div>"""
    back = f"""
<div class="abs" style="left:46px;top:110px;width:590px;color:{green};font-size:18px;line-height:1.3">
 <div style="font-weight:700;font-size:20px">BOISSON RAFRAÎCHISSANTE GAZEUSE AU MATÉ</div>
 <p style="margin-top:7px"><b>Ingrédients :</b> eau gazéifiée, infusion de yerba maté 8 % (eau, feuilles de maté), sucre de canne 4,2 %,
 jus de citron à base de concentré 1 %, acidifiant : acide citrique, arôme naturel de maté.</p>
 <p style="margin-top:7px;font-weight:700">Teneur élevée en caféine. Déconseillé aux enfants et aux femmes enceintes ou allaitantes (20 mg / 100 ml).</p>
 <div style="margin-top:9px">{nutrition([('Énergie', '72 kJ / 17 kcal'), ('Matières grasses', '0 g'), ('Glucides', '4,2 g'), ('dont sucres', '4,2 g'),
      ('Protéines', '0 g'), ('Sel', '0,01 g')], green)}</div>
</div>
<div class="abs" style="left:1420px;top:112px;width:580px;color:{green};font-size:18px;line-height:1.35">
 <div style="display:flex;gap:30px;align-items:flex-start">
  <div>{ean13('376022810474', green, 1.7, 100)}</div>
  <div><div style="color:{mustard};font-weight:700;letter-spacing:2px;font-size:20px">PEU SUCRÉ</div><div>4,2 g de sucres<br>pour 100 ml</div>
   <div style="margin-top:10px;font-family:Serif;font-size:30px;line-height:1">Lot n° 47</div></div></div>
 <div style="margin-top:14px">{infotri(green)}</div>
 <p style="margin-top:10px">Brassé et mis en canette à Grenoble, avec du maté du Paraná. Servir très frais.<br>
 Nord Boissons · 4 rue Très-Cloîtres, 38000 Grenoble · nord-mate.fr</p></div>"""
    deco = f"""
<div class="abs" style="left:0;right:0;top:30px;bottom:30px;background:{cream}"></div>
<div class="abs" style="left:0;right:0;top:30px;height:52px;background:{green}"></div>
<div class="abs" style="left:0;right:0;bottom:30px;height:46px;background:{green}"></div>
<div class="abs" style="left:0;right:0;bottom:76px;height:18px;background:{mustard}"></div>
<div class="abs" style="left:0;right:0;top:41px;display:flex;justify-content:space-around;color:{cream};font-size:19px;letter-spacing:9px;font-weight:600">
 <span>NORD</span><span>MATÉ</span><span>NORD</span><span>MATÉ</span><span>NORD</span><span>MATÉ</span></div>"""
    page('emb-nord', W, H, deco + back + front)


def minuit():
    W, H = 1806, 1165
    white, black, lime = '#F1F0EA', '#121212', '#C4EC3A'
    front = f"""
<svg class="abs" style="left:{W // 2 - 32}px;top:290px" width="64" height="64" viewBox="0 0 90 90"><circle cx="45" cy="45" r="38" fill="{black}"/><circle cx="62" cy="34" r="33" fill="{white}"/></svg>
<div class="abs din" style="left:{W // 2}px;top:410px;transform:translateX(-50%);font-size:272px;line-height:.8;color:{black};letter-spacing:-5px;white-space:nowrap">00:00</div>
<div class="abs futura" style="left:{W // 2}px;top:680px;transform:translateX(-50%);font-size:70px;letter-spacing:18px;color:{black};padding-left:18px">MINUIT</div>
<div class="abs" style="left:{W // 2}px;top:780px;transform:translateX(-50%);font-size:23px;letter-spacing:4px;color:{black};white-space:nowrap">ÉNERGIE · ZÉRO SUCRE</div>
<div class="abs din" style="left:{W // 2}px;top:900px;transform:translateX(-50%);font-size:52px;color:{black}">25 CL</div>"""
    back = f"""
<div class="abs" style="left:50px;top:210px;width:500px;color:{black};font-size:19px;line-height:1.3">
 <div style="font-weight:700;font-size:21px">BOISSON ÉNERGISANTE SANS SUCRES, AVEC ÉDULCORANTS</div>
 <p style="margin-top:8px"><b>Ingrédients :</b> eau gazéifiée, acidifiant : acide citrique, taurine (0,4 %), correcteur d’acidité : citrates de sodium,
 caféine (0,03 %), arômes, édulcorants : sucralose, acésulfame K, vitamines (niacine, B6, B12).</p>
 <p style="margin-top:8px;font-weight:700">Teneur élevée en caféine. Déconseillé aux enfants et aux femmes enceintes ou allaitantes (30 mg / 100 ml).</p>
 <div style="margin-top:12px">{nutrition([('Énergie', '13 kJ / 3 kcal'), ('Matières grasses', '0 g'), ('Glucides', '0,5 g'), ('dont sucres', '0 g'),
      ('Protéines', '0 g'), ('Sel', '0,08 g'), ('Niacine', '8,0 mg (50 %*)'), ('Vitamine B12', '0,8 µg (32 %*)')], black)}
 <div style="font-size:15px;margin-top:5px">*VNR. Une canette (250 ml) contient 75 mg de caféine.</div></div>
</div>
<div class="abs" style="left:1260px;top:220px;width:480px;color:{black};font-size:18px;line-height:1.35">
 {ean13('376047330158', black, 1.8, 115)}
 <div style="margin-top:22px">{infotri(black)}</div>
 <p style="margin-top:16px">Servir frais. Ne pas consommer plus de 2 canettes par jour.<br>
 Minuit Boissons · 7 place Sathonay, 69001 Lyon · minuit.energy</p></div>"""
    deco = f"""
<div class="abs" style="left:0;right:0;top:110px;bottom:66px;background:{white}"></div>
<div class="abs" style="left:0;right:0;top:110px;height:40px;background:{lime}"></div>
<div class="abs mono" style="left:0;right:0;top:119px;display:flex;justify-content:space-around;font-size:18px;letter-spacing:4px;color:{black}">
 <span>23:57</span><span>23:58</span><span>23:59</span><span>00:00</span><span>00:01</span><span>00:02</span><span>00:03</span></div>
<div class="abs" style="left:0;right:0;bottom:66px;height:14px;background:{black}"></div>"""
    page('emb-minuit', W, H, deco + back + front)


# ------------------------------------------------------------------ Pente (coffee roaster, stamp on the kraft sleeve)
def pente():
    W, H = 2730, 420
    ink = '#1A1714'

    def stamp():
        r = 150
        return f"""<svg width="340" height="340" viewBox="0 0 340 340" fill="none" stroke="{ink}">
<defs><path id="c" d="M170 170 m-128 0 a128 128 0 1 1 256 0 a128 128 0 1 1 -256 0"/></defs>
<circle cx="170" cy="170" r="{r}" stroke-width="7"/><circle cx="170" cy="170" r="104" stroke-width="3"/>
<text fill="{ink}" stroke="none" style="font:700 25px Inter;letter-spacing:6px"><textPath href="#c" startOffset="0">PENTE · TORRÉFACTEUR · CAFÉ · LYON 1ER ·</textPath></text>
<path d="M96 214 h34 v-22 h28 v-22 h28 v-22 h28 v-22 h30" stroke-width="9" stroke-linejoin="miter"/>
<circle cx="236" cy="104" r="9" fill="{ink}" stroke="none"/>
<text x="170" y="234" text-anchor="middle" fill="{ink}" stroke="none" style="font:600 18px Inter;letter-spacing:4px">DEPUIS 2016</text></svg>"""

    def bloc(x):
        return (f'<div class="abs" style="left:{x}px;top:40px">{stamp()}</div>'
                f'<div class="abs" style="left:{x + 380}px;top:118px;color:{ink};font-size:26px;line-height:1.3">'
                f'<div style="font-family:Serif;font-size:74px;line-height:.9">Pente</div>'
                f'<div style="letter-spacing:3px;font-weight:600;margin-top:8px">CAFÉ DE SPÉCIALITÉ</div>'
                f'<div style="margin-top:4px">14 montée de la Grande-Côte</div></div>')
    page('emb-pente', W, H, bloc(170) + bloc(1535))


if __name__ == '__main__':
    for fn in (ampere, nord, minuit, pente):
        fn()
    print('ok')
