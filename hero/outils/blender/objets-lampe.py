
# ================================================================== desk lamp: four current designs, modelled here
# A ressorts (balanced arm with springs, round base on the box pile), B pince (swing arm clamped on the riser),
# C tiges (thin tubes and tension wires, disc base), D LED (flat arms, horizontal LED bar).
# Studio prototypes: rendus-lampe.sh (main_lampe). In the lab: option lampe=A|B|C|D (desk_props_rest in labo3-v3.py).
# Built in world coordinates from desk-frame points (F.p); every light is named al_light_* so it joins the 'bureau' light group,
# emissive parts are named dk_* for the same reason.
from mathutils import Quaternion
LAMP_WARM = (1.0, 0.79, 0.56)


def materials_lampe():
    if 'lp_black' in M:
        return
    M['lp_black'] = m_surface('lp_black', (0.016, 0.016, 0.018), rough=0.42, var=0.05, grain=900, bump=0.008)
    M['lp_satin'] = m_surface('lp_satin', (0.018, 0.018, 0.02), rough=0.32, var=0.03, grain=1600, bump=0.004, metal=0.35)
    M['lp_spring'] = mat_color('lp_spring', (0.56, 0.57, 0.59), rough=0.24, metal=1.0)
    M['lp_wire'] = mat_color('lp_wire', (0.5, 0.5, 0.52), rough=0.3, metal=1.0)
    M['lp_knob'] = m_plastic('lp_knob', (0.012, 0.012, 0.013), rough=0.5)
    M['lp_inner'] = mat_color('lp_inner', (0.8, 0.78, 0.74), rough=0.55)
    M['lp_inner_alu'] = mat_color('lp_inner_alu', (0.72, 0.72, 0.73), rough=0.32, metal=1.0)
    M['lp_cable'] = mat_color('lp_cable', (0.012, 0.012, 0.013), rough=0.55)
    M['lp_rubber'] = mat_color('lp_rubber', (0.01, 0.01, 0.01), rough=0.85)
    for nm, strength in (('lp_bulb', 22.0), ('lp_led', 2.2)):
        m = new_mat(nm)
        p = principled(m)
        p.inputs['Base Color'].default_value = (1.0, 0.93, 0.82, 1)
        p.inputs['Emission Color'].default_value = (*LAMP_WARM, 1)
        p.inputs['Emission Strength'].default_value = strength
        M[nm] = m
    M['lp_paper'] = mat_color('lp_paper', (0.78, 0.77, 0.74), rough=0.8)


# ------------------------------------------------------------------ helpers
def _lathe(name, prof, mat, inner=None, thick=0.0, seg=48, sharp=()):
    """Surface of revolution around local +z of (r, z) points (ordered so that the outside is on the right).
    With thick: solidified inwards, inner shell in `inner`."""
    bm = bmesh.new()
    rings = []
    for r, z in prof:
        if r < 1e-6:
            rings.append([bm.verts.new((0.0, 0.0, z))])
        else:
            rings.append([bm.verts.new((r * math.cos(2 * math.pi * k / seg), r * math.sin(2 * math.pi * k / seg), z)) for k in range(seg)])
    for a, b in zip(rings, rings[1:]):
        if len(a) == 1 and len(b) == 1:
            continue
        for k in range(seg):
            k2 = (k + 1) % seg
            if len(a) == 1:
                f = bm.faces.new((a[0], b[k2], b[k]))
            elif len(b) == 1:
                f = bm.faces.new((a[k], a[k2], b[0]))
            else:
                f = bm.faces.new((a[k], a[k2], b[k2], b[k]))
            f.smooth = True
    for i in sharp:
        ring = set(rings[i])
        for e in bm.edges:
            if e.verts[0] in ring and e.verts[1] in ring:
                e.smooth = False
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    o = link(bpy.data.objects.new(name, me))
    if thick:
        me.materials.append(inner or mat)
        s = o.modifiers.new('solid', 'SOLIDIFY')
        s.thickness = thick
        s.offset = -1.0
        s.use_even_offset = True
        s.use_rim = True
        s.material_offset = 1
        s.material_offset_rim = 0
    return o


def _spring(name, a, b, coil_r, wire_r, turns, mat, hook=0.007):
    a, b = Vector(a), Vector(b)
    d = b - a
    L = d.length
    u = d / L
    q = u.to_track_quat('Z', 'Y')
    pts = [a, a + u * hook * 0.5]
    n = int(turns * 14)
    for i in range(n + 1):
        t = i / n
        ang = 2 * math.pi * turns * t
        pts.append(a + q @ Vector((coil_r * math.cos(ang), coil_r * math.sin(ang), hook + (L - 2 * hook) * t)))
    pts += [b - u * hook * 0.5, b]
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = wire_r
    cu.bevel_resolution = 2
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for p, v in zip(sp.points, pts):
        p.co = (v.x, v.y, v.z, 1.0)
    cu.materials.append(mat)
    return link(bpy.data.objects.new(name, cu))


