# Studio : le site

Le dossier du futur site du studio. Il contient pour l'instant le hero : le labo souterrain en 3D.

**Rangé le 19/11/2026.** Le coin bureau est terminé. Seuls les choix retenus et les fichiers utiles sont gardés. À la corbeille :
- le plan du site et le robot guide, deux idées abandonnées ;
- les rendus bruts de Blender (9,6 Go) ;
- les étapes intermédiaires de la vidéo ;
- les pages HTML de Figma et leurs générateurs ;
- les zips des modèles, déjà dézippés.

Figma : https://www.figma.com/design/OKjyDqYXB7VLSlSEhXyA6K/creative-developer-website.

GitHub : https://github.com/amndrd/studio-site (public, depuis le 19/11).
- Le dépôt ne contient pas le contenu de tiers : les modèles 3D (`hero/outils/assets/`), les images d'inspiration et de recherche, et la sculpture.
- Il ne contient pas non plus la scène `.blend`, trop lourde pour GitHub.
- Le détail est dans `.gitignore` et `README.md`.

## Structure

```
hero/                  le hero du site : le labo souterrain en 3D
  synthese/            la synthèse de tout ce qui a été retenu (synthese.png se glisse dans Figma)
  labo/                le décor du labo : la suite du travail
    rendus/            le labo actuel : plan large dans l'axe, 2-zones/, 3-plan/ (vue de dessus)
    recherche/         la recherche par zone (bureau, coin projets, atelier, serveurs, architecture, ventilateur, ambiance)
    pour-plus-tard/    sculpture-cristofol/ : la sculpture de Cristòfol (1969, numérisation CC BY), à placer dans le labo
  bureau/              le coin bureau, terminé le 19/11
    rendus/            un dossier par élément retenu, dans l'ordre des étapes (1-bureau … 11-cables), et bureau-complet/
    coulisses/         les captures de la scène Blender (A-interface, C-decomposition), sans texte, 132 images
    video/             la vidéo de la construction du bureau (voir plus bas)
    pages/             les pages de chaque étape, en PNG (06 à 14)
    recherche/         la recherche de chaque élément (1-ensemble … 15-cables), puis coulisses/, video/, video-fond/
    scene/             bureau-complet.blend : tout le coin bureau en studio, à ouvrir dans Blender
  references/          tes images d'inspiration (1 à 9, puis v2/)
  outils/              les scripts Blender, les modèles, les textures (voir plus bas)
  credits.md           les crédits des modèles 3D tiers, à reprendre dans les mentions du site
```

## Le labo (la suite)

La base est retenue depuis le 14/11 : une salle à charpente acier avec un ventilateur, en lumière D.

- `hero/outils/blender/rendus-labo.sh` refait le labo complet : plan large, zones, lampe, vue de dessus. Il faut environ 10 min sur le M4. Les rendus finis arrivent dans `hero/labo/rendus/`.
- Pour un essai rapide : `rendus-labo.sh test bureau`.

## Le coin bureau (terminé le 19/11)

Les choix retenus :

