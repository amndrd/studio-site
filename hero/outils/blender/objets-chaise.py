
# ================================================================== desk chair prototypes (object alone, studio)
# Built by rendus-chaise.sh: labo2-base.py + objets-bureau.py + objets-rangements.py (minus their last lines) + this file.
# One model, faithful to the research image 3-01 (mesh task chair with headrest), in three finishes:
# G graphite, N all black, A graphite with a polished aluminium base. Built at the origin, seat front towards -y.
FINIS_C = OPT.get('finitions', 'G,N,A').split(',')
VUES_C = OPT.get('vues', 'tq,profil,dos,detail').split(',')


def m_weave(name, color, nu=190, nv=150, fu=0.7, fv=0.16, rough=0.45):
    """Woven mesh: vertical strands (u) and thinner horizontal ones (v), transparent between them."""
    m = mat_color(name, color, rough=rough, metal=0.0)
    n, l = _nodes(m)
    p = principled(m)
    try:
        p.inputs['Sheen Weight'].default_value = 0.4
    except KeyError:
        pass
    out = next(x for x in n if x.type == 'OUTPUT_MATERIAL')
    tc = n.new('ShaderNodeTexCoord')
    sp = n.new('ShaderNodeSeparateXYZ')
    l.new(tc.outputs['UV'], sp.inputs['Vector'])
    strands = []
    for comp, N_, fill in (('X', nu, fu), ('Y', nv, fv)):
        mu = n.new('ShaderNodeMath')
        mu.operation = 'MULTIPLY'
        mu.inputs[1].default_value = N_
        l.new(sp.outputs[comp], mu.inputs[0])
        fr = n.new('ShaderNodeMath')
        fr.operation = 'FRACT'
        l.new(mu.outputs[0], fr.inputs[0])
        lt = n.new('ShaderNodeMath')
        lt.operation = 'LESS_THAN'
        lt.inputs[1].default_value = fill
        l.new(fr.outputs[0], lt.inputs[0])
        strands.append(lt)
    mx_ = n.new('ShaderNodeMath')
    mx_.operation = 'MAXIMUM'
    l.new(strands[0].outputs[0], mx_.inputs[0])
    l.new(strands[1].outputs[0], mx_.inputs[1])
    tr = n.new('ShaderNodeBsdfTransparent')
    mix = n.new('ShaderNodeMixShader')
    l.new(mx_.outputs[0], mix.inputs['Fac'])
    l.new(tr.outputs[0], mix.inputs[1])
    l.new(p.outputs[0], mix.inputs[2])
    l.new(mix.outputs[0], out.inputs['Surface'])
    return m


def finish_c(f):
    key = 'chair_' + f
    if key in M:
        return M[key]
    if f == 'N':
        d = dict(frame=m_powder('ch_frame_N', (0.017, 0.017, 0.018), rough=0.45, metal=0.1, peel=0.03),
                 mesh=m_weave('ch_mesh_N', (0.016, 0.016, 0.017)),
                 base=m_powder('ch_base_N', (0.02, 0.02, 0.021), rough=0.4, metal=0.3, peel=0.03))
    else:
        d = dict(frame=m_powder('ch_frame_G', (0.055, 0.056, 0.06), rough=0.42, metal=0.15, peel=0.03),
                 mesh=m_weave('ch_mesh_G', (0.035, 0.036, 0.04)),
                 base=m_powder('ch_base_G', (0.065, 0.066, 0.07), rough=0.38, metal=0.5, peel=0.03))
        if f == 'A':
            d['base'] = mat_color('ch_base_A', (0.86, 0.865, 0.87), rough=0.12, metal=1.0)
    d['pad'] = mat_color('ch_pad', (0.018, 0.018, 0.019), rough=0.6)
    d['chrome'] = mat_color('ch_chrome', (0.9, 0.9, 0.9), rough=0.08, metal=1.0)
    M[key] = d
    return d