def _axis_cyl(name, c, axis, r, length, mat, verts=24):
    c, axis = Vector(c), Vector(axis).normalized()
    return tube_between(name, c - axis * length / 2, c + axis * length / 2, r, mat, verts=verts)


def _bar(name, a, b, w, t, mat, bev=0.0015):
    """Flat bar from a to b: w across (horizontal), t in the arm plane."""
    a, b = Vector(a), Vector(b)
    d = b - a
    o = box(name, (w, t, d.length), (a + b) / 2, mat)
    o.rotation_euler = d.normalized().to_track_quat('Z', 'Y').to_euler()
    if bev:
        m = o.modifiers.new('bev', 'BEVEL')
        m.width = bev
        m.segments = 2
    for f in o.data.polygons:
        f.use_smooth = True
    return o


def _ik2(p0, p2, l1, l2):
    """Elbow of a two-link arm from p0 to p2 (lengths l1, l2), bent upwards in the vertical plane."""
    v = p2 - p0
    d = min(v.length, l1 + l2 - 1e-4)
    u = v.normalized()
    side = u.cross(Vector((0, 0, 1)))
    if side.length < 1e-6:
        side = Vector((1, 0, 0))
    side.normalize()
    perp = side.cross(u).normalized()
    if perp.z < 0:
        perp = -perp
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    hh = math.sqrt(max(l1 * l1 - a * a, 0.0))
    return p0 + u * a + perp * hh


def _frame(p0, hj):
    f = hj - p0
    f.z = 0
    f.normalize()
    side = Vector((f.y, -f.x, 0.0))
    return f, side


def _sphere(name, c, r, mat):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=r)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for f in me.polygons:
        f.use_smooth = True
    me.materials.append(mat)
    o = link(bpy.data.objects.new(name, me))
    o.location = c
    return o


def _shade(tag, mouth, d, prof, outer, inner, thick=0.0011, sharp=(0,)):
    """Shade whose mouth (profile z=0) is centred on `mouth`, opening along d."""
    o = _lathe(f'lp{tag}_shade', prof, outer, inner, thick, sharp=sharp)
    o.location = mouth
    o.rotation_euler = (-d).to_track_quat('Z', 'Y').to_euler()
    return o


def _light(tag, mouth, d, target, energy, inside=0.035, spot=84, size=0.025):
    pos = mouth - d * inside
    return add_light('SPOT', f'al_light_{tag}', pos, energy, LAMP_WARM, target=target, size=size, spot=spot, blend=0.55, c=CUR[0])


# ------------------------------------------------------------------ A : balanced arm with springs, round base
def lamp_A(b, hj, target, desk_z, energy=210):
    b, hj, target = Vector(b), Vector(hj), Vector(target)
    K = M['lp_black']
    _lathe('lpA_base', [(0, 0), (0.092, 0), (0.095, 0.003), (0.094, 0.01), (0.08, 0.02), (0.05, 0.03), (0.024, 0.036), (0, 0.037)], K, sharp=(1,)).location = b
    _lathe('lpA_foot', [(0, -0.001), (0.088, -0.001), (0.088, 0.0005), (0, 0.0005)], M['lp_rubber']).location = b
    cyl('lpA_turret', 0.016, 0.036, b + Vector((0, 0, 0.055)), K, verts=24)
    p0 = b + Vector((0, 0, 0.072))
    L1 = L2 = 0.32
    e = _ik2(p0, hj, L1, L2)
    f, side = _frame(p0, hj)
    for s in (-1, 1):
        o = side * 0.013 * s
        tube_between('lpA_arm', p0 + o, e + o, 0.0042, K, verts=10)
        tube_between('lpA_arm', e + o, hj + o, 0.0042, K, verts=10)
        box('lpA_yoke', (0.03, 0.004, 0.034), p0 + side * 0.019 * s + Vector((0, 0, -0.008)), K, rot=(0, 0, math.atan2(f.y, f.x)))
    # parallel link under the upper arm
    u2 = (hj - e).normalized()
    dn = side.cross(u2).normalized()
    if dn.z > 0:
        dn = -dn
    tube_between('lpA_link', e + dn * 0.03, hj + dn * 0.03, 0.0026, K, verts=8)
    tube_between('lpA_lever', e, e + dn * 0.032, 0.0035, K, verts=8)
    tube_between('lpA_lever', hj, hj + dn * 0.032, 0.0035, K, verts=8)
    # joints and knobs
    _axis_cyl('lpA_joint', p0, side, 0.009, 0.044, K)
    _axis_cyl('lpA_joint', e, side, 0.011, 0.034, K)
    _axis_cyl('lpA_joint', hj, side, 0.0095, 0.034, K)
    for s in (-1, 1):
        _axis_cyl('lpA_knob', e + side * 0.021 * s, side, 0.013, 0.008, M['lp_knob'])
        _axis_cyl('lpA_knob', p0 + side * 0.026 * s, side, 0.01, 0.007, M['lp_knob'])
    # springs between the turret and the lower arm
    for s in (-1, 1):
        tube_between('lpA_anchor', b + Vector((0, 0, 0.042)), b + Vector((0, 0, 0.042)) + side * 0.027 * s - f * 0.006, 0.0022, K, verts=8)
        _spring('lpA_spring', b + Vector((0, 0, 0.042)) + side * 0.027 * s - f * 0.006, p0 + (e - p0) * 0.36 + side * 0.027 * s, 0.0055, 0.0009, 18, M['lp_spring'])
    # head
    d = (target - hj).normalized()
    back = hj + d * 0.022
    tube_between('lpA_neck', hj, back, 0.007, K, verts=12)
    mouth = back + d * 0.154
    _shade('A', mouth, d, [(0.074, 0.0), (0.0735, 0.006), (0.07, 0.03), (0.06, 0.07), (0.046, 0.105), (0.032, 0.13), (0.024, 0.145), (0.016, 0.152), (0, 0.154)], K, M['lp_inner'])
    _sphere('dk_lampeA_bulb', mouth - d * 0.075, 0.026, M['lp_bulb'])
    _light('A', mouth, d, target, energy)
    dl = side.cross((e - p0).normalized()).normalized()
    if dl.dot(f) > 0:
        dl = -dl
    along = [back + dn * 0.012] + [hj + (e - hj) * t + dn * 0.012 - side * 0.006 for t in (0.3, 0.65, 0.95)]
    along += [p0 + (e - p0) * t + dl * 0.012 - side * 0.006 for t in (0.85, 0.5, 0.15)]
    _lamp_cable('lpA_cable', along + [b + Vector((0, 0, 0.03)) - f * 0.07, b - f * 0.11 + Vector((0, 0, 0.004))], b, f, desk_z)


