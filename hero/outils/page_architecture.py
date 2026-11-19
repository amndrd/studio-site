# La planche de la recherche « nouvelle architecture du labo » (19/11/2026).
# Lit hero/labo/recherche/8-nouvelle-architecture/sources.json et écrit planche.html à côté ;
# l'export PNG se fait avec hero/synthese/export.mjs (voir la fin du fichier).
# usage : python3 hero/outils/page_architecture.py
import json, html, subprocess
from pathlib import Path

HERO = Path(__file__).resolve().parents[1]
DOS = HERO / 'labo/recherche/8-nouvelle-architecture'
SRC = json.loads((DOS / 'sources.json').read_text())

THEMES = [
    ('01-bases-secretes', 'Bases secrètes', 'concept art, jeux',
     "Tout s'organise autour d'un centre : une fosse, une plateforme ronde, un noyau. On voit les niveaux depuis le sol. La construction, nette, tranche sur la roche brute."),
    ('02-cavernes-et-roche', 'Cavernes et roche', 'Pionen, Temppeliaukio, Salina Turda',
     "Le labo n'est plus une boîte construite, c'est un vide creusé. La roche reste brute aux murs et au plafond. Le béton, l'acier et le verre sont posés dedans, sans la toucher."),
    ('03-citernes-et-colonnes', 'Citernes et colonnes', 'G-Cans, Buffalo Bayou, El Jadida',
     "Un rythme de colonnes tient tout le volume, cadre le bureau et donne la profondeur. Le sol mouillé reflète la lumière. Une passerelle étroite traverse la forêt de piliers."),
    ('04-bunkers-et-silos', 'Bunkers et silos', 'Cheyenne Mountain, silos Titan',
     "On passe d'un couloir bas et d'une porte blindée au grand volume. Le silo propose un ordre vertical : des anneaux de plateformes autour d'un vide."),
    ('05-beton-brut', 'Béton brut', 'Kahn, parkings brutalistes',
     "Le plafond devient le motif : caissons, voûte, colonnes champignons. Les rampes et les spirales des parkings donnent des circulations qui se lisent de loin."),
    ('06-niveaux-et-passerelles', 'Niveaux et passerelles', 'caillebotis, fosses, pièces vitrées',
     "Casser le sol plat : une fosse de quelques marches pour le bureau ou les projets, une passerelle en caillebotis qui fait le tour, des pièces vitrées posées dans le hall."),
    ('07-halls-et-centrales', 'Halls et centrales', 'centrales souterraines, salles des machines',
     "Un long hall sous une voûte de roche, un pont roulant sur ses rails, des machines dans des fosses. Cette échelle industrielle justifie un ventilateur géant."),
    ('08-souffleries', 'Souffleries', 'NASA Ames et Langley',
     "Le ventilateur peut devenir la raison d'être du lieu : le labo s'installe dans une ancienne soufflerie. Le hall est la veine d'essai et l'axe mène au ventilateur. Le passage du scroll à travers lui devient logique."),
    ('09-labos-et-salles-techniques', 'Labos et salles techniques', 'MareNostrum, CERN, salles propres',
     "Des pièces techniques nettes et vitrées, posées dans une enveloppe brute (MareNostrum dans sa chapelle). Les chemins de câbles au plafond racontent le lieu."),
    ('10-lumiere', 'Lumière', 'fentes, gorges, oculus',
     "La lumière se dessine avec l'architecture : fentes, gorges cachées, oculus, plafonds lumineux, lumière rasante sur la roche. Sous terre, ces sources sont toutes artificielles : elles peuvent s'allumer une à une à l'intro."),
    ('11-plans-et-coupes', 'Plans et coupes', 'écorchés, axonométries, maquettes',
     "Penser le labo en coupe, pas seulement en plan : les niveaux, le trajet de la caméra, le ventilateur. Ces dessins sont des modèles pour le nouveau plan."),
    ('12-decors-de-cinema', 'Décors de cinéma', 'Ken Adam, Ex Machina, Blade Runner 2049',
     "Les repaires de Ken Adam sont dessinés pour la caméra : un élément central fort, des plans en profondeur, des sols qui reflètent, des flaques de lumière maîtrisées."),
]

def e(s): return html.escape(s, quote=True)

def section(tid, titre, sous, note):
    items = sorted((k, v) for k, v in SRC.items() if k.startswith(tid + '/'))
    n = tid[:2]
    figs = []
    for k, v in items:
        num = k.split('/')[1][:2]
        figs.append(f'<figure><img src="{e(k)}" alt=""><div class="cap"><b>{n}·{num}</b> {e(v["titre"])}</div></figure>')
    return (f'<section class="theme"><div class="stitle">{n} {e(titre)}</div>'
            f'<div class="snote">{len(items)} images · {e(sous)}</div>'
            f'<div class="grid">{"".join(figs)}</div>'
            f'<div class="keep"><span class="lbl">À retenir pour le labo</span><div class="txt">{e(note)}</div></div></section>')

