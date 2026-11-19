# ================================================================== the cables of the desk corner (step 11, B retained 17/11)
# What is plugged in (the user's list): the desk lamp, the two screens (each one: its power and a USB-C cable to the Mac
# Studio), the Mac Studio's power, and the white table fan of the decor. The MacBook has no cable. Everything goes to a
# black power strip (French sockets, earth pins) under the desk, which can be glimpsed; its own cable leaves behind the
# desk, runs along the floor and disappears behind the cabinet of the return (it is never plugged into a wall).
# Common route: the screens' cables leave from ports under the back of each screen, are clipped under the arm, go round
# the pole (through a grommet in the riser), down the pole in a velcro-tied bundle; the two power cables go over the
# back edge on both sides of the clamp, the two USB-C cables run along the desk top behind the riser to the Mac Studio's
# Thunderbolt ports. The Mac Studio's power cable drops behind the desk. Under the top, everything lies in the cable
# tray of desk D; the lamp's cable comes off the books, over the back edge, along the apron (adhesive clips) to the tray.
# Retained 17/11: B "le long du pied": the cables leave the tray at its right end and go down the back right leg in one
# row (velcro straps); the strip lies on the floor beside the leg, behind the bin. (A au sol and C sur le caisson went
# to the Trash.) Option cables=aucun brings back the old placeholders.
# The fan's cable, retained 17/11 "par le bureau", white: down the cartons, a short way on the floor to the back left leg,
# up its inner face (two velcros), clipped under the back apron beside the lamp's cable, through the tray and down the
# right leg with the others to the strip. (The first version along the floor behind the whole desk, a floor box and a
# battery fan went to the Trash.)
# Every point is computed in the desk frame from the real objects (ports of the Mac Studio, bottom of the screens'
# backs, arm segments, pole, lamp's old cable, fan instance), so the same code works in the studio and in the lab.
# verif=1 runs a collision check: every cable against every surface nearby (BVH, ray casts along the centre line) and
# against the other cables; it prints CABLE CROISE lines.
CABLES = [OPT.get('cables', 'B')]
PISTES_CB = ('B',)
MCB = {}
CB = []          # (name, desk-frame points, radius) of every cable built, for the checks
CB_OBJS = []     # every object built here (cables, connectors, strip, clips), excluded from the scene's BVH
CB_LU = {}       # what was read from the scene (ports, anchors), once
R_ALIM, R_USBC, R_LAMPE, R_VENT, R_SECT = 0.0035, 0.0024, 0.0021, 0.0027, 0.004      # power, USB-C, lamp, fan, strip mains (radius)
ZT, YE = 0.74, 0.4                     # desk top, back edge (desk frame)
EPS = 0.001                            # clearance kept between a cable and the surface it rests on or hugs
APRON = (0.345, 0.375, 0.656)          # back apron: y from, y to, underside
TRAY = (-0.45, 0.95, 0.18, 0.32, 0.596)  # cable tray: x from, x to, y from, y to, top of its bottom


def m_cables():
    if MCB:
        return MCB
    MCB['noir'] = m_surface('cb_gaine_noire', (0.013, 0.013, 0.015), rough=0.42, var=0.015, grain=2400, bump=0.0015)
    MCB['blanc'] = m_surface('cb_gaine_blanche', (0.78, 0.78, 0.76), rough=0.4, var=0.012, grain=2400, bump=0.0015)
    MCB['plast'] = mat_color('cb_plastique', (0.02, 0.02, 0.022), rough=0.46)
    MCB['plast_b'] = mat_color('cb_plastique_blanc', (0.8, 0.8, 0.78), rough=0.38)
    MCB['alu'] = mat_color('cb_alu', (0.72, 0.72, 0.74), rough=0.24, metal=1.0)
    MCB['metal'] = mat_color('cb_metal', (0.75, 0.75, 0.76), rough=0.3, metal=1.0)
    MCB['mp'] = mat_color('cb_multiprise', (0.016, 0.016, 0.018), rough=0.34)
    MCB['fond'] = mat_color('cb_fond', (0.004, 0.004, 0.004), rough=0.7)
    MCB['velcro'] = m_surface('cb_velcro', (0.02, 0.02, 0.021), rough=0.95, var=0.02, grain=3000, bump=0.004)
    MCB['inter'] = mat_color('cb_interrupteur', (0.06, 0.06, 0.065), rough=0.3)
    # braided sleeve: black PET, a woven relief from two crossing diagonal wave textures (object coordinates)
    m = new_mat('cb_tresse')
    nt = m.node_tree
    p = principled(m)
    p.inputs['Base Color'].default_value = (0.017, 0.017, 0.019, 1)
    p.inputs['Roughness'].default_value = 0.55
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mul = nt.nodes.new('ShaderNodeMath')
    mul.operation = 'MULTIPLY'
    for k, ang in enumerate((0.7, -0.7)):
        mp = nt.nodes.new('ShaderNodeMapping')
        mp.inputs['Rotation'].default_value = (ang, 0.0, ang * 0.6)
        w = nt.nodes.new('ShaderNodeTexWave')
        w.wave_type = 'BANDS'
        w.inputs['Scale'].default_value = 260.0
        w.inputs['Distortion'].default_value = 0.0
        nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
        nt.links.new(mp.outputs['Vector'], w.inputs['Vector'])
        nt.links.new(w.outputs['Fac'], mul.inputs[k])
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.6
    bump.inputs['Distance'].default_value = 0.0006
    nt.links.new(mul.outputs[0], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], p.inputs['Normal'])
    MCB['tresse'] = m
    return MCB


# ------------------------------------------------------------------ desk frame <-> world
def _W(F, p):
    return Vector(F.p(p[0], p[1], p[2]))


def _Wd(F, d):
    c, s = math.cos(F.r), math.sin(F.r)
    return Vector((d[0] * c - d[1] * s, d[0] * s + d[1] * c, d[2]))


def _D(F, w):
    w = Vector(w) - Vector(F.o)
    c, s = math.cos(-F.r), math.sin(-F.r)
    return Vector((w.x * c - w.y * s, w.x * s + w.y * c, w.z))


def _Dd(F, d):
    c, s = math.cos(-F.r), math.sin(-F.r)
    return Vector((d[0] * c - d[1] * s, d[0] * s + d[1] * c, d[2]))


# ------------------------------------------------------------------ slack: cables lying on a surface are never ruler-straight
# Where a cable rests flat (desk top, floor, tray), a gentle meander is added across it, in the horizontal plane, ramped
# in and out over 6 cm. Zones where it must stay put (clips, lanes, narrow gaps, beside the legs) limit the amplitude,
# with a soft 6 cm transition.
ZONES_SOUPLE = [   # desk frame box (x0, x1, y0, y1, z0, z1) and the largest meander allowed in it
    ((-0.47, 0.97, 0.17, 0.33, 0.55, 0.63), 0.003),          # the cable tray: lanes 2 cm apart
    ((-1.2, 1.2, 0.33, 0.41, 0.63, 0.67), 0.0),              # clipped under the back apron
    ((-1.0, 1.5, -0.5, 0.6, 0.95, 1.5), 0.0),                # under the arm
    ((0.12, 0.62, 0.28, 0.42, 0.735, 0.77), 0.003),          # the USB-C lanes behind the riser
    ((-1.25, -0.6, 0.28, 0.37, -0.01, 0.03), 0.004),         # behind the left pedestal, between it and the leg
    ((1.05, 1.32, 0.28, 0.43, -0.01, 0.03), 0.004),          # beside the back right leg and the return's leg
    ((0.9, 1.05, -0.02, 0.42, -0.01, 0.03), 0.004),          # round the strip
    ((-1.2, -1.13, 0.33, 0.38, -0.01, 0.7), 0.0),            # the fan's cable round the back left leg and up it
]


def _amp_max(p, amp):
    a = amp
    for (x0, x1, y0, y1, z0, z1), za in ZONES_SOUPLE:
        if not (z0 <= p.z <= z1):
            continue
        dx = max(x0 - p.x, 0.0, p.x - x1)
        dy = max(y0 - p.y, 0.0, p.y - y1)
        d = math.hypot(dx, dy)
        t = min(1.0, d / 0.06)
        t = t * t * (3 - 2 * t)
        a = min(a, za + (amp - za) * t)
    return a


