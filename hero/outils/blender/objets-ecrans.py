
# ================================================================== screens, MacBook, keyboards, mice (desk setups)
# Built by rendus-ecrans.sh: labo2-base.py + objets-bureau.py + objets-rangements.py + objets-chaise.py + objets-mandy.py (minus their last lines) + this file.
# Everything is built in the desk frame (x along the desk, y towards the back, z up, desk top at 0.74), under an empty `root`.
TEXB2 = os.path.normpath(os.path.join(HERE, '..', 'textures-bureau'))
SETUPS_E = OPT.get('setups', 'A,B,C,D').split(',')
DESK_Z = 0.74


def under(parent, o):
    o.parent = parent
    return o


def empty(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    e = bpy.data.objects.new(name, None)
    e.location = loc
    e.rotation_euler = rot
    link(e)
    if parent is not None:
        e.parent = parent
    return e


def rrect_mesh(name, w, d, t, r, mat, seg=8, side=None, bev=0.0008):
    """Rounded-rectangle slab (w along x, d along y, t along z), centred."""
    r = min(r, w / 2 - 1e-4, d / 2 - 1e-4)
    bm = bmesh.new()
    pts = []
    for cx, cy, a0 in ((w / 2 - r, d / 2 - r, 0), (-w / 2 + r, d / 2 - r, 90), (-w / 2 + r, -d / 2 + r, 180), (w / 2 - r, -d / 2 + r, 270)):
        for k in range(seg + 1):
            a = math.radians(a0 + 90 * k / seg)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    vs = [bm.verts.new((x, y, -t / 2)) for x, y in pts]
    f = bm.faces.new(vs)
    ext = bmesh.ops.extrude_face_region(bm, geom=[f])
    for v in [e for e in ext['geom'] if isinstance(e, bmesh.types.BMVert)]:
        v.co.z += t
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    me.materials.append(mat)
    if side is not None:
        me.materials.append(side)
        for p in me.polygons:
            p.material_index = 0 if abs(p.normal.z) > 0.5 else 1
    for p in me.polygons:
        p.use_smooth = True
    if bev:
        b = o.modifiers.new('bev', 'BEVEL')
        b.width = bev
        b.segments = 3
        b.limit_method = 'ANGLE'
        b.angle_limit = rad(40)
        b.harden_normals = True
    return link(o)


def keys_mesh(name, rows, unit, h, mats, top_shrink=0.0018, gap=0.0016):
    """One mesh for a whole keyboard. rows: list of (row height in units, [(width in units, material index), ...]).
    Rows run from the back (first) to the front (last); the mesh is centred."""
    bm = bmesh.new()
    total_w = max(sum(w for w, _ in r[1]) for r in rows) * unit
    total_d = sum(r[0] for r in rows) * unit
    y = total_d / 2
    for rh, keys in rows:
        x = -total_w / 2
        ry = y - rh * unit / 2
        for (wu, mi) in keys:
            kw, kd = wu * unit - gap, rh * unit - gap
            cx = x + wu * unit / 2
            if mi >= 0:
                s = top_shrink
                bot = [(cx - kw / 2, ry - kd / 2, 0), (cx + kw / 2, ry - kd / 2, 0), (cx + kw / 2, ry + kd / 2, 0), (cx - kw / 2, ry + kd / 2, 0)]
                top = [(cx - kw / 2 + s, ry - kd / 2 + s * 1.3, h), (cx + kw / 2 - s, ry - kd / 2 + s * 1.3, h), (cx + kw / 2 - s, ry + kd / 2 - s * 0.7, h * 0.92), (cx - kw / 2 + s, ry + kd / 2 - s * 0.7, h * 0.92)]
                vb = [bm.verts.new(p) for p in bot]
                vt = [bm.verts.new(p) for p in top]
                faces = [bm.faces.new(list(reversed(vb))), bm.faces.new(vt)]
                for i in range(4):
                    faces.append(bm.faces.new((vb[i], vb[(i + 1) % 4], vt[(i + 1) % 4], vt[i])))
                for fc in faces:
                    fc.material_index = mi
            x += wu * unit
        y -= rh * unit
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    o = bpy.data.objects.new(name, me)
    b = o.modifiers.new('bev', 'BEVEL')
    b.width = min(0.0012, h * 0.25)
    b.segments = 2
    b.limit_method = 'ANGLE'
    for p in me.polygons:
        p.use_smooth = True
    return link(o)


def materials_ecrans():
    if 'mon_black' in M:
        return
    M['mon_black'] = m_plastic('mon_black', (0.014, 0.014, 0.016), rough=0.38)
    M['mon_back'] = m_plastic('mon_back', (0.02, 0.02, 0.022), rough=0.55)
    M['alu_e'] = m_surface('alu_e', (0.72, 0.73, 0.74), rough=0.3, var=0.015, grain=1800, bump=0.004, metal=1.0)
    M['mbp'] = m_surface('mbp_grey', (0.2, 0.205, 0.21), rough=0.33, var=0.012, grain=2000, bump=0.003, metal=1.0)
    M['mbp_pad'] = mat_color('mbp_pad', (0.17, 0.175, 0.18), rough=0.22, metal=0.85)
    M['glass_black'] = mat_color('glass_black', (0.004, 0.004, 0.005), rough=0.05)
    M['key_dark'] = m_plastic('key_dark', (0.03, 0.031, 0.034), rough=0.55)
    M['key_mid'] = m_plastic('key_mid', (0.11, 0.112, 0.118), rough=0.55)
    M['key_light'] = m_plastic('key_light', (0.42, 0.42, 0.41), rough=0.55)
    M['key_lp'] = m_plastic('key_lp', (0.012, 0.012, 0.013), rough=0.45)
    M['case_kb'] = m_surface('case_kb', (0.05, 0.051, 0.055), rough=0.45, var=0.02, grain=1500, bump=0.004, metal=0.6)
    M['mouse'] = m_plastic('mouse', (0.04, 0.041, 0.044), rough=0.5)
    M['felt'] = m_surface('felt', (0.075, 0.077, 0.08), rough=0.95, var=0.12, grain=900, bump=0.04)
    M['cable_e'] = mat_color('cable_e', (0.012, 0.012, 0.013), rough=0.5)
    M['webcam_lens'] = mat_color('webcam_lens', (0.0, 0.0, 0.0), rough=0.05)


def scr(path, s=1.6):
    m = mat_screen(path, s)
    return m


# ------------------------------------------------------------------ monitors
def ecran(parent, name, w, h, tex, loc, rz=0.0, tilt=0.0, stand='foot', strength=1.6, bezel=0.006, curve=0.0, chin=0.0):
    """Flat or curved monitor. loc = screen centre (desk frame). The screen faces -y. stand: foot, arm or none.
    Returns (empty, back mount point in the desk frame)."""
    E = empty('mon_' + name, loc, (tilt, 0, rz), parent)
    tw, th = w + 2 * bezel, h + 2 * bezel + chin
    if curve:
        R_ = curve
        nu, nv = 64, 2

        def surf(nm, ww, hh, off, mat, solid=0.0):
            verts, faces = [], []
            for j in range(nv + 1):
                for i in range(nu + 1):
                    u = -ww / 2 + ww * i / nu
                    a = u / R_
                    verts.append((R_ * math.sin(a), -R_ * (1 - math.cos(a)) + off, -hh / 2 + hh * j / nv))
            for j in range(nv):
                for i in range(nu):
                    a0 = j * (nu + 1) + i
                    faces.append((a0, a0 + 1, a0 + nu + 2, a0 + nu + 1))
            me = bpy.data.meshes.new(nm)
            me.from_pydata(verts, [], faces)
            uvl = me.uv_layers.new()
            for poly in me.polygons:
                for li in poly.loop_indices:
                    vi = me.loops[li].vertex_index
                    uvl.data[li].uv = ((vi % (nu + 1)) / nu, (vi // (nu + 1)) / nv)
                poly.use_smooth = True
            o = bpy.data.objects.new(nm, me)
            me.materials.append(mat)
            link(o)
            if solid:
                sm = o.modifiers.new('solid', 'SOLIDIFY')
                sm.thickness = solid
                sm.offset = -1
            return under(E, o)
        surf('mon_panel_' + name, tw, th, 0.0015, M['mon_black'], solid=0.012)
        surf('mon_screen_' + name, w, h, -0.0002, scr(tex, strength))
        back_y = 0.03
    else:
        p = rrect_mesh('mon_panel_' + name, tw, th, 0.009, 0.004, M['mon_black'])
        p.rotation_euler = (rad(90), 0, 0)
        p.location = (0, 0.0045, -chin / 2)
        under(E, p)
        under(E, plane('mon_screen_' + name, w, h, (0, -0.0003, 0), scr(tex, strength), rot=(rad(90), 0, 0)))
        back_y = 0.0
    b = rrect_mesh('mon_back_' + name, tw * 0.62, th * 0.62, 0.028, 0.03, M['mon_back'], bev=0.004)
    b.rotation_euler = (rad(90), 0, 0)
    b.location = (0, back_y + 0.009 + 0.014, -chin / 2)
    under(E, b)
    v = bx('mon_vesa_' + name, (0.1, 0.012, 0.1), (0, back_y + 0.042, -chin / 2), M['mon_back'], bev=0.003)
    under(E, v)
    if stand == 'foot':
        dz = DESK_Z - loc[2]
        col_h = -dz - 0.04
        c_ = bx('mon_column_' + name, (0.055, 0.022, col_h), (0, back_y + 0.06, dz + col_h / 2 + 0.006), M['mon_black'], bev=0.004)
        under(E, c_)
        f_ = rrect_mesh('mon_foot_' + name, 0.24, 0.17, 0.01, 0.03, M['mon_black'], bev=0.002)
        f_.location = (0, back_y + 0.035, dz + 0.005)
        under(E, f_)
        hj = bx('mon_hinge_' + name, (0.07, 0.03, 0.05), (0, back_y + 0.055, -chin / 2), M['mon_black'], bev=0.006)
        under(E, hj)
    c, s_ = math.cos(rz), math.sin(rz)
    mount = (loc[0] - (back_y + 0.05) * s_, loc[1] + (back_y + 0.05) * c, loc[2])
    return E, mount


def monitor_arm(parent, pole_xy, mounts, top=None, tag='arm'):
    """Desk clamp, pole, one arm per monitor back mount (desk frame)."""
    px, py = pole_xy
    top = top or max(m[2] for m in mounts) + 0.08
    # C clamp gripping the back edge of the top (desk D: edge 7 cm behind the pole, top 25 mm thick, apron 25 mm in front
    # of the edge): top plate out to the edge, back plate behind it, lower jaw, screw, pad and knob (17/11: the old back
    # plate went through the desk top)
    ey, y0 = py + 0.07, py - 0.045
    under(parent, bx(f'{tag}_clamp', (0.07, ey + 0.0125 - y0, 0.012), (px, (y0 + ey + 0.0125) / 2, DESK_Z + 0.006), M['mon_black'], bev=0.003))
    under(parent, bx(f'{tag}_clamp_v', (0.07, 0.012, 0.064), (px, ey + 0.0065, DESK_Z - 0.02), M['mon_black'], bev=0.003))
    under(parent, bx(f'{tag}_clamp_jaw', (0.07, ey + 0.0125 - (py + 0.048), 0.01), (px, (py + 0.048 + ey + 0.0125) / 2, DESK_Z - 0.047), M['mon_black'], bev=0.002))
    under(parent, cyl(f'{tag}_clamp_screw', 0.0045, 0.014, (px, py + 0.06, DESK_Z - 0.035), M['mon_black'], verts=16))
    under(parent, cyl(f'{tag}_clamp_pad', 0.011, 0.003, (px, py + 0.059, DESK_Z - 0.0265), M['mon_black'], verts=24))
    under(parent, cyl(f'{tag}_clamp_knob', 0.012, 0.018, (px, py + 0.06, DESK_Z - 0.061), M['mon_black'], verts=24))
    under(parent, cyl(f'{tag}_pole', 0.017, top - DESK_Z, (px, py, (top + DESK_Z) / 2), M['mon_black'], verts=24))
    under(parent, cyl(f'{tag}_cap', 0.019, 0.012, (px, py, top), M['mon_black'], verts=24))
    for k, (mx, my, mz) in enumerate(mounts):
        z = mz
        under(parent, cyl(f'{tag}_collar{k}', 0.022, 0.03, (px, py, z), M['mon_black'], verts=24))
        mid = ((px + mx) / 2 + (0.06 if mx > px else -0.06) * 0, (py + my) / 2 + 0.06, z)
        under(parent, tube_between(f'{tag}_seg{k}a', (px, py, z), mid, 0.013, M['mon_black'], verts=16))
        under(parent, tube_between(f'{tag}_seg{k}b', mid, (mx, my, mz), 0.012, M['mon_black'], verts=16))
        under(parent, cyl(f'{tag}_joint{k}', 0.016, 0.03, mid, M['mon_black'], verts=20))


# ------------------------------------------------------------------ MacBook Pro 16"
LAPTOP_ROWS = [(0.62, [(1.5, 0)] + [(1, 0)] * 12 + [(1.5, 0)]),
               (1, [(1, 0)] * 13 + [(2, 0)]),
               (1, [(1.5, 0)] + [(1, 0)] * 12 + [(1.5, 0)]),
               (1, [(1.75, 0)] + [(1, 0)] * 11 + [(2.25, 0)]),
               (1, [(2.25, 0)] + [(1, 0)] * 10 + [(2.75, 0)]),
               (1, [(1.25, 0), (1, 0), (1, 0), (1.25, 0), (5, 0), (1.25, 0), (1.25, 0), (1, 0), (1, 0), (1, 0)])]


def macbook(parent, loc, rz=0.0, tilt=0.0, angle=112.0, tex=None):
    W, D, T = 0.3557, 0.2481, 0.0168
    E = empty('mbp', loc, (tilt, 0, rz), parent)
    under(E, rrect_mesh('mbp_base', W, D, T, 0.012, M['mbp'], bev=0.0012)).location = (0, 0, T / 2)
    k = keys_mesh('mbp_keys', LAPTOP_ROWS, 0.0186, 0.0007, [M['key_lp']], top_shrink=0.0004, gap=0.0024)
    k.location = (0, 0.038, T - 0.0001)
    under(E, k)
    under(E, plane('mbp_kbwell', 0.288, 0.112, (0, 0.038, T + 0.00005), M['glass_black']))
    under(E, rrect_mesh('mbp_pad', 0.162, 0.1, 0.0004, 0.006, M['mbp_pad'], bev=0)).location = (0, -0.07, T + 0.0001)
    for sx in (-1, 1):
        under(E, plane('mbp_grille', 0.028, 0.115, (sx * 0.158, 0.038, T + 0.0001), M['perf_black']))
    under(E, cyl('mbp_hinge', 0.006, W - 0.07, (0, D / 2 - 0.006, T - 0.001), M['mbp'], rot=(0, rad(90), 0), verts=24))
    L = empty('mbp_lid', (0, D / 2 - 0.006, T + 0.001), (rad(-angle), 0, 0), E)
    under(L, rrect_mesh('mbp_lidslab', W, D, 0.0065, 0.012, M['mbp'], bev=0.001)).location = (0, -D / 2, 0.00325)
    under(L, plane('mbp_glass', W - 0.008, D - 0.008, (0, -D / 2, -0.0001), M['glass_black'], rot=(rad(180), 0, 0)))
    under(L, plane('mon_screen_mbp', 0.3446, 0.2154, (0, -D / 2 - 0.006, -0.0003), scr(tex or os.path.join(TEXB2, 'ecran-macbook.jpg'), 1.5), rot=(rad(180), 0, 0)))
    under(L, plane('mbp_notch', 0.032, 0.0075, (0, -D + 0.0115, -0.0004), M['glass_black'], rot=(rad(180), 0, 0)))
    return E


def laptop_stand(parent, loc, rz=0.0, tilt=14.0):
    """Aluminium stand: base plate, two legs, tilted top plate. Returns the top-plate frame for the laptop."""
    S = empty('stand', loc, (0, 0, rz), parent)
    under(S, rrect_mesh('stand_base', 0.22, 0.2, 0.005, 0.02, M['alu_e'], bev=0.001)).location = (0, 0.0, DESK_Z + 0.0025)
    for sx in (-1, 1):
        under(S, bx('stand_leg', (0.012, 0.03, 0.12), (sx * 0.1, 0.07, DESK_Z + 0.06), M['alu_e'], rot=(rad(-8), 0, 0), bev=0.002))
    top = empty('stand_top', (0, 0.0, DESK_Z + 0.085), (rad(tilt), 0, 0), S)
    under(top, rrect_mesh('stand_plate', 0.26, 0.24, 0.006, 0.02, M['alu_e'], bev=0.001)).location = (0, 0, 0)
    under(top, bx('stand_lip', (0.2, 0.008, 0.012), (0, -0.118, 0.008), M['alu_e'], bev=0.002))
    return top


# ------------------------------------------------------------------ keyboards, mice, mat
MECH_ROWS = [(1, [(1, 2)] + [(1, 1)] * 15),
             (1, [(1, 0)] * 13 + [(2, 1), (1, 1)]),
             (1, [(1.5, 1)] + [(1, 0)] * 12 + [(1.5, 1), (1, 1)]),
             (1, [(1.75, 1)] + [(1, 0)] * 11 + [(2.25, 2), (1, 1)]),
             (1, [(2.25, 1)] + [(1, 0)] * 10 + [(1.75, 1), (1, 1), (1, -1)]),
             (1, [(1.25, 1), (1.25, 1), (1.25, 1), (6.25, 0), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1)])]
LOWP_ROWS = [(0.6, [(1, 0)] * 15),
             (1, [(1, 0)] * 13 + [(2, 0)]),
             (1, [(1.5, 0)] + [(1, 0)] * 12 + [(1.5, 0)]),
             (1, [(1.75, 0)] + [(1, 0)] * 11 + [(2.25, 0)]),
             (1, [(2.25, 0)] + [(1, 0)] * 10 + [(2.75, 0)]),
             (1, [(1, 0), (1, 0), (1.25, 0), (1.25, 0), (5, 0), (1.25, 0), (1.25, 0), (1, 0), (1, 0)])]


def keyboard_mech(parent, loc, rz=0.0):
    E = empty('kb_mech', loc, (0, 0, rz), parent)
    case = rrect_mesh('kb_case', 0.33, 0.135, 0.024, 0.008, M['case_kb'], bev=0.0015)
    case.location = (0, 0, DESK_Z + 0.014)
    case.rotation_euler = (rad(4), 0, 0)
    under(E, case)
    k = keys_mesh('kb_keys', MECH_ROWS, 0.0192, 0.0085, [M['key_mid'], M['key_dark'], M['key_light']])
    k.location = (0, -0.001, DESK_Z + 0.025)
    k.rotation_euler = (rad(4), 0, 0)
    under(E, k)
    under(E, curve_cable('kb_cable', [(0, 0.07, DESK_Z + 0.015), (0.02, 0.16, DESK_Z + 0.004), (0.1, 0.3, DESK_Z + 0.004), (0.15, 0.4, DESK_Z - 0.02)], 0.0022, M['cable_e']))
    return E


def keyboard_lowp(parent, loc, rz=0.0):
    E = empty('kb_lowp', loc, (0, 0, rz), parent)
    case = rrect_mesh('kb_lp_case', 0.279, 0.115, 0.007, 0.008, M['alu_e'], bev=0.001)
    case.location = (0, 0, DESK_Z + 0.006)
    case.rotation_euler = (rad(2.5), 0, 0)
    under(E, case)
    k = keys_mesh('kb_lp_keys', LOWP_ROWS, 0.0172, 0.0012, [M['key_lp']], top_shrink=0.0004, gap=0.0022)
    k.location = (0, -0.002, DESK_Z + 0.0095)
    k.rotation_euler = (rad(2.5), 0, 0)
    under(E, k)
    return E


def mouse_ergo(parent, loc, rz=0.0):
    E = empty('mouse_ergo', loc, (0, 0, rz), parent)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=40, v_segments=20, radius=1.0)
    for v in bm.verts:
        x, y, z = v.co
        z = z if z > 0 else z * 0.12
        x = x * (0.042 + 0.006 * y)
        v.co = Vector((x, y * 0.062, z * (0.03 + 0.006 * (-x / 0.042)) + 0.004))
    me = bpy.data.meshes.new('mouse_body')
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new('mouse_body', me)
    me.materials.append(M['mouse'])
    link(o)
    o.location = (0, 0, DESK_Z)
    under(E, o)
    under(E, cyl('mouse_wheel', 0.0095, 0.007, (0.004, -0.03, DESK_Z + 0.028), M['key_dark'], rot=(0, rad(90), 0), verts=24))
    return E


def mouse_flat(parent, loc, rz=0.0):
    E = empty('mouse_flat', loc, (0, 0, rz), parent)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=40, v_segments=20, radius=1.0)
    for v in bm.verts:
        x, y, z = v.co
        z = z if z > 0 else z * 0.1
        v.co = Vector((x * 0.029, y * 0.057, z * 0.0105 + 0.002))
    me = bpy.data.meshes.new('mouse_flat_body')
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new('mouse_flat_body', me)
    me.materials.append(M['mbp'])
    link(o)
    o.location = (0, 0, DESK_Z)
    under(E, o)
    return E


