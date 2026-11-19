# Finishing pass (vignette + film grain) of the raw Blender renders into the prototype folders.
# usage: python -I finition.py <hero_dir> labo|poste|contenus|complet|papiers|objets
#   autour   : outils/blender/_bruts/autour (blender/rendus-autour.sh) -> bureau/rendus/10-autour (retained D)
#   cables   : outils/blender/_bruts/cables (blender/rendus-cables.sh) -> bureau/rendus/11-cables (A, B, C, communs)
#   sol      : outils/blender/_bruts/labo + complet (blender/rendus-sol.sh) -> bureau/rendus/9-sol (no floor, the bin)
#   objets   : outils/blender/_bruts/objets (blender/rendus-objets.sh) -> bureau/rendus/8-objets (retained objects, sculpture for later)
#   contenus : outils/blender/_bruts/contenus (blender/rendus-contenus.sh) -> bureau/rendus/6-contenu-rangements
#   papiers  : outils/blender/_bruts/papiers (blender/rendus-papiers.sh) -> bureau/rendus/7-papiers
#   complet  : outils/blender/_bruts/complet (blender/rendus-bureau-complet.sh) -> bureau/rendus/bureau-complet
#   labo  : outils/blender/_bruts/labo  (blender/rendus-labo.sh)  -> labo/rendus
#   poste : outils/blender/_bruts/poste (blender/rendus-poste.sh) -> bureau/rendus/4-poste
import os, sys
import numpy as np
from PIL import Image

H, JOB = sys.argv[1], sys.argv[2]

# grades: (vignette strength, vignette start, ellipse factor, grain, grain floor)
GRADE = {'labo': (0.3, 0.35, 0.85, 0.016, 0.35), 'studio': (0.22, 0.4, 0.8, 0.012, 0.4), 'none': None}

JOBS = {
    'labo': ('labo/rendus', [
        ('V3-axe.png', '1-plan-large-axe.png', 'labo'),
        ('V3-bureau.png', '2-zones/1-bureau.png', 'labo'),
        ('V3-projets.png', '2-zones/2-coin-projets.png', 'labo'),
        ('V3-atelier.png', '2-zones/3-atelier.png', 'labo'),
        ('V3-serveurs.png', '2-zones/4-serveurs.png', 'labo'),
        ('V3-ventilo.png', '2-zones/5-ventilateur.png', 'labo'),
        ('V3-lampe.png', '2-zones/6-lampe-de-bureau.png', 'labo'),
        ('V3-plan.png', '3-plan/vue-de-dessus.png', 'none')]),
    'poste': ('bureau/rendus/4-poste', [
        ('labo/V3-bureau-B2.png', '1-dans-le-labo-cadrage-bureau.png', 'labo'),
        ('labo/V3-axe-B2.png', '2-dans-le-labo-plan-large.png', 'labo'),
        ('B2-tq.png', '3-trois-quarts.png', 'studio'),
        ('B2-face.png', '4-face.png', 'studio'),
        ('B2-det.png', '5-detail-clavier-souris.png', 'studio'),
        ('B2-clavier.png', '6-clavier.png', 'studio'),
        ('B2-mac.png', '7-detail-macbook.png', 'studio'),
        ('B2-objets.png', '8-detail-objets.png', 'studio')]),
}
# storage contents, retained mix M (blender/rendus-contenus.sh). The four prototype pistes went to the Trash on 15/11.
JOBS['contenus'] = ('bureau/rendus/6-contenu-rangements', [
    ('M-grp.png', '1-ensemble.png', 'studio'), ('M-ouvert.png', '2-caisson-ouvert.png', 'studio'),
    ('M-tiroirs.png', '3-tiroirs.png', 'studio'), ('M-desserte.png', '4-desserte.png', 'studio'),
    ('M-bur.png', '5-avec-le-bureau.png', 'studio'), ('M-rehausse.png', '6-rehausse.png', 'studio'),
    ('labo/V3-bureau-M.png', '7-dans-le-labo-cadrage-bureau.png', 'labo'),
    ('labo/V3-rangements-M.png', '8-dans-le-labo-rangements.png', 'labo')])

# the whole desk corner in the studio, without the lab (blender/rendus-bureau-complet.sh)
JOBS['complet'] = ('bureau/rendus/bureau-complet', [
    ('bureau-ensemble.png', '1-ensemble.png', 'studio'), ('bureau-poste.png', '2-poste.png', 'studio'),
    ('bureau-face.png', '3-face.png', 'studio'), ('bureau-droite.png', '4-cote-droit.png', 'studio')])

# papers on the desk, the B + C mix retained on 15/11 (blender/rendus-papiers.sh). Pistes A, B, C went to the Trash.
JOBS['papiers'] = ('bureau/rendus/7-papiers', [(f'M-{v}.png', n, 'studio') for v, n in (
    ('ensemble', '1-ensemble.png'), ('dessus', '2-vue-de-dessus.png'), ('lampe', '3-sous-la-lampe.png'), ('retour', '4-retour.png'),
    ('poste', '5-poste.png'), ('livres', '6-livres-sous-la-lampe.png'))] + [('labo/V3-bureau-M.png', '7-dans-le-labo-cadrage-bureau.png', 'labo')])

