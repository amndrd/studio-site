
# ================================================================== desk storage prototypes (object alone, studio)
# Built by rendus-rangements.sh: labo2-base.py + objets-bureau.py (minus its last line) + this file.
# Four pieces (pedestal, open unit, low cabinet under the return, trolley) in three material directions:
# N black steel, P birch plywood + slate linoleum fronts, G light grey steel. Each piece is built at the origin
# (front towards -y) and placed with place().
PISTES_R = OPT.get('pistes', 'N,P,G').split(',')
OUVERT_R = {}          # per piece, extra arguments (open drawers), set by objets-contenus.py
TIROIRS_OUVERTS = []   # interiors of the open drawers of the piece being built (for the contents)
VUES_R = OPT.get('vues', 'grp,det,bur').split(',')
PLY = {}


def ply_for(axis):
    if axis not in PLY:
        PLY[axis] = m_ply_edge('ply_' + axis, axis=axis)
    return PLY[axis]


def board(name, size, loc, face, edge=None, bev=0.0015):
    o = box(name, size, loc, face)
    me = o.data
    thin = min(range(3), key=lambda i: size[i])
    if edge == 'ply':
        edge = ply_for('XYZ'[thin])
    if edge is not None:
        me.materials.append(edge)
        for f in me.polygons:
            f.material_index = 0 if abs(f.normal[thin]) > 0.5 else 1
    for f in me.polygons:
        f.use_smooth = True
    if bev:
        b = o.modifiers.new('bev', 'BEVEL')
        b.width = bev
        b.segments = 2
        b.limit_method = 'ANGLE'
        b.harden_normals = True
    return o


def look(p):
    """Materials of a direction: carcass, fronts, inside, handle style."""
    if p == 'N':
        return dict(car=(M['black_pc'], None), fr=(M['black_pc'], None), inside=(M['black_pc'], None), handle='lip', t=0.012)
    if p == 'G':
        return dict(car=(M['grey_r'], None), fr=(M['grey_r'], None), inside=(M['grey_r'], None), handle='bar', t=0.012)
    return dict(car=(M['birch'], 'ply'), fr=(M['lino'], 'ply'), inside=(M['birch'], 'ply'), handle='hole', t=0.018)


LABEL_I = [0]
LABEL_P = ['', 0]      # piece being built and index of its label (words chosen by objets-contenus.py)


def label(x, y, z, w=0.085):
    k = LABEL_I[0] % 6
    LABEL_I[0] += 1
    key = f'lab_white_{k}'
    m = mot_label(*LABEL_P) if 'mot_label' in globals() else None
    LABEL_P[1] += 1
    m = m or bpy.data.materials.get(key) or m_label(key, os.path.join(TEXB, f'etiquette-blanc-{k}.png'), os.path.join(TEXB, f'etiquette-blanc-{k}-relief.png'))
    plane('r_label', w, w * 150 / 900, (x, y - 0.0006, z), m, rot=(rad(90), 0, rad(R.uniform(-1.2, 1.2))))


def handle(L, x, y, z_top, w):
    """y = front face of the drawer front; z_top = top edge of the front."""
    if L['handle'] == 'lip':
        board('r_grip', (w - 0.04, 0.014, 0.018), (x, y + 0.006, z_top - 0.011), M['black'], bev=0.002)
    elif L['handle'] == 'bar':
        z = z_top - 0.035
        board('r_bar', (0.15, 0.01, 0.012), (x, y - 0.024, z), M['alu'], bev=0.003)
        for dx in (-0.06, 0.06):
            cyl('r_bar_post', 0.004, 0.024, (x + dx, y - 0.012, z), M['alu'], rot=(rad(90), 0, 0), verts=12)
    else:
        cyl('r_hole', 0.016, 0.019, (x, y + 0.0085, z_top - 0.035), M['hole'], rot=(rad(90), 0, 0), verts=36)


def caster(x, y, z_top):
    board('r_cplate', (0.045, 0.045, 0.004), (x, y, z_top - 0.002), M['black'], bev=0.001)
    cyl('r_cswivel', 0.012, 0.012, (x, y, z_top - 0.01), M['black'], verts=16)
    for dx in (-0.011, 0.011):
        board('r_cfork', (0.003, 0.03, 0.032), (x + dx, y + 0.006, z_top - 0.028), M['black'], bev=0.0008)
    cyl('r_cwheel', 0.021, 0.018, (x, y + 0.01, 0.021), M['rubber'], rot=(0, rad(90), 0), verts=28)


def glide(x, y):
    cyl('r_glide', 0.014, 0.01, (x, y, 0.005), M['black'], verts=16)


