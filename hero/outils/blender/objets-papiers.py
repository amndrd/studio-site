
# ================================================================== papers on the desk, and the books under the lamp
# Built after objets-contenus.py (uses grp(), MC, mats_contenus()). Option papiers=M (the B + C mix, retained on 15/11,
# default; papiers=aucun removes them). The documents belong to two fictional clients of the studio (Halde, galerie & café, with the
# architects Vesper & Morel; Ombelle, speakers): textures from hero/outils/textures_papiers.py (captures of the HTML/SVG
# pages in papiers-contenus/, printed on paper and annotated by hand) and textures_livres.py (book covers).
# Every sheet is draped on a height field of the desk frame (desk top, desk mat, return, then each sheet laid before it),
# so sheets rest on one another and never cross. livres_lampe() builds the three books the lamp stands on (P3).
TEXP = os.path.join(TEXB, 'papiers')
TEXL = os.path.join(TEXB, 'livres')
PAPIERS = [OPT.get('papiers', 'M')]          # M retained on 15/11 ('aucun' = no papers)
MP = {}
RP = random.Random(31)
A4, A3, A2 = (0.21, 0.297), (0.297, 0.42), (0.42, 0.594)


def tp(name):
    return os.path.join(TEXP, name + '.png')


def m_base():
    if 'back' not in MP:
        MP['back'] = mat_color('p_dos', (0.8, 0.8, 0.77), rough=0.82)
        MP['edge'] = m_surface('p_tranche', (0.8, 0.8, 0.76), rough=0.85, var=0.05, grain=4000, bump=0.004)
        MP['roll'] = m_surface('p_rouleau', (0.84, 0.84, 0.8), rough=0.8, var=0.02, grain=700, bump=0.002)
        MP['pages'] = m_surface('p_pages', (0.78, 0.76, 0.7), rough=0.88, var=0.06, grain=5000, bump=0.01)
    return MP['back']


def m_print(name, rough=0.78, path=None):
    key = ('print', name, rough)
    if key not in MP:
        MP[key] = mat_paper(path or tp(name), rough)
    return MP[key]


def m_calque(name):
    """Tracing paper: milky translucent sheet (28 % opaque), pencil lines from the RGBA texture fully opaque."""
    key = ('calque', name)
    if key in MP:
        return MP[key]
    m = new_mat('p_calque_' + name)
    nt = m.node_tree
    p = principled(m)
    t = nt.nodes.new('ShaderNodeTexImage')
    t.image = img(tp(name))
    mix = nt.nodes.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    nt.links.new(t.outputs['Alpha'], mix.inputs[0])
    next(s for s in mix.inputs if s.identifier == 'A_Color').default_value = (0.86, 0.87, 0.86, 1)
    nt.links.new(t.outputs['Color'], next(s for s in mix.inputs if s.identifier == 'B_Color'))
    nt.links.new(next(s for s in mix.outputs if s.identifier == 'Result_Color'), p.inputs['Base Color'])
    ma = nt.nodes.new('ShaderNodeMath')
    ma.operation = 'MULTIPLY_ADD'
    nt.links.new(t.outputs['Alpha'], ma.inputs[0])
    ma.inputs[1].default_value = 0.72
    ma.inputs[2].default_value = 0.28
    nt.links.new(ma.outputs[0], p.inputs['Alpha'])
    p.inputs['Roughness'].default_value = 0.35
    MP[key] = m
    return m