def desk_mat(parent, loc, w=0.9, d=0.38, rz=0.0):
    m = rrect_mesh('deskmat', w, d, 0.003, 0.02, M['felt'], bev=0.0008)
    m.location = (loc[0], loc[1], DESK_Z + 0.0015)
    m.rotation_euler = (0, 0, rz)
    return under(parent, m)


def cable_down(parent, a, name='mon_cable'):
    x, y, z = a
    return under(parent, curve_cable(name, [(x, y, z), (x, y + 0.04, z - 0.1), (x + 0.02, 0.36, DESK_Z + 0.004), (x + 0.03, 0.43, DESK_Z - 0.05), (x + 0.03, 0.44, 0.2)], 0.003, M['cable_e']))


# ------------------------------------------------------------------ the four setups (desk frame)
T2E = os.path.normpath(os.path.join(HERE, '..', 'textures-v2'))
TX = dict(code=os.path.join(T2E, 'ecran-code.jpg'), design=os.path.join(T2E, 'ecran-design.jpg'), d3=os.path.join(T2E, 'ecran-3d.jpg'),
          dash=os.path.join(T2E, 'ecran-dashboard.jpg'), term=os.path.join(T2E, 'ecran-terminal-serveur.jpg'),
          vert=os.path.join(TEXB2, 'ecran-code-vertical.jpg'), uw=os.path.join(TEXB2, 'ecran-ultrawide.jpg'))


