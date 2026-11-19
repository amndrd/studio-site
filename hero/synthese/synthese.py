# Global synthesis of the project, from the start: only what was retained. One long page in the minimal plan style
# (the hero lab, the desk corner step by step, the current step, roadmap, rules). The site plan and the robot guide are
# left out on purpose (asked 15/11; both ideas dropped on 19/11): the synthesis covers the hero only.
# Images are copied (resized) from the project folders into synthese/img. Export to PNG with export.mjs.
# usage: python -I synthese.py        (needs Pillow)
import json, os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # hero/ (the synthesis is in hero/synthese)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def web(src, name, w, h=None, q=86):
    """Resized copy; with h, cropped to w x h (cover, centred)."""
    im = Image.open(src).convert('RGB')
    if h:
        r = max(w / im.width, h / im.height)
        im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
        x = (im.width - w) // 2
        y = (im.height - h) // 2
        im = im.crop((x, y, x + w, y + h))
    else:
        im.thumbnail((w, w * 3), Image.LANCZOS)
    im.save(os.path.join(IMG, name), quality=q, optimize=True)
    return im.size


def fig(src, name, w, h=None, cap=''):
    if not os.path.exists(src):
        return ''
    sw, sh = web(src, name, w * 2, h * 2 if h else None)
    hh = h or round(w * sh / sw)
    c = f'<div class="cap">{cap}</div>' if cap else ''
    return f'<figure style="width:{w}px"><img src="img/{name}" width="{w}" height="{hh}">{c}</figure>'


def section(num, title, body, note=''):
    n = f'<div class="snote">{note}</div>' if note else ''
    return f'<section><div class="sh"><span class="num">{num}</span><div><div class="stitle">{title}</div>{n}</div></div>{body}</section>'


def row(*items, gap=18):
    return f'<div class="row" style="gap:{gap}px">{"".join(items)}</div>'


def ul(items):
    return '<ul class="list">' + ''.join(f'<li>{t}</li>' for t in items) + '</ul>'


# ------------------------------------------------------------------ 1. the hero lab
L = os.path.join(ROOT, 'labo', 'rendus')
zones = ''.join(fig(os.path.join(L, '2-zones', f), f'labo-z{i}.jpg', 300, 169, f[2:-4].replace('-', ' ')) for i, f in enumerate(sorted(os.listdir(os.path.join(L, '2-zones')))))
s1 = section('01', 'Le hero · le labo souterrain', row(fig(os.path.join(L, '1-plan-large-axe.png'), 'labo-axe.jpg', 1240, cap='plan large dans l’axe'),
                                                       fig(os.path.join(L, '3-plan', 'vue-de-dessus.png'), 'labo-plan.jpg', 600, cap='vue de dessus'))
              + f'<div class="row" style="gap:12px">{zones}</div>' + ul([
    'Base retenue le 14/11 : la salle à charpente acier avec le grand ventilateur, lumière D, plan large dans l’axe et caméra sur le bureau.',
    'Un décor sans personnage, des objets d’aujourd’hui (rien de rétro). Six zones : bureau, coin projets, atelier, serveurs, ventilateur, lampe.',
    'Depuis le 14/11, le coin bureau est repris en détail, élément par élément (section 02). Ces vues montrent déjà tous les choix retenus.']),
    '13/11 → 16/11 · hero/labo/rendus · Blender, Cycles')