def _assouplir(dense, amp, lam=0.34, phase=0.0):
    """Meander on the flat stretches of a dense path (slope under 4 %, at least 8 cm long)."""
    if amp <= 0 or len(dense) < 3:
        return dense
    P = [Vector(p) for p in dense]
    n = len(P)
    flat = [False] * n
    for i in range(1, n - 1):
        d = P[i + 1] - P[i - 1]
        h = math.hypot(d.x, d.y)
        flat[i] = h > 1e-6 and abs(d.z) / h < 0.04
    out = list(P)
    i = 0
    while i < n:
        if not flat[i]:
            i += 1
            continue
        j = i
        while j < n and flat[j]:
            j += 1
        S = [0.0]
        for k in range(i + 1, j):
            S.append(S[-1] + (P[k] - P[k - 1]).length)
        L = S[-1]
        if L >= 0.08:
            for k in range(i, j):
                sk = S[k - i]
                env = min(1.0, sk / 0.06, (L - sk) / 0.06)
                env = env * env * (3 - 2 * env)
                d = P[min(k + 1, n - 1)] - P[max(k - 1, 0)]
                nrm = Vector((-d.y, d.x, 0.0))
                if nrm.length < 1e-9:
                    continue
                nrm.normalize()
                w = 0.65 * math.sin(2 * math.pi * sk / lam + phase) + 0.35 * math.sin(2 * math.pi * sk / (0.47 * lam) + 2.1 * phase)
                out[k] = P[k] + nrm * (_amp_max(P[k], amp) * env * w)
        i = j
    return out


# ------------------------------------------------------------------ cables
def _cr(pts, step=0.003):
    """Smooth path through the points: cubic Hermite segments whose tangents follow the neighbours (Catmull-Rom
    directions) but are never longer than the shorter of the two adjacent segments, so a short segment next to a long
    one cannot overshoot into the surface the cable rests on. Sampled about every step metres."""
    P = [Vector(p) for p in pts]
    n = len(P)
    L = [(P[i + 1] - P[i]).length for i in range(n - 1)]
    D = []
    for i in range(n):
        a = P[i - 1] if i > 0 else P[i]
        b = P[i + 1] if i < n - 1 else P[i]
        d = b - a
        D.append(d.normalized() if d.length > 1e-9 else Vector((0, 0, 0)))
    out = []
    for i in range(n - 1):
        li = L[i]
        if li < 1e-9:
            continue
        m0 = D[i] * min(li, L[i - 1] if i > 0 else li)
        m1 = D[i + 1] * min(li, L[i + 1] if i + 1 < n - 1 else li)
        k = max(2, int(li / step))
        for j in range(k):
            t = j / k
            t2, t3 = t * t, t * t * t
            out.append((2 * t3 - 3 * t2 + 1) * P[i] + (t3 - 2 * t2 + t) * m0 + (-2 * t3 + 3 * t2) * P[i + 1] + (t3 - t2) * m1)
    out.append(P[-1])
    return out


SOUPLE = {'cb_lampe': 0.012, 'cb_ventilo': 0.022, 'cb_multiprise_secteur': 0.02}   # meander on flat stretches (m)


def cable(F, name, pts, r, mat, caps=True):
    """A cable through the desk-frame points (dense bounded Hermite), round section of radius r, with some slack where
    it lies flat (SOUPLE, default 4 mm)."""
    dense = _cr(pts)
    dense = _assouplir(dense, SOUPLE.get(name, 0.004), phase=(sum(map(ord, name)) % 17) * 0.37)
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = r
    cu.bevel_resolution = 4
    cu.use_fill_caps = caps
    sp = cu.splines.new('POLY')
    sp.points.add(len(dense) - 1)
    for k, p in enumerate(dense):
        w = _W(F, p)
        sp.points[k].co = (w.x, w.y, w.z, 1.0)
    cu.materials.append(mat)
    o = link(bpy.data.objects.new(name, cu))
    CB.append((name, dense, r))
    CB_OBJS.append(o)
    return o


# ------------------------------------------------------------------ connectors (built along local +z = the cable's way out)
def _rrect(w, h, r, seg=4):
    r = min(r, w / 2 - 1e-5, h / 2 - 1e-5)
    pts = []
    for cx, cy, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        for k in range(seg + 1):
            a = math.radians(a0 + 90 * k / seg)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def _circ(r, n=20):
    return [(r * math.cos(2 * math.pi * k / n), r * math.sin(2 * math.pi * k / n)) for k in range(n)]


class Piece:
    """A connector or a small part: lofted rings in its own frame, one object."""

    def __init__(self):
        self.bm = bmesh.new()
        self.mats = []

    def _mi(self, m):
        if m not in self.mats:
            self.mats.append(m)
        return self.mats.index(m)

    def loft(self, rings, mat, cap0=True, cap1=True, smooth=True):
        """rings: [(profile, z, sx, sy)] with the same point count; bridged in order and capped."""
        mi = self._mi(mat)
        vs = [[self.bm.verts.new((x * sx, y * sy, z)) for x, y in prof] for prof, z, sx, sy in rings]
        n = len(vs[0])
        for a, b in zip(vs[:-1], vs[1:]):
            for i in range(n):
                f = self.bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
                f.material_index = mi
                f.smooth = smooth
        for ring, ok, rev in ((vs[0], cap0, True), (vs[-1], cap1, False)):
            if ok:
                f = self.bm.faces.new(list(reversed(ring)) if rev else ring)
                f.material_index = mi

    def relief(self, z0, z1, r0, r1, mat, grooves=3):
        """Strain relief: a tapered sleeve with shallow grooves, from radius r0 at z0 to r1 at z1."""
        c = _circ(1.0, 20)
        rings = []
        n = 4 * grooves + 2
        for k in range(n + 1):
            t = k / n
            r = r0 + (r1 - r0) * t
            if 0 < k < n and k % 4 == 2:
                r *= 0.9
            rings.append((c, z0 + (z1 - z0) * t, r, r))
        self.loft(rings, mat)

    def obj(self, name, M):
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces)
        me = bpy.data.meshes.new(name)
        self.bm.to_mesh(me)
        self.bm.free()
        for m in self.mats:
            me.materials.append(m)
        o = link(bpy.data.objects.new(name, me))
        o.matrix_world = M
        CB_OBJS.append(o)
        return o


def _cb_frame(F, origin, zdir, xdir):
    """World matrix of a connector: origin and axes given in the desk frame."""
    z = _Wd(F, zdir).normalized()
    x = _Wd(F, xdir)
    x = (x - z * x.dot(z)).normalized()
    y = z.cross(x)
    o = _W(F, origin)
    return Matrix(((x.x, y.x, z.x, o.x), (x.y, y.y, z.y, o.y), (x.z, y.z, z.z, o.z), (0, 0, 0, 1)))


def usb_c(F, name, origin, zdir, xdir, M_=None):
    """USB-C plug: steel shell in the port, black overmold, strain relief; returns the length out of the port."""
    M_ = M_ or m_cables()
    p = Piece()
    sh = _rrect(0.0083, 0.0025, 0.00124, 3)
    p.loft([(sh, -0.006, 1, 1), (sh, 0.0006, 1, 1)], M_['metal'])
    body = _rrect(0.0118, 0.0064, 0.0024, 4)
    p.loft([(body, 0.0005, 1, 1), (body, 0.0015, 1.02, 1.04), (body, 0.015, 0.97, 0.98), (body, 0.0175, 0.88, 0.9)], M_['plast'])
    p.relief(0.0172, 0.027, 0.0031, 0.0027, M_['plast'], grooves=2)
    p.obj(name, _cb_frame(F, origin, zdir, xdir))
    return 0.027


def c13(F, name, origin, zdir, xdir):
    """IEC C13 connector (screen power), black, with its strain relief; returns the length out of the inlet."""
    M_ = m_cables()
    p = Piece()
    body = _rrect(0.0225, 0.0155, 0.0035, 4)
    p.loft([(body, 0.0, 1, 1), (body, 0.002, 1.015, 1.02), (body, 0.028, 0.95, 0.95), (body, 0.034, 0.7, 0.72)], M_['plast'])
    p.relief(0.033, 0.05, 0.0058, 0.0041, M_['plast'], grooves=3)
    p.obj(name, _cb_frame(F, origin, zdir, xdir))
    return 0.05