def _lamp_cable(name, pts, b, f, desk_z):
    """Cable along the arm, then off the back of the box pile and onto the desk."""
    pts = list(pts) + [b - f * 0.19 + Vector((0, 0, -0.08)), b - f * 0.22 + Vector((0, 0, desk_z - b.z + 0.004)), b - f * 0.42 + Vector((0.0, 0.06, desk_z - b.z + 0.004))]
    curve_cable(name, pts, 0.0021, M['lp_cable'])


# ------------------------------------------------------------------ B : swing arm clamped on the riser, vented dome
def lamp_B(edge, outward, hj, target, desk_z, energy=230):
    """edge: point on the edge of the riser top sheet (top face), outward: horizontal direction leaving the sheet."""
    edge, out, hj, target = Vector(edge), Vector(outward).normalized(), Vector(hj), Vector(target)
    K = M['lp_black']
    yaw = math.atan2(out.y, out.x)
    rz = (0, 0, yaw)
    box('lpB_jaw_top', (0.05, 0.045, 0.02), edge - out * 0.018 + Vector((0, 0, 0.0115)), K, rot=rz, bevel=0.002)
    box('lpB_spine', (0.012, 0.045, 0.075), edge + out * 0.013 + Vector((0, 0, -0.016)), K, rot=rz, bevel=0.0015)
    box('lpB_jaw_low', (0.042, 0.045, 0.012), edge - out * 0.012 + Vector((0, 0, -0.048)), K, rot=rz, bevel=0.0015)
    cyl('lpB_screw', 0.0035, 0.044, edge - out * 0.02 + Vector((0, 0, -0.03)), M['lp_spring'], verts=12)
    cyl('lpB_knob', 0.015, 0.012, edge - out * 0.02 + Vector((0, 0, -0.06)), M['lp_knob'], verts=28)
    cyl('lpB_post', 0.009, 0.075, edge - out * 0.018 + Vector((0, 0, 0.059)), K, verts=20)
    p0 = edge - out * 0.018 + Vector((0, 0, 0.1))
    L1 = L2 = 0.47
    e = _ik2(p0, hj, L1, L2)
    f, side = _frame(p0, hj)
    for pa, pb, tag in ((p0, e, 'low'), (e, hj, 'up')):
        u = (pb - pa).normalized()
        n = side.cross(u).normalized()
        for k in (-1, 1):
            tube_between('lpB_arm', pa + n * 0.011 * k, pb + n * 0.011 * k, 0.0038, K, verts=10)
        _spring('lpB_spring', pa + (pb - pa) * 0.1 + side * 0.017, pa + (pb - pa) * 0.62 + side * 0.017, 0.0048, 0.0008, 30, M['lp_spring'])
        tube_between('lpB_hook', pa + (pb - pa) * 0.1, pa + (pb - pa) * 0.1 + side * 0.017, 0.0016, M['lp_spring'], verts=6)
        tube_between('lpB_hook', pa + (pb - pa) * 0.62, pa + (pb - pa) * 0.62 + side * 0.017, 0.0016, M['lp_spring'], verts=6)
    for c, r in ((p0, 0.012), (e, 0.014), (hj, 0.011)):
        _axis_cyl('lpB_joint', c, side, r, 0.03, K)
        _axis_cyl('lpB_knob', c - side * 0.02, side, r * 1.1, 0.01, M['lp_knob'])
    d = (target - hj).normalized()
    back = hj + d * 0.02
    mouth = back + d * 0.14
    _shade('B', mouth, d, [(0.085, 0.0), (0.0845, 0.005), (0.082, 0.025), (0.074, 0.05), (0.06, 0.075), (0.042, 0.095), (0.033, 0.105), (0.033, 0.14), (0, 0.14)], K, M['lp_inner'], sharp=(0, 6))
    # vents round the neck of the dome
    q = (-d).to_track_quat('Z', 'Y')
    for k in range(14):
        a = 2 * math.pi * k / 14
        c = mouth + q @ Vector((0.0335 * math.cos(a), 0.0335 * math.sin(a), 0.123))
        v = box('lpB_vent', (0.0016, 0.006, 0.02), c, M['lp_rubber'])
        v.rotation_euler = (q @ Quaternion((0, 0, 1), a)).to_euler()
    tube_between('lpB_neck', hj, back, 0.006, K, verts=12)
    _axis_cyl('lpB_switch', mouth - d * 0.13 + q @ Vector((0, 0.036, 0)), q @ Vector((0, 1, 0)), 0.006, 0.012, M['lp_knob'])
    _sphere('dk_lampeB_bulb', mouth - d * 0.07, 0.03, M['lp_bulb'])
    _light('B', mouth, d, target, energy, spot=90)
    curve_cable('lpB_cable', [back - side * 0.012] + [hj + (e - hj) * t - side * 0.014 for t in (0.25, 0.6, 0.95)] + [p0 + (e - p0) * t - side * 0.014 for t in (0.8, 0.45, 0.1)] + [p0 + Vector((0, 0, -0.02)) - side * 0.015,
                              edge + out * 0.03 + Vector((0, 0, -0.08)), edge + out * 0.05 + Vector((0, 0, -0.4)), edge + out * 0.09 + Vector((0.05, 0, -0.72))], 0.0021, M['lp_cable'])


