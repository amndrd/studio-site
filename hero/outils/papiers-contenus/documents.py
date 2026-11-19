# The printed documents on the desk, as real pages (HTML/CSS/SVG), for two fictional clients of the studio:
#   Halde, galerie & café (architects Vesper & Morel, Lyon): ground-floor plan A2, section A3, website site map, quote,
#   materials board;  Ombelle (speaker brand): homepage printed from the browser, mobile screens exported from Figma,
#   brand guidelines page, configurator code listing.
# Writes pages/*.html (+ img/matiere-*.png swatches); capture.sh screenshots them into captures/.
# usage: python -I documents.py
import os, sys, html
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import plans  # noqa: E402

PAGES = os.path.join(HERE, 'pages')
IMG = os.path.join(HERE, 'img')
os.makedirs(PAGES, exist_ok=True)
NP = np.random.default_rng(5)

BASE_CSS = """
@font-face{font-family:Inter;font-weight:400;src:url(../polices/inter-latin-400-normal.woff2)}
@font-face{font-family:Inter;font-weight:500;src:url(../polices/inter-latin-500-normal.woff2)}
@font-face{font-family:Inter;font-weight:600;src:url(../polices/inter-latin-600-normal.woff2)}
@font-face{font-family:Inter;font-weight:700;src:url(../polices/inter-latin-700-normal.woff2)}
@font-face{font-family:Serif;font-style:normal;src:url(../polices/instrument-serif-latin-400-normal.woff2)}
@font-face{font-family:Serif;font-style:italic;src:url(../polices/instrument-serif-latin-400-italic.woff2)}
@font-face{font-family:Mono;font-weight:400;src:url(../polices/jetbrains-mono-latin-400-normal.woff2)}
@font-face{font-family:Mono;font-weight:500;src:url(../polices/jetbrains-mono-latin-500-normal.woff2)}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#fff;color:#141414;font-family:Inter,sans-serif;-webkit-font-smoothing:antialiased}
body{overflow:hidden}
"""


def page(name, w, h, body, css=''):
    doc = (f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>{BASE_CSS}'
           f'body{{width:{w}px;height:{h}px}}{css}</style></head><body>{body}</body></html>')
    open(os.path.join(PAGES, name + '.html'), 'w', encoding='utf-8').write(doc)


