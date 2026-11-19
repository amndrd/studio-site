# La planche de l'idée « la caméra au centre » (19/11/2026, idée mise de côté pendant la recherche).
# Lit hero/labo/recherche/9-camera-au-centre/sources.json, écrit planche.html à côté et l'exporte en PNG
# avec hero/synthese/export.mjs.
# usage : python3 hero/outils/page_camera.py
import json, html, subprocess
from pathlib import Path

HERO = Path(__file__).resolve().parents[1]
DOS = HERO / 'labo/recherche/9-camera-au-centre'
SRC = json.loads((DOS / 'sources.json').read_text())

THEMES = [
    ('1-le-principe-dans-les-jeux', 'Le principe dans les jeux', 'Rusty Lake, Myst',
     "Le principe existe et se comprend tout de suite. Rusty Lake montre un mur à la fois, avec une flèche de chaque côté. Myst enchaîne des images précalculées, d'un point de vue à l'autre. Ses salles rondes placent un poste dans chaque alcôve."),
    ('2-sites-et-dioramas', 'Sites 3D et dioramas', 'le coin en diorama',
     "Le coin en diorama (deux murs et un sol) est le format des portfolios 3D. Ici, chaque coin deviendrait un diorama plein écran, éclairé de l'intérieur. Les coins se touchent tous autour d'un même axe."),
    ('3-pieces-autour-d-un-centre', 'Pièces autour d\'un centre', 'rotondes, octogones, plans en secteurs',
     "Une rotonde ou un octogone donne une niche par direction : depuis le centre, la caméra voit chaque coin cadré par l'architecture. Un plan rond en secteurs sépare les fonctions sans couloir."),
    ('4-le-decor-qui-tourne', 'Le décor qui tourne', 'plateaux tournants, coupes, portes secrètes',
     "Au théâtre, c'est le décor qui tourne. Un plateau coupé par des murs porte plusieurs pièces dos à dos. Le bateau en coupe de La Vie aquatique montre tout un lieu, pièce par pièce. Une bibliothèque qui pivote peut servir de transition."),
    ('5-coins-plein-cadre', 'Des coins plein cadre', 'bureaux, bras robotiques, ateliers',
     "Chaque coin se compose comme le bureau : deux murs, deux points de fuite et une lumière principale. Selon le coin, c'est le halo derrière l'écran, la lampe au-dessus de l'établi ou les écrans du bras robotique."),
    ('6-fenetres-sous-terre', 'Des fenêtres sous terre', 'verrières intérieures, faux jours',
     "Sous terre, une fenêtre peut donner sur le reste du labo : une verrière, ou un bureau vitré dans le hall. Ce peut aussi être un panneau dépoli éclairé par derrière. On a la lumière d'une fenêtre, sans voir le dehors."),
]

def e(s): return html.escape(s, quote=True)

def section(tid, titre, sous, note, n):
    items = sorted((k, v) for k, v in SRC.items() if k.startswith(tid + '/'))
    figs = ''.join(f'<figure><img src="{e(k)}" alt=""><div class="cap"><b>{n}·{i:02d}</b> {e(v["titre"])}</div></figure>'
                   for i, (k, v) in enumerate(items, 1))
    return (f'<section class="theme"><div class="stitle">{n} {e(titre)}</div>'
            f'<div class="snote">{len(items)} images · {e(sous)}</div><div class="grid">{figs}</div>'
            f'<div class="keep"><span class="lbl">À retenir</span><div class="txt">{e(note)}</div></div></section>')

DEFS = ('<defs><marker id="fl" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M0,0 L10,5 L0,10 z" fill="#111"/></marker></defs>')

# l'idée : une pièce carrée, un coin par fonction, la caméra au centre
IDEE = f'''<svg width="460" height="400" viewBox="0 0 460 400">{DEFS}
<rect class="wall" x="60" y="40" width="340" height="340"/><rect class="o" x="72" y="52" width="316" height="316"/>
<polygon points="230,210 72,120 160,52" fill="#EEF3FA" stroke="#9A9A9A" stroke-width=".8" stroke-dasharray="2 4"/>
<rect class="hatch" x="80" y="60" width="70" height="26"/><rect class="hatch" x="80" y="60" width="26" height="70"/>
<rect class="hatch" x="310" y="60" width="70" height="40"/><circle class="o" cx="345" cy="130" r="14"/>
<rect class="hatch" x="300" y="334" width="80" height="26"/><circle class="o" cx="330" cy="300" r="16"/>
<rect class="dash" x="82" y="300" width="60" height="60"/>
<path d="M262,186 A36,36 0 0 1 262,234" class="l" fill="none" marker-end="url(#fl)"/>
<path d="M198,234 A36,36 0 0 1 198,186" class="l" fill="none" marker-end="url(#fl)"/>
<circle class="cam" cx="230" cy="210" r="7"/>
<text class="t" x="80" y="30">1 Bureau</text><text class="t" x="318" y="30">2 Projets</text>
<text class="t" x="318" y="398">3 Atelier</text><text class="t" x="80" y="398">4 ?</text>
<text class="small" x="244" y="268">la caméra</text></svg>'''