# ------------------------------------------------------------------ C : thin tubes and tension wires, disc base, small cone
def lamp_C(b, hj, target, desk_z, energy=200):
    b, hj, target = Vector(b), Vector(hj), Vector(target)
    K = M['lp_satin']
    _lathe('lpC_base', [(0, 0), (0.112, 0), (0.115, 0.004), (0.114, 0.009), (0.105, 0.012), (0.03, 0.013), (0.022, 0.017), (0.02, 0.04), (0, 0.04)], K, sharp=(1, 5)).location = b
    p0 = b + Vector((0, 0, 0.05))
    L1, L2 = 0.38, 0.41
    e = _ik2(p0, hj, L1, L2)
    f, side = _frame(p0, hj)
    tube_between('lpC_arm', p0, e, 0.0055, K, verts=14)
    tube_between('lpC_arm', e, hj, 0.0055, K, verts=14)
    for c, r, w in ((p0, 0.013, 0.016), (e, 0.015, 0.02), (hj, 0.011, 0.016)):
        _axis_cyl('lpC_joint', c, side, r, w, K, verts=28)
        _axis_cyl('lpC_cap', c + side * (w / 2 + 0.001), side, r * 0.7, 0.002, M['lp_inner_alu'], verts=28)
    # tension wires running from small brackets behind the joints
    u1, u2 = (e - p0).normalized(), (hj - e).normalized()
    br0 = p0 - f * 0.035 + Vector((0, 0, 0.012))
    br1 = e + Vector((0, 0, 0.045))
    tube_between('lpC_bracket', p0, br0, 0.0022, K, verts=8)
    tube_between('lpC_bracket', e, br1, 0.0022, K, verts=8)
    tube_between('lpC_wire', br0, p0 + u1 * L1 * 0.62, 0.00055, M['lp_wire'], verts=6)
    tube_between('lpC_wire', br1, e + u2 * L2 * 0.55, 0.00055, M['lp_wire'], verts=6)
    cyl('lpC_spring_box', 0.007, 0.05, e - u1 * 0.05, K, verts=12).rotation_euler = u1.to_track_quat('Z', 'Y').to_euler()
    d = (target - hj).normalized()
    back = hj + d * 0.03
    tube_between('lpC_neck', hj, back, 0.004, K, verts=10)
    mouth = back + d * 0.115
    _shade('C', mouth, d, [(0.064, 0.0), (0.0635, 0.004), (0.058, 0.03), (0.045, 0.07), (0.035, 0.095), (0.035, 0.115), (0, 0.115)], K, M['lp_inner_alu'], sharp=(0, 4))
    q = (-d).to_track_quat('Z', 'Y')
    _axis_cyl('lpC_knob', mouth + q @ Vector((0.038, 0, 0.1)), q @ Vector((1, 0, 0)), 0.006, 0.012, M['lp_knob'])
    _sphere('dk_lampeC_bulb', mouth - d * 0.06, 0.022, M['lp_bulb'])
    _light('C', mouth, d, target, energy, spot=78)
    _lamp_cable('lpC_cable', [b + Vector((0, 0, 0.01)) - f * 0.03, b + Vector((0, 0, 0.008)) - f * 0.1, b - f * 0.13 + Vector((0, 0, 0.004))], b, f, desk_z)