cols = [THEMES[:6], THEMES[6:]]
colhtml = ''.join('<div class="colw">' + ''.join(section(*t) for t in c) + '</div>' for c in cols)

notes = f'''
<div class="colw notes">
<section>
  <div class="stitle">La nouvelle architecture du labo : la recherche</div>
  <div class="snote">19/11/2026 · 156 images en 12 thèmes · sources dans sources.json</div>
  <div class="txt">Le point de départ : repenser l'espace à zéro, puis y replacer le bureau et sa caméra. Les images se citent par leur numéro (par exemple 08·02).</div>
</section>
<section>
  <div class="stitle">Le labo actuel</div>
  <img class="plan" src="../../rendus/3-plan/vue-de-dessus.png" alt="">
  <ul class="list">
    <li>Une seule boîte de 16 × 22 m, un seul niveau, la même hauteur partout.</li>
    <li>Le centre est vide ; le bureau flotte au milieu, sans rien autour pour le tenir.</li>
    <li>Les zones sont collées aux murs, sans lien entre elles.</li>
    <li>Les poteaux suivent une grille régulière qui n'organise rien.</li>
    <li>Pas de circulation ni de hiérarchie : rien ne conduit le regard vers le ventilateur.</li>
  </ul>
</section>
<section>
  <div class="stitle">Ce que la recherche fait ressortir</div>
  <div class="snote">Quatre familles d'espaces ; elles se combinent</div>
  <ol class="z">
    <li><b>1</b><span><span class="lbl2">La soufflerie.</span> Le labo s'installe dans une ancienne soufflerie souterraine. Le ventilateur ferme l'axe et le hall est la veine d'essai (08).</span></li>
    <li><b>2</b><span><span class="lbl2">La caverne.</span> Un vide creusé dans le granit, avec des pièces construites posées dedans (02, 07).</span></li>
    <li><b>3</b><span><span class="lbl2">La citerne.</span> Une forêt de colonnes, un sol mouillé, le bureau sur un îlot et une passerelle qui traverse (03, 05).</span></li>
    <li><b>4</b><span><span class="lbl2">Le puits.</span> Des anneaux de niveaux autour d'une fosse centrale ; le bureau en bas ou sur une plateforme (01, 04, 06).</span></li>
  </ol>
  <div class="txt">Dans tous les cas : plusieurs niveaux plutôt qu'un sol plat, un centre fort, une lumière dessinée avec l'architecture (10), et un plan pensé en coupe (11).</div>
</section>
<section>
  <div class="stitle">Pour continuer la recherche</div>
  <div class="snote">Tout le détail : ou-chercher.md, dans ce dossier</div>
  <ul class="list">
    <li>Pars d'une image : sur Pinterest, la loupe en bas de l'épingle permet de recadrer un détail (un plafond, une colonne) et de trouver des images proches.</li>
    <li>Tape en anglais et avec des noms propres : <i>G-Cans</i>, <i>Pionen</i>, <i>Ken Adam</i>, <i>wind tunnel fan</i>.</li>
    <li>ArtStation pour le concept art, ArchDaily pour les plans et les coupes, Film-Grab pour les images de films.</li>
  </ul>
</section>
<section>
  <div class="stitle">Questions</div>
  <ol class="list">
    <li>Quels thèmes ou quelles images te parlent le plus ? Donne les numéros.</li>
    <li>Le ventilateur reste-t-il l'élément central, au bout de l'axe ?</li>
    <li>Un seul niveau, ou plusieurs : fosse, mezzanine, passerelles ?</li>
    <li>Roche brute, béton, ou les deux ?</li>
  </ol>
</section>
</div>'''

page = f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Labo, nouvelle architecture : recherche</title>
<link rel="stylesheet" href="../../../outils/plan_style.css">
<style>
body{{font-family:"Inter","Helvetica Neue",Helvetica,Arial,sans-serif}}
section.theme{{width:1560px}}
.grid{{display:flex;flex-wrap:wrap;gap:14px 12px}}
.grid figure{{display:inline-flex;flex-direction:column;gap:6px}}
.grid img{{height:170px;width:auto;max-width:300px;object-fit:cover;display:block;background:#EEE}}
.grid .cap{{width:0;min-width:100%;font-size:11px;line-height:1.35;color:#6B6B6B}}
.grid .cap b{{color:#111;font-weight:600}}
.keep{{border-top:1px solid #E6E6E6;padding-top:14px;display:flex;flex-direction:column;gap:4px;max-width:1100px}}
.keep .lbl{{margin-top:0}}
.notes section{{width:620px}}
img.plan{{width:300px;display:block}}
ol.z li{{display:flex;gap:0;align-items:flex-start}}
ol.z li b{{flex:none;margin-top:1px}}
.lbl2{{font-weight:600;color:#111}}
</style></head><body>
{notes}
{colhtml}
</body></html>'''

out = DOS / 'planche.html'
out.write_text(page)
print('écrit', out)

if __name__ == '__main__':
    png = DOS / 'planche.png'
    subprocess.run(['node', str(HERO / 'synthese/export.mjs'), str(out), str(png), '1'], check=True)
