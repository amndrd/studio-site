
# ================================================================== the decor around the desk (step 10, retained 16/11)
# Retained 16/11: prototype D "sobre" with the white table fan. On the left of the desk, two shipping cartons stacked
# (archives 2024 and cables: kraft board, black tape, printed pictograms, white labels) and on top of them, at the height
# of the desk top, the user's table fan (Ventilator, METHYSCAD, CC BY 4.0) in white, turned towards the chair.
# The bin and its paper balls are in objets-sol.py. No plants around the desk.
# The fan's model has no materials file (colours rebuilt here) and carries a real brand in relief on its front badge:
# the letters are removed and a plain cap is fitted over the badge (_sans_marque).
# Prototypes A-C (home-made fans, plants) and E-F (moving-in cartons, shelving, pedestal fan) went to the Trash.
# Option autour=aucun brings back the lab's old placeholders (white box fan, two taped boxes, a fern).
# Built in every lab build and in the complete desk (bureau-complet.py) after objets-sol.py.
# verif=1 prints AUTOUR CROISE for any new group whose box overlaps a unit of the corner.
AUTOUR = [OPT.get('autour', 'D')]
PISTES_AU = ('D',)
TEXA = os.path.join(TEXB, 'autour')
MA = {}
AU_NEWS = []
VENTILO_AU = dict(x=-1.92, y=-0.18, rz=rad(-84), z=0.634)     # the carton stack (desk frame) and the fan on its top


def _sans_marque(objs, c=(0.0, 0.3065), r=0.046):
    """The table fan's front badge carries a real brand in relief, as loose letters: they are removed, the badge stays
    plain (islands smaller than 1.5 cm lying on the badge, in the model's imported coordinates)."""
    for o in objs:
        if o.type != 'MESH':
            continue
        bm = bmesh.new()
        bm.from_mesh(o.data)
        W = o.matrix_world
        seen, kill = set(), []
        for v in bm.verts:
            if v in seen:
                continue
            isl, stack = [], [v]
            seen.add(v)
            while stack:
                a = stack.pop()
                isl.append(a)
                for e in a.link_edges:
                    w = e.other_vert(a)
                    if w not in seen:
                        seen.add(w)
                        stack.append(w)
            ps = [W @ x.co for x in isl]
            size = max(max(p[i] for p in ps) - min(p[i] for p in ps) for i in range(3))
            if size < 0.015 and min(p.y for p in ps) > 0.07 and all(math.hypot(p.x - c[0], p.z - c[1]) < r for p in ps):
                kill += isl
        bmesh.ops.delete(bm, geom=kill, context='VERTS')
        # the letters were cut through the badge: a plain cap over it, following the badge as measured (axis tilted 13 deg
        # up with the head, centre below; a very flat dome, 3.8 mm high at r 10 mm down to 2.0 mm at r 46 mm, cap to r 46.5 mm), 0.5 mm in
        # front of it, in the badge's material
        slot = next((i for i, m in enumerate(o.data.materials) if m and m.name.startswith('Soft Rough White #2')), 0)
        Wi = W.inverted()
        cen, ax = Vector((0.0002, 0.0859, 0.3053)), Vector((0.0034, 0.9743, 0.2252)).normalized()
        e1 = ax.cross(Vector((1, 0, 0))).normalized()
        e2 = ax.cross(e1)
        prof = lambda q: (0.0038 if q < 0.01 else 0.0038 - 0.05 * (q - 0.01)) + 0.0005
        n, rings = 72, [0.0, 0.002, 0.005, 0.008] + [0.008 + 0.0385 * k / 12 for k in range(1, 13)]
        grid = []
        for q in rings:
            row = []
            for j in range(1 if q == 0 else n):
                t = 2 * math.pi * j / n
                row.append(bm.verts.new(Wi @ (cen + ax * prof(q) + (e1 * math.cos(t) + e2 * math.sin(t)) * q)))
            grid.append(row)
        faces = []
        for j in range(n):
            faces.append(bm.faces.new((grid[0][0], grid[1][(j + 1) % n], grid[1][j])))
        for a_, b_ in zip(grid[1:-1], grid[2:]):
            for j in range(n):
                faces.append(bm.faces.new((a_[j], a_[(j + 1) % n], b_[(j + 1) % n], b_[j])))
        for f in faces:
            f.material_index = slot
            f.smooth = True
        bmesh.ops.recalc_face_normals(bm, faces=faces)
        if (W.to_3x3() @ faces[n].normal).dot(ax) < 0:    # facing the front (along the badge's axis)
            for f in faces:
                f.normal_flip()
        bm.to_mesh(o.data)
        bm.free()
        print('VENTILO badge sans marque :', len(kill), 'sommets retirés, capot', len(faces), 'faces', flush=True)