# ------------------------------------------------------------------ D : flat arms, horizontal LED bar
def lamp_D(b, hj, target, desk_z, energy=35):
    b, hj, target = Vector(b), Vector(hj), Vector(target)
    K = M['lp_satin']
    p0 = b + Vector((0, 0, 0.042))
    L1, L2 = 0.34, 0.34
    e = _ik2(p0, hj, L1, L2)
    f, side = _frame(p0, hj)
    yaw = math.atan2(f.y, f.x)
    base = rrect_mesh('lpD_base', 0.19, 0.13, 0.02, 0.022, K, seg=10, bev=0.002)
    base.location = b + Vector((0, 0, 0.01))
    base.rotation_euler = (0, 0, yaw)
    cyl('lpD_led_dot', 0.0035, 0.0006, b + f * 0.065 + Vector((0, 0, 0.0202)), M['lp_led'], verts=16)
    box('lpD_stem', (0.016, 0.03, 0.03), b + Vector((0, 0, 0.032)), K, rot=(0, 0, yaw), bevel=0.003)
    _bar('lpD_arm', p0, e, 0.016, 0.008, K)
    _bar('lpD_arm', e, hj, 0.014, 0.007, K)
    for c, r in ((p0, 0.011), (e, 0.012), (hj, 0.01)):
        _axis_cyl('lpD_hinge', c, side, r, 0.02, K, verts=28)
    # the LED bar across the arm, slightly tilted towards the target
    ang = 0.0
    head = rrect_mesh('lpD_head', 0.34, 0.032, 0.012, 0.006, K, seg=6, bev=0.0012)
    head.location = hj + Vector((0, 0, -0.012))
    sy = math.atan2(side.y, side.x)
    head.rotation_euler = (Euler((0, 0, sy)).to_matrix() @ Euler((-ang, 0, 0)).to_matrix()).to_euler()
    led = plane('dk_lampeD_led', 0.31, 0.012, hj + Vector((0, 0, -0.0182)), M['lp_led'])
    led.rotation_euler = (Euler((0, 0, sy)).to_matrix() @ Euler((-ang + math.pi, 0, 0)).to_matrix()).to_euler()
    lt = add_light('AREA', 'al_light_D', hj + Vector((0, 0, -0.02)), energy, LAMP_WARM, c=CUR[0])
    lt.data.shape = 'RECTANGLE'
    lt.data.size, lt.data.size_y = 0.31, 0.014
    lt.data.spread = rad(70)                       # LED lens: keeps the light on the desk, not on the boxes behind
    lt.visible_camera = False                      # the strip itself shows the LED; the emitter would bloom
    lt.rotation_euler = (Euler((0, 0, sy)).to_matrix() @ Euler((-ang, 0, 0)).to_matrix()).to_euler()
    _lamp_cable('lpD_cable', [b - f * 0.09 + Vector((0, 0, 0.012)), b - f * 0.12 + Vector((0, 0, 0.006))], b, f, desk_z)


# ------------------------------------------------------------------ S : Sketchfab "Desk lamp" (udayjeet, Sketchfab Standard licence)
# One mesh in 68 loose parts, posed with the head raised. The head parts are turned about their real swivel axis so the
# shade looks at the desk; the lamp is turned so its arm faces the lit area. Finishes rebuilt from the author's texture set.
DL_DIR = os.path.join(SKF, 'desk-lamp', '_archive')
DL_SCALE = 0.14                                 # model units -> m (base 17 cm across, about 53 cm tall as posed)
DL_PIVOT = Vector((0.19, 0.03, 3.12))           # head swivel (axis along model y)
DL_SHADE, DL_BULB = Vector((0.814, 0.156, 3.198)), Vector((0.657, 0.109, 3.319))
DL_FIN = {
    'N': dict(name='Noir d’origine'),
    'M': dict(name='Noir mat poudré', paint=((0.016, 0.016, 0.018), 0.0, 0.55)),
    'L': dict(name='Noir et laiton', screw=((0.78, 0.57, 0.3), 1.0, 0.28)),
    'A': dict(name='Aluminium', paint=((0.62, 0.63, 0.64), 1.0, 0.3)),
}