def setup_A(root):
    """Trio: 32" in the middle, 27" vertical on the left, MacBook on a stand on the right; mechanical keyboard."""
    _, m1 = ecran(root, 'main', 0.708, 0.398, TX['d3'], (0.12, 0.05, 1.12), rz=0.0, stand='foot')
    _, m2 = ecran(root, 'vert', 0.336, 0.597, TX['vert'], (-0.53, 0.0, 1.13), rz=rad(24), stand='foot')
    top = laptop_stand(root, (0.76, -0.04, 0), rz=rad(-26))
    macbook(top, (0, 0.0, 0.004), angle=108)
    desk_mat(root, (0.12, -0.2))
    keyboard_mech(root, (0.08, -0.22, 0), rz=rad(-2))
    mouse_ergo(root, (0.43, -0.2, 0), rz=rad(-8))
    cable_down(root, m1)
    cable_down(root, m2)


def setup_B(root):
    """Two 27" on a dual arm, MacBook open on the desk; low-profile keyboard."""
    _, a = ecran(root, 'left', 0.597, 0.336, TX['code'], (-0.2, 0.06, 1.12), rz=rad(9), stand='none')
    _, b = ecran(root, 'right', 0.597, 0.336, TX['design'], (0.42, 0.06, 1.12), rz=rad(-9), stand='none')
    monitor_arm(root, (0.11, 0.33), [a, b])
    macbook(root, (0.84, -0.08, DESK_Z), rz=rad(-22), angle=112, tex=TX['dash'])
    desk_mat(root, (0.1, -0.2))
    keyboard_lowp(root, (0.08, -0.22, 0))
    mouse_flat(root, (0.36, -0.2, 0), rz=rad(-4))
    cable_down(root, (0.11, 0.35, 1.0))