def fiche_mac(F, name, origin, zdir, xdir):
    """The Mac Studio's round power plug; returns its length."""
    M_ = m_cables()
    p = Piece()
    c = _circ(1.0, 28)
    p.loft([(c, -0.004, 0.0062, 0.0062), (c, 0.0, 0.0062, 0.0062), (c, 0.0004, 0.0074, 0.0074), (c, 0.015, 0.0072, 0.0072),
            (c, 0.0175, 0.0058, 0.0058)], M_['plast'])
    p.relief(0.017, 0.03, 0.0052, 0.004, M_['plast'], grooves=2)
    p.obj(name, _cb_frame(F, origin, zdir, xdir))
    return 0.03


def fiche_fr(F, name, origin, zdir, xdir, mat=None):
    """French plug (type E, earth hole), round: the part inside the socket's recess, a flattened grip, the relief.
    origin: the socket's face; returns the length above it."""
    M_ = m_cables()
    mat = mat or M_['plast']
    p = Piece()
    c = _circ(1.0, 32)
    p.loft([(c, -0.0155, 0.0181, 0.0181), (c, 0.0, 0.0181, 0.0181), (c, 0.0012, 0.0186, 0.0186), (c, 0.004, 0.0186, 0.0186),
            (c, 0.012, 0.0178, 0.0128), (c, 0.026, 0.0166, 0.0118), (c, 0.034, 0.0118, 0.0092), (c, 0.039, 0.0068, 0.0066)], mat)
    p.relief(0.0385, 0.056, 0.0058, 0.0041, mat, grooves=3)
    p.obj(name, _cb_frame(F, origin, zdir, xdir))
    return 0.056


def europlug(F, name, origin, zdir, xdir, mat=None, r_out=0.0033):
    """Flat two-pin plug (lamp, fan): flat body in the socket's recess, tapered grip, relief; returns its length."""
    M_ = m_cables()
    mat = mat or M_['plast']
    p = Piece()
    b = _rrect(0.034, 0.0135, 0.0055, 4)
    p.loft([(b, -0.0145, 1, 1), (b, 0.0, 1, 1), (b, 0.0012, 1.02, 1.05), (b, 0.014, 0.9, 1.0), (b, 0.02, 0.42, 0.62)], mat)
    p.relief(0.0195, 0.034, 0.0046, r_out + 0.0004, mat, grooves=3)
    p.obj(name, _cb_frame(F, origin, zdir, xdir))
    return 0.034


def manchon(F, name, origin, zdir, xdir, r, length=0.012, mat=None):
    """A strain relief where a cable leaves a device (lamp base, fan foot)."""
    M_ = m_cables()
    p = Piece()
    p.relief(-0.003, length, r + 0.0022, r + 0.0006, mat or M_['plast'], grooves=2)
    p.obj(name, _cb_frame(F, origin, zdir, xdir))
    return length


# ------------------------------------------------------------------ the power strip (French sockets, black)
N_PRISES, PAS_PRISE, L_MP, W_MP, H_MP = 6, 0.047, 0.32, 0.056, 0.04