def _dl_material(fin):
    key = 'dl_' + fin
    if key in M:
        return M[key]
    F = DL_FIN[fin]
    m = new_mat(key)
    n, l = m.node_tree.nodes, m.node_tree.links
    p = principled(m)
    def tex(f, nc):
        t = n.new('ShaderNodeTexImage')
        t.image = img(os.path.join(DL_DIR, 'textures', f), noncolor=nc)
        return t
    tb, tm, tr, tn, te = tex('lamp_BaseColor.png', False), tex('lamp_Metallic.png', True), tex('lamp_Roughness.png', True), tex('lamp_Normal.png', True), tex('lamp_Emission.png', False)
    nm = n.new('ShaderNodeNormalMap')
    l.new(tn.outputs['Color'], nm.inputs['Color'])
    l.new(nm.outputs['Normal'], p.inputs['Normal'])
    # masks: painted parts are dark metal, screws and springs light metal
    bw = n.new('ShaderNodeRGBToBW')
    l.new(tb.outputs['Color'], bw.inputs['Color'])
    hi = n.new('ShaderNodeMapRange')
    hi.inputs['From Min'].default_value, hi.inputs['From Max'].default_value = 0.3, 0.4
    l.new(bw.outputs['Val'], hi.inputs['Value'])
    lo = n.new('ShaderNodeMath')
    lo.operation = 'SUBTRACT'
    lo.inputs[0].default_value = 1.0
    l.new(hi.outputs['Result'], lo.inputs[1])
    masks = {}
    for k, src in (('paint', lo), ('screw', hi)):
        mul = n.new('ShaderNodeMath')
        mul.operation = 'MULTIPLY'
        l.new(tm.outputs['Color'], mul.inputs[0])
        l.new(src.outputs[0], mul.inputs[1])
        masks[k] = mul.outputs[0]
    col, met, rou = tb.outputs['Color'], tm.outputs['Color'], tr.outputs['Color']
    for k in ('paint', 'screw'):
        if k not in F:
            continue
        c, mv, rv = F[k]
        mx = n.new('ShaderNodeMix')
        mx.data_type = 'RGBA'
        l.new(masks[k], mx.inputs[0])
        l.new(col, mx.inputs[6])
        mx.inputs[7].default_value = (*c, 1)
        col = mx.outputs[2]
        for src, val, nm_ in ((met, mv, 'met'), (rou, rv, 'rou')):
            mr = n.new('ShaderNodeMapRange')
            mr.clamp = True
            l.new(masks[k], mr.inputs['Value'])
            l.new(src, mr.inputs['To Min'])
            mr.inputs['To Max'].default_value = val
            if nm_ == 'met':
                met = mr.outputs['Result']
            else:
                rou = mr.outputs['Result']
    l.new(col, p.inputs['Base Color'])
    l.new(met, p.inputs['Metallic'])
    l.new(rou, p.inputs['Roughness'])
    em = n.new('ShaderNodeMix')
    em.data_type = 'RGBA'
    em.blend_type = 'MULTIPLY'
    em.inputs[0].default_value = 1.0
    l.new(te.outputs['Color'], em.inputs[6])
    em.inputs[7].default_value = (*LAMP_WARM, 1)
    l.new(em.outputs[2], p.inputs['Emission Color'])
    p.inputs['Emission Strength'].default_value = float(OPT.get('dl_em', 3.0))   # the bulb glows; the spot lights the desk
    M[key] = m
    return m


def lamp_skf(fin, b, target, desk_z, energy=210):
    b, target = Vector(b), Vector(target)
    new = import_file(os.path.join(DL_DIR, 'inner', 'lamp_sketchfab.obj'))
    dirh = target - b
    dirh.z = 0
    item = _wrap(new, 'lampeS', None, b, math.atan2(dirh.y, dirh.x), scale=DL_SCALE, lift=b.z)
    bpy.context.view_layer.update()
    lamp = next(o for o in new if o.type == 'MESH' and o.name.startswith('lamp'))
    # The mesh is Y up (its object stands it upright): the constants above are written Z up, so they are turned into
    # mesh space, (x, y, z) -> (x, z, -y), and the head swivel (axis along the constants' y) turns about the mesh Z.
    # Fixed 17/11: before, the head never turned (its test read the wrong axis) and the spot stood away from the lamp.
    up = lambda v: Vector((v.x, v.z, -v.y))
    piv, bulb = up(DL_PIVOT), up(DL_BULB)
    mw = lamp.matrix_world.copy()
    tm = mw.inverted() @ target
    bm = bmesh.new()
    bm.from_mesh(lamp.data)
    seen, head = set(), []
    for v in bm.verts:
        if v.index in seen:
            continue
        stack, comp = [v], []
        seen.add(v.index)
        while stack:
            x = stack.pop()
            comp.append(x)
            for e in x.link_edges:
                w = e.other_vert(x)
                if w.index not in seen:
                    seen.add(w.index)
                    stack.append(w)
        c = sum((x.co for x in comp), Vector()) / len(comp)
        if c.x > 0.15 and c.y > 2.75:                # the shade and its parts, beyond the swivel
            head.append(comp)
    # the shade's axis: from the bulb to the centre of the shade's box (the largest part of the head), as in the video
    big = max(head, key=len)
    shade = (Vector([min(x.co[i] for x in big) for i in range(3)]) + Vector([max(x.co[i] for x in big) for i in range(3)])) / 2
    rot = lambda th, v: piv + Matrix.Rotation(th, 3, 'Z') @ (v - piv)
    th = 0.0
    for _ in range(4):
        bb, ss = rot(th, bulb), rot(th, shade)
        a, want = ss - bb, tm - bb
        th += math.atan2(want.y, want.x) - math.atan2(a.y, a.x)
    lamp['dl_tete'] = th                            # the head's turn (read by the construction video)
    R = Matrix.Rotation(th, 3, 'Z')
    for comp in head:
        for x in comp:
            x.co = piv + R @ (x.co - piv)
    bm.to_mesh(lamp.data)
    bm.free()
    for o in new:
        if o.type != 'MESH':
            continue
        if o.name.startswith('lamp'):
            o.name = 'dk_lampeS'
            o.data.materials.clear()
            o.data.materials.append(_dl_material(fin))
        else:
            o.name = 'dk_lampeS_fil'
            o.data.materials.clear()
            o.data.materials.append(M['lp_cable'])
        for f in o.data.polygons:
            f.use_smooth = True
    bb, ss = rot(th, bulb), rot(th, shade)
    a = (ss - bb).normalized()
    # the spot in the shade, just ahead of the bulb (the bulb's mesh is opaque: at 3.5 cm it was still blocked)
    pos = mw @ (bb + a * 0.43)
    print('LAMPE tete', round(th, 3), 'spot', [round(x, 3) for x in pos], flush=True)
    add_light('SPOT', 'al_light_S', pos, energy, LAMP_WARM, target=mw @ (bb + a * 3.0), size=0.025, spot=84, blend=0.55, c=CUR[0])
    # mains cable from the back of the base; if the lamp stands higher, it drops off to where it lands (desk_z)
    f = dirh.normalized()
    pts = [b - f * 0.075 + Vector((0, 0, 0.01)), b - f * 0.11 + Vector((0, 0, 0.004))]
    if b.z - desk_z > 0.03:
        pts += [b - f * 0.19 + Vector((0, 0, -0.06)), b - f * 0.22 + Vector((0, 0, desk_z - b.z + 0.004))]
    pts += [b - f * 0.36 + Vector((0.0, 0.05, desk_z - b.z + 0.004)), b - f * 0.5 + Vector((0.0, 0.12, desk_z - b.z + 0.004))]
    curve_cable('lpS_cable', pts, 0.0021, M['lp_cable'])
    return item