def setup_C(root):
    """Curved 38" ultrawide, MacBook on a stand on the right; mechanical keyboard."""
    _, m = ecran(root, 'uw', 0.88, 0.369, TX['uw'], (0.08, 0.06, 1.1), stand='foot', curve=2.3)
    top = laptop_stand(root, (0.8, -0.05, 0), rz=rad(-28))
    macbook(top, (0, 0.0, 0.004), angle=108, tex=TX['code'])
    desk_mat(root, (0.1, -0.2))
    keyboard_mech(root, (0.06, -0.22, 0))
    mouse_ergo(root, (0.41, -0.2, 0), rz=rad(-6))
    cable_down(root, m)


def setup_D(root):
    """Two 27" stacked on a pole, MacBook on a stand on the right; low-profile keyboard."""
    _, a = ecran(root, 'low', 0.597, 0.336, TX['code'], (0.1, 0.05, 1.0), stand='none')
    _, b = ecran(root, 'high', 0.597, 0.336, TX['dash'], (0.1, 0.09, 1.365), tilt=rad(-8), stand='none')
    monitor_arm(root, (0.1, 0.33), [a, b], top=1.45)
    top = laptop_stand(root, (0.76, -0.04, 0), rz=rad(-26))
    macbook(top, (0, 0.0, 0.004), angle=108, tex=TX['design'])
    desk_mat(root, (0.1, -0.2))
    keyboard_lowp(root, (0.08, -0.22, 0))
    mouse_ergo(root, (0.38, -0.2, 0), rz=rad(-6))
    cable_down(root, (0.1, 0.35, 0.95))