def mini(kind):
    s = f'<svg width="270" height="190" viewBox="0 0 270 190">{DEFS}'
    if kind == 'tourelle':
        s += ('<rect class="o" x="65" y="15" width="150" height="150"/><circle class="cam" cx="140" cy="90" r="6"/>'
              '<polygon points="140,90 66,40 90,16" fill="#EEF3FA" stroke="#9A9A9A" stroke-width=".8" stroke-dasharray="2 4"/>'
              '<path d="M162,72 A28,28 0 0 1 162,108" class="l" fill="none" marker-end="url(#fl)"/>')
    elif kind == 'avancer':
        s += ('<rect class="o" x="65" y="15" width="150" height="150"/><circle class="cam" cx="140" cy="90" r="6"/>'
              '<path d="M134,84 L100,50" class="dashl" marker-end="url(#fl)"/><circle class="cam" cx="94" cy="44" r="4"/>'
              '<path d="M146,96 L180,130" class="dashl" marker-end="url(#fl)"/><circle class="cam" cx="186" cy="136" r="4"/>')
    elif kind == 'plateau':
        s += ('<circle class="o" cx="140" cy="82" r="68"/><line class="thick" x1="72" y1="82" x2="208" y2="82"/>'
              '<line class="thick" x1="140" y1="14" x2="140" y2="150"/>'
              '<path d="M210,40 A80,80 0 0 1 212,124" class="l" fill="none" marker-end="url(#fl)"/>'
              '<circle class="cam" cx="140" cy="178" r="6"/><polygon points="140,178 104,150 176,150" fill="#EEF3FA" stroke="#9A9A9A" stroke-width=".8" stroke-dasharray="2 4"/>')
    elif kind == 'coupe':
        for i in range(4):
            s += f'<rect class="o" x="{15+i*62}" y="25" width="58" height="90"/>'
        s += ('<circle class="cam" cx="44" cy="160" r="6"/><polygon points="44,160 18,116 70,116" fill="#EEF3FA" stroke="#9A9A9A" stroke-width=".8" stroke-dasharray="2 4"/>'
              '<path d="M70,172 L220,172" class="l" marker-end="url(#fl)"/>')
    elif kind == 'puits':
        for i in range(4):
            s += f'<rect class="o" x="70" y="{8+i*44}" width="150" height="40"/>'
        s += ('<circle class="cam" cx="40" cy="28" r="6"/><polygon points="40,28 70,10 70,46" fill="#EEF3FA" stroke="#9A9A9A" stroke-width=".8" stroke-dasharray="2 4"/>'
              '<path d="M40,44 L40,170" class="l" marker-end="url(#fl)"/>')
    return s + '</svg>'

FACONS = [
    ('tourelle', '1 La tourelle', "La caméra tourne sur elle-même, d'un quart de tour par coin. C'est ton idée, la plus simple."),
    ('avancer', '2 Tourner, puis avancer', "Un quart de tour vers le coin, puis un travelling avant jusqu'au cadre du bureau. On revient au centre avant le coin suivant."),
    ('plateau', '3 Le plateau tournant', "La caméra reste fixe et c'est la pièce qui tourne, comme une scène de théâtre ou une bibliothèque secrète. Des murs séparent les coins."),
    ('coupe', '4 La coupe', "Les coins sont côte à côte, comme le bateau de La Vie aquatique. La caméra glisse de côté : c'est le plus simple sur téléphone."),
    ('puits', '5 Le puits', "Les coins sont empilés, et on descend d'un étage à chaque coin. Le scroll devient une descente dans la base."),
]
facons = ''.join(f'<figure class="mini">{mini(k)}<div class="lbl2">{e(t)}</div><div class="cap">{e(c)}</div></figure>' for k, t, c in FACONS)