# ------------------------------------------------------------------ 2. the desk corner, step by step
B = os.path.join(ROOT, 'bureau', 'rendus')
STEPS = [('1-bureau', 'Bureau D', 'Acier noir fin, linoléum ardoise sur contreplaqué, réhausse en acier perforé plié. Étiquettes blanches, scotch noir, marquage au sol blanc.',
          ('1-trois-quarts.png', '4-dans-le-labo-cadrage-bureau.png')),
         ('2-rangements', 'Rangements N, noir', 'Caisson ouvert, caisson à tiroirs, meuble bas sous le retour, desserte.', ('1-ensemble.png', '3-avec-le-bureau.png')),
         ('3-chaise', 'Chaise Mandy D01', 'Graphite, sans appui-tête.', ('1-trois-quarts.png', '3-dans-le-labo.png')),
         ('4-poste', 'Poste B2', 'Deux écrans 27" sur bras double, MacBook Pro, clavier, souris, AirPods, Mac Studio modélisé. Vrais contenus d’écran (code, Figma, GitHub).',
          ('3-trois-quarts.png', '8-detail-objets.png')),
         ('5-lampe', 'Lampe', 'Lampe de bureau Sketchfab, noir d’origine, posée sur trois classiques : K&amp;R, Albers, Müller-Brockmann.', ('4-trois-quarts.png', '2-dans-le-labo-gros-plan.png')),
         ('6-contenu-rangements', 'Contenu des rangements', 'Le mix : dossiers suspendus d’archives, réhausse, desserte et caissons vécus, le NAS posé au bout de la réhausse ; réglette LED sous le bureau.',
          ('6-rehausse.png', '2-caisson-ouvert.png')),
         ('7-papiers', 'Papiers', 'Le mix B + C : vrais documents de deux clients fictifs (Halde, galerie &amp; café ; Ombelle, enceintes), annotés à la main ; la table à plans sur le retour.',
          ('3-sous-la-lampe.png', '4-retour.png')),
         ('8-objets', 'Objets du bureau', 'Tes modèles Sketchfab : le café du torréfacteur inventé Pente sous la lampe, deux crayons, la gomme et le stylo sur les papiers, une petite plante sur la réhausse, une plante en pot de béton sur la table à plans. Sans canettes.',
          ('3-sous-la-lampe.png', '5-retour.png')),
         ('9-sol', 'Sol', 'Pas de revêtement : le coin bureau est posé directement sur le béton mouillé du labo. Une corbeille en maille d’acier noir (ton modèle), avec ses boulettes de papier (une est tombée à côté).',
          ('2-dans-le-labo-plan-large.png', '3-la-corbeille-dans-le-labo.png')),
         ('10-autour', 'Autour du bureau', 'La piste D sobre : deux cartons d’expédition à gauche du bureau (scotch noir, étiquettes blanches) et ton ventilateur de table en blanc posé dessus, tourné vers la chaise. Pas de plantes autour du bureau.',
          ('7-dans-le-labo-plan-large.png', '4-ventilateur.png')),
         ('11-cables', 'Les câbles', 'La piste B : sous le plateau, tout passe dans la goulotte et descend en rangée le long du pied arrière droit jusqu’à la multiprise, posée au sol derrière la corbeille ; son câble part derrière le bureau et s’y cache. Le fil blanc du ventilateur passe par le pied gauche, sous le plateau et dans la goulotte. Le MacBook n’a pas de câble.',
          ('10-dans-le-labo-plan-large.png', '4-la-multiprise.png'))]
steps = ''
for i, (d, t, txt, (a, b)) in enumerate(STEPS, 1):
    steps += (f'<div class="step"><div class="col" style="gap:6px;width:340px"><div class="stitle" style="font-size:15px">{i} · {t}</div><p class="txt">{txt}</p></div>'
              f'{fig(os.path.join(B, d, a), f"b{i}a.jpg", 720, 405)}{fig(os.path.join(B, d, b), f"b{i}b.jpg", 720, 405)}</div>')
C = os.path.join(B, 'bureau-complet')
complet = row(fig(os.path.join(C, '1-ensemble.png'), 'complet-1.jpg', 920, cap='ensemble'), fig(os.path.join(C, '2-poste.png'), 'complet-2.jpg', 920, cap='le poste'))
complet += row(fig(os.path.join(C, '3-face.png'), 'complet-3.jpg', 920, cap='de face'), fig(os.path.join(C, '4-cote-droit.png'), 'complet-4.jpg', 920, cap='côté droit'))
s2 = section('02', 'Le coin bureau · étape par étape', f'<div class="col" style="gap:22px">{steps}</div>'
             + '<div class="stitle" style="font-size:15px;margin-top:10px">Le bureau complet, en studio, avec tout ce qui est retenu</div>' + complet,
             '14/11 → 17/11 · hero/bureau/rendus · bureau-complet = rendus-bureau-complet.sh')

# ------------------------------------------------------------------ 3. now, roadmap, rules
s3 = section('03', 'Dernière étape · la vidéo de la construction du bureau, validée', ul([
    'Une vidéo pour le site : le bureau se construit du début à la fin, dans l’ordre physique, sans sol. Chaque élément apparaît en fil de fer, se modélise, passe en argile, se colorise, puis se texture.',
    'Un plan-séquence autour du bureau, entrecoupé de gros plans. La lampe lève son bras puis s’allume, la chaise arrive en roulant, les écrans s’allument. Les deux scènes de la fenêtre de Blender sont retirées de la vidéo (18/11).',
    'Style retenu : la coupe nette. La v2 (17/11) est plus rapide (57 s) et a des gros plans plus larges ; le MacBook remplace le Mac Studio ; la lampe et la chaise apparaissent dans le plan large ; les câbles arrivent à la fin. La lampe du décor est corrigée (sa tête vers les papiers, son spot dans l’ampoule).',
    'Le fond retenu (18/11) : la grille claire de Blender, un sol gris clair aux lignes foncées et un horizon presque blanc ; elle s’efface à la fin dans un béton clair taché. Aucun texte, pas de son, en 16:9.',
    'Le rendu final est terminé et validé (19/11, 74 s, dans hero/bureau/video) : EEVEE pour la construction, Cycles à partir des LED. Après ta relecture : plus de tache claire au début, le ventilateur se modélise après ses cartons, et une présentation du bureau terminé en six plans (du dessus, le MacBook, de côté, la lampe, de derrière, au ras du plateau) avant le plan final du poste.',
    'La vidéo tourne en boucle (19/11, hero/bureau/video) : la dernière seconde du plan final se fond dans la grille vide du début, puis la vidéo repart. Retenu le fondu enchaîné, plus simple que les trois façons de défaire le bureau qui étaient proposées.',
    'La version téléphone (19/11, hero/bureau/video) : le simple recadrage vertical de la vidéo en boucle, 608 × 1080, un fichier de 14 Mo pour le site.',
    'Les captures « dans les coulisses » sont retenues et livrées : A et C au complet, six vues, 132 images (hero/bureau/coulisses).',
    'La sculpture (Leandre Cristòfol, 1969, numérisation CC BY) attend l’étape du décor : au clic, le site affichera sa notice.']), '17/11 → 19/11')