SPECS['ventilo_table'] = dict(f=_so('ventilator', '_archive', 'inner', 'Ventilator.obj'), rot=(0, 0, 180), scale=1.0, prep=_sans_marque)


def m_ventilo_table(o, n, v):
    """The table fan's slots (KeyShot names, no materials file), in white: body, grilles, grey translucent blades,
    the motor's metal parts."""
    if n == 'Soft Shiny Blue':
        return m_plain('vt_blanc_pales', (0.74, 0.76, 0.78), 0.16, trans=0.55, ior=1.49)
    if n.startswith('Soft Rough White #'):
        return m_plain('vt_blanc_grille', (0.82, 0.82, 0.8), 0.3)
    if n in ('Soft Rough White', 'Soft Shiny White') or n.startswith(('respaldo', 'plantilla', 'pivote')):
        return m_plain('vt_blanc_corps' + ('_brillant' if 'Shiny' in n else ''), (0.8, 0.8, 0.78), 0.22 if 'Shiny' in n else 0.38,
                       coat=0.2 if 'Shiny' in n else 0.0)
    if n.startswith(('motor.', 'interno')):
        return m_plain('vt_moteur', (0.03, 0.03, 0.032), 0.55)
    return m_plain('vt_metal', (0.62, 0.62, 0.64), 0.3, metal=1.0)


MATS_X['ventilo_table'] = m_ventilo_table


def m_autour():
    if MA:
        return MA
    mats_contenus()
    MA['noir_mat'] = m_surface('au_noir_mat', (0.018, 0.018, 0.02), rough=0.62, var=0.02, grain=1200, bump=0.003)
    MA['kraft'] = m_surface('au_kraft', (0.38, 0.27, 0.16), rough=0.82, var=0.07, grain=380, bump=0.012)
    MA['tape'] = mat_color('au_tape', (0.014, 0.014, 0.016), rough=0.2)
    MA['pictos'] = m_label('au_pictos', os.path.join(TEXA, 'carton-pictos.png'), rough=0.8, alpha=True)
    MA['colis'] = m_label('au_colis', os.path.join(TEXA, 'etiquette-colis.png'), rough=0.4)
    return MA


def lab_au(slug):
    """A label of textures_autour.py, else one of the storage contents."""
    p = os.path.join(TEXA, f'etiquette-{slug}.png')
    if not os.path.exists(p):
        return lab_mat('etiquette-' + slug)
    key = 'lab_' + slug
    if key not in MA:
        MA[key] = m_label('au_' + key, p, rough=0.45)
    return MA[key]


def ventilo(z=0.0, rz=0.0):
    """An instance of the table fan, built at the origin (inside a group), front towards -y."""
    e = bpy.data.objects.new('au_ventilo_table', None)
    e.instance_type = 'COLLECTION'
    e.instance_collection = proto('ventilo_table')[0]
    e.location = (0, 0, z)
    e.rotation_euler = (0, 0, rz)
    return link(e)


# ------------------------------------------------------------------ cartons
def carton_exp(w, d, h, label=None, colis=False, pictos=True, seed=1):
    """Shipping carton, closed: kraft board, black tape over the seam and down the ends, ink print, white label."""
    M_ = m_autour()
    rng = random.Random(seed)
    bx('au_carton', (w, d, h), (0, 0, h / 2), M_['kraft'], bev=0.004)
    bx('au_carton_joint', (w - 0.01, 0.0025, 0.0006), (0, 0, h + 0.0002), M_['noir_mat'], bev=0)
    bx('au_scotch', (w + 0.0016, 0.05, 0.0007), (0, 0, h + 0.0005), M_['tape'], bev=0)
    for sx in (-1, 1):
        bx('au_scotch', (0.0007, 0.05, 0.075), (sx * (w / 2 + 0.0005), 0, h - 0.0375), M_['tape'], bev=0)
    if pictos:
        pw = min(w * 0.62, 0.36)
        front_plane('au_pictos', pw, pw / 2, w / 2 - pw / 2 - 0.03, -d / 2 - 0.0007, h * 0.42, M_['pictos'])
    if label:
        front_plane('au_lab', 0.12, 0.02, -w / 2 + 0.1, -d / 2 - 0.0008, h * 0.8, lab_au(label))
    if colis:
        plane('au_colis', 0.1, 0.15, (-w / 2 + 0.085, d / 2 - 0.11, h + 0.0012), M_['colis'], rot=(0, 0, rad(rng.uniform(-6, 6)) + rad(90)))




# ------------------------------------------------------------------ the retained decor
def _place(F, x, y, rz, build):
    p = F.p(x, y, 0)
    return grp(Vector((p.x, p.y, p.z)), F.r + rz, build)