LAMPES = {'A': 'Ressorts', 'B': 'Pince', 'C': 'Tiges et câbles', 'D': 'LED', 'S-N': 'Sketchfab, noir d’origine', 'S-M': 'Sketchfab, noir mat', 'S-L': 'Sketchfab, noir et laiton', 'S-A': 'Sketchfab, aluminium'}
# desk-frame positions (x, y along the desk, z above the desk top h): base on the box pile (top at h+0.3), head pivot, target
LAMP_POS = {
    'A': dict(base=(-0.98, 0.1, 0.3), head=(-0.58, -0.06, 0.66), target=(-0.3, -0.22, 0.0)),
    'B': dict(edge=(-1.0, 0.4, 0.0), out=(0, 1, 0), head=(-0.52, -0.08, 0.68), target=(-0.28, -0.22, 0.0)),
    'C': dict(base=(-0.98, 0.1, 0.3), head=(-0.56, -0.08, 0.7), target=(-0.3, -0.22, 0.0)),
    'D': dict(base=(-0.98, 0.1, 0.3), head=(-0.58, -0.2, 0.55), target=(-0.45, -0.25, 0.0)),
}


# placements of the Sketchfab lamp (no box pile): base (x, y, height above the desk top, or 'livres'), lit point
LAMP_SPOTS = {
    'P1': dict(name='Coin gauche du bureau', base=(-1.0, 0.2, 0.0), target=(-0.42, -0.16)),
    'P2': dict(name='Sur la réhausse', base=(-0.7, 0.27, 0.3015), target=(-0.35, -0.15)),
    'P3': dict(name='Sur une pile de livres', base=(-0.98, 0.12, 'livres'), target=(-0.42, -0.16)),
    'P4': dict(name='Sur le retour, à droite', base=(1.5, 0.28, -0.1), target=(0.8, -0.18)),
}


def lampe_au_bureau(k, F, h):
    materials_lampe()
    if k.startswith('S-'):
        S = LAMP_SPOTS[OPT.get('lpos', 'P3')]
        x, y, z = S['base']
        if z == 'livres':
            if 'livres_lampe' in globals():                          # the three classics with their covers (objets-papiers.py)
                z = livres_lampe(F, x, y, h) - h
            else:
                z = book_stack(F.p(x, y, h), 3, F.r + rad(-12), 4) - F.o.z - h
        land = F.o.z + h + (z if z < 0 else 0.0)          # where the mains cable lands: desk top, or the return
        lamp_skf(k[2:], F.p(x, y, h + z), F.p(S['target'][0], S['target'][1], h), land)
        return
    P = LAMP_POS[k]
    hd, tg = F.p(P['head'][0], P['head'][1], h + P['head'][2]), F.p(P['target'][0], P['target'][1], h + P['target'][2])
    if k == 'B':
        e = F.p(P['edge'][0], P['edge'][1], h + P['edge'][2])
        out = F.p(P['out'][0], P['out'][1], 0) - F.p(0, 0, 0)
        lamp_B(e, out, hd, tg, F.o.z + h)
    else:
        b = F.p(P['base'][0], P['base'][1], h + P['base'][2])
        {'A': lamp_A, 'C': lamp_C, 'D': lamp_D}[k](b, hd, tg, F.o.z + h)