s4 = section('04', 'Feuille de route du coin bureau', '<ol class="list">' + ''.join(f'<li>{t}</li>' for t in [
    'Bureau, rangements, chaise, poste, lampe, contenu des rangements, papiers : faits et retenus.', 'Objets sur le bureau : faits et retenus (B en cours, sans canettes).', 'Le sol : pas de revêtement, le béton du labo ; la corbeille (ton modèle en maille, 16/11).',
    'Le décor autour du coin bureau : retenu, D sobre avec le ventilateur de table blanc (16/11).',
    'La gestion des câbles : retenue, B le long du pied, le fil du ventilateur par le bureau (17/11).',
    'Les captures « dans les coulisses » de la scène Blender : A et C retenues, six vues, livrées (17/11).',
    'La vidéo de la construction du bureau : coupe nette et grille claire de Blender retenues ; rendu final avec la présentation du bureau terminé, validée le 19/11 ; en boucle par un fondu enchaîné.']) + '</ol>')
s5 = section('05', 'Les règles du décor', ul([
    'Étiquettes blanches, scotch noir, marquage au sol blanc (pas d’orange sur les étiquettes).',
    'Aucun personnage dans la scène, des objets d’aujourd’hui (rien de rétro).',
    'Rien de l’atelier ni du coin projets sur le bureau ; les plantes restent discrètes sur le bureau.',
    'Tout ce qui se lit est un vrai document travaillé et crédible, pour des clients fictifs ; pas d’images du bureau sur le bureau, pas tes propres modèles.',
    'Les prototypes sont des rendus PNG de qualité pro, rangés dans le projet ; les pages Figma restent sobres.',
    'Les modèles tiers : licences libres seulement (CC0, CC BY crédité dans hero/credits.md).']))

CSS = """
@font-face{font-family:Inter;font-weight:400;src:url(../plan-du-site/polices/inter-latin-400-normal.woff2)}
@font-face{font-family:Inter;font-weight:500;src:url(../plan-du-site/polices/inter-latin-500-normal.woff2)}
@font-face{font-family:Inter;font-weight:600;src:url(../plan-du-site/polices/inter-latin-600-normal.woff2)}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#EFEFEF}
body{font-family:Inter,sans-serif;color:#111;font-size:13px;line-height:1.5;padding:100px;width:2140px;display:flex;flex-direction:column;gap:80px}
header{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:1px solid #111;padding-bottom:22px}
header h1{font-size:40px;font-weight:600;letter-spacing:-.5px}
header .sub{font-size:15px;color:#555;margin-top:6px}
header .meta{text-align:right;color:#555;font-size:13px}
section{background:#fff;padding:40px;display:flex;flex-direction:column;gap:22px;width:1940px}
.sh{display:flex;gap:18px;align-items:flex-start}
.num{font-size:13px;font-weight:600;color:#fff;background:#111;padding:3px 8px;margin-top:2px}
.stitle{font-size:20px;font-weight:600}
.snote{font-size:12px;color:#8A8A8A;margin-top:2px}
.row{display:flex;align-items:flex-start}
.wrap{flex-wrap:wrap}
.col{display:flex;flex-direction:column}
figure{display:flex;flex-direction:column;gap:6px}
figure img{display:block;object-fit:cover}
.cap{font-size:12px;color:#6B6B6B;line-height:1.4}
.txt{font-size:13px;color:#333}
ul.list,ol.list{padding-left:18px;display:flex;flex-direction:column;gap:6px;font-size:13.5px;color:#222;max-width:1500px}
.step{display:flex;gap:20px;padding-bottom:22px;border-bottom:1px solid #EEE}
"""
doc = (f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Studio · synthèse du projet</title><style>{CSS}</style>'
       '<script src="https://mcp.figma.com/mcp/html-to-design/capture.js" async></script></head><body>'
       '<header><div><h1>Studio · synthèse du projet</h1><div class="sub">Le hero : ce qui a été retenu, du labo souterrain au coin bureau</div></div>'
       '<div class="meta">13 → 17 novembre 2026<br>hero 3D · Blender, Cycles</div></header>'
       f'{s1}{s2}{s3}{s4}{s5}</body></html>')
open(os.path.join(HERE, 'synthese.html'), 'w', encoding='utf-8').write(doc)
print('ok', len(doc))