def carcass(L, w, d, h, z0, back=True):
    t = L['t']
    f, e = L['car']
    board('r_side', (t, d, h - t), (-w / 2 + t / 2, 0, z0 + (h - t) / 2), f, e)
    board('r_side', (t, d, h - t), (w / 2 - t / 2, 0, z0 + (h - t) / 2), f, e)
    board('r_top', (w, d, t), (0, 0, z0 + h - t / 2), f, e)
    board('r_bottom', (w - 2 * t, d, t), (0, 0, z0 + t / 2), f, e)
    if back:
        board('r_back', (w - 2 * t, t, h - 2 * t), (0, d / 2 - t / 2, z0 + h / 2), f, e)
    board('r_top_gap', (w - 2 * t, d - 0.004, 0.0005), (0, 0, z0 + h - t - 0.0003), M['black'], bev=0)


def drawer(L, x, w, d, z, hd, open_by=0.0, lock=False, contents=False):
    """Drawer front (with label and handle) and, when open, its box."""
    f, e = L['fr']
    yf = -d / 2 - 0.009 - open_by
    board('r_front', (w - 0.004, 0.018, hd - 0.004), (x, yf, z + hd / 2), f, e, bev=0.0015)
    yface = yf - 0.009
    label(x - w / 2 + 0.07, yface, z + hd - 0.022 if L['handle'] != 'lip' else z + hd - 0.045)
    handle(L, x, yface, z + hd - 0.002, w)
    if lock:
        cyl('r_lock', 0.009, 0.006, (x + w / 2 - 0.035, yface - 0.003, z + hd - 0.03), M['alu'], rot=(rad(90), 0, 0), verts=20)
        board('r_keyslot', (0.002, 0.002, 0.008), (x + w / 2 - 0.035, yface - 0.0062, z + hd - 0.03), M['black'], bev=0)
    if open_by > 0:
        fi, ei = L['inside']
        ti = 0.008
        dd = d - 0.06
        yc = yf + 0.009 + dd / 2
        TIROIRS_OUVERTS.append(dict(x=x, y=yc, w=w - 0.05 - 2 * ti, d=dd - 2 * ti, z0=z + 0.024, z1=z + hd - 0.03, hd=hd))
        board('r_dbottom', (w - 0.05, dd, ti), (x, yc, z + 0.02), fi, ei)
        for sx in (-1, 1):
            board('r_dside', (ti, dd, hd - 0.05), (x + sx * (w / 2 - 0.025), yc, z + 0.02 + (hd - 0.05) / 2), fi, ei)
        board('r_dback', (w - 0.05, ti, hd - 0.05), (x, yc + dd / 2, z + 0.02 + (hd - 0.05) / 2), fi, ei)
        if contents:
            board('r_papers', (0.21, 0.297, 0.03), (x - 0.04, yc - 0.03, z + 0.04), M['paperw'], bev=0.002)
            for k in range(3):
                tube_between('r_pen', (x + 0.11, yc - 0.12 + 0.03 * k, z + 0.035), (x + 0.12, yc + 0.02 + 0.03 * k, z + 0.035), 0.004, M['black'] if k else M['alu'], verts=8)


# ------------------------------------------------------------------ the four pieces
def pedestal(L, open_by=0.16, open_i=1, contents=True):
    """Drawer pedestal on casters, under the desk: two small drawers and a file drawer."""
    w, d, h = 0.42, 0.55, 0.53
    z0 = 0.05
    carcass(L, w, d, h, z0)
    hs = [0.29, 0.12, 0.12]
    z = z0
    for i, hd in enumerate(hs):
        drawer(L, 0, w - 2 * L['t'] + 0.012, d, z, hd, open_by=open_by if i == open_i else 0.0, lock=i == 2, contents=contents and i == open_i)
        z += hd
    for sx in (-1, 1):
        for sy in (-1, 1):
            caster(sx * (w / 2 - 0.04), sy * (d / 2 - 0.05), z0)


def open_unit(L):
    """Open two-level unit on the left, like Birdcage: a labelled drawer on top, a shelf below."""
    w, d, h = 0.45, 0.58, 0.61
    z0 = 0.012
    carcass(L, w, d, h, z0)
    t = L['t']
    f, e = L['car']
    board('r_shelf', (w - 2 * t, d - t, t), (0, -t / 2, z0 + 0.28), f, e)
    drawer(L, 0, w - 2 * t + 0.012, d, z0 + h - t - 0.13, 0.13)
    label(-0.12, -d / 2 - 0.001, z0 + 0.28 - t / 2 - 0.002, w=0.07)
    for sx in (-1, 1):
        for sy in (-1, 1):
            glide(sx * (w / 2 - 0.04), sy * (d / 2 - 0.05))


def low_cabinet(L, open_at=None, open_by=0.0):
    """Low wide cabinet under the return: two columns of two drawers, on a recessed plinth."""
    w, d, h = 1.0, 0.46, 0.51
    z0 = 0.04
    board('r_plinth', (w - 0.06, d - 0.06, z0), (0, 0.01, z0 / 2), M['black'], bev=0.002)
    carcass(L, w, d, h, z0)
    t = L['t']
    f, e = L['car']
    board('r_div', (t, d - t, h - 2 * t), (0, -t / 2, z0 + h / 2), f, e)
    cw = (w - 3 * t) / 2
    for sx in (-1, 1):
        x = sx * (t / 2 + cw / 2)
        z = z0 + t
        for k, hd in enumerate([(h - 2 * t) / 2, (h - 2 * t) / 2]):
            drawer(L, x, cw + 0.008, d, z, hd, open_by=open_by if open_at == (sx, k) else 0.0)
            z += hd