def surface_grid(name, fn, nu, nv, mat):
    """Grid surface from fn(s, t) -> (x, y, z), s in [-1, 1], t in [0, 1]; UVs follow (s, t). Returns the object and its outline."""
    verts, uvs = [], []
    for j in range(nv + 1):
        for i in range(nu + 1):
            s, t = -1 + 2 * i / nu, j / nv
            verts.append(fn(s, t))
    faces = []
    for j in range(nv):
        for i in range(nu):
            a = j * (nu + 1) + i
            faces.append((a, a + 1, a + nu + 2, a + nu + 1))
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    uvl = me.uv_layers.new()
    for poly in me.polygons:
        for li in poly.loop_indices:
            vi = me.loops[li].vertex_index
            i, j = vi % (nu + 1), vi // (nu + 1)
            uvl.data[li].uv = (i / nu, j / nv)
        poly.use_smooth = True
    o = bpy.data.objects.new(name, me)
    me.materials.append(mat)
    link(o)
    ring_ = [fn(-1 + 2 * i / nu, 0) for i in range(nu + 1)] + [fn(1, j / nv) for j in range(1, nv + 1)] + \
            [fn(1 - 2 * i / nu, 1) for i in range(1, nu + 1)] + [fn(-1, 1 - j / nv) for j in range(1, nv)]
    return o, ring_


def frame_loop(name, pts, r, mat, step=2):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = r
    cu.bevel_resolution = 4
    sp = cu.splines.new('BEZIER')
    pts = pts[::step]
    sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
    sp.use_cyclic_u = True
    o = bpy.data.objects.new(name, cu)
    cu.materials.append(mat)
    return link(o)


