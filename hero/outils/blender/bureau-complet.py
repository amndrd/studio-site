
# ================================================================== the whole desk corner in the studio (no lab)
# Every retained choice of the desk detail pass, assembled on the studio cyclorama: desk D with its riser, storage N
# with the retained contents (mix M) and the LED strips, workstation B2, desk lamp (Sketchfab, original black) on three
# books, chair Mandy D01 graphite without headrest, the papers (mix M), the objects (B without cans, 15/11), no floor
# covering, the mesh bin (16/11), the decor around the desk (D: two cartons, the white table fan, 16/11) and the
# cables (B le long du pied, 17/11; the fan's cable: option fil=).
# Built by rendus-bureau-complet.sh after labo2-base, objets-bureau, -rangements, -chaise, -mandy, -ecrans, -poste,
# -lampe, -contenus, -papiers, -poses, -sol, -autour and -cables (each minus its last line).
if 'book_stack' not in globals():
    def book_stack(loc, n, rz=0.0, seed=1):
        """Same pile of books as in the lab (labo3-v3.py), for the lamp position P3."""
        x, y, z = loc
        rng = random.Random(seed)
        cols = [(0.78, 0.77, 0.74), (0.15, 0.16, 0.18), (0.55, 0.57, 0.6), (0.85, 0.45, 0.12), (0.3, 0.36, 0.42)]
        for i in range(n):
            w, d, h = rng.uniform(0.17, 0.26), rng.uniform(0.22, 0.3), rng.uniform(0.018, 0.04)
            key = 'book_%d' % (i % len(cols))
            m = bpy.data.materials.get(key) or mat_color(key, cols[i % len(cols)], 0.6)
            box('book', (w, d, h), (x + rng.uniform(-0.02, 0.02), y + rng.uniform(-0.02, 0.02), z + h / 2), m, rot=(0, 0, rz + rng.uniform(-0.15, 0.15)))
            z += h
        return z

SHOT_BC = {
    'ensemble': dict(cam=(-2.45, -3.35, 1.85), target=(0.72, 0.1, 0.62), lens=30, fstop=11, focus=None),
    'poste': dict(cam=(-1.75, -2.3, 1.62), target=(0.12, 0.12, 0.98), lens=30, fstop=8, focus=None),
    'face': dict(cam=(1.0, -7.4, 1.25), target=(1.0, 0.0, 0.72), lens=56, fstop=16, focus=None),
    'droite': dict(cam=(4.35, -3.35, 1.8), target=(0.95, 0.15, 0.74), lens=30, fstop=11, focus=None),
    'corbeille': dict(cam=(0.15, -1.45, 0.62), target=(0.95, -0.3, 0.12), lens=40, fstop=5.6, focus=None),
}


def build_bureau_complet():
    """Studio, lights, and every retained piece of the desk corner (the papers are added by the caller)."""
    setup_render()
    try:
        SC.view_settings.look = 'AgX - Medium High Contrast'
    except TypeError:
        pass
    materials_bureau()
    materials_ecrans()
    materials_lampe()
    M['grey_r'] = m_powder('grey_r', (0.58, 0.59, 0.585), rough=0.4)
    M['hole'] = mat_color('hole', (0.035, 0.028, 0.02), rough=0.8)
    M['paperw'] = m_surface('paperw', (0.82, 0.82, 0.8), rough=0.75, var=0.02)
    studio()
    for o in bpy.data.objects:
        if o.type == 'LIGHT':
            o.data.energy *= float(OPT.get('dim', 0.7))
    build_with_desk(look('N'))                                   # desk D + riser + the four storage pieces, filled (mix M)
    remplir_rehausse(_FC, H0 + 0.3015, 0.27, -0.85, 1.05, H0)    # riser contents
    led_sous_bureau(_FC, H0, H1)                                 # LED strips under the desk top and the return
    build_setup('B2')                                            # two 27" on a dual arm, MacBook Pro, keyboard, mouse, AirPods, Mac Studio
    OPT.setdefault('lpos', 'P3')
    before = {o for o in bpy.data.objects if o.type == 'LIGHT'}
    lampe_au_bureau('S-N', _F0, H0)                              # Sketchfab lamp, original black, on three books
    for o in bpy.data.objects:
        if o.type == 'LIGHT' and o not in before:
            o.data.energy *= float(OPT.get('lk', 0.45))          # the studio is far brighter than the lab
    import_mandy(OPT.get('mfin', 'graphite'), OPT.get('mvar', 'sans-appui-tete'), (-0.05, -0.8), math.pi + rad(-15))


def main_bureau_complet():
    build_bureau_complet()
    if 'papiers_bureau' in globals():
        papiers_bureau(_F0, H0, H1)                              # retained papers (objets-papiers.py, option papiers=)
    if 'objets_bureau' in globals():
        objets_bureau(_F0, H0, H1)                               # retained objects (objets-poses.py, option objets=)
    if 'sol_bureau' in globals():
        sol_bureau(_F0, H0, H1)                                  # no floor covering, the mesh bin and its paper balls (objets-sol.py)
    if 'autour_bureau' in globals():
        autour_bureau(_F0, H0, H1)                               # around the desk, retained D: two cartons, the white table fan (objets-autour.py)
    if 'cables_bureau' in globals():
        cables_bureau(_F0, H0, H1)                               # the cables and the power strip, B le long du pied (objets-cables.py)
    os.makedirs(OUT, exist_ok=True)
    vues = OPT.get('vues', 'ensemble,poste,face,droite').split(',')
    if OPT.get('save'):
        # save=1 -> OUT/bureau-complet.blend, save=<path.blend> -> that file (hero/bureau/scene/ for the user); rendu=0: no render
        path = OPT['save'] if OPT['save'].endswith('.blend') else os.path.join(OUT, 'bureau-complet.blend')
        cams = [make_camera(dict(SHOT_BC[v]), f'CAM_{v}') for v in vues]
        SC.camera = cams[0]
        SC.render.resolution_x = RES
        SC.render.resolution_y = int(RES * 9 / 16)
        bpy.ops.wm.save_as_mainfile(filepath=path)
        print('SAVED', path, flush=True)
        if OPT.get('rendu', '1') == '0':
            return
        for c in cams:
            bpy.data.objects.remove(c, do_unlink=True)
    for v in vues:
        SC.camera = make_camera(dict(SHOT_BC[v]), f'CAM_{v}')
        SC.render.resolution_x = RES
        SC.render.resolution_y = int(RES * 9 / 16)
        SC.render.filepath = os.path.join(OUT, f'bureau-{v}.png')
        print('RENDER', SC.render.filepath, flush=True)
        bpy.ops.render.render(write_still=True)


main_bureau_complet()