SETUP_FN = {'A': setup_A, 'B': setup_B, 'C': setup_C, 'D': setup_D}
SETUP_NAMES = {'A': 'Trio : 32 pouces, écran vertical, MacBook sur support', 'B': 'Deux 27 pouces sur bras, MacBook ouvert',
               'C': 'Ultra-large incurvé 38 pouces, MacBook sur support', 'D': 'Deux 27 pouces superposés, MacBook sur support'}


def build_setup(key, F=None):
    materials_ecrans()
    root = empty('setup_' + key)
    if F is not None:
        root.location = F.o
        root.rotation_euler = (0, 0, F.r)
    SETUP_FN[key](root)
    return root


SHOT_E = {
    'tq': dict(cam=(-1.7, -2.35, 1.6), target=(0.2, 0.0, 0.95), lens=35, fstop=8, focus=None),
    'face': dict(cam=(0.15, -2.6, 1.15), target=(0.15, 0.0, 1.0), lens=40, fstop=8, focus=None),
    'det': dict(cam=(0.05, -1.0, 1.08), target=(0.45, -0.12, 0.82), lens=45, fstop=2.8, focus=None),
}


def main_ecrans():
    setup_render()
    try:
        SC.view_settings.look = 'AgX - Medium High Contrast'
    except TypeError:
        pass
    materials_bureau()
    studio()
    for o in bpy.data.objects:
        if o.type == 'LIGHT':
            o.data.energy *= float(OPT.get('dim', 0.7))
    colls = {}
    for k in SETUPS_E:
        c = coll('E_' + k)
        CUR[0] = c
        concept_D()
        build_setup(k)
        colls[k] = c
    os.makedirs(OUT, exist_ok=True)
    if OPT.get('save') == '1':
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'ecrans-prototypes.blend'))
    for k in SETUPS_E:
        for k2, c in colls.items():
            c.hide_render = k2 != k
        for v in OPT.get('vues', 'tq,face,det').split(','):
            SC.camera = make_camera(dict(SHOT_E[v]), f'CAM_{k}_{v}')
            SC.render.resolution_x = RES
            SC.render.resolution_y = int(RES * 9 / 16)
            SC.render.filepath = os.path.join(OUT, f'{k}-{v}.png')
            print('RENDER', SC.render.filepath, flush=True)
            bpy.ops.render.render(write_still=True)


main_ecrans()