def leg_mesh(name, a, mat, r0=0.035, r1=0.335, n=10):
    """One leg of the five-star base, tapered and sloping down, with a ridge on top."""
    bm = bmesh.new()
    rings = []
    ca, sa = math.cos(a), math.sin(a)
    for k in range(n + 1):
        u = k / n
        r = r0 + (r1 - r0) * u
        w = 0.068 - 0.03 * u
        h = 0.058 - 0.026 * u
        zc = 0.112 - 0.04 * u ** 1.3
        sec = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2 * 0.8, h / 2 * 0.7), (0, h / 2), (-w / 2 * 0.8, h / 2 * 0.7)]
        ring_ = []
        for (px, pz) in sec:
            x, y = r * ca - px * sa, r * sa + px * ca
            ring_.append(bm.verts.new((x, y, zc + pz)))
        rings.append(ring_)
    m_ = len(rings[0])
    for k in range(n):
        for i in range(m_):
            bm.faces.new((rings[k][i], rings[k][(i + 1) % m_], rings[k + 1][(i + 1) % m_], rings[k + 1][i]))
    bm.faces.new(rings[-1])
    bm.faces.new(list(reversed(rings[0])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for f in me.polygons:
        f.use_smooth = True
    o = bpy.data.objects.new(name, me)
    me.materials.append(mat)
    b = o.modifiers.new('sub', 'SUBSURF')
    b.levels = b.render_levels = 1
    return link(o)


def mesh_chair(F_):
    """The chair. F_ is the finish dict (frame, mesh, base, pad, chrome)."""
    fr, ms, bs, pd, ch = F_['frame'], F_['mesh'], F_['base'], F_['pad'], F_['chrome']
    # five-star base, casters, gas lift
    cyl('chair_hub', 0.045, 0.07, (0, 0, 0.105), bs, verts=32)
    for k in range(5):
        a = math.pi / 2 + 2 * math.pi * k / 5 + math.pi
        leg_mesh('chair_leg', a, bs)
        tx, ty = 0.335 * math.cos(a), 0.335 * math.sin(a)
        cyl('chair_caster_top', 0.016, 0.03, (tx, ty, 0.072), bs, verts=16)
        cyl('chair_caster_hood', 0.024, 0.05, (tx + 0.012 * math.cos(a), ty + 0.012 * math.sin(a), 0.038), pd, rot=(0, rad(90), a + math.pi / 2), verts=24)
        for d_ in (-0.013, 0.013):
            px, py = -math.sin(a) * d_, math.cos(a) * d_
            cyl('chair_wheel', 0.029, 0.014, (tx + 0.012 * math.cos(a) + px, ty + 0.012 * math.sin(a) + py, 0.029), pd, rot=(0, rad(90), a + math.pi / 2), verts=28)
    cyl('chair_gas', 0.026, 0.19, (0, 0, 0.225), F_['pad'], verts=32)
    cyl('chair_gas_rod', 0.014, 0.04, (0, 0, 0.335), ch, verts=24)
    # tilt mechanism: horizontal housing, front block, levers
    cyl('chair_mech', 0.055, 0.27, (0, 0.05, 0.37), fr, rot=(0, rad(90), 0), verts=40)
    bx('chair_mech_front', (0.13, 0.18, 0.05), (0, -0.07, 0.395), fr, bev=0.012, seg=3)
    for sx in (-1, 1):
        cyl('chair_mech_cap', 0.058, 0.012, (sx * 0.14, 0.05, 0.37), fr, rot=(0, rad(90), 0), verts=40)
    tb('chair_lever', (-0.06, -0.08, 0.385), (-0.24, -0.15, 0.36), 0.0075, fr, verts=12)
    cyl('chair_lever_knob', 0.017, 0.07, (-0.27, -0.165, 0.357), pd, rot=(0, rad(90), rad(-20)), verts=24)
    tb('chair_lever2', (0.06, -0.02, 0.38), (0.16, -0.12, 0.36), 0.006, fr, verts=12)

    # seat: mesh on a thick frame, waterfall front edge
    def seat(s, t):
        tt = 2 * t - 1
        hw = 0.25 - 0.045 * t ** 1.5
        x = s * hw * (1 - 0.12 * abs(tt) ** 6)
        y = -0.02 + tt * 0.23 * (1 - 0.18 * abs(s) ** 5)
        z = 0.47 - 0.03 * (1 - s * s) * (1 - tt * tt) ** 0.8 + 0.012 * s ** 4 + 0.02 * max(0.0, tt) ** 2
        if tt < -0.55:
            z -= 0.045 * ((-0.55 - tt) / 0.45) ** 2
        return (x, y, z)
    _, ring_ = surface_grid('chair_seat', seat, 28, 24, ms)
    frame_loop('chair_seat_frame', ring_, 0.0125, fr)

    # back: inverted trapezoid, reclined, lumbar curve, wrapping edges
    zb, zt = 0.53, 1.07

    def back(s, t):
        hw = 0.125 + 0.13 * t ** 0.75
        x = s * hw * (1 - 0.07 * t ** 12)
        z = zb + t * (zt - zb) * (1 - 0.035 * abs(s) ** 4)
        y = 0.22 + (z - zb) * 0.22 - 0.03 * math.exp(-((t - 0.25) / 0.15) ** 2) - 0.06 * s * s
        return (x, y, z)
    _, ring_ = surface_grid('chair_back', back, 24, 30, ms)
    frame_loop('chair_back_frame', ring_, 0.013, fr)
    bx('chair_lumbar', (0.17, 0.014, 0.035), (0, 0.232, 0.63), fr, bev=0.006, seg=3)
    # side spines from the back down to the seat pivots and the mechanism
    for sx in (-1, 1):
        cu = curve_cable('chair_spine', [(sx * 0.125, 0.19, 0.535), (sx * 0.2, 0.17, 0.49), (sx * 0.17, 0.11, 0.405), (sx * 0.09, 0.06, 0.375)], 0.019, fr)
        cyl('chair_pivot', 0.03, 0.02, (sx * 0.225, 0.155, 0.475), fr, rot=(0, rad(90), 0), verts=32)
        cyl('chair_pivot_cap', 0.016, 0.004, (sx * 0.236, 0.155, 0.475), ch, rot=(0, rad(90), 0), verts=24)
        # arm: post rising from the pivot, flat pad
        curve_cable('chair_armpost', [(sx * 0.225, 0.13, 0.48), (sx * 0.255, 0.09, 0.56), (sx * 0.262, 0.05, 0.645)], 0.021, fr)
        bx('chair_armjoint', (0.05, 0.06, 0.03), (sx * 0.262, 0.045, 0.655), fr, bev=0.01, seg=3)
        bx('chair_armpad', (0.085, 0.26, 0.03), (sx * 0.268, -0.02, 0.678), pd, rot=(0, 0, sx * rad(-4)), bev=0.013, seg=4)

    # headrest on a stem
    hz0, hz1 = 1.13, 1.28

    def head(s, t):
        tt = 2 * t - 1
        x = s * 0.15 * (1 - 0.14 * abs(tt) ** 6)
        z = hz0 + t * (hz1 - hz0) * (1 - 0.08 * abs(s) ** 6)
        y = 0.37 - (z - hz0) * 0.18 - 0.05 * s * s
        return (x, y, z)
    _, ring_ = surface_grid('chair_head', head, 20, 10, ms)
    frame_loop('chair_head_frame', ring_, 0.012, fr)
    tb('chair_stem', (0, 0.365, 0.98), (0, 0.395, 1.15), 0.012, fr, verts=16)
    bx('chair_stem_clamp', (0.07, 0.035, 0.05), (0, 0.375, 1.02), fr, bev=0.01, seg=3)
    cyl('chair_stem_knob', 0.016, 0.02, (0, 0.4, 1.02), pd, rot=(rad(90), 0, 0), verts=24)
    bx('chair_head_bar', (0.1, 0.02, 0.022), (0, 0.39, 1.122), fr, bev=0.007, seg=3)


def place_chair(f, x, y, rz):
    before = set(bpy.data.objects)
    mesh_chair(finish_c(f))
    root = bpy.data.objects.new('chair_root', None)
    root.location = (x, y, 0)
    root.rotation_euler = (0, 0, rz)
    link(root)
    for o in set(bpy.data.objects) - before:
        if o.parent is None and o is not root:
            o.parent = root
    return root


SHOT_C = {
    'tq': dict(cam=(-1.55, -2.35, 1.35), target=(0.0, 0.04, 0.66), lens=45, fstop=8, focus=None),
    'profil': dict(cam=(-2.9, 0.05, 0.78), target=(0.0, 0.05, 0.64), lens=60, fstop=11, focus=None),
    'dos': dict(cam=(1.35, 2.35, 1.45), target=(0.0, 0.1, 0.68), lens=45, fstop=8, focus=None),
    'detail': dict(cam=(-0.55, -0.62, 1.42), target=(0.0, 0.33, 1.12), lens=70, fstop=2.8, focus=None),
}


def main_chaise():
    setup_render()
    try:
        SC.view_settings.look = 'AgX - Medium High Contrast'
    except TypeError:
        pass
    materials_bureau()
    studio()
    colls = {}
    for f in FINIS_C:
        c = coll('C_' + f)
        CUR[0] = c
        place_chair(f, 0, 0, 0)
        colls[f] = c
    os.makedirs(OUT, exist_ok=True)
    if OPT.get('save') == '1':
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'chaise-prototypes.blend'))
    for f in FINIS_C:
        for k, c in colls.items():
            c.hide_render = k != f
        for v in VUES_C:
            SC.camera = make_camera(dict(SHOT_C[v]), f'CAM_{f}_{v}')
            SC.render.resolution_x = RES
            SC.render.resolution_y = int(RES * 9 / 16)
            SC.render.filepath = os.path.join(OUT, f'{f}-{v}.png')
            print('RENDER', SC.render.filepath, flush=True)
            bpy.ops.render.render(write_still=True)


main_chaise()