# ------------------------------------------------------------------ height field of the desk frame
class Champ:
    """Max height of what lies on the desk (desk frame), on a 4 mm grid: desk top, desk mat, return, then every item laid."""
    def __init__(self, h, hr):
        self.x0, self.y0, self.s = -1.25, -0.45, 0.004
        self.nx, self.ny = int(3.8 / self.s), int(0.9 / self.s)
        self.z = [[-1.0] * self.nx for _ in range(self.ny)]
        self.rect(-1.2, 1.2, -0.4, 0.4, h)
        self.rect(-0.35, 0.55, -0.39, -0.01, h + 0.003)                  # desk mat of setup B2
        self.rect(1.25, 2.45, -0.2, 0.4, hr)

    def idx(self, x, y):
        return int((x - self.x0) / self.s), int((y - self.y0) / self.s)

    def rect(self, xa, xb, ya, yb, z):
        i0, j0 = self.idx(xa, ya)
        i1, j1 = self.idx(xb, yb)
        for j in range(max(0, j0), min(self.ny, j1 + 1)):
            row = self.z[j]
            for i in range(max(0, i0), min(self.nx, i1 + 1)):
                row[i] = max(row[i], z)

    def at(self, x, y, r=0.0):
        i0, j0 = self.idx(x - r, y - r)
        i1, j1 = self.idx(x + r, y + r)
        m = -1.0
        for j in range(max(0, j0), min(self.ny, j1 + 1)):
            row = self.z[j]
            for i in range(max(0, i0), min(self.nx, i1 + 1)):
                if row[i] > m:
                    m = row[i]
        return m

    def footprint(self, x, y, rz, w, d, ztop=None):
        """Max height under a rotated rectangle; with ztop, raises the rectangle to ztop."""
        c, s_ = math.cos(rz), math.sin(rz)
        hw, hd = w / 2, d / 2
        ex, ey = abs(hw * c) + abs(hd * s_), abs(hw * s_) + abs(hd * c)
        i0, j0 = self.idx(x - ex, y - ey)
        i1, j1 = self.idx(x + ex, y + ey)
        m = -1.0
        for j in range(max(0, j0), min(self.ny, j1 + 1)):
            yy = self.y0 + (j + 0.5) * self.s - y
            row = self.z[j]
            for i in range(max(0, i0), min(self.nx, i1 + 1)):
                xx = self.x0 + (i + 0.5) * self.s - x
                lx, ly = xx * c + yy * s_, -xx * s_ + yy * c
                if abs(lx) <= hw and abs(ly) <= hd:
                    if ztop is None:
                        m = max(m, row[i])
                    else:
                        row[i] = max(row[i], ztop)
        return m

    def raster(self, x, y, rz, w, d, Z, nx, ny, t=0.00025):
        """Raises the field under a draped sheet: bilinear height of its vertex grid Z, plus its thickness."""
        c, s_ = math.cos(rz), math.sin(rz)
        hw, hd = w / 2, d / 2
        ex, ey = abs(hw * c) + abs(hd * s_), abs(hw * s_) + abs(hd * c)
        i0, j0 = self.idx(x - ex, y - ey)
        i1, j1 = self.idx(x + ex, y + ey)
        for j in range(max(0, j0), min(self.ny, j1 + 1)):
            yy = self.y0 + (j + 0.5) * self.s - y
            row = self.z[j]
            for i in range(max(0, i0), min(self.nx, i1 + 1)):
                xx = self.x0 + (i + 0.5) * self.s - x
                lx, ly = xx * c + yy * s_, -xx * s_ + yy * c
                u, v = lx / w + 0.5, ly / d + 0.5
                if 0 <= u <= 1 and 0 <= v <= 1:
                    fu, fv = u * nx, v * ny
                    a, b = min(int(fu), nx - 1), min(int(fv), ny - 1)
                    tu, tv = fu - a, fv - b
                    z = (Z[b][a] * (1 - tu) * (1 - tv) + Z[b][a + 1] * tu * (1 - tv) + Z[b + 1][a] * (1 - tu) * tv + Z[b + 1][a + 1] * tu * tv)
                    if z + t > row[i]:
                        row[i] = z + t


CH = [None]