| Étape | Retenu |
|---|---|
| 1 Bureau | D, acier noir et linoléum ; étiquettes blanches, scotch noir, marquage au sol blanc |
| 2 Rangements | N, noir |
| 3 Chaise | Mandy D01 graphite, sans appui-tête |
| 4 Poste | deux écrans 27" sur bras double, MacBook Pro, clavier, souris, AirPods, Mac Studio |
| 5 Lampe | lampe Sketchfab, noir d'origine, posée sur trois livres |
| 6 Contenu des rangements | le mix : archives, réhausse, desserte et caissons, NAS, réglette LED sous le bureau |
| 7 Papiers | les vrais documents de deux clients fictifs (Halde, Ombelle), trois classiques sous la lampe |
| 8 Objets | B, sans canettes ni gobelet sur les plans |
| 9 Sol | pas de sol, le béton du labo ; ta corbeille en maille |
| 10 Autour | D sobre : deux cartons et ton ventilateur de table blanc |
| 11 Câbles | B le long du pied ; le fil du ventilateur passe par le bureau |
| Coulisses | A (l'interface de Blender) et C (sans interface), six vues, en 16:9 et 4:5 |
| Vidéo | la construction du bureau sur la grille claire de Blender, coupe nette, validée le 19/11 |

### La vidéo (`hero/bureau/video/`)

- `la-construction-du-bureau.mp4` : la vidéo validée, en 1920 × 1080, 24 i/s, 74 s, sans texte ni son.
- `la-construction-du-bureau-en-boucle.mp4` : la même vidéo en boucle. La dernière seconde se fond dans la grille vide du début.
- `la-construction-du-bureau-telephone.mp4` : la boucle recadrée en vertical pour le téléphone (608 × 1080).
- `pour-le-site/` contient les fichiers à mettre en ligne, en H.264 sans son :
  - `ordinateur-1920x1080.mp4` (27 Mo) ;
  - `telephone-608x1080.mp4` (14 Mo).
- `images/` : 26 images clés, soit 20 de la construction et 6 de la présentation du bureau terminé.

## outils/ (`hero/outils/`)

**Les scènes Blender** (`blender/`) : la scène est faite de modules, assemblés par les scripts de rendu. Les choix retenus sont les réglages par défaut. Les autres variantes restent en options (`bureau=`, `rangements=`, `chaise=`, `ecrans=`, `lampe=`, `contenu=`, `papiers=`, `objets=`, `autour=`, `cables=`…).

- **Le labo :** `labo2-base.py` (moteur de rendu, matières, objets de base), `labo2-v2.py` (les éléments du labo) et `labo3-v3.py` (le labo actuel et ses cadrages).
- **Les objets du coin bureau :** `objets-bureau.py`, `objets-rangements.py`, `objets-chaise.py`, `objets-mandy.py`, `objets-ecrans.py`, `objets-poste.py`, `objets-lampe.py`, `objets-contenus.py`, `objets-papiers.py`, `objets-poses.py`, `objets-sol.py`, `objets-autour.py` et `objets-cables.py`. `bureau-complet.py` les assemble en studio.
- **Les scripts de rendu `rendus-*.sh` :**
  - `labo` et `bureau-complet` ;
  - un script par étape du bureau : `poste`, `contenus`, `papiers`, `objets`, `sol`, `autour`, `cables`. Avec `verif`, ils listent ce qui se croise ;
  - `coulisses` ouvre un second Blender avec son interface, qui se ferme tout seul ;
  - `fictifs` fait les rendus des projets fictifs.
- **Le fonctionnement :** chaque script construit la scène et rend les images brutes dans `blender/_bruts/` (recréé au besoin). Il lance ensuite `finition.py` (vignettage et grain), qui range les images finies dans `hero/labo/rendus/` ou `hero/bureau/rendus/`. `finition.py` a besoin de Pillow et numpy, et le Python utilisé se choisit avec `PY=…`.
- **La scène à ouvrir :** `hero/bureau/scene/bureau-complet.blend` est générée par les scripts, on ne l'enregistre pas depuis Blender. Pour la refaire, lance `_bureau-complet.py` (construit par `rendus-bureau-complet.sh`) avec `save=<fichier.blend> rendu=0`.

**La vidéo :** `blender/rendus-video.sh` construit le bureau complet et l'anime avec `video/trace.py`, `video/construction.py`, `video/boucle.py` et `video/main.py`.
- Le test d'un objet : `macstudio <style>`.
- La vidéo entière : `animatique coupe 1920 48 frames=1-1195`, puis `moteur=cycles` (256 échantillons) à partir de l'image 1196.
- Les options :
  - `frames=a-b` reprend un rendu là où il s'est arrêté ;
  - `boucle=A|B|C` donne les trois façons de défaire le bureau, écartées ;
  - `format=9x16` donne le recadrage vertical dans Blender, écarté.
- Le montage : `video_montage.py <dossiers d'images> <sortie.mp4>` monte la vidéo dans l'ordre de `montage.json`, puis `video_fondu.py` en fait la boucle.

**Les textures et les contenus :**
- `papiers.py` et `ecrans.py` génèrent les plans, papiers et écrans du labo (`textures/`, `textures-v2/`) ;
- `textures_*.py` font les étiquettes, papiers, livres, objets et cartons du bureau (`textures-bureau/`) ;
- `clavier_magic.py` fait le clavier AZERTY.

Les pages capturées en haute définition :
- `papiers-contenus/` : les documents des clients fictifs et les emballages (marques inventées) ;
- `ecrans-contenus/` : les écrans du poste.

**Les modèles** (`assets/`) :
- `polyhaven/` est sous licence CC0, et `polyhaven-download.py` en télécharge d'autres ;
- `sketchfab/` contient les modèles dézippés, avec leurs licences dans `credits.md` ;
- `fbx_ascii_obj.py` convertit un FBX texte en OBJ.

**Les pages :**
- `plan_style.css` est le style minimal des pages de travail ;
- `hero/synthese/` refait la synthèse : `python3 synthese.py && node export.mjs synthese.html synthese.png`.