def trolley(L):
    """Trolley on casters: two sides, three trays with lips, a side handle."""
    w, d, h = 0.42, 0.42, 0.62
    z0 = 0.05
    t = L['t']
    f, e = L['car']
    for sx in (-1, 1):
        board('r_tside', (t, d, h), (sx * (w / 2 - t / 2), 0, z0 + h / 2), f, e)
    for k, z in enumerate((z0 + 0.03, z0 + 0.3, z0 + h - 0.02)):
        board('r_tray', (w - 2 * t, d, t), (0, 0, z), f, e)
        for sy in (-1, 1):
            board('r_lip', (w - 2 * t, t, 0.045), (0, sy * (d / 2 - t / 2), z + 0.0225 + t / 2), f, e)
    for sy in (-1, 1):
        cyl('r_hpost', 0.006, 0.05, (w / 2 + 0.025, sy * 0.13, z0 + h - 0.06), M['alu'], rot=(0, rad(90), 0), verts=12)
    tube_between('r_handle', (w / 2 + 0.05, -0.15, z0 + h - 0.06), (w / 2 + 0.05, 0.15, z0 + h - 0.06), 0.011, M['alu'], verts=20)
    for sx in (-1, 1):
        for sy in (-1, 1):
            caster(sx * (w / 2 - 0.04), sy * (d / 2 - 0.05), z0)
    label(0, -d / 2 - 0.001, z0 + 0.3 + 0.03, w=0.07)


def place(fn, L, x, y, rz=0.0):
    before = set(bpy.data.objects)
    TIROIRS_OUVERTS.clear()
    LABEL_P[:] = [fn.__name__, 0]
    fn(L, **OUVERT_R.get(fn.__name__, {}))
    if 'remplir' in globals():
        remplir(fn.__name__, L)          # storage contents (objets-contenus.py)
    root = bpy.data.objects.new('r_root', None)
    root.location = (x, y, 0)
    root.rotation_euler = (0, 0, rz)
    link(root)
    for o in set(bpy.data.objects) - before:
        if o.parent is None and o is not root:
            o.parent = root
    return root


def build_group(L):
    place(open_unit, L, -1.25, 0.0)
    place(pedestal, L, -0.55, 0.0)
    place(low_cabinet, L, 0.5, 0.0)
    place(trolley, L, 1.45, 0.0, rad(-10))


def build_with_desk(L):
    concept_D()
    place(open_unit, L, -0.895, 0.02)
    place(pedestal, L, 0.55, 0.0)
    place(low_cabinet, L, RX, RY + 0.01)
    place(trolley, L, 2.95, -0.32, rad(-14))


SHOT_R = {
    'grp': dict(cam=(-1.85, -2.85, 1.38), target=(0.08, 0.0, 0.3), lens=33, fstop=11, focus=None),
    'det': dict(cam=(-0.99, -1.02, 0.8), target=(-0.53, -0.3, 0.4), lens=55, fstop=2.8, focus=None),
    'bur': dict(cam=(-2.45, -3.35, 1.85), target=(0.72, 0.1, 0.5), lens=32, fstop=11, focus=None),
}
NAMES_R = {'N': 'noir', 'P': 'contreplaque-lino', 'G': 'gris-clair'}


def main_rangements():
    setup_render()
    try:
        SC.view_settings.look = 'AgX - Medium High Contrast'
    except TypeError:
        pass
    materials_bureau()
    M['grey_r'] = m_powder('grey_r', (0.58, 0.59, 0.585), rough=0.4)
    M['hole'] = mat_color('hole', (0.035, 0.028, 0.02), rough=0.8)
    M['paperw'] = m_surface('paperw', (0.82, 0.82, 0.8), rough=0.75, var=0.02)
    studio()
    colls = {}
    for p in PISTES_R:
        L = look(p)
        for kind, fn in (('grp', build_group), ('bur', build_with_desk)):
            c = coll(f'R_{p}_{kind}')
            CUR[0] = c
            fn(L)
            colls[(p, kind)] = c
    os.makedirs(OUT, exist_ok=True)
    if OPT.get('save') == '1':
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'rangements-prototypes.blend'))
    for p in PISTES_R:
        for v in VUES_R:
            kind = 'bur' if v == 'bur' else 'grp'
            for key, c in colls.items():
                c.hide_render = key != (p, kind)
            cam = make_camera(dict(SHOT_R[v]), f'CAM_{p}_{v}')
            SC.camera = cam
            SC.render.resolution_x = RES
            SC.render.resolution_y = int(RES * 9 / 16)
            SC.render.filepath = os.path.join(OUT, f'{p}-{v}.png')
            print('RENDER', SC.render.filepath, flush=True)
            bpy.ops.render.render(write_still=True)


main_rangements()