def multiprise(F, origin, zdir, xdir, name='cb_multiprise'):
    """Six French sockets in a line along local x, facing local +z; origin at the centre of the back face (the face
    that rests on the floor or on the pedestal). Switch at -x, mains cable leaving at +x. Returns the world matrix and
    the socket centres (local)."""
    M_ = m_cables()
    Mw = _cb_frame(F, origin, zdir, xdir)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * L_MP, v.co.y * W_MP, v.co.z * H_MP + H_MP / 2 + 0.002))
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.007, segments=4, affect='EDGES')
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(M_['mp'])
    for f in me.polygons:
        f.use_smooth = True
    body = link(bpy.data.objects.new(name, me))
    body.matrix_world = Mw
    xs = [-L_MP / 2 + 0.058 + i * PAS_PRISE for i in range(N_PRISES)]
    top = H_MP + 0.002
    # recesses: one cutter (six cylinders), boolean difference, applied through the evaluated mesh
    cb = bmesh.new()
    for x in xs:
        bmesh.ops.create_cone(cb, cap_ends=True, segments=40, radius1=0.0195, radius2=0.0195, depth=0.04,
                              matrix=Matrix.Translation((x, 0, top)))
    cme = bpy.data.meshes.new(name + '_cut')
    cb.to_mesh(cme)
    cb.free()
    cut = link(bpy.data.objects.new(name + '_cut', cme))
    cut.matrix_world = Mw @ Matrix.Translation((0, 0, 0.003))            # recess bottom 17 mm below the face
    mod = body.modifiers.new('prises', 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cut
    mod.solver = 'EXACT'
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me2 = bpy.data.meshes.new_from_object(body.evaluated_get(dg))
    body.modifiers.clear()
    body.data = me2
    bpy.data.objects.remove(cut)
    CB_OBJS.append(body)
    # inside each recess: the dark bottom, two holes, the earth pin; the switch; rubber feet; the cable's relief
    p = Piece()
    rb = top - 0.017
    for x in xs:
        p.loft([(_circ(0.0193, 32), rb + 0.0002, 1, 1), (_circ(0.0193, 32), rb + 0.0004, 1, 1)], M_['fond'], cap0=False)
        for sy in (-1, 1):
            p.loft([([(px + x, py + sy * 0.0095) for px, py in _circ(0.0026, 12)], rb + 0.0005, 1, 1),
                    ([(px + x, py + sy * 0.0095) for px, py in _circ(0.0026, 12)], rb + 0.0006, 1, 1)], M_['fond'], cap0=False)
        pin = [(px + x + 0.0, py) for px, py in _circ(0.0024, 12)]
        p.loft([([(px, py) for px, py in pin], rb + 0.0004, 1, 1), ([(px, py) for px, py in pin], rb + 0.0085, 1, 1)], M_['metal'])
    sx = -L_MP / 2 + 0.021
    sw = lambda w, h, r: [(x + sx, y) for x, y in _rrect(w, h, r)]
    p.loft([(sw(0.016, 0.026, 0.002), top - 0.001, 1, 1), (sw(0.016, 0.026, 0.002), top + 0.0012, 1, 1)], M_['plast'])
    p.loft([(sw(0.012, 0.021, 0.0015), top + 0.0012, 1, 1), (sw(0.012, 0.021, 0.0015), top + 0.0042, 1, 1)], M_['inter'])
    for fx in (-L_MP / 2 + 0.03, L_MP / 2 - 0.03):
        for fy in (-0.017, 0.017):
            p.loft([([(px + fx, py + fy) for px, py in _circ(0.006, 12)], 0.0, 1, 1),
                    ([(px + fx, py + fy) for px, py in _circ(0.006, 12)], 0.0021, 1, 1)], M_['plast'])
    p.obj(name + '_details', Mw)
    q = Piece()
    q.relief(0.0, 0.02, 0.0065, R_SECT + 0.0006, M_['mp'], grooves=3)
    q.obj(name + '_sortie', Mw @ Matrix.Translation((L_MP / 2 - 0.002, 0, 0.013)) @ Matrix.Rotation(math.pi / 2, 4, 'Y'))
    return Mw, [Vector((x, 0, top)) for x in xs]


def _mp_point(F, Mw, local):
    """A strip-local point in the desk frame."""
    return _D(F, Mw @ Vector(local))


def _mp_dir(F, Mw, local):
    return _Dd(F, (Mw.to_3x3() @ Vector(local)).normalized())


# ------------------------------------------------------------------ small parts: velcro ties, adhesive clips, grommet
def velcro_rect(F, name, centre, w, d, width=0.014):
    """A velcro strap round a flat bundle (or a leg and its bundle): a band round a w x d rounded rectangle (desk frame,
    horizontal)."""
    M_ = m_cables()
    p = Piece()
    a, b = _rrect(w, d, 0.004, 4), _rrect(w + 0.0032, d + 0.0032, 0.0056, 4)
    p.loft([(b, -width / 2, 1, 1), (b, width / 2, 1, 1)], M_['velcro'], cap0=False, cap1=False)
    p.loft([(a, width / 2, 1, 1), (a, -width / 2, 1, 1)], M_['velcro'], cap0=False, cap1=False)
    p.loft([(a, -width / 2, 1, 1), (b, -width / 2, 1, 1)], M_['velcro'], cap0=False, cap1=False)
    p.loft([(b, width / 2, 1, 1), (a, width / 2, 1, 1)], M_['velcro'], cap0=False, cap1=False)
    p.obj(name, _cb_frame(F, centre, (0, 0, 1), (1, 0, 0)))


def velcro(F, name, centre, axis, r_in, width=0.014):
    M_ = m_cables()
    p = Piece()
    c = _circ(1.0, 40)
    p.loft([(c, -width / 2, r_in + 0.0016, r_in + 0.0016), (c, width / 2, r_in + 0.0016, r_in + 0.0016)], M_['velcro'], cap0=False, cap1=False)
    p.loft([(c, width / 2, r_in, r_in), (c, -width / 2, r_in, r_in)], M_['velcro'], cap0=False, cap1=False)
    p.loft([(c, -width / 2, r_in, r_in), (c, -width / 2, r_in + 0.0016, r_in + 0.0016)], M_['velcro'], cap0=False, cap1=False)
    p.loft([(c, width / 2, r_in + 0.0016, r_in + 0.0016), (c, width / 2, r_in, r_in)], M_['velcro'], cap0=False, cap1=False)
    ax = Vector(axis).normalized()
    side = Vector((1, 0, 0)) if abs(ax.x) < 0.9 else Vector((0, 1, 0))
    p.obj(name, _cb_frame(F, centre, ax, side))


def clip(F, name, centre, along, up, r, surf, gap=0.0006):
    """Adhesive cable clip: a U around the cable (centre, radius r) up to the surface it is stuck on, at distance surf
    from the cable's centre along up; a thin pad on that surface."""
    M_ = m_cables()
    a = Vector(along).normalized()
    u = Vector(up).normalized()
    s = a.cross(u).normalized()
    t = 0.0013
    d = r + gap + t / 2
    lo_, hi_ = -d - t / 2, surf - 0.0011
    parts = [(Vector(centre) - u * d, (0.01, 2 * d + t, t)),                                   # the bridge under the cable
             (Vector(centre) + s * d + u * ((lo_ + hi_) / 2), (0.01, t, hi_ - lo_)),           # the two sides
             (Vector(centre) - s * d + u * ((lo_ + hi_) / 2), (0.01, t, hi_ - lo_)),
             (Vector(centre) + u * (surf - 0.00055), (0.013, 2 * d + t + 0.003, 0.001))]        # the adhesive pad
    p = Piece()
    for c, (lx, ly, lz) in parts:
        prof = [(-lx / 2, -ly / 2), (lx / 2, -ly / 2), (lx / 2, ly / 2), (-lx / 2, ly / 2)]
        p.loft([([(x, y) for x, y in prof], -lz / 2, 1, 1), ([(x, y) for x, y in prof], lz / 2, 1, 1)], M_['plast'], smooth=False)
        o = p.obj(name, _cb_frame(F, c, u, a))
        p = Piece()


# ------------------------------------------------------------------ reading the desk
def _o(name):
    return bpy.data.objects.get(name)


def _segment(F, name):
    """End points (desk frame, xy) of an arm segment: the extremes of its vertices along its main direction."""
    o = _o(name)
    pts = [_D(F, o.matrix_world @ v.co) for v in o.data.vertices]
    c = sum(pts, Vector()) / len(pts)
    sxx = sum((p.x - c.x) ** 2 for p in pts)
    syy = sum((p.y - c.y) ** 2 for p in pts)
    sxy = sum((p.x - c.x) * (p.y - c.y) for p in pts)
    ang = 0.5 * math.atan2(2 * sxy, sxx - syy)
    d = Vector((math.cos(ang), math.sin(ang), 0))
    ts = [(p - c).dot(d) for p in pts]
    return c + d * min(ts), c + d * max(ts), min(p.z for p in pts)


def lire_bureau(F):
    """Ports and anchors of the real objects, in the desk frame."""
    R = {}
    ms = _o('ms_body')
    M = ms.matrix_world
    back = _Dd(F, (M.to_3x3() @ Vector((0, 1, 0))).normalized())
    R['ms_back'] = back
    for k, x in (('tb1', -0.0652), ('tb3', -0.0466), ('msp', 0.0005)):
        R[k] = _D(F, M @ Vector((x * 10, 0.09765 * 10, 0.0271 * 10)))
    for side in ('left', 'right'):
        mb = _o(f'mon_back_{side}')
        Mm = mb.matrix_world
        vs = [Mm @ v.co for v in mb.data.vertices]
        zmin = min(v.z for v in vs)
        bot = [v for v in vs if v.z < zmin + 0.0015]
        c = sum(bot, Vector()) / len(bot)
        R[f'mon_{side}'] = dict(c=_D(F, c), rx=_Dd(F, (Mm.to_3x3() @ Vector((1, 0, 0))).normalized()),
                                bk=_Dd(F, (Mm.to_3x3() @ Vector((0, 0, -1))).normalized()))
        dos = []
        for n in (f'mon_back_{side}', f'mon_panel_{side}'):
            o = _o(n)
            if o:
                dos += [_D(F, o.matrix_world @ v.co) for v in o.data.vertices]
        R[f'mon_{side}']['dos'] = [v for v in dos if c.z - 0.08 < v.z + 0.0 < 1.25]
    lip = _o('D_riser_lip')
    cs = [_D(F, lip.matrix_world @ Vector(c)) for c in lip.bound_box] if lip else []
    R['lip_y'] = min((c.y for c in cs), default=0.149)
    R['lip_z'] = max((c.z for c in cs), default=1.065)
    for k in ('arm_seg0b', 'arm_seg0a', 'arm_seg1b', 'arm_seg1a'):
        R[k] = _segment(F, k)
    pole = _o('arm_pole')
    R['pole'] = _D(F, pole.matrix_world.translation)
    R['collar_z'] = min((_o('arm_collar0').matrix_world @ Vector(c)).z for c in _o('arm_collar0').bound_box)
    lc = _o('lpS_cable')
    if lc:
        sp = lc.data.splines[0]
        pts = [lc.matrix_world @ Vector(b.co) for b in sp.bezier_points]
        R['lamp_exit'] = _D(F, pts[0])
        u = _D(F, pts[1]) - _D(F, pts[0])
        u.z = 0
        R['lamp_dir'] = u.normalized()
    fan = _o('au_ventilo_table')
    if fan:
        R['fan'] = fan
        R['pile'] = fan.parent.parent if fan.parent else None
    return R


def nettoyer():
    """Removes the placeholders: the strip on the desk top and its cables, the MacBook cable, the lamp's cable, the
    lab's two floor cables."""
    names = set()
    for o in bpy.data.objects:
        if o.name.startswith(('pst_strip', 'pst_cable', 'pst_power', 'pst_mbp', 'lpS_cable', 'dk_cable', 'mon_cable')):
            names.add(o.name)
            names.update(c.name for c in o.children_recursive)
    for n in names:
        o = bpy.data.objects.get(n)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)
    return sorted(names)