def forme(rng, corner=0.0, curl=0.0, edge=None, wave=0.0):
    """Own shape of a sheet above what it lies on: a lifted corner, a curled edge, a soft waviness."""
    ci = rng.randrange(4)
    e = edge or rng.choice('NSEW')
    ph = rng.uniform(0, 6.28)

    def f(u, v):
        z = 0.0
        if corner:
            cu, cv = ((0, 0), (1, 0), (1, 1), (0, 1))[ci]
            z += corner * max(0.0, 1 - math.hypot(u - cu, v - cv) / 0.42) ** 2
        if curl:
            t = {'N': v, 'S': 1 - v, 'E': u, 'W': 1 - u}[e]
            z += curl * max(0.0, (t - 0.8) / 0.2) ** 2
        if wave:
            z += wave * (0.5 + 0.5 * math.sin(u * 3.0 + ph) * math.sin(v * 2.2 + ph * 0.7))
        return z
    return f


def grid_mesh(name, w, d, Z, mat, nx, ny, dz=0.0, uvr=(0, 0, 1, 1)):
    verts = [((i / nx - 0.5) * w, (j / ny - 0.5) * d, Z[j][i] + dz) for j in range(ny + 1) for i in range(nx + 1)]
    faces = [(j * (nx + 1) + i, j * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i) for j in range(ny) for i in range(nx)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    uv = me.uv_layers.new()
    for poly in me.polygons:
        poly.use_smooth = True
        for li in poly.loop_indices:
            vi = me.loops[li].vertex_index
            uv.data[li].uv = (uvr[0] + (uvr[2] - uvr[0]) * (vi % (nx + 1)) / nx, uvr[1] + (uvr[3] - uvr[1]) * (vi // (nx + 1)) / ny)
    o = bpy.data.objects.new(name, me)
    me.materials.append(mat)
    return link(o)


def drape(F, x, y, rz, w, d, mat, back=True, gap=0.00035, uvr=(0, 0, 1, 1), rng=RP, **shape):
    """A sheet laid at (x, y, rz) of the desk frame, on whatever is already there (height field), then added to it."""
    ch = CH[0]
    nx, ny = max(6, int(w / 0.012)), max(6, int(d / 0.012))
    f = forme(rng, **shape)
    c, s_ = math.cos(rz), math.sin(rz)
    r = max(w / nx, d / ny) * 0.75
    Z = []
    for j in range(ny + 1):
        row = []
        for i in range(nx + 1):
            lx, ly = (i / nx - 0.5) * w, (j / ny - 0.5) * d
            row.append(ch.at(x + lx * c - ly * s_, y + lx * s_ + ly * c, r) + gap + f(i / nx, j / ny))
        Z.append(row)
    for _ in range(2):                                           # soften the steps over the sheets underneath
        Z = [[max(Z[j][i], 0.25 * (Z[j][max(i - 1, 0)] + Z[j][min(i + 1, nx)] + Z[max(j - 1, 0)][i] + Z[min(j + 1, ny)][i])) for i in range(nx + 1)] for j in range(ny + 1)]

    def build():
        grid_mesh('p_feuille', w, d, Z, mat, nx, ny, 0.0, uvr)
        if back:
            grid_mesh('p_dos', w, d, Z, m_base(), nx, ny, -0.00015)
    grp(F.p(x, y, 0.0), F.r + rz, build)
    ch.raster(x, y, rz, w, d, Z, nx, ny)


def scotch(F, x, y, rz, L=0.036):
    """Black tape (desk rules: labels white, tape black), draped on the sheet it holds."""
    drape(F, x, y, rz, L, 0.019, MC['tape'], back=False, gap=0.0002)


def corners(x, y, rz, w, d, inset=(0.006, 0.004)):
    c, s_ = math.cos(rz), math.sin(rz)
    out = []
    for sx, sy in ((-1, 1), (1, 1), (1, -1), (-1, -1)):
        lx, ly = sx * (w / 2 - inset[0]), sy * (d / 2 - inset[1])
        out.append((x + lx * c - ly * s_, y + lx * s_ + ly * c, sx * sy))
    return out


def calque(F, x, y, rz, w, d, name, tapes=4):
    drape(F, x, y, rz, w, d, m_calque(name), back=False, corner=0.003, wave=0.0008)
    for k, (cx, cy, sg) in enumerate(corners(x, y, rz, w, d)):
        if k < tapes:
            scotch(F, cx, cy, rz + (0.75 if sg > 0 else -0.75) + RP.uniform(-0.2, 0.2))


def pile(F, x, y, rz, w, d, n, top, clip=False):
    """A stack of n sheets (body with paper edges) on the field, the printed sheet on top, an optional binder clip."""
    ch = CH[0]
    z0 = ch.footprint(x, y, rz, w, d)
    t = n * 0.00011
    _P(F, x, y, z0, lambda: bx('p_pile', (w - 0.002, d - 0.002, t), (0, 0, t / 2), MP['edge'], bev=0.0004), rz)
    ch.footprint(x, y, rz, w - 0.002, d - 0.002, z0 + t)
    drape(F, x + 0.002, y - 0.002, rz + 0.012, w, d, m_print(top), back=False, wave=0.0004)
    if clip:
        zt = ch.footprint(x, y, rz, w, d)
        c, s_ = math.cos(rz), math.sin(rz)
        px, py = x + (w * 0.15) * c - (d / 2 - 0.006) * s_, y + (w * 0.15) * s_ + (d / 2 - 0.006) * c
        _P(F, px, py, zt, lambda: pince(0.032), rz)


def pince(L):
    """Black binder clip on a stack edge, handles folded flat towards the sheet."""
    bx('p_pince', (L, 0.016, 0.006), (0, 0.002, 0.003), MC['pblack'], bev=0.0012)
    for s in (-1, 1):
        a = Vector((s * L * 0.32, -0.002, 0.0062))
        tube_between('p_pince_fil', a, a + Vector((0, -0.026, 0.0)), 0.0009, MC['metal'], verts=6)
    tube_between('p_pince_fil', Vector((-L * 0.32, -0.028, 0.0062)), Vector((L * 0.32, -0.028, 0.0062)), 0.0009, MC['metal'], verts=6)


def disque(name, r, mat, n=40):
    verts = [(0, 0, 0)] + [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n), 0) for i in range(n)]
    faces = [(0, i + 1, (i + 1) % n + 1) for i in range(n)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    uv = me.uv_layers.new()
    for poly in me.polygons:
        for li in poly.loop_indices:
            vx, vy, _ = verts[me.loops[li].vertex_index]
            uv.data[li].uv = (0.5 + vx / (2 * r), 0.5 + vy / (2 * r))
    o = bpy.data.objects.new(name, me)
    me.materials.append(mat)
    return link(o)


def rouleau(F, x, y, rz, L=0.6, r=0.03, z=None, band=True):
    """Rolled plan lying along its local x: paper body, spiral ends, the last turn's edge, a black tape band."""
    ch = CH[0]
    z0 = ch.footprint(x, y, rz, L, 2 * r * 0.6) if z is None else z

    def build():
        cyl('p_rouleau', r, L, (0, 0, r), MP['roll'], rot=(0, rad(90), 0), verts=40)
        m = m_print('rouleau-bout', 0.8)
        for s in (-1, 1):
            o = disque('p_rouleau_bout', r * 0.985, m)
            o.location = (s * (L / 2 + 0.0004), 0, r)
            o.rotation_euler = (0, rad(90) * s, RP.uniform(0, 6.28))
        a = RP.uniform(0.6, 2.4)
        bx('p_rouleau_bord', (L, 0.0012, 0.0006), (0, r * math.cos(a), r + r * math.sin(a)), MP['roll'], rot=(a, 0, 0), bev=0)
        if band:
            cyl('p_rouleau_bande', r + 0.0006, 0.022, (RP.uniform(-0.12, 0.12), 0, r), MC['tape'], rot=(0, rad(90), 0), verts=40, caps=False)
    _P(F, x, y, z0, build, rz)
    ch.footprint(x, y, rz, L, 2 * r * 0.8, z0 + 2 * r)
    return z0


def chemise(F, x, y, rz, top, out=0.04, w=0.24, d=0.32):
    """Kraft folder, a few sheets inside sticking out of it (the printed one on top)."""
    drape(F, x, y, rz, w, d, MC['kraft'], back=False, gap=0.0003)
    c, s_ = math.cos(rz), math.sin(rz)
    for k in range(3):
        oy = out * (k + 1) / 3
        drape(F, x - oy * s_ + RP.uniform(-0.006, 0.006), y + oy * c, rz + RP.uniform(-0.03, 0.03), A4[0], A4[1],
              m_print(top) if k == 2 else m_base(), back=False, wave=0.0003)
    drape(F, x + 0.002, y - 0.004, rz + RP.uniform(-0.02, 0.01), w, d, MC['kraft'], back=False, gap=0.0004)


def plie(F, x, y, rz, name):
    """An A4 folded in half (the top half of the page shows), the fold slightly open."""
    drape(F, x, y, rz, A4[0], A4[1] / 2, m_base(), back=False)
    drape(F, x, y, rz, A4[0], A4[1] / 2, m_print(name), back=False, curl=0.0025, edge='S', wave=0.0005, uvr=(0, 0.5, 1, 1))


def postit(F, x, y, rz, name, curl=0.004):
    drape(F, x, y, rz, 0.076, 0.076, m_print(name, 0.6), back=False, curl=curl, edge='S')


def _P(F, x, y, z, build, rz=0.0, rx=0.0):
    return grp(F.p(x, y, z), F.r + rz, build, rx=rx)


# ------------------------------------------------------------------ books under the lamp
LIVRES = [('grid', 0.21, 0.30, 0.022, True), ('albers', 0.165, 0.235, 0.017, False), ('knr', 0.178, 0.234, 0.014, False)]


def quad(name, pts, uvs, mat):
    me = bpy.data.meshes.new(name)
    me.from_pydata(pts, [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for li, (u, v) in enumerate(uvs):
        uv.data[li].uv = (u, v)
    o = bpy.data.objects.new(name, me)
    me.materials.append(mat)
    return link(o)


def livre(key, W, Ht, T, hard):
    """A book lying cover up, spine towards -x (seen from the hero camera), top of the book towards +y.
    Cover image: spine on the left, top up. Spine image: horizontal strip, book top on the left."""
    cov = m_print(key + '-couverture', 0.45 if not hard else 0.55, os.path.join(TEXL, key + '-couverture.png'))
    spi = m_print(key + '-tranche', 0.45, os.path.join(TEXL, key + '-tranche.png'))
    b = 0.0025 if hard else 0.0006                                # board thickness
    o = 0.003 if hard else 0.0                                     # boards overhang the page block
    plain = MP.setdefault(('dos', key), mat_color('p_livre_dos_' + key, {'grid': (0.78, 0.2, 0.12), 'albers': (0.93, 0.92, 0.9), 'knr': (0.93, 0.92, 0.9)}[key], rough=0.5))
    bx('p_livre_plat', (W, Ht, b), (0, 0, b / 2), plain, bev=0.0008 if hard else 0.0002)
    bx('p_livre_plat', (W, Ht, b), (0, 0, T - b / 2), plain, bev=0.0008 if hard else 0.0002)
    bx('p_livre_pages', (W - o - 0.002, Ht - 2 * o - 0.002, T - 2 * b), (o / 2 + 0.001, 0, T / 2), MP['pages'], bev=0.0003)
    bx('p_livre_dos', (b, Ht, T), (-W / 2 + b / 2, 0, T / 2), plain, bev=0.0006 if hard else 0.0002)
    e = 0.0002
    quad('p_livre_couv', [(-W / 2, -Ht / 2, T + e), (W / 2, -Ht / 2, T + e), (W / 2, Ht / 2, T + e), (-W / 2, Ht / 2, T + e)],
         [(0, 0), (1, 0), (1, 1), (0, 1)], cov)
    quad('p_livre_tranche', [(-W / 2 - e, Ht / 2, 0), (-W / 2 - e, -Ht / 2, 0), (-W / 2 - e, -Ht / 2, T), (-W / 2 - e, Ht / 2, T)],
         [(0, 0), (1, 0), (1, 1), (0, 1)], spi)


def livres_lampe(F, x, y, h):
    """The three books (design and code classics, covers redrawn) the lamp stands on. Returns the top height (desk frame)."""
    mats_contenus()
    m_base()
    z = h
    for k, (key, W, Ht, T, hard) in enumerate(LIVRES):
        dx = (W - LIVRES[0][1]) / 2 + (0.004, -0.006, 0.008)[k]             # spines roughly aligned on the left
        dy = (-0.01, 0.012, -0.004)[k]
        rz = rad((-3.0, 2.5, -1.5)[k])
        _P(F, x + dx, y + dy, z, lambda key=key, W=W, Ht=Ht, T=T, hard=hard: livre(key, W, Ht, T, hard), rz)
        z += T
    if CH[0]:
        CH[0].footprint(x, y, 0.0, 0.22, 0.31, z)
    return z


# ------------------------------------------------------------------ the M layout (mix of B en cours and C foisonnant)
def papiers_bureau(F, h=0.74, hr=0.64, k=None):
    k = k or PAPIERS[0]
    if k != 'M':
        return
    mats_contenus()
    m_base()
    CH[0] = Champ(h, hr)
    RP.seed(31)
    # under the lamp: the Ombelle homepage printout annotated in red, the mobile screens behind, the speaker sketch on
    # tracing paper taped over it, a photo print, a post-it
    drape(F, -0.6, 0.03, rad(4), A4[1], A4[0], m_print('ombelle-mobile-a4'), corner=0.004, wave=0.001)
    drape(F, -0.56, -0.17, rad(6), A3[0], A3[1], m_print('ombelle-accueil-a3'), wave=0.0012, curl=0.004, edge='S')
    calque(F, -0.5, -0.21, rad(-9), A4[0], A4[1], 'calque-enceinte', tapes=2)
    drape(F, -0.42, 0.07, rad(-10), 0.1, 0.13, m_print('tirage-ombelle-sauge', 0.25), corner=0.003)
    postit(F, -0.66, -0.31, rad(7), 'postit-jaune')
    # front right: the configurator code, folded in half, a pink post-it on it
    plie(F, 1.07, -0.3, rad(3), 'ombelle-code-a4')
    postit(F, 1.12, -0.33, rad(12), 'postit-rose', 0.003)
    # under the riser: the kraft folder with the quote sticking out, a clipped stack with the brand guidelines
    chemise(F, -0.63, 0.27, rad(84), 'halde-devis-a4', 0.045)
    pile(F, -0.32, 0.26, rad(97), A4[0], A4[1], 40, 'ombelle-charte-a4', clip=True)
    # the return, the plans table: plan A2 with the café variant on tracing paper taped over it, section, materials board,
    # site map, meeting notes, the week card, three rolls
    drape(F, 1.6, 0.08, rad(3), A2[1], A2[0], m_print('halde-plan-a2'), wave=0.0015)
    calque(F, 1.62, 0.07, rad(-4), A3[1], A3[0], 'calque-halde')
    drape(F, 2.12, 0.21, rad(5), A3[1], A3[0], m_print('halde-materiaux-a3'), wave=0.001)
    drape(F, 2.15, -0.02, rad(-8), A3[1], A3[0], m_print('halde-coupe-a3'), wave=0.001, corner=0.005)
    drape(F, 1.5, -0.04, rad(2), A3[1], A3[0], m_print('halde-sitemap-a3'), wave=0.001)
    drape(F, 1.42, -0.03, rad(18), A4[0], A4[1], m_print('notes-halde'), corner=0.006, curl=0.004, edge='S')
    drape(F, 2.24, -0.11, rad(14), 0.148, 0.105, m_print('fiche-semaine'), corner=0.004)
    zr = CH[0].footprint(1.62, 0.333, rad(1), 0.62, 0.13)
    for i, (yy, dz, r) in enumerate(((0.3, 0.0, 0.03), (0.365, 0.0, 0.03), (0.333, 0.052, 0.028))):
        rouleau(F, 1.62 + 0.03 * i, yy, rad(2 - 3 * i), 0.6 - 0.05 * (i % 2), r, z=zr + dz)
    # two photo prints taped on the outer face of the left riser leg, one above the other (never overlapping)
    for name, yy, zz, rzz in (('tirage-halde-maquette', 0.268, 0.952, 1.2), ('tirage-ombelle-trio', 0.278, 0.852, -1.0)):
        _P(F, -0.8525, yy, zz, lambda name=name: _tirage_vertical(name), rad(-90) + rad(rzz), rx=rad(90))


def _tirage_vertical(name):
    """A 13 x 8.7 cm print flat against a vertical face (built facing +z, turned by the caller), two black tapes on top."""
    w, d = 0.13, 0.087
    grid_mesh('p_tirage', w, d, [[0.0004] * 7 for _ in range(7)], m_print(name, 0.25), 6, 6)
    grid_mesh('p_dos', w, d, [[0.00025] * 7 for _ in range(7)], m_base(), 6, 6)
    for sx in (-1, 1):
        bx('p_scotch', (0.03, 0.019, 0.0003), (sx * 0.058, d / 2 - 0.004, 0.0007), MC['tape'], rot=(0, 0, sx * 0.2), bev=0)


# ------------------------------------------------------------------ studio prototypes
SHOT_PA = {
    'ensemble': dict(cam=(-2.45, -3.35, 1.85), target=(0.72, 0.1, 0.62), lens=30, fstop=11, focus=None),
    'dessus': dict(cam=(0.62, -0.42, 3.55), target=(0.62, 0.02, 0.7), lens=24, fstop=11, focus=None),
    'lampe': dict(cam=(-1.0, -1.15, 1.32), target=(-0.5, -0.06, 0.76), lens=35, fstop=5.6, focus=None),
    'retour': dict(cam=(1.15, -1.25, 1.42), target=(1.82, 0.1, 0.66), lens=32, fstop=6.3, focus=None),
    'poste': dict(cam=(-1.75, -2.3, 1.62), target=(0.12, 0.12, 0.98), lens=30, fstop=8, focus=None),
    'livres': dict(cam=(-1.55, -0.42, 0.98), target=(-0.97, 0.13, 0.79), lens=55, fstop=4, focus=None),
}


def main_papiers():
    build_bureau_complet()
    keys = OPT.get('pistes', 'M').split(',')
    colls = {}
    for k in keys:
        c = coll('P_' + k)
        CUR[0] = c
        papiers_bureau(_F0, H0, H1, k)
        colls[k] = c
    os.makedirs(OUT, exist_ok=True)
    if OPT.get('save') == '1':
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'papiers.blend'))
    for k in keys:
        for k2, c in colls.items():
            c.hide_render = k2 != k
        for v in OPT.get('vues', 'ensemble,dessus,lampe,retour,poste,livres').split(','):
            SC.camera = make_camera(dict(SHOT_PA[v]), f'CAM_{k}_{v}')
            SC.render.resolution_x = RES
            SC.render.resolution_y = int(RES * 9 / 16)
            SC.render.filepath = os.path.join(OUT, f'{k}-{v}.png')
            print('RENDER', SC.render.filepath, flush=True)
            bpy.ops.render.render(write_still=True)


main_papiers()