# ------------------------------------------------------------------ material swatches (procedural, no photos)
def noise(h, w, scale, oct=4):
    a = np.zeros((h, w), np.float32)
    amp = 1.0
    for o in range(oct):
        s = max(2, int(scale / (2 ** o)))
        n = NP.normal(0, 1, (h // s + 2, w // s + 2)).astype(np.float32)
        a += amp * np.asarray(Image.fromarray(n).resize((w, h), Image.BICUBIC))
        amp *= 0.5
    return (a - a.min()) / (np.ptp(a) + 1e-6)


def save_sw(name, a):
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(os.path.join(IMG, f'matiere-{name}.png'))


def swatches():
    S = 520
    n = noise(S, S, 120)
    save_sw('beton', (np.array([150, 148, 142]) + (n[..., None] - 0.5) * 40 + NP.normal(0, 5, (S, S, 1))))
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    warp = noise(S, S, 160, 3) * 40
    g = np.sin((xx + warp * 3) / 7.0 + noise(S, S, 60, 2) * 4) * 0.5 + 0.5
    wood = np.array([150, 104, 66]) * (0.78 + 0.22 * g[..., None]) + NP.normal(0, 4, (S, S, 1))
    save_sw('chene', wood)
    st = noise(S, S, 200, 3)
    streak = np.asarray(Image.fromarray((NP.normal(0, 1, (S, 8)) * 60 + 128).astype(np.uint8)).resize((S, S), Image.BICUBIC)).astype(np.float32) / 255
    save_sw('acier', np.array([52, 55, 58]) * (0.8 + 0.25 * st[..., None] + 0.12 * streak[..., None]))
    base = np.ones((S, S, 3), np.float32) * np.array([226, 222, 212])
    im = Image.fromarray(base.astype(np.uint8))
    from PIL import ImageDraw
    d = ImageDraw.Draw(im)
    for i in range(520):
        cx, cy, r = NP.uniform(0, S), NP.uniform(0, S), NP.uniform(2, 14)
        col = [(120, 120, 116), (60, 60, 58), (190, 160, 130), (150, 160, 150), (240, 240, 236), (170, 110, 90)][int(NP.integers(0, 6))]
        pts = [(cx + r * np.cos(a) * NP.uniform(0.6, 1.2), cy + r * np.sin(a) * NP.uniform(0.6, 1.2)) for a in np.linspace(0, 6.28, int(NP.integers(4, 7)), endpoint=False)]
        d.polygon(pts, fill=col)
    save_sw('terrazzo', np.asarray(im).astype(np.float32) + NP.normal(0, 4, (S, S, 1)))
    save_sw('enduit', np.array([232, 226, 214]) + (noise(S, S, 90)[..., None] - 0.5) * 22 + NP.normal(0, 3, (S, S, 1)))
    br = np.asarray(Image.fromarray((NP.normal(0, 1, (S, 3)) * 80 + 128).clip(0, 255).astype(np.uint8)).resize((S, S), Image.BILINEAR)).astype(np.float32) / 255
    save_sw('laiton', np.array([182, 146, 82]) * (0.82 + 0.25 * br[..., None] + 0.1 * noise(S, S, 140, 2)[..., None]))


# ------------------------------------------------------------------ Halde: plan and section
def halde_plans():
    page('plan-rdc', 1684, 1191, plans.plan_rdc(), 'svg{display:block;width:1684px;height:1191px}')
    page('coupe-aa', 1191, 842, plans.coupe_aa(), 'svg{display:block;width:1191px;height:842px}')


# ------------------------------------------------------------------ Halde: website site map (A3 landscape)
def halde_sitemap():
    tree = [('Programmation', ['Expositions en cours', 'À venir', 'Archives 2019–2026', 'Fiche exposition']),
            ('Le café', ['Carte de saison', 'Horaires', 'Privatisation']),
            ('Visite 3D', ['Halle en WebGL', 'Mode guidé', 'Mode libre']),
            ('Le lieu', ['Histoire de la halle', 'Les architectes', 'Accès &amp; plan']),
            ('Infos', ['Billetterie', 'Presse', 'Mentions légales']),
            ('Contact', ['Formulaire', 'Newsletter'])]
    cols = ''
    for i, (h, kids) in enumerate(tree):
        k = ''.join(f'<div class="leaf"><span class="t">{["B", "B", "C", "B", "A", "A"][i] if j else "B"}</span>{x}</div>' for j, x in enumerate(kids))
        cols += f'<div class="col"><div class="node">{h}<em>{["/programmation", "/cafe", "/visite", "/lieu", "/infos", "/contact"][i]}</em></div><div class="kids">{k}</div></div>'
    body = f"""
<header><div><b>HALDE</b> — arborescence du site</div><div>v2 · 13.11.2026 · studio</div></header>
<div class="root"><div class="node big">Accueil<em>/</em></div></div>
<div class="bar"></div>
<div class="cols">{cols}</div>
<footer>
 <div class="leg"><span class="t">A</span> gabarit simple <span class="t">B</span> gabarit éditorial <span class="t">C</span> gabarit immersif (WebGL)</div>
 <div>27 gabarits · 3 modèles · bilingue FR / EN en phase 2</div>
</footer>"""
    css = """
body{padding:48px 56px;font-size:11px}
header{display:flex;justify-content:space-between;border-bottom:1.5px solid #141414;padding-bottom:10px;font-size:15px}
header b{letter-spacing:2px}
.root{display:flex;justify-content:center;margin-top:46px}
.node{border:1.5px solid #141414;padding:9px 12px;font-weight:600;font-size:12.5px;background:#fff;display:flex;justify-content:space-between;gap:10px}
.node em{font-style:normal;font-family:Mono;font-weight:400;font-size:9.5px;color:#666;align-self:center}
.node.big{background:#141414;color:#fff;font-size:15px;padding:12px 26px}
.node.big em{color:#bbb}
.bar{height:30px;border-left:1.5px solid #141414;margin-left:50%;position:relative}
.bar:after{content:'';position:absolute;left:-1px;bottom:0;width:0}
.cols{display:grid;grid-template-columns:repeat(6,1fr);gap:16px;border-top:1.5px solid #141414;padding-top:24px;position:relative}
.col{position:relative}
.col:before{content:'';position:absolute;left:50%;top:-25px;height:25px;border-left:1.5px solid #141414}
.kids{margin:12px 0 0 14px;border-left:1px solid #141414;padding-left:12px;display:flex;flex-direction:column;gap:9px}
.leaf{border:1px solid #141414;padding:7px 8px;font-size:11px;position:relative;display:flex;gap:7px;align-items:center}
.leaf:before{content:'';position:absolute;left:-13px;top:50%;width:12px;border-top:1px solid #141414}
.t{display:inline-block;width:15px;height:15px;border:1px solid #141414;font-size:9px;font-weight:600;text-align:center;line-height:13px;flex:none}
footer{position:absolute;left:56px;right:56px;bottom:40px;display:flex;justify-content:space-between;border-top:1px solid #141414;padding-top:9px;font-size:10.5px;color:#333}
.leg{display:flex;gap:8px;align-items:center}
"""
    page('halde-sitemap', 1191, 842, body, css)


# ------------------------------------------------------------------ Halde: quote (A4)
def devis():
    rows = [('Atelier de cadrage, arborescence, contenus', 2, 'j', 650), ('Direction artistique, maquettes UX/UI (27 gabarits)', 9, 'j', 650),
            ('Développement front-end, CMS headless', 12, 'j', 600), ('Visite 3D de la halle (WebGL), modélisation et éclairage', 10, 'j', 650),
            ('Intégration de la billetterie (API)', 2, 'j', 600), ('Recette, accessibilité RGAA, mise en ligne', 3, 'j', 600),
            ('Hébergement et maintenance, 12 mois', 1, 'forf.', 1200)]
    tr, tot = '', 0
    for i, (lab, q, u, pu) in enumerate(rows, 1):
        m = q * pu
        tot += m
        tr += f'<tr><td>{i:02d}</td><td>{lab}</td><td class="n">{q}</td><td>{u}</td><td class="n">{pu:,} €</td><td class="n">{m:,} €</td></tr>'.replace(',', ' ')
    tva = tot * 0.2
    f = lambda v: f'{v:,.0f}'.replace(',', ' ')
    body = f"""
<div class="top"><div class="logo">s</div><div class="who"><b>studio</b><br>création numérique &amp; 3D temps réel<br>Lyon</div>
<div class="doc"><div class="dn">DEVIS</div><div>N° 2026-118</div><div>Lyon, le 13 novembre 2026</div><div>Valable 30 jours</div></div></div>
<div class="cli"><div class="lab">Client</div><b>SAS Halde</b><br>12 quai de la Halde<br>69007 Lyon</div>
<div class="obj"><span class="lab">Objet</span> Site internet de la galerie &amp; café, et visite 3D de la halle</div>
<table><thead><tr><th></th><th>Désignation</th><th class="n">Qté</th><th>Unité</th><th class="n">P.U. HT</th><th class="n">Montant HT</th></tr></thead><tbody>{tr}</tbody></table>
<div class="tot"><div><span>Total HT</span><b>{f(tot)} €</b></div><div><span>TVA 20 %</span><b>{f(tva)} €</b></div><div class="g"><span>Total TTC</span><b>{f(tot + tva)} €</b></div></div>
<div class="cond"><div class="lab">Conditions</div>Acompte de 30 % à la commande, 40 % à la validation des maquettes, solde à la mise en ligne.
Paiement à 30 jours. Planning indicatif : 14 semaines à compter du cadrage. Les contenus (textes, visuels des expositions) sont fournis par le client.</div>
<div class="sig"><div>Bon pour accord, date et signature</div><div class="box"></div></div>
<footer>studio · création numérique · Lyon · page 1/1</footer>"""
    css = """
body{padding:44px 46px;font-size:9.5px;line-height:1.45}
.top{display:flex;gap:14px;align-items:flex-start}
.logo{width:34px;height:34px;background:#141414;color:#fff;font-family:Serif;font-style:italic;font-size:28px;text-align:center;line-height:30px}
.who{flex:1;color:#333}
.who b{font-size:12px;color:#141414}
.doc{text-align:right;color:#333}
.dn{font-size:22px;font-weight:600;letter-spacing:3px;color:#141414}
.cli{margin:30px 0 0 auto;width:210px;border-left:2px solid #141414;padding-left:10px}
.lab{font-size:8px;text-transform:uppercase;letter-spacing:1px;color:#666;margin-bottom:2px}
.obj{margin:26px 0 12px;font-size:10.5px}
.obj .lab{display:inline;margin-right:8px}
table{width:100%;border-collapse:collapse}
th{font-weight:600;text-align:left;border-bottom:1.2px solid #141414;padding:5px 4px;font-size:8.5px;text-transform:uppercase;letter-spacing:.6px}
td{border-bottom:.6px solid #bbb;padding:6px 4px;vertical-align:top}
.n{text-align:right;white-space:nowrap}
.tot{margin:12px 0 0 auto;width:220px}
.tot div{display:flex;justify-content:space-between;padding:4px 0;border-bottom:.6px solid #bbb}
.tot .g{border-bottom:1.5px solid #141414;font-size:11.5px}
.cond{margin-top:26px;width:330px;color:#333}
.sig{position:absolute;right:46px;bottom:90px;width:200px;font-size:8.5px;color:#555}
.sig .box{height:62px;border:.8px solid #999;margin-top:6px}
footer{position:absolute;left:46px;right:46px;bottom:30px;border-top:.6px solid #bbb;padding-top:6px;font-size:7.5px;color:#777}
"""
    page('devis', 595, 842, body, css)


# ------------------------------------------------------------------ Ombelle: homepage printed from the browser (A3 portrait)
def ombelle_accueil():
    body = """
<div class="ph"><span>15/11/2026 16:12</span><span>Ombelle — Enceintes fabriquées à Lyon</span></div>
<div class="site">
 <nav><div class="lg">ombelle</div><div class="links"><span>Enceintes</span><span>Atelier</span><span>Journal</span><span>Support</span></div><div class="cart">Compte · Panier (0)</div></nav>
 <section class="hero"><div class="txt"><div class="kick">Nouveau · Ombelle One</div><h1>Le son,<br>sans le bruit.</h1>
  <p>Une enceinte compacte en chêne massif et laine recyclée, accordée à l’oreille dans notre atelier de Lyon. Bluetooth, AirPlay 2, et un bouton, rien de plus.</p>
  <div class="btns"><span class="b1">Découvrir One — 490 €</span><span class="b2">Écouter un extrait</span></div></div>
  <div class="pic"><img src="../img/ombelle-sauge.png"></div></section>
 <div class="strip"><span>Livraison offerte</span><span>Garantie 5 ans</span><span>Réparable, pièces détachées</span><span>Fabriquée à Lyon</span></div>
 <section class="trio"><h2>Trois teintes, une seule voix.</h2><img src="../img/ombelle-trio.png"></section>
 <section class="specs"><div><b>2 × 40 W</b><span>amplification classe D</span></div><div><b>38 Hz – 22 kHz</b><span>réponse en fréquence</span></div>
  <div><b>Chêne massif</b><span>plateau huilé, fabriqué en France</span></div><div><b>4,2 kg</b><span>17 × 15 × 27 cm</span></div></section>
 <section class="cards"><div><div class="im s"></div><b>One · Sauge</b><span>490 €</span></div><div><div class="im a"></div><b>One · Argile</b><span>490 €</span></div><div><div class="im e"></div><b>One · Encre</b><span>490 €</span></div></section>
 <section class="journal"><h3>Journal</h3><div class="arts"><div><i>Atelier</i><b>Accorder une enceinte à l’oreille</b><span>8 min de lecture</span></div><div><i>Matières</i><b>Pourquoi la laine plutôt que le polyester</b><span>5 min</span></div><div><i>Écoute</i><b>Douze disques pour une première écoute</b><span>12 min</span></div></div></section>
 <footer class="sf"><div class="lg">ombelle</div><div><b>Boutique</b><span>Enceintes</span><span>Accessoires</span><span>Cartes cadeaux</span></div><div><b>Aide</b><span>Livraison</span><span>Retours</span><span>Réparations</span></div><div class="nl"><b>Lettre d’information</b><div class="in">votre@adresse.fr</div></div></footer>
</div>
<div class="pf"><span>localhost:3000/</span><span>1/1</span></div>"""
    css = """
body{padding:22px 26px;background:#fff}
.ph,.pf{display:flex;justify-content:space-between;font-size:8px;color:#333;font-family:Helvetica,Arial,sans-serif}
.pf{position:absolute;left:26px;right:26px;bottom:16px}
.site{margin-top:10px;border:0;background:#f4f1ec;height:1110px;padding:0 0 0;overflow:hidden;color:#1e1e1c}
nav{display:flex;align-items:center;justify-content:space-between;padding:18px 34px;font-size:9.5px}
.lg{font-family:Serif;font-style:italic;font-size:24px;letter-spacing:-.3px}
.links{display:flex;gap:22px}
.hero{display:grid;grid-template-columns:1fr 1fr;align-items:center;padding:10px 34px 30px;gap:24px}
.kick{font-size:8.5px;letter-spacing:1.4px;text-transform:uppercase;color:#6d7a6b;margin-bottom:12px}
h1{font-family:Serif;font-weight:400;font-size:62px;line-height:.95;letter-spacing:-1.2px}
.hero p{font-size:10px;line-height:1.55;color:#4a4a46;margin:16px 0 18px;max-width:300px}
.btns{display:flex;gap:10px;font-size:9px}
.b1{background:#1e1e1c;color:#f4f1ec;padding:9px 14px;border-radius:20px}
.b2{border:1px solid #1e1e1c;padding:9px 14px;border-radius:20px}
.pic{height:360px;border-radius:6px;overflow:hidden;background:#d9d6d0}
.pic img{width:100%;height:100%;object-fit:cover}
.strip{display:flex;justify-content:space-around;border-top:1px solid #d5d0c6;border-bottom:1px solid #d5d0c6;padding:10px 0;font-size:8.5px;color:#4a4a46}
.trio{padding:30px 34px 10px}
h2{font-family:Serif;font-weight:400;font-size:34px;letter-spacing:-.6px;margin-bottom:14px}
.trio img{width:100%;height:250px;object-fit:cover;border-radius:6px}
.specs{display:grid;grid-template-columns:repeat(4,1fr);padding:20px 34px;gap:14px}
.specs div{border-top:1px solid #1e1e1c;padding-top:8px;display:flex;flex-direction:column;gap:3px;font-size:8.5px;color:#4a4a46}
.specs b{font-size:13px;color:#1e1e1c;font-weight:500}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;padding:6px 34px 20px;font-size:9px}
.cards div{display:flex;flex-direction:column;gap:4px}
.im{height:90px;border-radius:5px}
.im.s{background:#8a9a86}.im.a{background:#b07b5e}.im.e{background:#2a2a28}
.journal{padding:6px 34px 18px}
h3{font-family:Serif;font-weight:400;font-size:24px;margin-bottom:10px}
.arts{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;font-size:9px}
.arts div{border-top:1px solid #d5d0c6;padding-top:7px;display:flex;flex-direction:column;gap:4px}
.arts i{font-style:normal;font-size:7.5px;letter-spacing:1px;text-transform:uppercase;color:#6d7a6b}
.arts b{font-family:Serif;font-weight:400;font-size:15px;line-height:1.1}
.arts span{color:#777;font-size:8px}
.sf{display:grid;grid-template-columns:1.2fr 1fr 1fr 1.4fr;gap:14px;background:#1e1e1c;color:#e8e4dc;padding:22px 34px 40px;font-size:8.5px}
.sf div{display:flex;flex-direction:column;gap:5px}
.in{border-bottom:1px solid #777;padding:6px 0;color:#999}
"""
    page('ombelle-accueil', 842, 1191, body, css)


# ------------------------------------------------------------------ Ombelle: mobile screens exported from Figma (A4 landscape)
def ombelle_mobile():
    def phone(title, inner):
        return f'<div class="fr"><div class="fl">{title}</div><div class="ph"><div class="sb"><span>9:41</span><span>● ● ▮</span></div>{inner}</div></div>'
    p1 = """<div class="mn"><span class="lg">ombelle</span><span>☰</span></div><div class="img"><img src="../img/ombelle-sauge.png"></div>
<div class="pad"><div class="k">Enceinte</div><div class="h">One · Sauge</div><div class="pr">490 €</div>
<div class="dots"><i class="s on"></i><i class="a"></i><i class="e"></i></div><div class="cta">Ajouter au panier</div>
<div class="row"><span>Livraison offerte</span><span>›</span></div><div class="row"><span>Caractéristiques</span><span>›</span></div></div>"""
    p2 = """<div class="mn"><span>‹</span><span class="t">Choisir une teinte</span><span></span></div>
<div class="pad"><div class="sw s"><b>Sauge</b><span>laine recyclée, chêne huilé</span></div><div class="sw a"><b>Argile</b><span>laine recyclée, chêne huilé</span></div>
<div class="sw e"><b>Encre</b><span>laine recyclée, chêne fumé</span></div><div class="cta">Valider · One Sauge</div></div>"""
    p3 = """<div class="mn"><span>‹</span><span class="t">Panier</span><span></span></div><div class="pad">
<div class="it"><div class="th s"></div><div><b>One · Sauge</b><span>Qté 1</span></div><b>490 €</b></div>
<div class="it"><div class="th e"></div><div><b>Support mural</b><span>Qté 2</span></div><b>78 €</b></div>
<div class="sum"><span>Sous-total</span><span>568 €</span></div><div class="sum"><span>Livraison</span><span>offerte</span></div>
<div class="sum big"><span>Total</span><span>568 €</span></div><div class="cta">Payer</div><div class="ap">Paiement express</div></div>"""
    body = (f'<div class="top"><b>Ombelle — Mobile v3</b><span>Export Figma · page « Parcours achat » · 14.11.2026</span></div>'
            f'<div class="frs">{phone("01 Produit", p1)}{phone("02 Teinte", p2)}{phone("03 Panier", p3)}</div>'
            '<div class="pin" style="left:268px;top:286px">1</div><div class="pin" style="left:520px;top:400px">2</div><div class="pin" style="left:792px;top:480px">3</div>'
            '<div class="cm"><b>Commentaires</b><span>1 · Image produit : passer en 4:5 ?</span><span>2 · Libellé teinte + matière OK</span><span>3 · Apple Pay en premier ?</span></div>')
    css = """
body{background:#e9e9e9;padding:22px 26px;font-size:8px}
.top{display:flex;justify-content:space-between;font-size:9px;color:#333}
.frs{display:flex;gap:50px;margin-top:20px;padding-left:20px}
.fl{font-size:8px;color:#666;margin-bottom:5px}
.ph{width:200px;height:430px;background:#f4f1ec;border-radius:2px;overflow:hidden;color:#1e1e1c;box-shadow:0 0 0 .5px #ccc}
.sb{display:flex;justify-content:space-between;padding:7px 14px 4px;font-size:7.5px;font-weight:600}
.mn{display:flex;justify-content:space-between;align-items:center;padding:6px 14px;font-size:9px}
.mn .lg{font-family:Serif;font-style:italic;font-size:16px}
.mn .t{font-weight:600;font-size:9.5px}
.img{height:190px;background:#d9d6d0}.img img{width:100%;height:100%;object-fit:cover}
.pad{padding:10px 14px;display:flex;flex-direction:column;gap:7px}
.k{font-size:6.5px;letter-spacing:1px;text-transform:uppercase;color:#6d7a6b}
.h{font-family:Serif;font-size:22px;line-height:1}
.pr{font-size:10px}
.dots{display:flex;gap:6px}.dots i{width:14px;height:14px;border-radius:50%;display:block}
.dots .on{box-shadow:0 0 0 1.5px #f4f1ec,0 0 0 2.5px #1e1e1c}
.s{background:#8a9a86}.a{background:#b07b5e}.e{background:#2a2a28}
.cta{background:#1e1e1c;color:#f4f1ec;text-align:center;padding:9px;border-radius:16px;font-size:8.5px;margin-top:4px}
.row{display:flex;justify-content:space-between;border-top:1px solid #d5d0c6;padding:7px 0;font-size:8px}
.sw{height:74px;border-radius:6px;padding:9px;display:flex;flex-direction:column;justify-content:flex-end;color:#f4f1ec;gap:2px}
.sw b{font-family:Serif;font-weight:400;font-size:16px}.sw span{font-size:6.5px;opacity:.85}
.sw.s{box-shadow:0 0 0 2px #1e1e1c}
.it{display:flex;gap:8px;align-items:center;border-bottom:1px solid #d5d0c6;padding:6px 0}
.it div{flex:1;display:flex;flex-direction:column;gap:2px}.it span{color:#777;font-size:7px}
.th{width:36px;height:36px;border-radius:4px;flex:none !important}
.sum{display:flex;justify-content:space-between;font-size:8px}.sum.big{font-size:10px;font-weight:600;border-top:1px solid #1e1e1c;padding-top:6px}
.ap{border:1px solid #1e1e1c;text-align:center;padding:8px;border-radius:16px;font-size:8.5px}
.pin{position:absolute;width:18px;height:18px;border-radius:50% 50% 50% 0;background:#3d6df2;color:#fff;font-size:8px;font-weight:600;text-align:center;line-height:18px}
.cm{position:absolute;right:26px;bottom:24px;width:170px;background:#fff;padding:8px;display:flex;flex-direction:column;gap:4px;font-size:7px;box-shadow:0 0 0 .5px #ccc}
"""
    page('ombelle-mobile', 842, 595, body, css)


# ------------------------------------------------------------------ Ombelle: brand guidelines page (A4 portrait)
def ombelle_charte():
    rays = ''.join(f'<line x1="60" y1="92" x2="{60 + 34 * np.cos(a):.1f}" y2="{92 - 34 * np.sin(a):.1f}" stroke="#1e1e1c" stroke-width="2"/>'
                   f'<circle cx="{60 + 38 * np.cos(a):.1f}" cy="{92 - 38 * np.sin(a):.1f}" r="5" fill="#1e1e1c"/>' for a in np.linspace(0.35, 2.79, 7))
    mark = f'<svg viewBox="0 0 120 130" width="92" height="100"><line x1="60" y1="92" x2="60" y2="128" stroke="#1e1e1c" stroke-width="2"/>{rays}</svg>'
    pal = [('Sauge', '#8A9A86', '138 154 134', '30 0 25 30'), ('Argile', '#B07B5E', '176 123 94', '0 40 50 25'), ('Encre', '#1E1E1C', '30 30 28', '70 60 60 85'),
           ('Lin', '#F4F1EC', '244 241 236', '3 4 6 0')]
    sw = ''.join(f'<div class="c"><div class="sq" style="background:{h}"></div><b>{n}</b><span>{h}</span><span>RVB {r}</span><span>CMJN {c}</span></div>' for n, h, r, c in pal)
    body = f"""
<header><span>Ombelle — charte graphique</span><span>v1.2 · novembre 2026</span></header>
<h1>02 — Logotype &amp; couleurs</h1>
<div class="logo"><div class="m">{mark}<div class="wm">ombelle</div></div>
<div class="note"><b>Construction</b>Le symbole reprend l’ombelle : sept rayons d’égale longueur, ouverts à 140°. Le mot-symbole est composé en Serif italique, approche −1 %.
<div class="zone"><div class="z"><div class="wm2">ombelle</div></div><span>zone de protection = hauteur du « o »</span></div></div></div>
<h2>Couleurs</h2><div class="pal">{sw}</div>
<h2>Typographies</h2>
<div class="ty"><div><div class="big serif">Aa</div><b>Serif italique</b><span>Titres, mot-symbole. Corps ≥ 24 pt.</span></div>
<div><div class="big">Aa</div><b>Inter</b><span>Texte courant, interfaces. 400 · 500 · 600.</span></div></div>
<h2>À éviter</h2>
<div class="no"><div><div class="wm3" style="color:#b07b5e;background:#8a9a86">ombelle</div><span>✕ deux couleurs de la gamme en aplat</span></div>
<div><div class="wm3" style="transform:scaleX(1.3)">ombelle</div><span>✕ déformer le mot-symbole</span></div>
<div><div class="wm3" style="font-family:Inter;font-style:normal;font-weight:700">ombelle</div><span>✕ changer de caractère</span></div></div>
<footer><span>studio pour Ombelle</span><span>page 4 / 18</span></footer>"""
    css = """
body{padding:34px 40px;font-size:8.5px;color:#1e1e1c;background:#fff}
header,footer{display:flex;justify-content:space-between;font-size:7.5px;color:#666}
footer{position:absolute;left:40px;right:40px;bottom:24px}
h1{font-family:Serif;font-weight:400;font-size:30px;margin:22px 0 14px;letter-spacing:-.4px}
h2{font-size:8px;letter-spacing:1.4px;text-transform:uppercase;margin:20px 0 9px;border-top:1px solid #1e1e1c;padding-top:6px}
.logo{display:grid;grid-template-columns:1.1fr 1fr;gap:18px}
.m{background:#f4f1ec;height:170px;display:flex;align-items:center;justify-content:center;gap:10px}
.wm{font-family:Serif;font-style:italic;font-size:44px;letter-spacing:-.5px}
.note{display:flex;flex-direction:column;gap:5px;line-height:1.45;color:#444}.note b{color:#1e1e1c}
.zone{margin-top:6px;display:flex;flex-direction:column;gap:4px;color:#777;font-size:7px}
.z{border:1px dashed #b07b5e;padding:12px 18px;align-self:flex-start}.wm2{font-family:Serif;font-style:italic;font-size:22px;outline:1px solid #ccc}
.pal{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.c{display:flex;flex-direction:column;gap:2px;font-size:7.5px;color:#555}.c b{color:#1e1e1c;font-size:9px}
.sq{height:62px;margin-bottom:4px;box-shadow:0 0 0 .5px #ccc}
.ty{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.ty div{display:flex;flex-direction:column;gap:3px;color:#555}.ty b{color:#1e1e1c}
.big{font-size:60px;line-height:1;color:#1e1e1c;font-weight:500}.serif{font-family:Serif;font-style:italic;font-weight:400}
.no{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.no div{display:flex;flex-direction:column;gap:4px;font-size:7px;color:#a33}
.wm3{font-family:Serif;font-style:italic;font-size:22px;color:#1e1e1c;background:#f4f1ec;padding:14px;text-align:center}
"""
    page('ombelle-charte', 595, 842, body, css)


# ------------------------------------------------------------------ Ombelle: configurator code listing (A4)
CODE = """import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { teintes, type Teinte } from './teintes'
import { prix } from '../boutique/prix'

/** Configurateur 3D de l'enceinte One : teinte, plateau, support. */
export class Configurateur {
  readonly scene = new THREE.Scene()
  readonly camera = new THREE.PerspectiveCamera(28, 1, 0.01, 20)
  private renderer: THREE.WebGLRenderer
  private controls: OrbitControls
  private tissu?: THREE.MeshStandardMaterial
  private plateau?: THREE.MeshStandardMaterial

  constructor(private canvas: HTMLCanvasElement) {
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true })
    this.renderer.setPixelRatio(Math.min(devicePixelRatio, 2))
    this.renderer.toneMapping = THREE.AgXToneMapping
    this.controls = new OrbitControls(this.camera, canvas)
    this.controls.enableDamping = true
    this.controls.minPolarAngle = Math.PI * 0.25
    this.controls.maxPolarAngle = Math.PI * 0.55
    this.camera.position.set(0.35, 0.22, 0.9)
  }

  async charger(url = '/modeles/one.glb') {
    const gltf = await new GLTFLoader().loadAsync(url)
    gltf.scene.traverse((o) => {
      if (!(o instanceof THREE.Mesh)) return
      if (o.name === 'tissu') this.tissu = o.material
      if (o.name === 'plateau') this.plateau = o.material
      o.castShadow = o.receiveShadow = true
    })
    this.scene.add(gltf.scene)
    this.appliquer(teintes.sauge)
  }

  appliquer(t: Teinte) {
    this.tissu?.color.set(t.tissu)
    this.plateau?.color.set(t.chene)
    document.dispatchEvent(new CustomEvent('prix', { detail: prix(t) }))
  }

  boucle = () => {
    this.controls.update()
    this.renderer.render(this.scene, this.camera)
    requestAnimationFrame(this.boucle)
  }
}"""


def code_listing():
    import re
    kw = r'\b(import|from|export|class|readonly|private|constructor|async|await|const|new|return|if|this|type|true|null)\b'
    lines = ''
    for i, ln in enumerate(CODE.split('\n'), 1):
        s = html.escape(ln)
        if s.strip().startswith('/**') or s.strip().startswith('//'):
            s = f'<i>{s}</i>'
        else:
            s = re.sub(r"('[^']*')", r'<u>\1</u>', s)
            s = re.sub(kw, r'<b>\1</b>', s)
        lines += f'<div><span class="n">{i}</span>{s or "&nbsp;"}</div>'
    body = f'<header><span>ombelle-web/src/configurateur/Configurateur.ts</span><span>1 / 3</span></header><pre>{lines}</pre><footer><span>14/11/2026 18:40</span><span>git main · a4f2c91</span></footer>'
    css = """
body{padding:30px 34px;font-family:Mono;font-size:7.6px;color:#111}
header,footer{display:flex;justify-content:space-between;font-family:Helvetica,Arial,sans-serif;font-size:7.5px;color:#333;border-bottom:.6px solid #999;padding-bottom:5px}
footer{position:absolute;left:34px;right:34px;bottom:22px;border:0;border-top:.6px solid #999;padding-top:5px}
pre{margin-top:12px;line-height:1.62;font-family:Mono;white-space:pre}
.n{display:inline-block;width:26px;color:#999;text-align:right;margin-right:12px}
b{font-weight:500;color:#000}i{color:#777;font-style:normal}u{text-decoration:none;color:#555}
"""
    page('code', 595, 842, body, css)


# ------------------------------------------------------------------ Halde: materials board (A3 landscape)
def halde_materiaux():
    mats = [('beton', 'Sol', 'Béton ciré, teinte ciment naturel, finition mate'), ('chene', 'Comptoir, banquette', 'Chêne massif huilé, lames 140 mm'),
            ('acier', 'Structure, garde-corps', 'Acier noirci, vernis mat'), ('terrazzo', 'Plan du comptoir', 'Terrazzo, granulats locaux'),
            ('enduit', 'Murs existants', 'Enduit à la chaux, teinte « grège »'), ('laiton', 'Détails, luminaires', 'Laiton brossé non verni')]
    cells = ''.join(f'<div class="m"><img src="../img/matiere-{k}.png"><div class="t"><b>{lab}</b><span>{d}</span><em>M{i + 1:02d}</em></div></div>' for i, (k, lab, d) in enumerate(mats))
    body = f"""
<header><div><b>HALDE</b> — matériaux &amp; ambiances</div><div>Vesper &amp; Morel · studio · v2 · 12.11.2026</div></header>
<div class="g"><div class="mats">{cells}</div>
<div class="side"><img src="../img/halde-maquette.png"><div class="cap">Maquette d’étude 1:100, carton plume et chêne</div>
<div class="pal"><i style="background:#8f8c86"></i><i style="background:#96683f"></i><i style="background:#34373a"></i><i style="background:#e2ded4"></i><i style="background:#b69252"></i></div>
<div class="nt"><b>Intentions</b><p>Garder la halle lisible : la structure acier reste apparente, les ajouts sont en bois et en laiton.
Le sol continu en béton ciré relie la galerie et le café. Lumière du nord par les sheds, éclairage d’appoint chaud (2700 K).</p></div></div></div>"""
    css = """
body{padding:40px 46px;font-size:10px}
header{display:flex;justify-content:space-between;border-bottom:1.5px solid #141414;padding-bottom:9px;font-size:14px}
header b{letter-spacing:2px}
.g{display:grid;grid-template-columns:2fr 1fr;gap:26px;margin-top:24px}
.mats{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.m img{width:100%;height:178px;object-fit:cover;display:block}
.t{display:flex;flex-direction:column;gap:2px;padding-top:6px;position:relative;font-size:9px;color:#444}
.t b{font-size:10.5px;color:#141414}.t em{position:absolute;right:0;top:6px;font-style:normal;font-family:Mono;color:#777}
.side img{width:100%;height:230px;object-fit:cover;display:block}
.cap{font-size:8.5px;color:#666;margin:5px 0 16px}
.pal{display:flex;gap:6px;margin-bottom:16px}.pal i{flex:1;height:40px;display:block}
.nt b{font-size:10.5px}.nt p{margin-top:5px;line-height:1.55;color:#333}
"""
    page('halde-materiaux', 1191, 842, body, css)


if __name__ == '__main__':
    swatches()
    for fn in (halde_plans, halde_sitemap, devis, ombelle_accueil, ombelle_mobile, ombelle_charte, code_listing, halde_materiaux):
        fn()
        print(fn.__name__)