def trou_rehausse(F, R):
    """A grommet in the riser's top sheet around the pole: the pole and the screens' cables go through it."""
    top = _o('D_riser_top')
    if not top:
        return
    M_ = m_cables()
    pc = R['pole']
    zt = max((top.matrix_world @ Vector(c)).z for c in top.bound_box)
    cb = bmesh.new()
    bmesh.ops.create_cone(cb, cap_ends=True, segments=48, radius1=0.031, radius2=0.031, depth=0.05)
    me = bpy.data.meshes.new('cb_trou')
    cb.to_mesh(me)
    cb.free()
    cut = link(bpy.data.objects.new('cb_trou', me))
    cut.matrix_world = Matrix.Translation(_W(F, (pc.x, pc.y, zt)))
    mod = top.modifiers.new('trou', 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cut
    mod.solver = 'EXACT'
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me2 = bpy.data.meshes.new_from_object(top.evaluated_get(dg))
    top.modifiers.clear()
    top.data = me2
    bpy.data.objects.remove(cut)
    p = Piece()
    c = _circ(1.0, 48)
    p.loft([(c, -0.012, 0.0285, 0.0285), (c, 0.0, 0.0285, 0.0285), (c, 0.0, 0.0305, 0.0305), (c, -0.012, 0.0305, 0.0305)], M_['plast'], cap0=False, cap1=False)
    p.loft([(c, 0.0, 0.0285, 0.0285), (c, 0.0028, 0.0285, 0.0285), (c, 0.0028, 0.0375, 0.0375), (c, 0.0, 0.0375, 0.0375)], M_['plast'], cap0=False, cap1=False)
    p.obj('cb_passe_cable', Matrix.Translation(_W(F, (pc.x, pc.y, zt))))


# ------------------------------------------------------------------ the routes
def _slot(pole, R_, th):
    """Point around the pole at angle th (degrees, from the back +y, clockwise towards +x)."""
    a = math.radians(th)
    return Vector((pole.x + R_ * math.sin(a), pole.y + R_ * math.cos(a), 0))


def routes_ecrans(F, R, M_):
    """The four cables of the screens, from their ports to the bottom of the pole; returns their lower ends
    (desk frame) and the arm's clip positions."""
    pole = R['pole']
    za = R['collar_z'] - 0.0045                      # under the collars and the arm's joints
    out = {}
    slots = {('left', 'pw'): -40, ('left', 'v'): -110, ('right', 'pw'): 40, ('right', 'v'): 100}
    for side, segb, sega, sgn in (('left', 'arm_seg0b', 'arm_seg0a', -1), ('right', 'arm_seg1b', 'arm_seg1a', 1)):
        m = R[f'mon_{side}']
        c, rx, bk = m['c'], m['rx'], m['bk']
        b0, b1, _ = R[segb]                          # b0/b1 sorted by the main axis: find the end at the screen
        if (b0 - c).length > (b1 - c).length:
            b0, b1 = b1, b0
        a0, a1, _ = R[sega]
        if (a0 - pole).length < (a1 - pole).length:
            a0, a1 = a1, a0                          # a0 at the joint, a1 at the pole
        for kind, off, r in (('pw', 0.03, R_ALIM), ('v', -0.006, R_USBC)):
            port = c + rx * (sgn * off)
            port.z = c.z
            if kind == 'pw':
                L = c13(F, f'cb_c13_{side}', port, (0, 0, -1), rx)
            else:
                L = usb_c(F, f'cb_usbc_ecran_{side}', port, (0, 0, -1), rx)
            # which side of the arm: power on the back side of both arms
            db = (b1 - b0).normalized()
            perp = Vector((-db.y, db.x, 0))
            if perp.y < 0:
                perp = -perp
            lat = (0.0042 if kind == 'pw' else -0.0042)
            da = (a1 - a0).normalized()
            perpa = Vector((-da.y, da.x, 0))
            if perpa.y < 0:
                perpa = -perpa
            s0 = port + Vector((0, 0, -L))
            # up the gap between the screen's back and the riser's lip, over the lip, under the arm
            yb = max((v.y for v in R[f'mon_{side}']['dos'] if abs(v.x - port.x) < 0.015), default=c.y + 0.04)
            yc = min(max((yb + R['lip_y']) / 2, yb + r + 0.002), R['lip_y'] - r - 0.002)
            q28 = b0 + (b1 - b0) * 0.28 + perp * lat
            pts = [s0, s0 + Vector((0, 0, -0.01)) + bk * 0.004, Vector((port.x, (s0.y + yc) / 2, c.z - 0.058)),
                   Vector((port.x, yc, c.z - 0.047)), Vector((port.x, yc, c.z)), Vector((port.x, yc, R['lip_z'] - 0.012)),
                   Vector((port.x + (q28.x - port.x) * 0.35, yc + 0.002, R['lip_z'] + r + 0.007))]
            for t in (0.28, 0.6, 0.9):
                q = b0 + (b1 - b0) * t + perp * lat
                pts.append(Vector((q.x, q.y, za)))
            for t in (0.15, 0.55):
                q = a0 + (a1 - a0) * t + perpa * lat
                pts.append(Vector((q.x, q.y, za)))
            # round the pole to the slot, then down
            th = slots[(side, kind)]
            Rs = 0.017 + r + 0.0005
            app = a1 - da * 0.03 + perpa * lat
            pts.append(Vector((app.x, app.y, za - 0.002)))
            th_in = math.degrees(math.atan2(app.x - pole.x, app.y - pole.y))
            steps = 4
            for k in range(1, steps + 1):
                t = k / steps
                q = _slot(pole, Rs, th_in + (th - th_in) * t)
                pts.append(Vector((q.x, q.y, za - 0.004 - 0.012 * t)))
            if (side, kind) == ('left', 'v'):           # the left screen's USB-C goes round the front of the pole
                for k, z in enumerate((1.0, 0.975, 0.95, 0.925, 0.9)):
                    q = _slot(pole, Rs, -110 - 30 * (k + 1) * 4 / 5)
                    pts.append(Vector((q.x, q.y, z)))
                th = -230
            q = _slot(pole, Rs, th)
            pts.append(Vector((q.x, q.y, 0.86)))
            pts.append(Vector((q.x, q.y, 0.8)))
            out[(side, kind)] = (pts, r, th, Rs)
    return out, za


def lanes_bas(R):
    """Lower part of the screens' cables, from the pole to the back edge (power) or along the desk top (USB-C)."""
    pole = R['pole']
    xl, xr = 0.0695 + (pole.x - 0.11), 0.1505 + (pole.x - 0.11)       # beside the clamp (70 mm wide, centred on the pole)
    low = {}
    for side, x, sgn in (('left', xl, -1), ('right', xr, 1)):
        q = _slot(pole, 0.017 + R_ALIM + 0.0005, -40 if side == 'left' else 40)
        low[(side, 'pw')] = [Vector((q.x, q.y, 0.79)), Vector(((q.x + x) / 2 + sgn * 0.002, 0.37, 0.766)),
                             Vector((x - sgn * 0.0045, 0.388, 0.7575)), Vector((x - sgn * 0.001, 0.396, 0.7495)),
                             Vector((x, 0.4005, ZT + R_ALIM + 0.0003)), Vector((x, 0.4055, ZT - 0.005)), Vector((x, 0.4068, 0.72)),
                             Vector((x, 0.4068, 0.70)), Vector((x, 0.405, 0.675)), Vector((x, 0.392, 0.659)),
                             Vector((x, 0.375, 0.6505)), Vector((x, 0.356, 0.646)), Vector((x, 0.338, 0.636)),
                             Vector((x, 0.322, 0.618)), Vector((x, 0.308, 0.603)), Vector((x, 0.297, TRAY[4] + R_ALIM + EPS))]
    for side, th, yy, ylane in (('right', 100, 0.3265, 0.392), ('left', -230, 0.3172, 0.382)):
        q = _slot(pole, 0.017 + R_USBC + 0.0005, th)
        y0 = q.y
        low[(side, 'v')] = [Vector((q.x, q.y, 0.79)), Vector((q.x + 0.004, y0 + 0.0005, 0.772)), Vector((pole.x + 0.028, y0 + 0.0015, 0.7585)),
                            Vector((pole.x + 0.0385, y0 + 0.003, 0.7537)), Vector((pole.x + 0.045, y0 + 0.0045, ZT + R_USBC + 0.0025)),
                            Vector((pole.x + 0.06, y0 + 0.007, ZT + R_USBC + EPS)), Vector((0.25, (y0 + ylane) / 2 - 0.012, ZT + R_USBC + EPS)),
                            Vector((0.35, ylane - 0.016, ZT + R_USBC + EPS)), Vector((0.43, ylane - 0.002, ZT + R_USBC + EPS))]
    return low


def route_mac(R):
    """The two USB-C cables at the Mac Studio's back (straight plugs, the cables bend left), and its power cable."""
    tb1, tb3, msp = R['tb1'], R['tb3'], R['msp']
    L = 0.027
    z = tb1.z
    v_left = [Vector((0.458, 0.383, ZT + R_USBC + EPS)), Vector((0.472, 0.388, ZT + R_USBC + 0.0012)), Vector((tb1.x - 0.0138, 0.3935, 0.749)),
              Vector((tb1.x - 0.0076, 0.3995, 0.7565)), Vector((tb1.x - 0.0023, 0.4012, 0.7635)), Vector((tb1.x, tb1.y + L + 0.0038, z - 0.0003)),
              Vector((tb1.x, tb1.y + L, z))]
    v_right = [Vector((0.455, 0.393, ZT + R_USBC + EPS)), Vector((0.468, 0.396, 0.7455)), Vector((tb1.x - 0.015, 0.402, 0.7515)),
               Vector((tb1.x - 0.0028, 0.4075, 0.7575)), Vector((tb3.x - 0.0114, 0.4075, 0.761)), Vector((tb3.x - 0.0029, 0.4045, 0.7645)),
               Vector((tb3.x, tb3.y + L + 0.0043, z - 0.0003)), Vector((tb3.x, tb3.y + L, z))]
    Lm = 0.03
    x = msp.x
    power = [Vector((x, msp.y + Lm, z)), Vector((x, 0.404, z - 0.0011)), Vector((x, 0.4085, 0.758)), Vector((x, 0.4105, 0.742)),
             Vector((x, 0.4095, 0.715)), Vector((x, 0.405, 0.675)), Vector((x, 0.392, 0.659)), Vector((x, 0.375, 0.6505)),
             Vector((x, 0.356, 0.646)), Vector((x, 0.338, 0.636)), Vector((x, 0.322, 0.618)), Vector((x, 0.308, 0.603)),
             Vector((x, 0.297, TRAY[4] + R_ALIM + EPS))]
    return v_left, v_right, power


def route_lampe(R):
    """From the lamp's base, off the books, on the desk to the back edge, down, along the apron to the tray's left end."""
    E, u = R['lamp_exit'], R['lamp_dir']
    s0 = E + u * 0.012
    zb = 0.793 + R_LAMPE + EPS
    pts = [s0, Vector((s0.x + u.x * 0.012, s0.y + u.y * 0.012, zb + 0.004)), Vector((-1.0785, 0.1695, zb)),
           Vector((-1.0832, 0.1715, zb - 0.0025)), Vector((-1.0868, 0.173, 0.7855)), Vector((-1.0905, 0.1748, 0.7812)),
           Vector((-1.0955, 0.1765, 0.7808)), Vector((-1.0985, 0.1772, 0.7765)), Vector((-1.0995, 0.178, 0.768)),
           Vector((-1.0995, 0.1792, 0.758)), Vector((-1.103, 0.1815, 0.7485)), Vector((-1.112, 0.188, ZT + R_LAMPE + EPS)),
           Vector((-1.128, 0.212, ZT + R_LAMPE + EPS)), Vector((-1.14, 0.26, ZT + R_LAMPE + EPS)), Vector((-1.142, 0.31, ZT + R_LAMPE + EPS)),
           Vector((-1.136, 0.355, ZT + R_LAMPE + EPS)), Vector((-1.131, 0.385, ZT + R_LAMPE + EPS)),
           Vector((-1.13, 0.3985, ZT + R_LAMPE + 0.0005)), Vector((-1.13, 0.4032, ZT - 0.002)), Vector((-1.13, 0.4045, 0.725)),
           Vector((-1.13, 0.4045, 0.70)), Vector((-1.129, 0.401, 0.676)), Vector((-1.127, 0.391, 0.6575)),
           Vector((-1.124, 0.382, APRON[2] - R_LAMPE - EPS - 0.0015)), Vector((-1.118, 0.37, APRON[2] - R_LAMPE - EPS)), Vector((-1.10, 0.362, APRON[2] - R_LAMPE - EPS - 0.001))]
    zc = APRON[2] - R_LAMPE - EPS                    # held by the clips, sagging a little between them
    for x, z in ((-1.05, zc - 0.004), (-1.0, zc), (-0.9, zc - 0.006), (-0.8, zc), (-0.7, zc - 0.006), (-0.6, zc), (-0.55, zc - 0.003)):
        pts.append(Vector((x, 0.36, z)))
    pts += [Vector((-0.5, 0.358, APRON[2] - R_LAMPE - 0.002)), Vector((-0.468, 0.345, 0.646)), Vector((-0.452, 0.327, 0.626)),
            Vector((-0.44, 0.308, 0.607)), Vector((-0.425, 0.285, TRAY[4] + R_LAMPE + EPS))]
    return pts


def route_ventilo(F, R):
    """From the fan's foot, over the top carton, down its side, onto the lower carton's ledge, down to the floor;
    returns the desk-frame points down to the floor and the fan's cable exit (origin, direction)."""
    fan, pile = R['fan'], R['pile']
    Mf = fan.matrix_world
    ex = _D(F, Mf @ Vector((0, 0.098, 0.011)))
    ed = _Dd(F, (Mf.to_3x3() @ Vector((0, 1, 0))).normalized())
    Mp = pile.matrix_world
    tc = lambda x, y, z: _D(F, Mp @ (Matrix.Translation((0.02, 0.01, 0.362)) @ Matrix.Rotation(rad(6), 4, 'Z') @ Vector((x, y, z))))
    lo = lambda x, y, z: _D(F, Mp @ Vector((x, y, z)))
    zt = 0.27 + 0.0007 + R_VENT + EPS                    # on the top carton (over the tape)
    s0 = ex + ed * 0.012
    rw = R_VENT + 0.0016                                  # round the edges at this distance from them
    pts = [s0, s0 + ed * 0.012 + Vector((0, 0, -0.011 + R_VENT + 0.001)), tc(-0.12, -0.105, zt), tc(-0.192, -0.097, zt),
           tc(-0.2 - rw * 0.71, -0.096, 0.27 + rw * 0.71), tc(-0.2 - rw, -0.095, 0.265), tc(-0.2 - rw, -0.095, 0.2),
           tc(-0.2 - rw, -0.095, 0.08), tc(-0.2 - rw, -0.096, 0.012), tc(-0.2 - rw, -0.096, 0.03), tc(-0.2 - rw - 0.002, -0.0965, -0.002 + R_VENT + EPS + 0.004),
           tc(-0.212, -0.097, -0.002 + R_VENT + EPS), tc(-0.235, -0.098, -0.002 + R_VENT + EPS)]
    pts += [lo(-0.244, -0.104, 0.36 + rw), lo(-0.25 - rw * 0.71, -0.105, 0.36 + rw * 0.71), lo(-0.25 - rw, -0.105, 0.354),
            lo(-0.25 - rw, -0.105, 0.2), lo(-0.25 - rw, -0.106, 0.04), lo(-0.25 - rw, -0.106, 0.016), lo(-0.25 - rw - 0.003, -0.106, R_VENT + EPS + 0.004), lo(-0.265, -0.106, R_VENT + EPS), lo(-0.29, -0.104, R_VENT + EPS)]
    return pts, ex, ed


# ------------------------------------------------------------------ the cables: tray, down the right leg, strip
def cables_bureau(F, h=0.74, hr=0.64, k=None):
    """Builds the desk's cables (desk frame F): B le long du pied, the fan's cable par le bureau."""
    k = k or CABLES[0]
    if k not in PISTES_CB:
        return []
    M_ = m_cables()
    if not CB_LU:                                    # read once per scene: the placeholders go, the riser gets its grommet
        CB_LU.update(lire_bureau(F))
        gone = nettoyer()
        print('CABLES retirés', len(gone), flush=True)
        trou_rehausse(F, CB_LU)
    R = CB_LU
    before = set(bpy.data.objects)
    ecr, za = routes_ecrans(F, R, M_)
    low = lanes_bas(R)
    v_left, v_right, mac_pw = route_mac(R)
    lampe = route_lampe(R)
    fan_pts, fan_ex, fan_ed = route_ventilo(F, R) if 'fan' in R else (None, None, None)
    # the Mac Studio's plugs
    usb_c(F, 'cb_usbc_mac_1', R['tb1'], R['ms_back'], (0, 0, 1))
    usb_c(F, 'cb_usbc_mac_3', R['tb3'], R['ms_back'], (0, 0, 1))
    fiche_mac(F, 'cb_fiche_mac', R['msp'], R['ms_back'], (0, 0, 1))
    # the lamp's and the fan's reliefs
    manchon(F, 'cb_manchon_lampe', R['lamp_exit'], R['lamp_dir'], (0, 0, 1), R_LAMPE)
    if fan_ex is not None:
        manchon(F, 'cb_manchon_ventilo', fan_ex, fan_ed, (0, 0, 1), R_VENT, mat=M_['plast_b'])
    # the screens' port panels (dark recess under each back)
    for side in ('left', 'right'):
        m = R[f'mon_{side}']
        sgn = -1 if side == 'left' else 1
        p = Piece()
        p.loft([(_rrect(0.068, 0.024, 0.004), -0.0004, 1, 1), (_rrect(0.068, 0.024, 0.004), 0.0, 1, 1)], M_['fond'])
        p.obj(f'cb_ports_{side}', _cb_frame(F, m['c'] + m['rx'] * (sgn * 0.012), (0, 0, -1), m['rx']))
    # B (retained 17/11): the power cables go right in the tray, out at its right end, down the back right leg in one row
    # (velcro straps round the leg), to the strip lying on the floor beside the leg, along the depth of the desk
    pole = R['pole']
    xl, xr = 0.0695 + (pole.x - 0.11), 0.1505 + (pole.x - 0.11)
    zl = lambda r: TRAY[4] + r + EPS
    mp_c = Vector((0.985, 0.19, 0))
    Mw, socks = multiprise(F, mp_c, (0, 0, 1), (0, 1, 0))
    sx = lambda i: _mp_point(F, Mw, socks[i])
    xc = 1.145 - R_ALIM - EPS                    # one row against the leg's inner face, in the order of the lanes
    lane = {'lamp': 0.21, 'monL': 0.23, 'monR': 0.25, 'mac': 0.27}
    col = {'lamp': 0.346, 'monL': 0.3535, 'monR': 0.3625, 'mac': 0.3715}
    sock = {'lamp': 1, 'monL': 2, 'monR': 3, 'mac': 4}
    zb = {'lamp': 0.205, 'monL': 0.188, 'monR': 0.168, 'mac': 0.15}           # the front one peels off first
    dz = {'lamp': 0.004, 'monL': 0.01, 'monR': 0.026, 'mac': 0.038}           # staggered heights where they meet
    if fan_pts:                                  # the fan's cable joins the row, between the lamp's and the screens'
        lane['fan'] = 0.22
        col.update(lamp=0.3395, fan=0.3455)
        sock.update(lamp=0, fan=1)
        zb['fan'], dz['fan'] = 0.196, 0.007

    def right(key, r, x_from, entry=True):
        yl = lane[key]
        cx, cy = xc, col[key]
        pts = []
        if entry:
            pts += [Vector((x_from + 0.012, yl + 0.02, zl(r))), Vector((x_from + 0.03, yl, zl(r)))]
        pts += [Vector((TRAY[1] - 0.04, yl, zl(r))), Vector((TRAY[1] - 0.005, yl + 0.002, zl(r))), Vector((TRAY[1] + 0.012, yl + 0.006, zl(r) - 0.0005)),
                Vector((TRAY[1] + 0.04, yl + 0.014, zl(r) - dz[key] * 0.5)),
                Vector((1.045, (yl + cy) / 2 + 0.012, zl(r) - dz[key] - 0.004)), Vector((1.095, cy, zl(r) - dz[key] - 0.009)),
                Vector((cx - 0.012, cy, zl(r) - dz[key] - 0.013)),
                Vector((cx, cy, zl(r) - dz[key] - 0.03)), Vector((cx, cy, 0.5)), Vector((cx, cy, 0.35)), Vector((cx, cy, zb[key] + 0.03)), Vector((cx, cy, zb[key]))]
        sp = sx(sock[key])
        lplug = 0.034 if key in ('lamp', 'fan') else 0.056
        top = sp + Vector((0, 0, lplug))
        pts += [Vector((cx - 0.012, cy, zb[key] - 0.016)), Vector((cx - 0.03, cy - 0.01 - (cy - sp.y) * 0.08, zb[key] - 0.035)),
                Vector(((cx + top.x) / 2 + 0.01, (cy + top.y) / 2, (zb[key] + top.z) / 2 - 0.005)),
                top + Vector((0.016, 0.0, 0.02)), top + Vector((0.003, 0.0, 0.008)), top]
        return pts, sp
    for key, side, x in (('monL', 'left', xl), ('monR', 'right', xr)):
        up, r, _, _ = ecr[(side, 'pw')]
        tail, sp = right(key, R_ALIM, x)
        cable(F, f'cb_ecran_{side}_alim', up + low[(side, 'pw')] + tail, R_ALIM, M_['noir'])
        fiche_fr(F, f'cb_fiche_{side}', sp, (0, 0, 1), (1, 0, 0))
    tail, sp = right('mac', R_ALIM, R['msp'].x)
    cable(F, 'cb_mac_alim', mac_pw + tail, R_ALIM, M_['noir'])
    fiche_fr(F, 'cb_fiche_mac_secteur', sp, (0, 0, 1), (1, 0, 0))
    tail, sp = right('lamp', R_LAMPE, TRAY[0] + 0.03, entry=False)
    cable(F, 'cb_lampe', lampe + [Vector((-0.39, lane['lamp'], zl(R_LAMPE)))] + tail, R_LAMPE, M_['noir'])
    europlug(F, 'cb_fiche_lampe', sp, (0, 0, 1), (1, 0, 0), r_out=R_LAMPE)
    if fan_pts:
        y_ = (0.3374 + 0.375) / 2
        for z in (0.5, 0.3):
            velcro_rect(F, 'cb_velcro_pied', Vector((1.156, y_, z)), 0.0415, 0.375 - 0.3374 + 0.0035)
    else:
        for z in (0.5, 0.3):
            velcro_rect(F, 'cb_velcro_pied', Vector((1.156, 0.36, z)), 0.0415, 0.0335)
    # the fan's cable
    z = R_VENT + EPS
    if fan_pts:                                  # up the back left leg, under the apron, through the tray, down the right leg
        xg, yg = -1.145 + R_VENT + EPS, 0.369    # on the leg's inner face; behind the lamp's cable under the apron
        zc = APRON[2] - R_VENT - EPS
        floor = [Vector((-1.86, 0.205, z)), Vector((-1.66, 0.275, z)), Vector((-1.45, 0.315, z)), Vector((-1.28, 0.333, z)),
                 Vector((-1.2, 0.3375, z)), Vector((-1.16, 0.3385, z)), Vector((xg - 0.0015, 0.3415, z)), Vector((xg, 0.35, z + 0.002)),
                 Vector((xg, 0.36, 0.014)), Vector((xg, 0.3665, 0.036)), Vector((xg, yg, 0.07))]
        leg = [Vector((xg, yg, 0.3)), Vector((xg, yg, 0.5)), Vector((xg, yg, 0.6)), Vector((xg + 0.004, yg, 0.627)), Vector((xg + 0.016, yg, 0.637)),
               Vector((-1.10, yg, 0.641)), Vector((-1.075, yg, 0.645)), Vector((-1.06, yg, zc))]
        apron = [Vector((x, yg, zz)) for x, zz in ((-0.98, zc - 0.006), (-0.9, zc), (-0.8, zc - 0.007), (-0.7, zc), (-0.6, zc - 0.007), (-0.5, zc),
                                                   (-0.43, zc - 0.004), (-0.39, zc - 0.0015))]
        xd = -0.36
        into = [Vector((xd - 0.008, yg - 0.003, 0.6505)), Vector((xd, 0.356, 0.646)), Vector((xd, 0.338, 0.636)), Vector((xd, 0.322, 0.618)),
                Vector((xd, 0.308, 0.603)), Vector((xd, 0.297, zl(R_VENT))), Vector((xd + 0.012, 0.26, zl(R_VENT))), Vector((xd + 0.03, 0.235, zl(R_VENT))),
                Vector((xd + 0.05, 0.2235, zl(R_VENT))), Vector((xd + 0.08, lane['fan'], zl(R_VENT)))]
        tail, sp = right('fan', R_VENT, None, entry=False)
        cable(F, 'cb_ventilo', fan_pts + floor + leg + apron + into + tail, R_VENT, M_['blanc'])
        europlug(F, 'cb_fiche_ventilo', sp, (0, 0, 1), (1, 0, 0), mat=M_['plast_b'], r_out=R_VENT)
        for zz in (0.45, 0.2):
            velcro_rect(F, 'cb_velcro_pied_gauche', Vector((-1.1568, 0.36, zz)), 0.0399, 0.0335)
        for x in (-1.06, -0.9, -0.7, -0.5):
            clip(F, 'cb_clip_ventilo', Vector((x, yg, zc)), (1, 0, 0), (0, 0, 1), R_VENT, R_VENT + 0.0006)
    # the strip's own cable: from its +y end, behind the leg, along the floor behind the return's cabinet
    s_ = _mp_point(F, Mw, (L_MP / 2 + 0.018, 0, 0.013))
    z = R_SECT + EPS
    cable(F, 'cb_multiprise_secteur', [s_, s_ + Vector((0, 0.012, -0.004)), Vector((s_.x + 0.004, s_.y + 0.035, z)), Vector((1.0, 0.43, z)),
                                       Vector((1.06, 0.45, z)), Vector((1.3, 0.455, z)), Vector((1.6, 0.455, z)), Vector((2.2, 0.45, z))], R_SECT, M_['noir'])
    # the screens' USB-C cables (common): down the pole, along the desk top, into the Mac Studio
    for side, tail in (('left', v_left), ('right', v_right)):
        up, r, _, _ = ecr[(side, 'v')]
        cable(F, f'cb_ecran_{side}_usbc', up + low[(side, 'v')] + tail, R_USBC, M_['noir'])
    # velcro ties round the pole bundle, clips under the arm and under the apron
    pc = R['pole']
    for z in (0.985, 0.87):
        velcro(F, 'cb_velcro', Vector((pc.x, pc.y, z)), (0, 0, 1), 0.017 + 2 * R_ALIM + 0.0012)
    for x in (-1.0, -0.8, -0.6):
        clip(F, 'cb_clip', Vector((x, 0.36, APRON[2] - R_LAMPE - EPS)), (1, 0, 0), (0, 0, 1), R_LAMPE, R_LAMPE + 0.0006)
    news = [o for o in bpy.data.objects if o not in before and o.parent is None]
    return news


# ------------------------------------------------------------------ checks
def verifier_cables(F, tol=0.0006):
    """Every cable against every surface nearby and against the other cables."""
    from mathutils.bvhtree import BVHTree
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    mine = {o.name for o in CB_OBJS}
    lo = _W(F, (-2.6, -1.6, -0.05))
    verts, polys, owner = [], [], []
    box_d = (Vector((-2.7, -1.6, -0.1)), Vector((2.6, 1.0, 1.5)))
    for inst in dg.object_instances:
        ob = inst.object
        if ob.type != 'MESH':
            continue
        name = (inst.parent.original.name + '/' if inst.is_instance and inst.parent else '') + ob.original.name
        if ob.original.name in mine or ob.original.name.startswith('cb_'):
            continue
        Mi = inst.matrix_world.copy()
        cs = [_D(F, Mi @ Vector(c)) for c in ob.bound_box]
        if (max(c.x for c in cs) < box_d[0].x or min(c.x for c in cs) > box_d[1].x or max(c.y for c in cs) < box_d[0].y or
                min(c.y for c in cs) > box_d[1].y or max(c.z for c in cs) < box_d[0].z or min(c.z for c in cs) > box_d[1].z):
            continue
        me = ob.to_mesh()
        base = len(verts)
        verts.extend(_D(F, Mi @ v.co) for v in me.vertices)
        for p in me.polygons:
            polys.append([base + i for i in p.vertices])
            owner.append(name)
        ob.to_mesh_clear()
    bvh = BVHTree.FromPolygons(verts, polys, epsilon=0.0)
    print('CABLES verif :', len(polys), 'faces autour du bureau', flush=True)
    bad = 0
    for name, pts, r in CB:
        hits = {}
        for i, p in enumerate(pts):
            loc, nrm, idx, d = bvh.find_nearest(p)
            if idx is not None and d < r - tol:
                hits.setdefault(owner[idx], [0, 0.0, p])
                hits[owner[idx]][0] += 1
                hits[owner[idx]][1] = max(hits[owner[idx]][1], r - d)
            if i:
                seg = p - pts[i - 1]
                if seg.length > 1e-7:
                    h = bvh.ray_cast(pts[i - 1], seg.normalized(), seg.length)
                    if h[0] is not None:
                        hits.setdefault(owner[h[2]], [0, 0.0, p])
                        hits[owner[h[2]]][0] += 1
                        hits[owner[h[2]]][1] = max(hits[owner[h[2]]][1], r)
        for o, (n, depth, p) in hits.items():
            bad += 1
            print('CABLE CROISE %-26s <> %-34s %3d pts, %.1f mm, vers (%.3f, %.3f, %.3f)' % (name, o[:34], n, depth * 1000, p.x, p.y, p.z), flush=True)
    for a in range(len(CB)):
        for b in range(a + 1, len(CB)):
            na, pa, ra = CB[a]
            nb, pb, rb = CB[b]
            worst, where, n = 0.0, None, 0
            for p in pa[::2]:
                for q in pb[::2]:
                    d = (p - q).length
                    if d < ra + rb - tol:
                        n += 1
                        if ra + rb - d > worst:
                            worst, where = ra + rb - d, p
            if n:
                bad += 1
                print('CABLE CROISE %-26s <> %-34s %3d pts, %.1f mm, vers (%.3f, %.3f, %.3f)' % (na, nb, n, worst * 1000, where.x, where.y, where.z), flush=True)
    print('CABLES verif terminée :', bad, 'problèmes', flush=True)
    return bad


# ------------------------------------------------------------------ studio renders of the prototypes
SHOT_CB = {
    'ensemble': dict(cam=(-2.45, -3.35, 1.85), target=(0.72, 0.1, 0.62), lens=30, fstop=11, focus=None),
    'dessous': dict(cam=(-0.55, -1.75, 0.42), target=(-0.02, 0.25, 0.28), lens=26, fstop=8, focus=None),
    'arriere': dict(cam=(0.75, 2.05, 1.3), target=(0.25, 0.38, 0.72), lens=28, fstop=11, focus=None),
    'bras': dict(cam=(0.45, 1.05, 1.32), target=(0.08, 0.26, 1.0), lens=32, fstop=8, focus=None),
    'mac': dict(cam=(0.78, 0.86, 0.93), target=(0.5, 0.38, 0.76), lens=45, fstop=5.6, focus=None),
    'lampe': dict(cam=(-1.62, 0.92, 1.02), target=(-1.1, 0.28, 0.72), lens=36, fstop=8, focus=None),
    'multiprise': dict(cam=(1.42, 1.05, 0.62), target=(1.02, 0.25, 0.16), lens=32, fstop=5.6, focus=None),
    'fil': dict(cam=(-3.15, 1.85, 1.45), target=(-1.55, 0.05, 0.42), lens=28, fstop=8, focus=None),        # the fan's cable, from behind left
}


def main_cables():
    os.makedirs(OUT, exist_ok=True)
    build_bureau_complet()
    papiers_bureau(_F0, H0, H1)
    objets_bureau(_F0, H0, H1)
    sol_bureau(_F0, H0, H1)
    autour_bureau(_F0, H0, H1)
    cables_bureau(_F0, H0, H1)
    if OPT.get('verif') == '1':
        verifier_cables(_F0)
    if OPT.get('rendu', '1') == '0':
        return
    for v in OPT.get('vues', 'ensemble,dessous,arriere,multiprise,fil,bras,mac,lampe').split(','):
        SC.camera = make_camera(dict(SHOT_CB[v]), f'CAM_{v}')
        SC.render.resolution_x = RES
        SC.render.resolution_y = int(RES * 9 / 16)
        SC.render.filepath = os.path.join(OUT, f'cables-{v}.png')
        print('RENDER', SC.render.filepath, flush=True)
        bpy.ops.render.render(write_still=True)


main_cables()