VUES_OB = (('ensemble', '1-ensemble'), ('dessus', '2-vue-de-dessus'), ('lampe', '3-sous-la-lampe'), ('mac', '4-a-droite-du-macbook'),
           ('retour', '5-retour'), ('plante', '6-plante-sur-la-rehausse'))
# objects on the desk, retained 15/11 (B without the cans and the cup on the plans); the sculpture waits for the lab decor
# (filed in labo/pour-plus-tard/sculpture-cristofol since the 19/11 tidy-up)
JOBS['objets'] = ('bureau/rendus/8-objets', [(f'B-{v}.png', f'{n}.png', 'studio') for v, n in VUES_OB]
                  + [('labo/V3-bureau-B.png', '7-dans-le-labo-cadrage-bureau.png', 'labo'),
                     ('S-sculpture.png', '../../../labo/pour-plus-tard/sculpture-cristofol/1-trois-quarts.png', 'studio'), ('S-sculpture-face.png', '../../../labo/pour-plus-tard/sculpture-cristofol/2-face.png', 'studio'),
                     ('S-sculpture-cote.png', '../../../labo/pour-plus-tard/sculpture-cristofol/3-cote.png', 'studio')])
# the floor of the desk corner, retained 16/11: no floor covering (the lab's concrete), the perforated bin
# (blender/rendus-sol.sh: the lab views come from _bruts/labo, the bin from _bruts/complet). Pistes A-D went to the Trash.
JOBS['sol'] = ('bureau/rendus/9-sol', [('../labo/V3-bureau.png', '1-dans-le-labo-cadrage-bureau.png', 'labo'),
                                          ('../labo/V3-axe.png', '2-dans-le-labo-plan-large.png', 'labo'),
                                          ('../labo/V3-corbeille.png', '3-la-corbeille-dans-le-labo.png', 'labo'),
                                          ('../complet/bureau-corbeille.png', '4-la-corbeille-en-studio.png', 'studio')])

# the decor around the desk, retained 16/11: D sobre with the white table fan (blender/rendus-autour.sh); the bin views.
# Prototypes A-C and E-F went to the Trash.
JOBS['autour'] = ('bureau/rendus/10-autour', [(f'D-{v}.png', f'{n}.png', 'studio') for v, n in (
    ('large', '1-ensemble'), ('dessus', '2-vue-de-dessus'), ('droite', '3-cote-droit'), ('ventilo', '4-ventilateur'), ('detail', '5-detail'),
    ('corbeille', '9-corbeille-sous-le-bureau'))]
    + [(f'labo/V3-{s}-D.png', f'{n}.png', 'labo') for s, n in (('bureau', '6-dans-le-labo-cadrage-bureau'), ('axe', '7-dans-le-labo-plan-large'),
                                                             ('corbeille', '10-corbeille-dans-le-labo'))])

# the cables of the desk corner, retained 17/11: B le long du pied, the fan's cable par le bureau (blender/rendus-cables.sh;
# the lab views come from _bruts/labo, rendus-labo.sh). Pistes A and C and the other fan solutions went to the Trash.
JOBS['cables'] = ('bureau/rendus/11-cables', [(f'cables-{v}.png', f'{n}.png', 'studio') for v, n in (
    ('ensemble', '1-ensemble'), ('dessous', '2-sous-le-bureau'), ('arriere', '3-derriere-le-bureau'), ('multiprise', '4-la-multiprise'),
    ('fil', '5-le-fil-du-ventilateur'), ('bras', '6-le-bras-et-le-mat'), ('mac', '7-derriere-le-mac-studio'), ('lampe', '8-la-lampe'))]
    + [('../labo/V3-bureau.png', '9-dans-le-labo-cadrage-bureau.png', 'labo'), ('../labo/V3-axe.png', '10-dans-le-labo-plan-large.png', 'labo')])


def finish(src, dst, grade):
    a = np.asarray(Image.open(src).convert('RGB')).astype(np.float32) / 255.0
    if GRADE[grade]:
        vig, start, ell, grain, floor = GRADE[grade]
        h, w = a.shape[:2]
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 * ell + ((yy - h / 2) / (h / 2)) ** 2 * ell)
        a *= (1.0 - vig * np.clip(r - start, 0, None) ** 1.6)[..., None]
        g = np.random.default_rng(len(dst)).normal(0, grain, (h, w, 1)).astype(np.float32)
        a += g * (floor + (1 - floor) * np.sqrt(np.clip(a.mean(axis=2, keepdims=True), 0, 1)))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)).save(dst, optimize=True)


root, items = JOBS[JOB]
root = os.path.join(H, root)
for src, dst, grade in items:
    p = os.path.join(H, 'outils', 'blender', '_bruts', JOB, src)
    if os.path.exists(p):
        finish(p, os.path.join(root, dst), grade)
        print(dst)
    else:
        print('absent', src)