class _F0:
    """Identity desk frame for the studio prototypes."""
    o = Vector((0, 0, 0))
    r = 0.0

    @staticmethod
    def p(x, y, z):
        return Vector((x, y, z))


def _pile_studio(boxes=True):
    """The box pile of the lab (two taped boxes) and a few sheets under the lamp, for the studio views."""
    for (x, y, z), (w, d, hh), r in (((-0.98, 0.1, H0), (0.3, 0.24, 0.18), -6), ((-0.97, 0.1, H0 + 0.18), (0.26, 0.2, 0.12), 8)) if boxes else ():
        bx('lp_carton', (w, d, hh), (x, y, z + hh / 2), M['lam_white'], rot=(0, 0, rad(r)), bev=0.002)
        bx('lp_scotch', (w + 0.002, 0.05, 0.0008), (x, y, z + hh + 0.0004), M['black_pc'], rot=(0, 0, rad(r)), bev=0)
    for k, (x, y, r) in enumerate(((-0.42, -0.2, 8), (-0.25, -0.12, -14), (-0.5, -0.02, 22))):
        bx('lp_feuille', (0.21, 0.297, 0.0004), (x, y, H0 + 0.0003 + k * 0.0004), M['lp_paper'], rot=(0, 0, rad(r)), bev=0)


SHOT_L = {
    'tq': dict(cam=(0.3, -1.8, 1.45), target=(-0.7, 0.02, 1.13), lens=34, fstop=8, focus=None),
    'profil': dict(cam=(-0.74, -2.05, 1.2), target=(-0.74, 0.04, 1.16), lens=40, fstop=10, focus=None),
    'tete': dict(cam=(-0.1, -0.86, 1.5), target=(-0.6, -0.04, 1.3), lens=50, fstop=5.6, focus=None),
    'nuit': dict(cam=(0.3, -1.8, 1.45), target=(-0.7, 0.02, 1.13), lens=34, fstop=8, focus=None),
    # the Sketchfab lamp, standing in the back-left corner of the desk
    's_tq': dict(cam=(-0.12, -1.35, 1.32), target=(-0.8, 0.06, 0.97), lens=38, fstop=8, focus=None),
    's_profil': dict(cam=(-1.62, -0.85, 1.05), target=(-0.92, 0.12, 0.99), lens=45, fstop=10, focus=None),
    's_tete': dict(cam=(-0.42, -0.42, 1.33), target=(-0.88, 0.1, 1.13), lens=58, fstop=5.6, focus=None),
    's_nuit': dict(cam=(-0.12, -1.35, 1.32), target=(-0.8, 0.06, 0.97), lens=38, fstop=8, focus=None),
}


def main_lampe():
    setup_render()
    try:
        SC.view_settings.look = 'AgX - Medium High Contrast'
    except TypeError:
        pass
    materials_bureau()
    materials_ecrans()
    materials_lampe()
    studio()
    studio_lights = [o for o in bpy.data.objects if o.type == 'LIGHT']
    for o in studio_lights:
        o.data.energy *= float(OPT.get('dim', 0.7))
    base_e = {o.name: o.data.energy for o in studio_lights}
    CUR[0] = coll('desk')
    concept_D()
    _pile_studio(OPT.get('pile', '1') == '1')
    colls = {}
    keys = OPT.get('lampes', 'A,B,C,D').split(',')
    OPT.setdefault('lpos', 'P1')                     # studio: the Sketchfab lamp stands in the desk corner (book_stack is lab-only)
    for k in keys:
        c = coll('L_' + k)
        CUR[0] = c
        lampe_au_bureau(k, _F0, H0)
        for o in c.objects:
            if o.type == 'LIGHT':
                o.data.energy *= float(OPT.get('lk', 0.45))   # the studio is far brighter than the lab
        colls[k] = c
    os.makedirs(OUT, exist_ok=True)
    for k in keys:
        for k2, c in colls.items():
            c.hide_render = k2 != k
        for v in OPT.get('vues', 'tq,profil,tete,nuit').split(','):
            for o in studio_lights:
                o.data.energy = base_e[o.name] * (0.05 if v == 'nuit' else 1.0)
            SC.camera = make_camera(dict(SHOT_L[('s_' + v) if k.startswith('S-') else v]), f'CAM_{k}_{v}')
            SC.render.resolution_x = RES
            SC.render.resolution_y = int(RES * 9 / 16)
            SC.render.filepath = os.path.join(OUT, f'{k}-{v}.png')
            print('RENDER', SC.render.filepath, flush=True)
            bpy.ops.render.render(write_still=True)


main_lampe()
