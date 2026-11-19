# ================================================================== contents of the desk storage
# Built after objets-rangements.py. Option contenu=M|A|B|C|D (default M, the retained mix; 'aucun' = the storage as before):
#   M retained 2026-11-15: A as the base (low cabinet with hanging files), D's riser (NAS of B instead of the cartons,
#     cartons moved left), D's trolley, D's open unit and pedestal reworked (nothing crosses a panel).
#   Prototypes: A archives (labelled grey boxes, hanging files, reams, printer), B matériel (industrial bins, taped cable coils,
#   drives, network box), C bibliothèque (books, magazines, notebooks), D vécu (a lived-in mix of the three).
# remplir() is called by place() for each storage piece; remplir_rehausse() fills the riser of desk D.
# Textures from hero/outils/textures_contenus.py (textures-bureau/contenus).
import json
TEXC = os.path.join(TEXB, "contenus")
CONTENU = [OPT.get('contenu', 'M')]
LAST_Z = [0.0]       # height of the last paper stack / magazine pile built
SPINES = json.load(open(os.path.join(TEXC, 'tranches.json'))) if os.path.exists(os.path.join(TEXC, 'tranches.json')) else []
MC = {}
RC = random.Random(21)


def mats_contenus():
    if MC:
        return
    MC['grey'] = m_surface('c_grey', (0.3, 0.31, 0.31), rough=0.72, var=0.04, grain=700, bump=0.008)
    MC['grey_lid'] = m_surface('c_grey_lid', (0.26, 0.27, 0.27), rough=0.7, var=0.04, grain=700, bump=0.008)
    MC['dark'] = m_surface('c_dark', (0.055, 0.056, 0.06), rough=0.62, var=0.04, grain=700, bump=0.006)
    MC['white'] = m_surface('c_white', (0.76, 0.76, 0.73), rough=0.62, var=0.02, grain=600, bump=0.004)
    MC['carton'] = m_surface('c_carton', (0.72, 0.71, 0.67), rough=0.75, var=0.03, grain=500, bump=0.01)
    MC['kraft'] = m_surface('c_kraft', (0.42, 0.31, 0.19), rough=0.78, var=0.06, grain=500, bump=0.01)
    MC['manila'] = m_surface('c_manila', (0.7, 0.6, 0.42), rough=0.78, var=0.03, grain=500, bump=0.004)
    MC['paper'] = m_surface('c_paper', (0.83, 0.83, 0.8), rough=0.82, var=0.015, grain=900, bump=0.002)
    MC['pages'] = m_surface('c_pages', (0.74, 0.73, 0.69), rough=0.85, var=0.06, grain=3000, bump=0.01)
    MC['bin'] = mat_color('c_bin', (0.2, 0.21, 0.22), rough=0.5)
    MC['pblack'] = mat_color('c_pblack', (0.018, 0.018, 0.02), rough=0.42)
    MC['pwhite'] = mat_color('c_pwhite', (0.8, 0.8, 0.78), rough=0.32)
    MC['pgrey'] = mat_color('c_pgrey', (0.36, 0.37, 0.38), rough=0.4)
    MC['cblack'] = mat_color('c_cblack', (0.012, 0.012, 0.013), rough=0.55)
    MC['cwhite'] = mat_color('c_cwhite', (0.78, 0.78, 0.76), rough=0.42)
    MC['tape'] = mat_color('c_tape', (0.016, 0.016, 0.018), rough=0.3)
    MC['metal'] = mat_color('c_metal', (0.72, 0.73, 0.74), rough=0.3, metal=1.0)
    MC['felt'] = m_surface('c_felt', (0.16, 0.16, 0.17), rough=0.95, var=0.05, grain=3000, bump=0.03)
    MC['led'] = mat_emit('c_led', (0.85, 1.0, 0.9), 4.0)
    MC['led_b'] = mat_emit('c_led_b', (0.55, 0.75, 1.0), 4.0)
    MC['screen'] = mat_screen(os.path.join(TEXC, 'ecran-imprimante.png'), 0.5)


def lab_mat(name):
    key = 'lab_' + name
    if key not in MC:
        MC[key] = m_label('c_' + key, os.path.join(TEXC, name + '.png'), rough=0.45)
    return MC[key]


def spine_mat(k):
    key = ('spine', k)
    if key not in MC:
        MC[key] = m_label(f'c_spine_{k}', os.path.join(TEXC, SPINES[k]['file']), rough=0.55)
    return MC[key]


def cover_mat(k):
    key = ('cover', k)
    if key not in MC:
        MC[key] = mat_color(f'c_cover_{k}', SPINES[k]['color'], rough=0.55)
    return MC[key]


# ------------------------------------------------------------------ grouping
def grp(loc, rz, build, rx=0.0, ry=0.0):
    """Runs build() (geometry around the origin, front towards -y) and parents it to an empty at loc."""
    before = set(bpy.data.objects)
    build()
    e = bpy.data.objects.new('c_item', None)
    e.location = loc
    e.rotation_euler = (rx, ry, rz)
    link(e)
    for o in set(bpy.data.objects) - before:
        if o.parent is None and o is not e:
            o.parent = e
    return e


def pose(x, y, z, build, rz=0.0):
    return grp(Vector((x, y, z)), rz, build)


def lay(x, y, z, w, h, build, rz=0.0):
    """A standing-built item (thickness w along x, height h) laid on its back cover, spine still to the front."""
    off = Vector((h / 2, 0, 0))
    off.rotate(Euler((0, 0, rz)))
    return grp(Vector((x, y, z + w / 2)) + off, rz, build, ry=rad(-90))