def _vers(x, y, cible=(0.0, -0.8)):
    """Angle (desk frame) that turns a front towards -y to look from (x, y) at the chair."""
    return math.atan2(cible[0] - x, -(cible[1] - y))


def autour_bureau(F, h=0.74, hr=0.64, k=None):
    """The decor around the desk corner (desk frame F): two cartons, the table fan on top; returns the new groups."""
    k = k or AUTOUR[0]
    if k not in PISTES_AU:
        return []
    m_autour()
    proto('ventilo_table')                       # prepared before any group: a first import inside grp() would be
    before = set(bpy.data.objects)               # parented to that group and shift every instance
    x, y, r0 = VENTILO_AU['x'], VENTILO_AU['y'], VENTILO_AU['rz']

    def pile():
        carton_exp(0.5, 0.4, 0.36, 'archives-24', seed=1)
        pose(0.02, 0.01, 0.362, lambda: carton_exp(0.4, 0.32, 0.27, 'cables', seed=2), rz=rad(6))
        pose(0.02, 0.01, VENTILO_AU['z'], ventilo, rz=_vers(x, y) - r0)
    _place(F, x, y, r0, pile)
    news = [o for o in bpy.data.objects if o not in before and o.parent is None]
    AU_NEWS[:] = news
    return news


# ------------------------------------------------------------------ checks
def _pts(o, M=None):
    W = M if M is not None else o.matrix_world
    P = []
    if o.type in ('MESH', 'CURVE'):
        P += [W @ Vector(c) for c in o.bound_box]
    elif o.type == 'EMPTY' and o.instance_type == 'COLLECTION' and o.instance_collection:
        for c in o.instance_collection.all_objects:
            P += _pts(c, W @ c.matrix_world)
    for ch in o.children:
        P += _pts(ch, (W @ ch.matrix_local) if M is not None else None)
    return P


def verifier_autour(news, olds):
    bpy.context.view_layer.update()

    def bb(o):
        P = _pts(o)
        if not P:
            return None
        return [min(p[i] for p in P) for i in range(3)] + [max(p[i] for p in P) for i in range(3)]
    A = [(o, bb(o)) for o in news]
    B = [(o, bb(o)) for o in olds if o.parent is None and o.type not in ('CAMERA', 'LIGHT')]
    for o, a in A:
        if not a:
            continue
        print('AUTOUR', o.name, 'x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f' % (a[0], a[3], a[1], a[4], a[2], a[5]), flush=True)
        for q, b in B:
            if not b or max(b[3] - b[0], b[4] - b[1]) > 4.5:
                continue
            if all(a[i] < b[i + 3] - 0.002 and b[i] < a[i + 3] - 0.002 for i in range(3)):
                print('AUTOUR CROISE', o.name, '<>', q.name, flush=True)





# ------------------------------------------------------------------ renders of the retained decor (studio)
SHOT_AU = {
    'large': dict(cam=(-3.05, -4.55, 2.05), target=(0.95, 0.0, 0.5), lens=26, fstop=11, focus=None),
    'dessus': dict(cam=(0.8, -0.45, 8.8), target=(0.8, -0.44, 0.0), lens=40, fstop=11, focus=None),
    'droite': dict(cam=(5.7, -3.0, 1.45), target=(3.45, 0.0, 0.6), lens=30, fstop=8, focus=None),
    'ventilo': dict(cam=(-0.72, -1.78, 1.18), target=(-1.9, -0.2, 0.68), lens=34, fstop=4, focus=None),
    'detail': dict(cam=(-3.4, -1.9, 1.25), target=(-1.95, -0.15, 0.62), lens=36, fstop=5.6, focus=None),
    'corbeille': dict(cam=(0.15, -1.45, 0.62), target=(0.95, -0.3, 0.12), lens=40, fstop=5.6, focus=None),
}


def main_autour():
    os.makedirs(OUT, exist_ok=True)
    build_bureau_complet()
    papiers_bureau(_F0, H0, H1)
    objets_bureau(_F0, H0, H1)
    sol_bureau(_F0, H0, H1)
    olds = list(bpy.data.objects)
    news = autour_bureau(_F0, H0, H1)
    if OPT.get('verif') == '1':
        verifier_autour(news, olds)
    if OPT.get('rendu', '1') == '0':
        return
    for v in OPT.get('vues', 'large,dessus,droite,ventilo,detail,corbeille').split(','):
        SC.camera = make_camera(dict(SHOT_AU[v]), f'CAM_{v}')
        SC.render.resolution_x = RES
        SC.render.resolution_y = int(RES * 9 / 16)
        SC.render.filepath = os.path.join(OUT, f'D-{v}.png')
        print('RENDER', SC.render.filepath, flush=True)
        bpy.ops.render.render(write_still=True)


main_autour()