notes = f'''
<div class="colw notes">
<section>
  <div class="stitle">L'idée : la caméra au centre</div>
  <div class="snote">19/11/2026 · une idée mise de côté pendant la recherche · 71 images en 6 thèmes</div>
  <div class="txt">Fini le grand plan du labo avec le ventilateur au fond. Une seule pièce, la caméra au centre, et un coin par activité : bureau, projets, atelier. Chaque coin prend tout l'écran et se travaille comme le coin bureau (fenêtres, décor). Avec des flèches, le scroll, un clic ou un glissé, la caméra tourne ou se déplace vers le coin suivant.</div>
  {IDEE}
</section>
<section>
  <div class="stitle">Mon avis</div>
  <ul class="list">
    <li><b>Une idée forte.</b> Le défaut du plan actuel disparaît : il n'y a plus de grand vide à remplir. Chaque coin reçoit le soin du bureau, et les zones cliquables du début deviennent des pages entières.</li>
    <li><b>Un atout technique.</b> Si la caméra ne fait que tourner autour d'un point, tout peut être rendu dans Cycles : une image fixe par coin, et une courte vidéo pour chaque passage, dans les deux sens. Le site enchaîne les vidéos et les images : la qualité des rendus du bureau, sans 3D en temps réel. C'est ce que faisait Myst en 1993.</li>
    <li><b>À surveiller.</b> Pendant la rotation, la caméra balaie les murs entre deux coins : il faut y mettre quelque chose, sinon le passage est vide. Depuis le centre, les coins sont loin, d'où la variante 2 qui avance vers chaque coin.</li>
    <li><b>Le ventilateur</b> n'est plus au fond du plan. Il peut devenir le quatrième coin, le plafond, ou la transition elle-même.</li>
  </ul>
</section>
<section>
  <div class="stitle">Cinq façons de passer d'un coin à l'autre</div>
  <div class="snote">Elles se combinent ; les références sont dans les thèmes 1, 3 et 4</div>
  <div class="minis">{facons}</div>
</section>
<section>
  <div class="stitle">Questions</div>
  <ol class="list">
    <li>Combien de coins, et lesquels ? Bureau, projets, atelier, et un quatrième (serveurs, ventilateur, entrée) ?</li>
    <li>La caméra tourne-t-elle seulement sur elle-même, ou s'approche-t-elle de chaque coin ?</li>
    <li>Le labo reste-t-il sous terre ? Les fenêtres seraient alors des verrières sur le reste du labo, ou de faux jours éclairés.</li>
    <li>Le ventilateur : on le garde, et à quelle place ?</li>
  </ol>
</section>
</div>'''

cols = [THEMES[:3], THEMES[3:]]
colhtml = ''.join('<div class="colw">' + ''.join(section(*t, f'{THEMES.index(t)+1:02d}') for t in c) + '</div>' for c in cols)

page = f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Labo, la caméra au centre</title>
<link rel="stylesheet" href="../../../outils/plan_style.css">
<style>
body{{font-family:"Inter","Helvetica Neue",Helvetica,Arial,sans-serif}}
section.theme{{width:1500px}}
.grid{{display:flex;flex-wrap:wrap;gap:14px 12px}}
.grid figure{{display:inline-flex;flex-direction:column;gap:6px}}
.grid img{{height:190px;width:auto;max-width:320px;object-fit:cover;display:block;background:#EEE}}
.grid .cap,.mini .cap{{width:0;min-width:100%;font-size:11px;line-height:1.35;color:#6B6B6B}}
.grid .cap b{{color:#111;font-weight:600}}
.keep{{border-top:1px solid #E6E6E6;padding-top:14px;display:flex;flex-direction:column;gap:4px;max-width:1100px}}
.keep .lbl{{margin-top:0}}
.notes section{{width:640px}}
.notes b{{font-weight:600;color:#111}}
.minis{{display:flex;flex-wrap:wrap;gap:22px 20px}}
.mini{{display:inline-flex;flex-direction:column;gap:6px;width:270px}}
.lbl2{{font-size:12px;font-weight:600;color:#111}}
svg .t{{font-weight:600}}
</style></head><body>
{notes}
{colhtml}
</body></html>'''

out = DOS / 'planche.html'
out.write_text(page)
print('écrit', out)
subprocess.run(['node', str(HERO / 'synthese/export.mjs'), str(out), str(DOS / 'planche.png'), '1'], check=True)