def prism_x(name, pts, x0, x1, mat):
    bm = bmesh.new()
    a = [bm.verts.new((x0, y, z)) for y, z in pts]
    b = [bm.verts.new((x1, y, z)) for y, z in pts]
    bm.faces.new(a[::-1])
    bm.faces.new(b)
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        bm.faces.new((a[i], a[j], b[j], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    me.materials.append(mat)
    return link(o)


def front_plane(name, w, h, x, y, z, mat):
    return plane(name, w, h, (x, y, z), mat, rot=(rad(90), 0, 0))


# ------------------------------------------------------------------ items (bottom at z=0, centred, front towards -y)
def box_lid(w, d, h, body, lid=None, label=None, lw=0.1, number=None, hole=False):
    lh = min(0.03, h * 0.3) if lid else 0.0
    bx('c_box', (w - 0.004, d - 0.004, h - lh * 0.5), (0, 0, (h - lh * 0.5) / 2), body, bev=0.0025)
    if lid:
        bx('c_lid', (w, d, lh), (0, 0, h - lh / 2), lid, bev=0.002)
    zl = (h - lh) * 0.5
    if number is not None:
        front_plane('c_num', 0.085, 0.06, 0, -d / 2 + 0.0015, zl, lab_mat(f'numero-{number:02d}'))
    elif label:
        front_plane('c_lab', lw, lw / 6, 0, -d / 2 + 0.0015, zl + (0.012 if hole else 0), lab_mat('etiquette-' + label))
    if hole:
        o = cyl('c_hole', 0.011, 0.002, (0, -d / 2 + 0.0012, zl - 0.03), MC['pblack'], rot=(rad(90), 0, 0), verts=24)
        o.scale = (1.9, 1, 1)


def archive_upright(w, d, h, body, number):
    """Archive box standing on its edge, numbered label and finger hole on the spine."""
    bx('c_arch', (w, d, h), (0, 0, h / 2), body, bev=0.002)
    front_plane('c_num', w * 0.86, w * 0.86 * 0.7, 0, -d / 2 - 0.0006, h * 0.68, lab_mat(f'numero-{number:02d}'))
    o = cyl('c_hole', 0.011, 0.002, (0, -d / 2 - 0.0004, h * 0.22), MC['pblack'], rot=(rad(90), 0, 0), verts=24)
    o.scale = (1.0, 1.9, 1)


def magfile(w, d, h, mat, label=None, papers=4, seed=1):
    """Magazine file, tall side to the front (label), papers standing inside."""
    rng = random.Random(seed)
    t = 0.0025
    prof = [(-d / 2, 0), (d / 2, 0), (d / 2, h * 0.42), (-d / 2 + d * 0.36, h), (-d / 2, h)]
    prism_x('c_mf_side', prof, -w / 2, -w / 2 + t, mat)
    prism_x('c_mf_side', prof, w / 2 - t, w / 2, mat)
    bx('c_mf_front', (w, t, h), (0, -d / 2 + t / 2, h / 2), mat, bev=0.0008)
    bx('c_mf_back', (w, t, h * 0.42), (0, d / 2 - t / 2, h * 0.21), mat, bev=0.0008)
    bx('c_mf_bottom', (w, d, t), (0, 0, t / 2), mat, bev=0.0005)
    if label:
        front_plane('c_lab', w * 0.8, w * 0.8 / 6, 0, -d / 2 - 0.0006, h * 0.8, lab_mat('etiquette-' + label))
    x = -w / 2 + t + 0.002
    for i in range(papers):
        th = rng.uniform(0.004, 0.011)
        if x + th > w / 2 - t:
            break
        ph = h * rng.uniform(0.86, 1.0)
        m = rng.choice([MC['paper'], MC['paper'], MC['manila'], MC['white']])
        bx('c_mf_paper', (th, d - 0.012, ph), (x + th / 2, 0.002, t + ph / 2), m, rot=(rng.uniform(-0.03, 0.03), 0, 0), bev=0.0008)
        x += th + 0.0008


def binder(w, d, h, mat, label):
    bx('c_bind', (w, d, h), (0, 0, h / 2), mat, bev=0.003)
    front_plane('c_lab', w * 0.7, w * 0.7 / 6 * 1.6, 0, -d / 2 - 0.0006, h * 0.66, lab_mat('etiquette-' + label))
    cyl('c_ring', 0.0135, 0.002, (0, -d / 2 - 0.0005, h * 0.2), MC['metal'], rot=(rad(90), 0, 0), verts=24)
    cyl('c_ringh', 0.011, 0.0026, (0, -d / 2 - 0.0006, h * 0.2), MC['pblack'], rot=(rad(90), 0, 0), verts=24)


def book(w, d, h, k):
    k %= len(SPINES)
    cov = cover_mat(k)
    t = 0.0018
    bx('c_bcov', (t, d, h), (-w / 2 + t / 2, 0, h / 2), cov, bev=0.0006)
    bx('c_bcov', (t, d, h), (w / 2 - t / 2, 0, h / 2), cov, bev=0.0006)
    bx('c_bspine', (w, t, h), (0, -d / 2 + t / 2, h / 2), cov, bev=0.0006)
    bx('c_bpages', (w - 2 * t, d - t - 0.0015, h - 0.006), (0, (t - 0.0015) / 2, h / 2), MC['pages'], bev=0.0004)
    front_plane('c_bspine_t', w - 0.0006, h - 0.0006, 0, -d / 2 - 0.0004, h / 2, spine_mat(k))


def ream(n=1, w=0.297, d=0.21, h=0.05):
    for i in range(n):
        z = i * h
        bx('c_ream', (w, d, h - 0.001), (0, 0, z + h / 2), MC['paper'], bev=0.003)
        front_plane('c_ream_l', w - 0.004, h - 0.006, 0, -d / 2 - 0.0005, z + h / 2, lab_mat('ramette'))


def euro_bin(w, d, h, label=None, mat=None):
    mat = mat or MC['bin']
    t = 0.004
    bx('c_bin_b', (w - 0.01, d - 0.01, t), (0, 0, t / 2), mat, bev=0.001)
    for sy in (-1, 1):
        bx('c_bin_w', (w, t, h), (0, sy * (d / 2 - t / 2), h / 2), mat, bev=0.0012)
    for sx in (-1, 1):
        bx('c_bin_w', (t, d, h), (sx * (w / 2 - t / 2), 0, h / 2), mat, bev=0.0012)
        o = plane('c_bin_hdl', 0.07, 0.022, (sx * (w / 2 + 0.0004), 0, h - 0.03), MC['pblack'], rot=(rad(90), 0, rad(90)))
    bx('c_bin_rim', (w + 0.008, 0.008, 0.006), (0, -d / 2 - 0.002, h - 0.003), mat, bev=0.001)
    bx('c_bin_rim', (w + 0.008, 0.008, 0.006), (0, d / 2 + 0.002, h - 0.003), mat, bev=0.001)
    if label:
        bx('c_bin_holder', (0.13, 0.002, 0.04), (0, -d / 2 - 0.0012, h * 0.5), MC['pgrey'], bev=0.0005)
        front_plane('c_lab', 0.11, 0.11 / 6, 0, -d / 2 - 0.0026, h * 0.5, lab_mat('etiquette-' + label))


def coil(r=0.05, turns=4.0, wire=0.0024, mat=None, tape=True, seed=0, tail=0.12, plug=True):
    rng = random.Random(seed)
    mat = mat or MC['cblack']
    n = int(turns * 14)
    ph = rng.uniform(0, 6.28)
    pts = []
    for i in range(n + 1):
        a = 2 * math.pi * turns * i / n + ph
        rr = r * (1 + 0.06 * math.sin(3 * a) + rng.uniform(-0.025, 0.025))
        pts.append(Vector((rr * math.cos(a), rr * math.sin(a) * 0.86, wire * (1.0 + 1.6 * i / n))))
    end = pts[-1]
    if tail:
        d = Vector((math.cos(ph + 2 * math.pi * turns + 0.5), math.sin(ph + 2 * math.pi * turns + 0.5), 0))
        pts.append(end + d * tail * 0.5 + Vector((0, 0, wire)))
        pts.append(end + d * tail + Vector((0, 0, 0)))
    curve_cable('c_cable', pts, wire, mat)
    if plug and tail:
        e = pts[-1]
        o = bx('c_plug', (0.022, 0.009, 0.006), (e.x, e.y, e.z), MC['pblack'] if mat is MC['cblack'] else MC['pwhite'], bev=0.0015)
        o.rotation_euler = (0, 0, math.atan2(d.y, d.x))
    if tape:
        o = bx('c_coil_tape', (0.016, 0.03, wire * 6.5), (r * math.cos(ph + 1.0), r * math.sin(ph + 1.0) * 0.86, wire * 2.6), MC['tape'], bev=0.0012)
        o.rotation_euler = (0, 0, ph + 1.0)


def adapter(w=0.06, d=0.06, h=0.028, white=True, seed=0):
    bx('c_adapt', (w, d, h), (0, 0, h / 2), MC['pwhite'] if white else MC['pblack'], bev=0.006)
    for sx in (-1, 1):
        bx('c_prong', (0.0016, 0.006, 0.016), (sx * 0.006, -d / 2 - 0.003, h / 2), MC['metal'], rot=(rad(90), 0, 0), bev=0)


def drive(w=0.08, d=0.12, h=0.02, mat=None):
    bx('c_drive', (w, d, h), (0, 0, h / 2), mat or MC['dark'], bev=0.005)
    bx('c_drive_led', (0.004, 0.0012, 0.002), (w / 2 - 0.012, -d / 2 - 0.0002, h * 0.55), MC['led_b'], bev=0)


def drive_up(w=0.022, d=0.085, h=0.125, mat=None):
    """External drive standing on its edge, label end up."""
    bx('c_drive', (w, d, h), (0, 0, h / 2), mat or MC['dark'], bev=0.004)
    bx('c_drive_led', (0.0012, 0.004, 0.002), (0, -d / 2 + 0.012, h + 0.0002), MC['led_b'], bev=0)
    front_plane('c_lab', 0.06, 0.01, 0, -d / 2 - 0.0005, h * 0.75, lab_mat('etiquette-sauvegardes'))


def nas(w=0.165, d=0.22, h=0.19):
    bx('c_nas', (w, d, h), (0, 0, h / 2), MC['pblack'], bev=0.004)
    bw = (w - 0.03) / 4
    for i in range(4):
        x = -w / 2 + 0.015 + bw * (i + 0.5)
        bx('c_bay', (bw - 0.004, 0.004, h - 0.05), (x, -d / 2 - 0.001, h / 2 - 0.006), MC['dark'], bev=0.001)
        bx('c_bay_led', (0.003, 0.001, 0.003), (x, -d / 2 - 0.0035, h - 0.022), MC['led'], bev=0)
    bx('c_nas_pwr', (0.006, 0.001, 0.006), (w / 2 - 0.012, -d / 2 - 0.0004, h - 0.012), MC['led_b'], bev=0)


def printer(w=0.37, d=0.33, h=0.21, body=None, sheets=0):
    body = body or MC['pwhite']
    hb = h * 0.78
    bx('c_pr_body', (w, d, hb), (0, 0, hb / 2), body, bev=0.006)
    bx('c_pr_top', (w, d * 0.42, h - hb), (0, d / 2 - d * 0.21, hb + (h - hb) / 2), body, bev=0.005)
    bx('c_pr_tray', (w * 0.74, d * 0.55, 0.004), (-w * 0.06, -d / 2 + d * 0.3, hb - 0.0005), MC['pblack'], bev=0.001)
    bx('c_pr_slot', (w * 0.7, 0.003, 0.008), (-w * 0.06, d / 2 - d * 0.42 - 0.0012, hb + 0.012), MC['pblack'], bev=0)
    bx('c_pr_cass', (w - 0.02, 0.002, 0.003), (0, -d / 2 - 0.0006, 0.07), MC['pgrey'], bev=0)
    bx('c_pr_handle', (0.08, 0.004, 0.012), (0, -d / 2 - 0.001, 0.045), MC['pgrey'], bev=0.001)
    o = plane('c_pr_screen', 0.05, 0.028, (w / 2 - 0.045, -d / 2 + 0.03, hb + 0.0012), MC['screen'])
    for k in range(2):
        cyl('c_pr_btn', 0.0045, 0.002, (w / 2 - 0.09 - 0.014 * k, -d / 2 + 0.03, hb + 0.001), MC['pgrey'], verts=16)
    for i in range(sheets):
        bx('c_pr_sheet', (0.21, 0.24, 0.0012), (-w * 0.06 + RC.uniform(-0.006, 0.006), -d / 2 + d * 0.32, hb + 0.003 + i * 0.0014), MC['paper'], rot=(0, 0, RC.uniform(-0.03, 0.03)), bev=0)


def hanging_files(dr, n, mats, tabs=True, papers=True, seed=3, messy=0.0):
    """Suspended folders on rails inside an open drawer (interior dict from TIROIRS_OUVERTS)."""
    rng = random.Random(seed)
    x0, y0, w, d, z0, z1 = dr['x'], dr['y'], dr['w'], dr['d'], dr['z0'], dr['z1']
    for sx in (-1, 1):
        bx('c_rail', (0.006, d, 0.01), (x0 + sx * (w / 2 - 0.003), y0, z1 - 0.004), MC['metal'], bev=0.0005)
    fh = min(0.235, z1 - z0 - 0.012)
    fw = w - 0.03
    for i in range(n):
        y = y0 - d / 2 + 0.035 + i * (d - 0.07) / max(1, n - 1) + rng.uniform(-0.006, 0.006)
        m = mats[i % len(mats)]
        bx('c_rod', (w - 0.002, 0.004, 0.005), (x0, y, z1 + 0.001), MC['pgrey'], bev=0.0006)
        tilt = rng.uniform(-1, 1) * messy * 0.12
        for s in (-1, 1):
            bx('c_folder', (fw, 0.0012, fh), (x0, y + s * 0.006, z1 - fh / 2), m, rot=(s * 0.045 + tilt, 0, 0), bev=0)
        if papers:
            ph = fh * rng.uniform(0.8, 1.0) + messy * rng.uniform(0, 0.05)
            bx('c_fpaper', (fw - 0.04, 0.007, ph), (x0 + rng.uniform(-0.01, 0.01), y, z1 - fh + ph / 2), MC['paper'], rot=(tilt, 0, 0), bev=0.0006)
        if tabs:
            tx = x0 + (-fw / 2 + 0.05 + (i * 0.11) % (fw - 0.1))
            plane('c_tab', 0.052, 0.016, (tx, y - 0.008, z1 + 0.012), lab_mat(f'onglet-{i % 10}'), rot=(rad(90), 0, 0))


def paper_stack(w, d, n, mats=None, messy=0.0, seed=5):
    rng = random.Random(seed)
    z = 0.0
    for i in range(n):
        th = rng.uniform(0.003, 0.008)
        m = rng.choice(mats or [MC['paper']])
        bx('c_pstack', (w, d, th), (rng.uniform(-1, 1) * messy * 0.03, rng.uniform(-1, 1) * messy * 0.04, z + th / 2), m,
           rot=(0, 0, rng.uniform(-1, 1) * (0.015 + messy * 0.12)), bev=0.0008)
        z += th
    LAST_Z[0] = z
    return z


def magazines(n, w=0.23, d=0.3, messy=0.3, seed=7):
    rng = random.Random(seed)
    z = 0.0
    for i in range(n):
        th = rng.uniform(0.004, 0.009)
        k = rng.randrange(len(SPINES))
        bx('c_mag', (w, d, th), (rng.uniform(-1, 1) * messy * 0.02, rng.uniform(-1, 1) * messy * 0.025, z + th / 2), cover_mat(k),
           rot=(0, 0, rng.uniform(-1, 1) * messy * 0.14), bev=0.0008)
        z += th
    return z


def pen(length=0.14, r=0.0045, mat=None, ang=0.0):
    d = Vector((math.cos(ang), math.sin(ang), 0)) * length / 2
    tube_between('c_pen', -d + Vector((0, 0, r)), d + Vector((0, 0, r)), r, mat or MC['pblack'], verts=10)


def label_maker():
    bx('c_lm', (0.07, 0.16, 0.038), (0, 0, 0.019), MC['pgrey'], bev=0.008)
    bx('c_lm_keys', (0.056, 0.08, 0.002), (0, -0.03, 0.038), MC['pblack'], bev=0.0008)
    plane('c_lm_scr', 0.04, 0.018, (0, 0.035, 0.0392), MC['screen'])
    bx('c_lm_tape', (0.012, 0.035, 0.0006), (0.0, 0.085, 0.03), MC['pwhite'], bev=0)


def notebook(w=0.13, d=0.21, h=0.015, mat=None):
    bx('c_nb', (w, d, h), (0, 0, h / 2), mat or MC['pblack'], bev=0.003)
    bx('c_nb_band', (0.006, d + 0.002, h + 0.002), (w / 2 - 0.02, 0, h / 2), MC['tape'], bev=0)


def carton(w, d, h, label='divers'):
    bx('c_carton', (w, d, h), (0, 0, h / 2), MC['carton'], bev=0.003)
    bx('c_ctape', (w + 0.002, 0.05, 0.0012), (0, 0, h + 0.0004), MC['tape'], bev=0)
    bx('c_ctape', (0.05, 0.0012, h * 0.35), (0, -d / 2 - 0.0004, h - h * 0.175), MC['tape'], bev=0)
    if label:
        front_plane('c_lab', 0.1, 0.1 / 6, -w / 2 + 0.08, -d / 2 - 0.0008, h * 0.45, lab_mat('etiquette-' + label))


def product_box(w, d, h):
    bx('c_prod', (w - 0.002, d - 0.002, h), (0, 0, h / 2), MC['white'], bev=0.0015)
    bx('c_prod_lid', (w, d, h * 0.45), (0, 0, h - h * 0.225), MC['pwhite'], bev=0.0015)


def tape_roll(r=0.045, h=0.025):
    cyl('c_troll', r, h, (0, 0, h / 2), MC['tape'], verts=40)
    cyl('c_troll_in', r * 0.8, h + 0.0006, (0, 0, h / 2), MC['kraft'], verts=40)
    cyl('c_troll_hole', r * 0.72, h + 0.0012, (0, 0, h / 2), MC['pblack'], verts=40)


def bookend(h=0.16, d=0.12):
    bx('c_bkend', (0.004, d, h), (0, 0, h / 2), MC['pblack'], bev=0.0008)
    bx('c_bkend', (0.1, d, 0.003), (0.05, 0, 0.0015), MC['pblack'], bev=0.0005)


def organiser(w, d, h=0.045, items=True, seed=9):
    """Black drawer organiser with compartments: adapters, coils, drives."""
    rng = random.Random(seed)
    t = 0.003
    bx('c_org_b', (w, d, t), (0, 0, t / 2), MC['pblack'], bev=0.0005)
    for sx in (-1, 1):
        bx('c_org_w', (t, d, h), (sx * (w / 2 - t / 2), 0, h / 2), MC['pblack'], bev=0.0005)
    for sy in (-1, 1):
        bx('c_org_w', (w, t, h), (0, sy * (d / 2 - t / 2), h / 2), MC['pblack'], bev=0.0005)
    bx('c_org_w', (t, d, h * 0.9), (-w / 6, 0, h * 0.45), MC['pblack'], bev=0.0005)
    bx('c_org_w', (t, d, h * 0.9), (w / 6, 0, h * 0.45), MC['pblack'], bev=0.0005)
    bx('c_org_w', (w, t, h * 0.9), (0, 0, h * 0.45), MC['pblack'], bev=0.0005)
    if not items:
        return
    cw, cd = w / 3, d / 2
    for i in range(3):
        for j in range(2):
            cx, cy = -w / 2 + cw * (i + 0.5), -d / 2 + cd * (j + 0.5)
            kind = (i + 2 * j + seed) % 4
            if kind == 0:
                grp(Vector((cx, cy, t)), 0, lambda: coil(min(cw, cd) * 0.32, 3.0, 0.002, MC['cwhite'] if j else MC['cblack'], seed=i + 4 * j, tail=0.0, tape=j == 0))
            elif kind == 1:
                grp(Vector((cx, cy, t)), rng.uniform(-0.2, 0.2), lambda: adapter(0.05, 0.05, 0.026, white=True))
            elif kind == 2:
                for k in range(2):
                    grp(Vector((cx, cy, t + k * 0.012)), rng.uniform(-0.1, 0.1), lambda: drive(0.055, 0.08, 0.011, MC['dark'] if k else MC['pgrey']))
            else:
                grp(Vector((cx, cy, t)), 0.3, lambda: adapter(0.04, 0.07, 0.024, white=False))


# ------------------------------------------------------------------ the four directions, piece by piece
# open_unit interior: x in [-0.213, 0.213], lower z [0.024, 0.286], upper z [0.298, 0.48], front y -0.29
# trolley trays (top surfaces): 0.086, 0.356, 0.656; interior x, y in [-0.198, 0.198]
OUVERTURES = {
    'A': dict(pedestal=dict(open_by=0.2, open_i=1, contents=False), low_cabinet=dict(open_at=(-1, 1), open_by=0.3)),
    'B': dict(pedestal=dict(open_by=0.2, open_i=1, contents=False), low_cabinet=dict(open_at=(-1, 1), open_by=0.32)),
    'C': dict(pedestal=dict(open_by=0.2, open_i=1, contents=False), low_cabinet=dict(open_at=(-1, 1), open_by=0.32)),
    'D': dict(pedestal=dict(open_by=0.24, open_i=1, contents=False), low_cabinet=dict(open_at=(-1, 1), open_by=0.26)),
    'M': dict(pedestal=dict(open_by=0.24, open_i=1, contents=False), low_cabinet=dict(open_at=(-1, 1), open_by=0.3)),
}


# words of the storage fronts, in build order: open unit (drawer, shelf), pedestal (bottom, middle, top),
# low cabinet (left bottom, left top, right bottom, right top), trolley
MOTS = {
    'A': dict(open_unit=['contrats', 'archives-25'], pedestal=['factures', 'divers', 'cles'], low_cabinet=['archives-24', 'factures', 'devis', 'notices'], trolley=['papier-a4']),
    'B': dict(open_unit=['manuels', 'cables-usbc'], pedestal=['sauvegardes', 'adaptateurs', 'cles'], low_cabinet=['reseau', 'chargeurs', 'cables-video', 'notices'], trolley=['disques']),
    'C': dict(open_unit=['croquis', 'revues'], pedestal=['echantillons', 'croquis', 'tirages'], low_cabinet=['manuels', 'revues', 'tirages', 'divers'], trolley=['revues']),
    'D': dict(open_unit=['devis', 'divers'], pedestal=['factures', 'divers', 'cles'], low_cabinet=['projets-af', 'projets-gm', 'archives-25', 'cables-usbc'], trolley=['papier-a4']),
    'M': dict(open_unit=['notices', 'revues'], pedestal=['clients', 'divers', 'cles'], low_cabinet=['archives-24', 'admin', 'papier-a3', 'manuels'], trolley=['papier-a4']),
}


def mot_label(piece, i):
    words = MOTS.get(CONTENU[0], {}).get(piece)
    if not words or i >= len(words):
        return None
    mats_contenus()
    return lab_mat('etiquette-' + words[i])


def set_contenu(k):
    CONTENU[0] = k
    OUVERT_R.clear()
    if k in OUVERTURES:
        OUVERT_R.update(OUVERTURES[k])


def books_row(x0, x1, y, z, hmax, seed, lean_last=True, d=0.17):
    rng = random.Random(seed)
    x = x0
    k = seed * 3
    while True:
        w = rng.uniform(0.014, 0.038)
        h = rng.uniform(hmax * 0.8, hmax)
        if x + w > x1:
            break
        pose(x + w / 2, y + (d - rng.uniform(0.15, d)) / 2, z, lambda w=w, h=h, k=k: book(w, rng.uniform(0.15, d), h, k))
        x += w + 0.0008
        k += 1
    return x


def remplir(piece, L):
    k = CONTENU[0]
    if k not in FILL:
        return
    mats_contenus()
    dr = TIROIRS_OUVERTS[0] if TIROIRS_OUVERTS else None
    FILL[k][piece](dr)


def _A_open(dr):
    pose(0, -0.12, 0.024, lambda: box_lid(0.4, 0.3, 0.12, MC['grey'], MC['grey_lid'], 'archives-24', 0.12, hole=True))
    pose(0, -0.12, 0.144, lambda: box_lid(0.4, 0.3, 0.12, MC['grey'], MC['grey_lid'], 'archives-25', 0.12, hole=True), rz=rad(-1.5))
    pose(-0.04, -0.13, 0.298, lambda: ream(3), rz=rad(1))
    pose(0.17, -0.18, 0.298, lambda: label_maker(), rz=rad(-8))


def _A_ped(dr):
    pose(dr['x'] - 0.06, dr['y'] + 0.02, dr['z0'], lambda: paper_stack(0.21, 0.297, 6), rz=rad(1))
    pose(dr['x'] + 0.11, dr['y'] - 0.05, dr['z0'], lambda: label_maker(), rz=rad(2))
    for i in range(3):
        pose(dr['x'] + 0.12 + 0.012 * i, dr['y'] + 0.12, dr['z0'], lambda i=i: pen(0.14, 0.0045, MC['pblack'] if i else MC['metal'], ang=rad(90)))


def _A_low(dr):
    hanging_files(dr, 9, [MC['dark'], MC['dark'], MC['pgrey']], seed=4)


def _A_trolley(dr):
    pose(0, 0.0, 0.656, lambda: printer(0.36, 0.32, 0.2, MC['pwhite'], sheets=3))
    pose(0, 0.0, 0.356, lambda: ream(4), rz=rad(2))
    pose(0, 0.01, 0.086, lambda: box_lid(0.36, 0.3, 0.115, MC['grey'], MC['grey_lid'], number=7))
    pose(0, 0.01, 0.201, lambda: box_lid(0.36, 0.3, 0.115, MC['grey'], MC['grey_lid'], number=8), rz=rad(-2))


def _B_open(dr):
    pose(0, -0.1, 0.024, lambda: euro_bin(0.4, 0.3, 0.13, 'cables-usbc'))
    for i in range(5):
        pose(-0.09 + 0.09 * (i % 3), -0.1 + 0.035 * (i % 2), 0.03 + 0.026 * i, lambda i=i: coil(0.06, 4, 0.0026, MC['cblack'] if i % 3 != 1 else MC['cwhite'], seed=i, tail=0.05 if i == 4 else 0.0))
    pose(-0.1, -0.08, 0.298, lambda: nas())
    pose(0.11, -0.1, 0.298, lambda: drive(0.085, 0.125, 0.021))
    pose(0.11, -0.1, 0.32, lambda: drive(0.085, 0.125, 0.021, MC['pgrey']), rz=rad(4))
    pose(0.11, -0.1, 0.342, lambda: coil(0.045, 3.5, 0.0022, seed=7, tail=0.08))


def _B_ped(dr):
    pose(dr['x'], dr['y'] + 0.02, dr['z0'], lambda: organiser(dr['w'] - 0.01, dr['d'] * 0.62, 0.045))
    pose(dr['x'] - 0.08, dr['y'] - 0.17, dr['z0'], lambda: coil(0.04, 3, 0.002, MC['cwhite'], seed=11, tail=0.0))


def _B_low(dr):
    pose(dr['x'] - 0.1, dr['y'] - 0.05, dr['z0'], lambda: product_box(0.17, 0.17, 0.075), rz=rad(3))
    pose(dr['x'] - 0.1, dr['y'] - 0.05, dr['z0'] + 0.075, lambda: product_box(0.15, 0.12, 0.05), rz=rad(-6))
    pose(dr['x'] + 0.11, dr['y'] - 0.04, dr['z0'], lambda: euro_bin(0.2, 0.3, 0.12, 'chargeurs', MC['bin']))
    for i in range(2):
        pose(dr['x'] + 0.11, dr['y'] - 0.06 + 0.1 * i, dr['z0'] + 0.01 + 0.03 * i, lambda i=i: adapter(0.06, 0.06, 0.03, white=i == 0))
    pose(dr['x'] - 0.06, dr['y'] + 0.16, dr['z0'], lambda: coil(0.05, 4, 0.0026, seed=12, tail=0.0))


def _B_trolley(dr):
    pose(0, 0.0, 0.656, lambda: printer(0.36, 0.32, 0.2, MC['pblack'], sheets=0))
    pose(0, 0.0, 0.356, lambda: euro_bin(0.38, 0.3, 0.13, 'sauvegardes'))
    for i in range(6):
        pose(-0.13 + 0.05 * i, 0.0, 0.361, lambda i=i: drive_up(0.024, 0.09, 0.13, MC['dark'] if i % 2 else MC['pgrey']), rz=rad(RC.uniform(-4, 4)))
    for i in range(3):
        pose(-0.11 + 0.11 * i, 0.02 * (i % 2), 0.086 + 0.004 * i, lambda i=i: coil(0.06, 4, 0.0028, MC['cblack'], seed=20 + i, tail=0.0))
    pose(0.0, -0.08, 0.1, lambda: tape_roll())


def _C_open(dr):
    x = books_row(-0.205, 0.21, -0.1, 0.024, 0.245, seed=2, d=0.2)
    z = 0.298
    pose(-0.08, -0.12, z, lambda: magazines(8))
    for i in range(3):
        pose(0.13, -0.15, z + 0.016 * i, lambda i=i: notebook(0.13, 0.21, 0.015, [MC['pblack'], MC['kraft'], MC['dark']][i]), rz=rad(4 - 5 * i))


def _C_ped(dr):
    for i in range(3):
        pose(dr['x'] - 0.07, dr['y'] - 0.02, dr['z0'] + 0.016 * i, lambda i=i: notebook(0.15, 0.21, 0.015, [MC['kraft'], MC['pblack'], MC['grey']][i]), rz=rad(-3 + 4 * i))
    for i in range(5):
        pose(dr['x'] + 0.1 + 0.011 * i, dr['y'] + 0.02, dr['z0'], lambda i=i: pen(0.17, 0.0038, [MC['pblack'], MC['kraft'], MC['pblack'], MC['metal'], MC['pgrey']][i], ang=rad(88)))
    pose(dr['x'] + 0.04, dr['y'] + 0.19, dr['z0'], lambda: bx('c_ruler', (0.3, 0.025, 0.002), (0, 0, 0.001), MC['metal'], bev=0))


def _C_low(dr):
    pose(dr['x'] - 0.1, dr['y'], dr['z0'], lambda: magazines(14, seed=3))
    pose(dr['x'] + 0.12, dr['y'] + 0.02, dr['z0'], lambda: magazines(10, w=0.2, d=0.27, seed=4))


def _C_trolley(dr):
    z = 0.656
    for i, (w, h, kk) in enumerate([(0.032, 0.3, 4), (0.024, 0.27, 9), (0.02, 0.25, 1)]):
        lay(0.0, 0.0, z, w, h, lambda w=w, h=h, kk=kk: book(w, 0.23 - 0.01 * i, h, kk), rz=rad(90 + 3 * i))
        z += w
    books_row(-0.19, 0.19, 0.0, 0.356, 0.25, seed=5, d=0.19)
    pose(-0.02, 0.0, 0.086, lambda: magazines(12, seed=6), rz=rad(4))


def _D_open(dr):
    pose(0, -0.11, 0.024, lambda: box_lid(0.4, 0.3, 0.12, MC['grey'], MC['grey_lid'], 'devis', 0.11, hole=True), rz=rad(1.5))
    pose(-0.02, -0.12, 0.144, lambda: magazines(6, messy=0.6, seed=8), rz=rad(-5))
    pose(0.08, -0.1, 0.19, lambda: coil(0.055, 3.5, 0.0025, seed=31, tail=0.1))
    books_row(-0.205, 0.05, -0.08, 0.298, 0.175, seed=8, d=0.17)
    pose(0.13, -0.15, 0.298, lambda: paper_stack(0.21, 0.297, 7, [MC['paper'], MC['manila'], MC['paper']], messy=0.8, seed=31), rz=rad(84))


def _D_ped(dr):
    pose(dr['x'] - 0.04, dr['y'] - 0.03, dr['z0'], lambda: paper_stack(0.21, 0.297, 7, [MC['paper'], MC['paper'], MC['manila']], messy=1.0, seed=33), rz=rad(6))
    pose(dr['x'] - 0.06, dr['y'] - dr['d'] / 2 + 0.09, dr['z0'] + 0.03, lambda: bx('c_sheet_out', (0.21, 0.297, 0.0012), (0, 0, 0), MC['paper'], rot=(rad(-8), 0, rad(-9)), bev=0))
    pose(dr['x'] + 0.12, dr['y'] + 0.12, dr['z0'], lambda: adapter(0.06, 0.06, 0.028))
    pose(dr['x'] + 0.11, dr['y'] - 0.1, dr['z0'], lambda: coil(0.04, 3, 0.002, MC['cwhite'], seed=34, tail=0.06))
    for i in range(3):
        pose(dr['x'] + 0.02 + 0.03 * i, dr['y'] + 0.15, dr['z0'] + 0.004, lambda i=i: pen(0.14, 0.0042, [MC['pblack'], MC['metal'], MC['kraft']][i], ang=rad(70 + 25 * i)))


def _D_low(dr):
    hanging_files(dr, 8, [MC['kraft'], MC['dark'], MC['manila'], MC['pgrey']], seed=7, messy=1.0)


def _D_trolley(dr, carton_label='divers'):
    pose(0, 0.0, 0.656, lambda: printer(0.36, 0.32, 0.2, MC['pwhite'], sheets=5))
    pose(-0.04, -0.03, 0.356, lambda: ream(2), rz=rad(-3))
    pose(0.0, 0.0, 0.456, lambda: magazines(3, messy=0.6, seed=40), rz=rad(8))
    pose(0.13, 0.135, 0.356, lambda: coil(0.045, 3.5, 0.0026, seed=41, tail=0.0))     # beside the reams, not through them
    pose(0.0, 0.0, 0.086, lambda: carton(0.34, 0.3, 0.16, carton_label), rz=rad(-4))
    lay(0.0, 0.0, 0.246, 0.03, 0.26, lambda: book(0.03, 0.2, 0.26, 7), rz=rad(84))


# ---- M, the retained mix. Open unit and pedestal of D, reworked so that every item stays inside its compartment.
def _M_open(dr):
    # lower compartment (x ±0.213, z 0.024–0.286): archive box, magazines and a coil on its lid
    pose(0, -0.11, 0.024, lambda: box_lid(0.4, 0.3, 0.12, MC['grey'], MC['grey_lid'], 'archives-25', 0.11, hole=True), rz=rad(1.5))
    pose(-0.05, -0.12, 0.144, lambda: magazines(6, messy=0.35, seed=8), rz=rad(-4))
    pose(0.135, -0.1, 0.144, lambda: coil(0.048, 3.5, 0.0025, seed=31, tail=0.0))
    # upper compartment (z 0.298–0.48): paperbacks standing on the left, an A4 stack lying on the right, both inside the sides
    books_row(-0.205, -0.045, -0.08, 0.298, 0.16, seed=8, d=0.16)
    pose(0.092, -0.12, 0.298, lambda: paper_stack(0.21, 0.297, 7, [MC['paper'], MC['manila'], MC['paper']], messy=0.2, seed=31), rz=rad(-1.5))


def _M_ped(dr):
    # open drawer interior: x ±dr['w']/2 (0.171), y ±dr['d']/2 (0.237), 6 cm high. A4 stack on the left, small things on the right,
    # pens along the back: nothing overlaps, nothing goes through the front.
    x, y, z = dr['x'], dr['y'], dr['z0']
    pose(x - 0.045, y - 0.03, z, lambda: paper_stack(0.21, 0.297, 7, [MC['paper'], MC['paper'], MC['manila']], messy=0.15, seed=33), rz=rad(2))
    pose(x + 0.118, y - 0.06, z, lambda: adapter(0.06, 0.06, 0.028), rz=rad(-8))
    pose(x + 0.115, y - 0.168, z, lambda: coil(0.034, 3, 0.002, MC['cwhite'], seed=34, tail=0.0))
    for i in range(3):
        pose(x - 0.05, y + 0.172 + 0.016 * i, z, lambda i=i: pen(0.14, 0.0042, [MC['pblack'], MC['metal'], MC['kraft']][i], ang=rad(2 - 3 * i)))


FILL = {
    'A': dict(open_unit=_A_open, pedestal=_A_ped, low_cabinet=_A_low, trolley=_A_trolley),
    'B': dict(open_unit=_B_open, pedestal=_B_ped, low_cabinet=_B_low, trolley=_B_trolley),
    'C': dict(open_unit=_C_open, pedestal=_C_ped, low_cabinet=_C_low, trolley=_C_trolley),
    'D': dict(open_unit=_D_open, pedestal=_D_ped, low_cabinet=_D_low, trolley=_D_trolley),
    'M': dict(open_unit=_M_open, pedestal=_M_ped, low_cabinet=_A_low, trolley=lambda dr: _D_trolley(dr, 'echantillons')),
}
set_contenu(CONTENU[0])


# ------------------------------------------------------------------ the riser of desk D (top at zsh, y centre ysh, x from xs0 to xs1)
def remplir_rehausse(F, zsh, ysh, xs0, xs1, h=None):
    """Riser contents (h, the desk top height, is kept for objects on the desk)."""
    k = CONTENU[0]
    mats_contenus()

    def P(x, y, z, build, rz=0.0):
        return grp(F.p(x, y, z), F.r + rz, build)

    y = ysh + 0.005
    if k == 'A':
        P(xs0 + 0.2, y, zsh, lambda: box_lid(0.3, 0.22, 0.12, MC['dark'], MC['dark'], 'contrats', 0.1), rad(-2))
        for i in range(6):
            P(0.02 + 0.105 * i, y, zsh, lambda i=i: archive_upright(0.1, 0.23, 0.33, MC['grey'], i + 1))
        for i in range(3):
            P(0.7 + 0.085 * i, y, zsh, lambda i=i: magfile(0.08, 0.23, 0.3, MC['pwhite'], ['factures', 'devis', 'notices'][i], seed=i))
    elif k == 'B':
        P(xs0 + 0.18, y, zsh, lambda: coil(0.07, 4, 0.003, seed=50, tail=0.0))
        for i in range(4):
            P(0.0 + 0.22 * i, y, zsh, lambda i=i: euro_bin(0.2, 0.22, 0.12, ['adaptateurs', 'cables-video', 'disques', 'cles'][i]))
        P(0.0, y, zsh + 0.12, lambda: product_box(0.18, 0.18, 0.08), rad(3))
        P(0.66, y, zsh + 0.12, lambda: product_box(0.2, 0.2, 0.1), rad(-4))
        P(0.94, y, zsh + 0.12, lambda: nas())
    elif k == 'C':
        P(xs0 + 0.18, y, zsh, lambda: magazines(5, seed=51), rad(4))
        P(0.0, y, zsh, lambda: bookend(0.18, 0.15), rad(180))
        x = 0.01
        rng = random.Random(12)
        kk = 2
        while x < 0.55:
            w, h = rng.uniform(0.016, 0.042), rng.uniform(0.22, 0.3)
            P(x + w / 2, y, zsh, lambda w=w, h=h, kk=kk: book(w, 0.21, h, kk))
            x += w + 0.001
            kk += 1
        P(x + 0.002, y, zsh, lambda: bookend(0.18, 0.15))
        for i in range(2):
            P(0.72 + 0.17 * i, y, zsh, lambda i=i: box_lid(0.16, 0.22, 0.13, MC['dark'], MC['dark'], ['tirages', 'echantillons'][i], 0.1))
    elif k == 'D':
        P(xs0 + 0.2, y, zsh, lambda: box_lid(0.3, 0.22, 0.12, MC['dark'], MC['dark'], 'contrats', 0.1), rad(-3))
        P(xs0 + 0.2, y, zsh + 0.12, lambda: magazines(4, messy=0.6, seed=52), rad(6))
        for i in range(5):
            P(0.02 + 0.075 * i, y, zsh, lambda i=i: binder(0.072, 0.26, 0.3, [MC['white'], MC['white'], MC['dark'], MC['grey'], MC['white']][i], ['factures', 'contrats', 'devis', 'projets-af', 'projets-gm'][i]),
              rad(-12) if i == 4 else 0.0)
        x = 0.42
        rng = random.Random(13)
        kk = 5
        while x < 0.62:
            w, h = rng.uniform(0.016, 0.04), rng.uniform(0.22, 0.29)
            P(x + w / 2, y, zsh, lambda w=w, h=h, kk=kk: book(w, 0.21, h, kk))
            x += w + 0.001
            kk += 1
        P(0.78, y, zsh, lambda: carton(0.28, 0.22, 0.17, 'tirages'), rad(5))
        P(0.78, y, zsh + 0.17, lambda: carton(0.24, 0.2, 0.11, None), rad(-6))
    elif k == 'M':
        # D's riser; the cartons move into the gap on the left, B's NAS stands on the riser where they were.
        # The riser top is 24 cm deep between its front lip (y 0.152) and its back edge (0.39): every item is centred on it
        # and at most 23 cm deep, with small turns, so nothing passes over an edge.
        y = ysh
        P(xs0 + 0.2, y, zsh, lambda: box_lid(0.3, 0.22, 0.12, MC['dark'], MC['dark'], 'contrats', 0.1), rad(-2))
        P(xs0 + 0.2, y, zsh + 0.12, lambda: magazines(4, messy=0.35, seed=52), rad(93))      # long side along the box
        # 17/11 (cables step): the screens' arm sweeps the riser between x -0.22 and 0.44 just above its top, and its pole
        # goes through it at x 0.11: that stretch stays clear (the arm, the pole's grommet and the cables pass there).
        # The two cartons move left against the box, three of the five binders stand between the books and the NAS.
        P(-0.34, y, zsh, lambda: carton(0.28, 0.22, 0.17, 'tirages'), 0.0)
        P(-0.34, y, zsh + 0.17, lambda: carton(0.24, 0.2, 0.11, None), rad(-3))
        for i in range(3):
            P(0.684 + 0.0745 * i, y, zsh, lambda i=i: binder(0.072, 0.225, 0.3, [MC['white'], MC['white'], MC['dark']][i], ['factures', 'devis', 'banque'][i]))
        x = 0.42
        rng = random.Random(13)
        kk = 5
        while x < 0.62:
            w, hb = rng.uniform(0.016, 0.04), rng.uniform(0.22, 0.29)
            P(x + w / 2, y, zsh, lambda w=w, hb=hb, kk=kk: book(w, 0.21, hb, kk))
            x += w + 0.001
            kk += 1
        P(float(OPT.get('nas_x', 0.962)), y, zsh, lambda: nas(), 0.0)
        # (B's cable coil lay on the desk top for a while on 15/11; removed at the user's request)


# ------------------------------------------------------------------ LED strips under the desk top and the return (lab option ledsous=1)
def led_sous_bureau(F, h=0.74, hr=0.64, e=None):
    """Thin warm-white LED strips under the front edge of the desk and of the return, aimed at the storage."""
    e = float(OPT.get('ledk', 1.0)) if e is None else e
    if 'c_led_strip' not in MC:
        MC['c_led_strip'] = mat_emit('c_led_strip', (1.0, 0.92, 0.82), 4.0)
    for (x, y, z, L, E) in ((0.0, -0.33, h - 0.03, 2.1, 9.0), (RX, RY - RD / 2 + 0.05, hr - 0.03, 1.08, 5.0)):
        o = box('dk_led_sous', (L, 0.012, 0.005), F.p(x, y, z), MC['c_led_strip'], rot=(0, 0, F.r))
        li = add_light('AREA', 'al_light_sous', F.p(x, y + 0.01, z - 0.006), E * e, (1.0, 0.92, 0.82), size=L)
        li.data.shape = 'RECTANGLE'
        li.data.size_y = 0.03
        li.data.spread = rad(120)
        li.rotation_euler = (rad(22), 0, F.r)


# ------------------------------------------------------------------ studio prototypes
class _FC:
    o = Vector((0, 0, 0))
    r = 0.0

    @staticmethod
    def p(x, y, z):
        return Vector((x, y, z))


SHOT_CT = {
    'grp': dict(cam=(-1.85, -2.85, 1.38), target=(0.08, 0.0, 0.3), lens=33, fstop=11, focus=None),
    'ouvert': dict(cam=(-1.72, -1.02, 0.66), target=(-1.25, 0.0, 0.27), lens=48, fstop=5.6, focus=None),
    'tiroirs': dict(cam=(-0.55, -1.45, 1.38), target=(-0.15, -0.32, 0.36), lens=36, fstop=8, focus=None),
    'desserte': dict(cam=(0.98, -1.3, 1.05), target=(1.45, 0.0, 0.4), lens=42, fstop=5.6, focus=None),
    'bur': dict(cam=(-2.45, -3.35, 1.85), target=(0.72, 0.1, 0.5), lens=32, fstop=11, focus=None),
    'rehausse': dict(cam=(-0.5, -1.45, 1.36), target=(0.1, 0.27, 1.12), lens=28, fstop=8, focus=None),
}


def main_contenus():
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
    L = look('N')
    keys = OPT.get('contenus', 'M').split(',')
    vues = OPT.get('vues', 'grp,ouvert,tiroirs,desserte,bur,rehausse').split(',')
    colls = {}
    for k in keys:
        set_contenu(k)
        c = coll(f'C_{k}_grp')
        CUR[0] = c
        build_group(L)
        colls[(k, 'grp')] = c
        if 'bur' in vues or 'rehausse' in vues:
            c = coll(f'C_{k}_bur')
            CUR[0] = c
            build_with_desk(L)
            remplir_rehausse(_FC, H0 + 0.3015, 0.27, -0.85, 1.05, H0)
            colls[(k, 'bur')] = c
    os.makedirs(OUT, exist_ok=True)
    if OPT.get('save') == '1':
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'contenus.blend'))
    for k in keys:
        for v in vues:
            kind = 'bur' if v in ('bur', 'rehausse') else 'grp'
            for key, c in colls.items():
                c.hide_render = key != (k, kind)
            SC.camera = make_camera(dict(SHOT_CT[v]), f'CAM_{k}_{v}')
            SC.render.resolution_x = RES
            SC.render.resolution_y = int(RES * 9 / 16)
            SC.render.filepath = os.path.join(OUT, f'{k}-{v}.png')
            print('RENDER', SC.render.filepath, flush=True)
            bpy.ops.render.render(write_still=True)


main_contenus()
