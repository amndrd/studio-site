
# ================================================================== renders of the fictional projects printed on the desk papers
# Two fictional clients of the studio: Ombelle (a speaker brand: product shots of "Ombelle One") and Halde (a gallery and
# café in a converted hall, by the fictional Vesper & Morel architectes: photo of the white study model).
# Built by rendus-fictifs.sh after labo2-base.py and objets-bureau.py (minus its last line).
# Output: hero/outils/papiers-contenus/img/*.png (used by the HTML documents and the photo prints).
COLS_O = {'sauge': ((0.36, 0.42, 0.36), (0.25, 0.3, 0.26)), 'argile': ((0.6, 0.38, 0.26), (0.42, 0.27, 0.2)), 'encre': ((0.06, 0.062, 0.066), (0.035, 0.036, 0.04))}


def m_fabric(name, color):
    return m_surface(name, color, rough=0.95, var=0.05, grain=9000, bump=0.06)


def enceinte(x, y, rz, col, scale=1.0):
    """Ombelle One: rounded cabinet, fabric front, oak top plate, brass knob and badge, felt feet."""
    body, fab = COLS_O[col]
    mb = m_surface('o_body_' + col, body, rough=0.5, var=0.02, grain=600, bump=0.003)
    mf = m_fabric('o_fab_' + col, fab)
    w, d, h = 0.17 * scale, 0.15 * scale, 0.26 * scale
    before = set(bpy.data.objects)
    bx('o_body', (w, d, h), (0, 0, h / 2 + 0.006), mb, bev=0.018 * scale, seg=6)
    bx('o_grille', (w - 0.024 * scale, 0.006, h - 0.06 * scale), (0, -d / 2 - 0.0005, h / 2 + 0.012), mf, bev=0.008 * scale, seg=4)
    bx('o_top', (w - 0.01 * scale, d - 0.01 * scale, 0.012 * scale), (0, 0, h + 0.006 + 0.004 * scale), M['birch'], bev=0.004 * scale, seg=3)
    cyl('o_knob', 0.016 * scale, 0.014 * scale, (w * 0.22, d * 0.12, h + 0.006 + 0.016 * scale), M['brass'], verts=40)
    bx('o_badge', (0.032 * scale, 0.002, 0.007 * scale), (0, -d / 2 - 0.0035, 0.032 * scale), M['brass'], bev=0.0006)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl('o_foot', 0.008 * scale, 0.006, (sx * w * 0.35, sy * d * 0.35, 0.003), M['rubber'], verts=20)
    root = bpy.data.objects.new('o_root', None)
    root.location = (x, y, 0)
    root.rotation_euler = (0, 0, rz)
    link(root)
    for o in set(bpy.data.objects) - before:
        if o.parent is None and o is not root:
            o.parent = root


def maquette():
    """Study model of Halde at 1:100: oak base, white card volumes, sawtooth roof, street, trees in felt."""
    white = m_surface('mq_blanc', (0.86, 0.86, 0.84), rough=0.85, var=0.015, grain=900, bump=0.002)
    grey = m_surface('mq_gris', (0.55, 0.55, 0.54), rough=0.9, var=0.02, grain=900, bump=0.002)
    dark = mat_color('mq_vitre', (0.05, 0.055, 0.06), rough=0.2)
    bx('mq_socle', (0.62, 0.44, 0.02), (0, 0, 0.01), M['birch'], bev=0.002)
    bx('mq_rue', (0.62, 0.09, 0.0015), (0, -0.165, 0.0208), grey, bev=0)
    L, W, Hh = 0.44, 0.22, 0.09
    bx('mq_halle', (L, W, Hh), (0, 0.03, 0.02 + Hh / 2), white, bev=0.0008)
    n = 5
    for i in range(n):                                            # sawtooth roof (sheds facing north)
        x0 = -L / 2 + i * L / n
        prof = [(x0, 0.02 + Hh), (x0 + L / n, 0.02 + Hh), (x0 + L / n, 0.02 + Hh + 0.045)]
        v = [(px, y, pz) for y in (-W / 2 + 0.03, W / 2 + 0.03) for px, pz in prof]
        me = bpy.data.meshes.new('mq_shed')
        me.from_pydata(v, [], [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)])
        me.validate()
        o = bpy.data.objects.new('mq_shed', me)
        me.materials.append(white)
        link(o)
        bx('mq_shed_vitre', (0.002, W - 0.01, 0.036), (x0 + L / n - 0.0012, 0.03 + 0.005, 0.02 + Hh + 0.022), dark, bev=0)
    for k in range(6):                                            # street facade openings
        bx('mq_baie', (0.05, 0.002, 0.055), (-0.18 + k * 0.072, 0.03 - W / 2 - 0.0005, 0.02 + 0.034), dark, bev=0)
    bx('mq_annexe', (0.12, 0.1, 0.05), (0.27, 0.12, 0.045), white, bev=0.0008)
    bx('mq_voisin', (0.16, 0.12, 0.13), (-0.25, 0.14, 0.085), grey, bev=0.0008)
    felt = m_surface('mq_arbre', (0.36, 0.4, 0.34), rough=1.0, var=0.08, grain=5000, bump=0.05)
    for x in (-0.24, -0.12, 0.0, 0.12, 0.24):
        cyl('mq_tronc', 0.0018, 0.03, (x, -0.2, 0.035), white, verts=8)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=0.018, location=(x, -0.2, 0.062))
        s = bpy.context.active_object
        s.data.materials.append(felt)
        bpy.context.collection.objects.unlink(s)
        link(s)


def main_fictifs():
    setup_render()
    try:
        SC.view_settings.look = 'AgX - Medium High Contrast'
    except TypeError:
        pass
    materials_bureau()
    if 'brass' not in M:
        M['brass'] = mat_color('brass', (0.78, 0.6, 0.32), rough=0.28, metal=1.0)
    out = OPT.get('out')
    os.makedirs(out, exist_ok=True)
    shots = []
    studio(0.42)                                                  # light warm-grey seamless backdrop, shared by every shot
    # Ombelle: three colours
    c = coll('ombelle')
    CUR[0] = c
    for k, (x, col) in enumerate(((-0.22, 'argile'), (0.0, 'sauge'), (0.22, 'encre'))):
        enceinte(x, 0.05 * (k == 1), rad(-12 + 12 * k), col)
    shots.append(('ombelle-trio', c, dict(cam=(0.15, -1.55, 0.42), target=(0.0, 0.0, 0.14), lens=70, fstop=8, focus=None), (1600, 1000)))
    c2 = coll('ombelle1')
    CUR[0] = c2
    enceinte(0.0, 0.0, rad(-24), 'sauge', 1.0)
    shots.append(('ombelle-sauge', c2, dict(cam=(0.35, -0.95, 0.36), target=(0.0, 0.0, 0.14), lens=85, fstop=4, focus=None), (1200, 1500)))
    c3 = coll('maquette')
    CUR[0] = c3
    maquette()
    shots.append(('halde-maquette', c3, dict(cam=(-0.72, -0.82, 0.62), target=(0.02, 0.03, 0.05), lens=50, fstop=5.6, focus=None), (1600, 1067)))
    for name, cc, cam, (w, h) in shots:
        for k in ('ombelle', 'ombelle1', 'maquette'):
            bpy.data.collections[k].hide_render = bpy.data.collections[k] is not cc
        SC.camera = make_camera(cam, 'CAM_' + name)
        SC.render.resolution_x, SC.render.resolution_y = w, h
        SC.render.filepath = os.path.join(out, name + '.png')
        print('RENDER', name, flush=True)
        bpy.ops.render.render(write_still=True)


main_fictifs()
