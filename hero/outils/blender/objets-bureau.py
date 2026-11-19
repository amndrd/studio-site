
# ================================================================== desk prototypes (object alone, studio)
# Built by rendus-bureau.sh: labo2-base.py + this file.
# blender -b --factory-startup -P bureau.py -- concepts=A,B,C,D,E shots=tq,face,detail res=1920 samples=128 out=<dir>
M = {}
TEXB = os.path.normpath(os.path.join(HERE, '..', 'textures-bureau'))
CONCEPTS = OPT.get('concepts', 'A,B,C,D,E').split(',')


# ------------------------------------------------------------------ geometry helpers
def bx(name, size, loc, mat, side=None, rot=(0, 0, 0), bev=0.0015, seg=2):
    o = box(name, size, loc, mat, rot=rot)
    me = o.data
    if side is not None:
        me.materials.append(side)
        for f in me.polygons:
            f.material_index = 0 if abs(f.normal.z) > 0.5 else 1
    for f in me.polygons:
        f.use_smooth = True
    if bev:
        b = o.modifiers.new('bev', 'BEVEL')
        b.width = bev
        b.segments = seg
        b.limit_method = 'ANGLE'
        b.harden_normals = True
    return o


def tb(name, a, b, r, mat, verts=32):
    o = tube_between(name, a, b, r, mat, verts=verts)
    return o


def extrude_profile(name, pts, length, mat, loc, rot=(0, 0, 0)):
    bm = bmesh.new()
    vs = [bm.verts.new((x, y, 0)) for x, y in pts]
    f = bm.faces.new(vs)
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    for v in [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]:
        v.co.z += length
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    o.location = loc
    o.rotation_euler = rot
    me.materials.append(mat)
    b = o.modifiers.new('bev', 'BEVEL')
    b.width = 0.0006
    b.segments = 1
    b.limit_method = 'ANGLE'
    return link(o)


def slot_profile(s=0.04, slot=0.008, depth=0.006):
    """40x40 aluminium extrusion outline with one T-slot opening per side (simplified)."""
    h = s / 2
    w = slot / 2
    pts = []
    for k in range(4):
        a = k * math.pi / 2
        c, s_ = math.cos(a), math.sin(a)
        side = [(h, -h + 0.003), (h, -w), (h - depth, -w), (h - depth, w), (h, w), (h, h - 0.003)]
        for (x, y) in side:
            pts.append((x * c - y * s_, x * s_ + y * c))
    return pts


def profile_between(name, a, b, mat):
    a, b = Vector(a), Vector(b)
    d = b - a
    o = extrude_profile(name, slot_profile(), d.length, mat, a)
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    return o


def foot(x, y, mat, h=0.02, r=0.022):
    cyl('foot', r, h * 0.6, (x, y, h * 0.3), mat, verts=24)
    cyl('foot_stem', 0.006, h, (x, y, h * 0.8), M['steelbright'], verts=12)


# ------------------------------------------------------------------ materials
def _nodes(m):
    return m.node_tree.nodes, m.node_tree.links


def m_powder(name, color, rough=0.4, metal=0.15, peel=0.06):
    m = mat_color(name, color, rough=rough, metal=metal)
    n, l = _nodes(m)
    p = principled(m)
    tc = n.new('ShaderNodeTexCoord')
    nz = n.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 900
    nz.inputs['Detail'].default_value = 2
    bp = n.new('ShaderNodeBump')
    bp.inputs['Strength'].default_value = peel
    bp.inputs['Distance'].default_value = 0.0004
    l.new(tc.outputs['Object'], nz.inputs['Vector'])
    l.new(nz.outputs['Fac'], bp.inputs['Height'])
    l.new(bp.outputs['Normal'], p.inputs['Normal'])
    # large smudges on roughness
    sm = n.new('ShaderNodeTexNoise')
    sm.inputs['Scale'].default_value = 6
    mr = n.new('ShaderNodeMapRange')
    mr.inputs['To Min'].default_value = rough - 0.06
    mr.inputs['To Max'].default_value = rough + 0.08
    l.new(tc.outputs['Object'], sm.inputs['Vector'])
    l.new(sm.outputs['Fac'], mr.inputs['Value'])
    l.new(mr.outputs['Result'], p.inputs['Roughness'])
    return m


def m_surface(name, color, rough=0.45, var=0.03, grain=900, bump=0.02, metal=0.0):
    m = mat_color(name, color, rough=rough, metal=metal)
    n, l = _nodes(m)
    p = principled(m)
    tc = n.new('ShaderNodeTexCoord')
    nz = n.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = grain
    nz.inputs['Detail'].default_value = 4
    l.new(tc.outputs['Object'], nz.inputs['Vector'])
    mix = n.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    mix.inputs['A'].default_value = (*[c * (1 - var) for c in color], 1)
    mix.inputs['B'].default_value = (*[min(1, c * (1 + var)) for c in color], 1)
    l.new(nz.outputs['Fac'], mix.inputs['Factor'])
    l.new(mix.outputs['Result'], p.inputs['Base Color'])
    bp = n.new('ShaderNodeBump')
    bp.inputs['Strength'].default_value = bump
    bp.inputs['Distance'].default_value = 0.0003
    l.new(nz.outputs['Fac'], bp.inputs['Height'])
    l.new(bp.outputs['Normal'], p.inputs['Normal'])
    sm = n.new('ShaderNodeTexNoise')
    sm.inputs['Scale'].default_value = 3.5
    mr = n.new('ShaderNodeMapRange')
    mr.inputs['To Min'].default_value = rough - 0.07
    mr.inputs['To Max'].default_value = rough + 0.1
    l.new(tc.outputs['Object'], sm.inputs['Vector'])
    l.new(sm.outputs['Fac'], mr.inputs['Value'])
    l.new(mr.outputs['Result'], p.inputs['Roughness'])
    return m


def m_galva(name, base=(0.6, 0.62, 0.63), cast=False):
    m = mat_color(name, base, rough=0.4, metal=1.0)
    n, l = _nodes(m)
    p = principled(m)
    tc = n.new('ShaderNodeTexCoord')
    vo = n.new('ShaderNodeTexVoronoi')
    vo.inputs['Scale'].default_value = 60 if not cast else 400
    l.new(tc.outputs['Object'], vo.inputs['Vector'])
    cr = n.new('ShaderNodeValToRGB')
    cr.color_ramp.elements[0].color = (*[c * 0.82 for c in base], 1)
    cr.color_ramp.elements[1].color = (*[min(1, c * 1.1) for c in base], 1)
    l.new(vo.outputs['Color'], cr.inputs['Fac'])
    l.new(cr.outputs['Color'], p.inputs['Base Color'])
    mr = n.new('ShaderNodeMapRange')
    mr.inputs['To Min'].default_value = 0.28 if not cast else 0.5
    mr.inputs['To Max'].default_value = 0.55 if not cast else 0.7
    l.new(vo.outputs['Distance'], mr.inputs['Value'])
    l.new(mr.outputs['Result'], p.inputs['Roughness'])
    return m


def m_ply_edge(name, ply=0.0026, axis='Z'):
    m = mat_color(name, (0.7, 0.58, 0.42), rough=0.55)
    n, l = _nodes(m)
    p = principled(m)
    tc = n.new('ShaderNodeTexCoord')
    sp = n.new('ShaderNodeSeparateXYZ')
    l.new(tc.outputs['Object'], sp.inputs['Vector'])
    mu = n.new('ShaderNodeMath')
    mu.operation = 'MULTIPLY'
    mu.inputs[1].default_value = 1 / ply
    l.new(sp.outputs[axis], mu.inputs[0])
    fr = n.new('ShaderNodeMath')
    fr.operation = 'FRACT'
    l.new(mu.outputs[0], fr.inputs[0])
    cr = n.new('ShaderNodeValToRGB')
    cr.color_ramp.interpolation = 'CONSTANT'
    cr.color_ramp.elements[0].position = 0.0
    cr.color_ramp.elements[0].color = (0.4, 0.29, 0.17, 1)
    cr.color_ramp.elements[1].position = 0.1
    cr.color_ramp.elements[1].color = (0.76, 0.64, 0.48, 1)
    e = cr.color_ramp.elements.new(0.52)
    e.color = (0.58, 0.45, 0.3, 1)
    e2 = cr.color_ramp.elements.new(0.6)
    e2.color = (0.7, 0.57, 0.41, 1)
    l.new(fr.outputs[0], cr.inputs['Fac'])
    l.new(cr.outputs['Color'], p.inputs['Base Color'])
    return m


def m_birch(name):
    m = mat_color(name, (0.72, 0.6, 0.45), rough=0.5)
    n, l = _nodes(m)
    p = principled(m)
    tc = n.new('ShaderNodeTexCoord')
    mp = n.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (1.0, 22.0, 1.0)
    l.new(tc.outputs['Object'], mp.inputs['Vector'])
    wv = n.new('ShaderNodeTexWave')
    wv.wave_type = 'BANDS'
    wv.bands_direction = 'X'
    wv.inputs['Scale'].default_value = 3.0
    wv.inputs['Distortion'].default_value = 6.0
    wv.inputs['Detail'].default_value = 3.0
    l.new(mp.outputs['Vector'], wv.inputs['Vector'])
    cr = n.new('ShaderNodeValToRGB')
    cr.color_ramp.elements[0].color = (0.66, 0.53, 0.38, 1)
    cr.color_ramp.elements[1].color = (0.78, 0.66, 0.5, 1)
    l.new(wv.outputs['Fac'], cr.inputs['Fac'])
    l.new(cr.outputs['Color'], p.inputs['Base Color'])
    return m


def m_tiled_alpha(name, path, tile, color, rough=0.4, metal=0.2):
    m = mat_color(name, color, rough=rough, metal=metal)
    n, l = _nodes(m)
    p = principled(m)
    out = next(x for x in n if x.type == 'OUTPUT_MATERIAL')
    tc = n.new('ShaderNodeTexCoord')
    mp = n.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (1 / tile, 1 / tile, 1 / tile)
    l.new(tc.outputs['Object'], mp.inputs['Vector'])
    t = n.new('ShaderNodeTexImage')
    t.image = img(path, True)
    t.projection = 'BOX'
    t.projection_blend = 0.0
    l.new(mp.outputs['Vector'], t.inputs['Vector'])
    tr = n.new('ShaderNodeBsdfTransparent')
    mx = n.new('ShaderNodeMixShader')
    l.new(t.outputs['Color'], mx.inputs['Fac'])
    l.new(tr.outputs[0], mx.inputs[1])
    l.new(p.outputs[0], mx.inputs[2])
    l.new(mx.outputs[0], out.inputs['Surface'])
    return m


def m_label(name, path, relief=None, rough=0.35, alpha=False):
    m = new_mat(name)
    n, l = _nodes(m)
    p = principled(m)
    p.inputs['Roughness'].default_value = rough
    t = n.new('ShaderNodeTexImage')
    t.image = img(path)
    t.extension = 'CLIP'
    l.new(t.outputs['Color'], p.inputs['Base Color'])
    if relief:
        r = n.new('ShaderNodeTexImage')
        r.image = img(relief, True)
        bp = n.new('ShaderNodeBump')
        bp.inputs['Strength'].default_value = 0.35
        bp.inputs['Distance'].default_value = 0.0006
        l.new(r.outputs['Color'], bp.inputs['Height'])
        l.new(bp.outputs['Normal'], p.inputs['Normal'])
    if alpha:
        out = next(x for x in n if x.type == 'OUTPUT_MATERIAL')
        tr = n.new('ShaderNodeBsdfTransparent')
        mx = n.new('ShaderNodeMixShader')
        l.new(t.outputs['Alpha'], mx.inputs['Fac'])
        l.new(tr.outputs[0], mx.inputs[1])
        l.new(p.outputs[0], mx.inputs[2])
        l.new(mx.outputs[0], out.inputs['Surface'])
    return m


def materials_bureau(keep=False):
    old = dict(M) if keep else {}
    M['steelbright'] = mat_color('steelbright', (0.75, 0.75, 0.75), rough=0.25, metal=1.0)
    M['rubber'] = mat_color('rubber', (0.015, 0.015, 0.016), rough=0.7)
    M['black'] = mat_color('black', (0.016, 0.016, 0.018), rough=0.42, metal=0.3)
    M['white_pc'] = m_powder('white_pc', (0.78, 0.78, 0.76), rough=0.36)
    M['grey_pc'] = m_powder('grey_pc', (0.66, 0.67, 0.66), rough=0.4)
    M['ped'] = m_powder('ped', (0.3, 0.31, 0.31), rough=0.42)
    M['black_pc'] = m_powder('black_pc', (0.022, 0.022, 0.024), rough=0.45, metal=0.25, peel=0.1)
    M['lam_grey'] = m_surface('lam_grey', (0.4, 0.405, 0.4), rough=0.42)
    M['lam_edge'] = m_surface('lam_edge', (0.2, 0.205, 0.21), rough=0.45)
    M['lam_white'] = m_surface('lam_white', (0.8, 0.8, 0.78), rough=0.5, var=0.015)
    M['compact'] = m_surface('compact', (0.045, 0.048, 0.052), rough=0.38, var=0.06, bump=0.01)
    M['compact_edge'] = m_surface('compact_edge', (0.03, 0.028, 0.026), rough=0.55, var=0.1)
    M['lino'] = m_surface('lino', (0.085, 0.1, 0.098), rough=0.72, var=0.08, grain=400, bump=0.03)
    M['ply_edge'] = m_ply_edge('ply_edge')
    M['birch'] = m_birch('birch')
    principled(M['birch']).inputs['Roughness'].default_value = 0.55
    M['galva'] = m_galva('galva')
    M['cast'] = m_galva('cast', base=(0.42, 0.43, 0.44), cast=True)
    M['alu'] = m_surface('alu', (0.78, 0.79, 0.8), rough=0.32, var=0.02, grain=1500, bump=0.005, metal=1.0)
    M['alu_dark'] = mat_color('alu_dark', (0.25, 0.26, 0.27), rough=0.4, metal=1.0)
    M['perf_white'] = m_tiled_alpha('perf_white', os.path.join(TEXB, 'perfore-alpha.png'), 0.19, (0.78, 0.78, 0.76), rough=0.38, metal=0.15)
    M['perf_black'] = m_tiled_alpha('perf_black', os.path.join(TEXB, 'perfore-alpha.png'), 0.19, (0.022, 0.022, 0.024), rough=0.45, metal=0.25)
    M['led'] = mat_emit('led', (0.92, 0.95, 1.0), 6.0)
    M['socket'] = mat_color('socket', (0.08, 0.08, 0.085), rough=0.5)
    M.update(old)


# ------------------------------------------------------------------ concepts (desk frame: x along the desk, y towards the back, z up)
H0, H1 = 0.74, 0.64          # main top, return top
RX, RY, RW, RD = 1.85, 0.1, 1.2, 0.6


def grommet(x, y, z):
    cyl('grommet', 0.04, 0.004, (x, y, z + 0.001), M['black'], verts=40)
    cyl('grommet_hole', 0.03, 0.005, (x, y, z + 0.0015), M['rubber'], verts=40)


def concept_A():
    """Grey laminate and white steel, the closest to Birdcage."""
    t = 0.025
    bx('A_top', (2.4, 0.8, t), (0, 0, H0 - t / 2), M['lam_grey'], side=M['lam_edge'], bev=0.0012)
    grommet(0.78, 0.3, H0)
    # left unit: open steel box with a middle shelf
    for x in (-1.185, -0.715):
        bx('A_side', (0.018, 0.72, H0 - t), (x, 0, (H0 - t) / 2), M['white_pc'], bev=0.002)
    for z in (0.05, 0.37):
        bx('A_shelf', (0.452, 0.7, 0.018), (-0.95, 0.005, z), M['white_pc'], bev=0.002)
    bx('A_back', (0.47, 0.012, H0 - t - 0.06), (-0.95, 0.354, (H0 - t) / 2 + 0.02), M['white_pc'], bev=0.0015)
    # right T-leg
    bx('A_leg', (0.08, 0.04, H0 - t - 0.06), (1.08, 0.0, (H0 - t) / 2), M['white_pc'], bev=0.003)
    bx('A_legfoot', (0.06, 0.7, 0.03), (1.08, 0.0, 0.035), M['white_pc'], bev=0.004)
    bx('A_legtop', (0.06, 0.7, 0.03), (1.08, 0.0, H0 - t - 0.015), M['white_pc'], bev=0.004)
    for y in (-0.33, 0.33):
        foot(1.08, y, M['rubber'])
    for y in (-0.25, 0.25):
        bx('A_beam', (1.78, 0.04, 0.03), (0.18, y, H0 - t - 0.015), M['white_pc'], bev=0.002)
    # perforated modesty panel and cable tray
    bx('A_modesty', (1.76, 0.003, 0.32), (0.18, 0.34, H0 - t - 0.2), M['perf_white'], bev=0)
    bx('A_tray', (1.3, 0.12, 0.003), (0.3, 0.24, 0.6), M['white_pc'], bev=0)
    bx('A_tray_lip', (1.3, 0.003, 0.06), (0.3, 0.18, 0.628), M['white_pc'], bev=0)
    # return: same laminate on a light white frame
    bx('A_rtop', (RW, RD, t), (RX, RY, H1 - t / 2), M['lam_grey'], side=M['lam_edge'], bev=0.0012)
    for sx in (-1, 1):
        for sy in (-1, 1):
            bx('A_rleg', (0.035, 0.035, H1 - t), (RX + sx * (RW / 2 - 0.05), RY + sy * (RD / 2 - 0.05), (H1 - t) / 2), M['white_pc'], bev=0.002)
        bx('A_rapron', (0.025, RD - 0.1, 0.05), (RX + sx * (RW / 2 - 0.05), RY, H1 - t - 0.025), M['white_pc'], bev=0.0015)
    for sy in (-1, 1):
        bx('A_rapron', (RW - 0.1, 0.025, 0.05), (RX, RY + sy * (RD / 2 - 0.05), H1 - t - 0.025), M['white_pc'], bev=0.0015)
    # back shelf on two clamped uprights
    for x in (-0.82, 1.02):
        bx('A_up', (0.04, 0.012, 0.42), (x, 0.394, H0 + 0.16), M['white_pc'], bev=0.0015)
        bx('A_clamp', (0.05, 0.05, 0.05), (x, 0.38, H0 - t - 0.03), M['white_pc'], bev=0.003)
        bx('A_bracket', (0.012, 0.24, 0.035), (x, 0.28, H0 + 0.31), M['white_pc'], bev=0.0015)
    bx('A_shelf_top', (1.9, 0.24, 0.02), (0.1, 0.28, H0 + 0.338), M['lam_grey'], side=M['lam_edge'], bev=0.0012)


def top_panel(name, size, ztop, xy, lino):
    """A top: compact laminate, or slate linoleum glued on birch plywood (the D top)."""
    w, d, t = size
    if lino:
        bx(name + '_core', (w, d, t - 0.0025), (xy[0], xy[1], ztop - 0.0025 - (t - 0.0025) / 2), M['birch'], side=M['ply_edge'], bev=0.0035, seg=3)
        bx(name + '_lino', (w - 0.006, d - 0.006, 0.0025), (xy[0], xy[1], ztop - 0.00125), M['lino'], bev=0.0004)
    else:
        bx(name, (w, d, t), (xy[0], xy[1], ztop - t / 2), M['compact'], side=M['compact_edge'], bev=0.001)


def concept_B(lino=False):
    """Laboratory bench: C frames, anthracite compact top (or the D linoleum top), superstructure with a power rail and a light under the shelf."""
    t = 0.025 if lino else 0.016
    top_panel('B_top', (2.4, 0.8, t), H0, (0, 0), lino)

    def cframe(x, h, depth=0.7):
        bx('B_post', (0.06, 0.06, h - t - 0.04), (x, 0.3, (h - t) / 2), M['grey_pc'], bev=0.004)
        bx('B_arm', (0.05, depth - 0.04, 0.04), (x, -0.02, h - t - 0.02), M['grey_pc'], bev=0.004)
        bx('B_foot', (0.06, depth, 0.045), (x, -0.02, 0.04), M['grey_pc'], bev=0.006)
        for y in (-0.34, 0.3):
            foot(x, y, M['rubber'], h=0.018)
    for x in (-1.12, 0.0, 1.12):
        cframe(x, H0)
    bx('B_rail', (2.24, 0.03, 0.06), (0, 0.33, H0 - t - 0.2), M['grey_pc'], bev=0.003)
    # superstructure
    for x in (-1.12, 1.12):
        bx('B_up', (0.05, 0.05, 0.62), (x, 0.355, H0 + 0.31), M['grey_pc'], bev=0.004)
        bx('B_bracket', (0.02, 0.28, 0.05), (x, 0.24, H0 + 0.42), M['grey_pc'], bev=0.003)
    bx('B_cross', (2.29, 0.05, 0.05), (0, 0.355, H0 + 0.6), M['grey_pc'], bev=0.004)
    top_panel('B_shelf', (2.3, 0.3, t), H0 + 0.453 + t / 2, (0, 0.24), lino)
    bx('B_powerrail', (2.19, 0.05, 0.07), (0, 0.355, H0 + 0.17), M['alu'], bev=0.003)
    for i in range(8):
        x = -0.875 + i * 0.25
        bx('B_socket', (0.05, 0.006, 0.05), (x, 0.328, H0 + 0.17), M['socket'], bev=0.003)
        for dx in (-0.009, 0.009):
            cyl('B_pin', 0.0028, 0.004, (x + dx, 0.325, H0 + 0.17), M['black'], rot=(rad(90), 0, 0), verts=10)
    bx('B_led', (2.1, 0.02, 0.008), (0, 0.12, H0 + 0.441), M['led'], bev=0)
    bx('B_led_housing', (2.12, 0.026, 0.014), (0, 0.12, H0 + 0.452), M['alu'], bev=0.001)
    # return
    top_panel('B_rtop', (RW, RD, t), H1, (RX, RY), lino)
    for x in (RX - RW / 2 + 0.07, RX + RW / 2 - 0.07):
        bx('B_rpost', (0.06, 0.06, H1 - t - 0.04), (x, RY + 0.22, (H1 - t) / 2), M['grey_pc'], bev=0.004)
        bx('B_rarm', (0.05, RD - 0.06, 0.04), (x, RY - 0.01, H1 - t - 0.02), M['grey_pc'], bev=0.004)
        bx('B_rfoot', (0.06, RD - 0.02, 0.045), (x, RY - 0.01, 0.04), M['grey_pc'], bev=0.006)
        for y in (RY - 0.26, RY + 0.22):
            foot(x, y, M['rubber'], h=0.018)


def fitting(p, axes, r=0.0213):
    """Cast clamp fitting at a tube junction: a sleeve along each axis given."""
    for ax in axes:
        a = Vector(p) - Vector(ax) * 0.035
        b = Vector(p) + Vector(ax) * 0.035
        tb('C_fit', a, b, r + 0.0075, M['cast'], verts=24)
    cyl('C_grub', 0.006, 0.012, Vector(p) + Vector((0, -r - 0.012, 0)), M['black'], rot=(rad(90), 0, 0), verts=6)


def concept_C():
    """Galvanised scaffold tubes with cast fittings, birch plywood top with visible plies."""
    t = 0.036
    r = 0.0213
    bx('C_top', (2.4, 0.8, t), (0, 0, H0 - t / 2), M['birch'], side=M['ply_edge'], bev=0.002)
    zt = H0 - t - r - 0.008
    legs = [(-1.12, -0.34), (1.12, -0.34), (-1.12, 0.34), (1.12, 0.34), (0.0, 0.34)]
    for (x, y) in legs:
        top = 1.12 if (y > 0 and abs(x) > 1) else zt + 0.03
        tb('C_leg', (x, y, 0.012), (x, y, top), r, M['galva'])
        cyl('C_flange', 0.055, 0.01, (x, y, 0.005), M['cast'], verts=32)
        cyl('C_flange_sock', 0.03, 0.05, (x, y, 0.035), M['cast'], verts=24)
        fitting((x, y, zt), [(0, 0, 1)])
    for y in (-0.34, 0.34):
        tb('C_rail', (-1.12, y, zt), (1.12, y, zt), r, M['galva'])
    for x in (-1.12, 1.12):
        tb('C_side', (x, -0.34, zt), (x, 0.34, zt), r, M['galva'])
        tb('C_side_low', (x, -0.34, 0.14), (x, 0.34, 0.14), r, M['galva'])
        for y in (-0.34, 0.34):
            fitting((x, y, 0.14), [(0, 1, 0)])
    tb('C_back_low', (-1.12, 0.34, 0.14), (1.12, 0.34, 0.14), r, M['galva'])
    # shelf on the extended back legs
    tb('C_shelf_bar', (-1.12, 0.34, 1.12), (1.12, 0.34, 1.12), r, M['galva'])
    for x in (-1.12, 1.12):
        fitting((x, 0.34, 1.12), [(1, 0, 0)])
        tb('C_shelf_arm', (x, 0.34, 1.02), (x, 0.12, 1.02), r, M['galva'])
        fitting((x, 0.34, 1.02), [(0, 1, 0)])
        cyl('C_cap', r + 0.003, 0.012, (x, 0.12, 1.02), M['cast'], rot=(rad(90), 0, 0), verts=24)
    bx('C_shelf', (2.32, 0.26, 0.018), (0, 0.23, 1.02 + r + 0.009), M['birch'], side=M['ply_edge'], bev=0.0015)
    # return
    bx('C_rtop', (RW, RD, t), (RX, RY, H1 - t / 2), M['birch'], side=M['ply_edge'], bev=0.002)
    zr = H1 - t - r - 0.008
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = RX + sx * (RW / 2 - 0.07), RY + sy * (RD / 2 - 0.07)
            tb('C_rleg', (x, y, 0.012), (x, y, zr + 0.03), r, M['galva'])
            cyl('C_flange', 0.055, 0.01, (x, y, 0.005), M['cast'], verts=32)
            fitting((x, y, zr), [(0, 0, 1)])
        tb('C_rside', (RX + sx * (RW / 2 - 0.07), RY - RD / 2 + 0.07, zr), (RX + sx * (RW / 2 - 0.07), RY + RD / 2 - 0.07, zr), r, M['galva'])
    for sy in (-1, 1):
        tb('C_rrail', (RX - RW / 2 + 0.07, RY + sy * (RD / 2 - 0.07), zr), (RX + RW / 2 - 0.07, RY + sy * (RD / 2 - 0.07), zr), r, M['galva'])


def concept_D():
    """Thin black steel, slate linoleum on plywood, folded perforated steel riser."""
    t = 0.022
    bx('D_core', (2.4, 0.8, t), (0, 0, H0 - 0.0025 - t / 2), M['birch'], side=M['ply_edge'], bev=0.0035, seg=3)
    bx('D_lino', (2.394, 0.794, 0.0025), (0, 0, H0 - 0.00125), M['lino'], bev=0.0004)
    s = 0.03
    zt = H0 - t - 0.0025
    for x in (-1.16, 1.16):
        for y in (-0.36, 0.36):
            bx('D_leg', (s, s, zt), (x, y, zt / 2), M['black_pc'], bev=0.002)
            foot(x, y, M['rubber'], h=0.012, r=0.014)
    for y in (-0.36, 0.36):
        bx('D_apron', (2.32 - s, s, 0.06), (0, y, zt - 0.03), M['black_pc'], bev=0.0015)
    for x in (-1.16, 1.16):
        bx('D_apron', (s, 0.72 - s, 0.06), (x, 0, zt - 0.03), M['black_pc'], bev=0.0015)
    # perforated cable tray
    bx('D_tray', (1.4, 0.14, 0.002), (0.25, 0.25, zt - 0.12), M['perf_black'], bev=0)
    bx('D_tray_lip', (1.4, 0.002, 0.07), (0.25, 0.18, zt - 0.085), M['perf_black'], bev=0)
    # folded perforated riser on the desk
    zr = H0 + 0.3
    bx('D_riser_top', (1.9, 0.24, 0.003), (0.1, 0.27, zr), M['perf_black'], bev=0)
    for x in (-0.85, 1.05):
        bx('D_riser_side', (0.003, 0.24, 0.3), (x, 0.27, H0 + 0.15), M['black_pc'], bev=0.0008)
    bx('D_riser_back', (1.9, 0.003, 0.09), (0.1, 0.389, zr - 0.045), M['black_pc'], bev=0.0008)
    bx('D_riser_lip', (1.9, 0.003, 0.025), (0.1, 0.151, zr + 0.0125), M['black_pc'], bev=0.0008)
    # return
    bx('D_rcore', (RW, RD, t), (RX, RY, H1 - 0.0025 - t / 2), M['birch'], side=M['ply_edge'], bev=0.0035, seg=3)
    bx('D_rlino', (RW - 0.006, RD - 0.006, 0.0025), (RX, RY, H1 - 0.00125), M['lino'], bev=0.0004)
    zr2 = H1 - t - 0.0025
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = RX + sx * (RW / 2 - 0.04), RY + sy * (RD / 2 - 0.04)
            bx('D_rleg', (s, s, zr2), (x, y, zr2 / 2), M['black_pc'], bev=0.002)
        bx('D_rapron', (s, RD - 0.08 - s, 0.05), (RX + sx * (RW / 2 - 0.04), RY, zr2 - 0.025), M['black_pc'], bev=0.0015)
    for sy in (-1, 1):
        bx('D_rapron', (RW - 0.08 - s, s, 0.05), (RX, RY + sy * (RD / 2 - 0.04), zr2 - 0.025), M['black_pc'], bev=0.0015)


def concept_E():
    """Slotted aluminium extrusions, matte white top, rail and shelf on the back posts."""
    t = 0.02
    bx('E_top', (2.4, 0.8, t), (0, 0, H0 - t / 2), M['lam_white'], side=M['black'], bev=0.0012)
    zt = H0 - t - 0.02
    for x in (-1.16, 1.16):
        for y in (-0.36, 0.36):
            top = 1.22 if y > 0 else zt + 0.02
            profile_between('E_post', (x, y, 0.03), (x, y, top), M['alu'])
            foot(x, y, M['black'], h=0.03, r=0.02)
            bx('E_cap', (0.04, 0.04, 0.004), (x, y, top + 0.002), M['black'], bev=0.001) if y > 0 else None
        profile_between('E_side', (x, -0.34, zt), (x, 0.34, zt), M['alu'])
        profile_between('E_side_low', (x, -0.34, 0.1), (x, 0.34, 0.1), M['alu'])
    for y in (-0.36, 0.36):
        profile_between('E_long', (-1.14, y, zt), (1.14, y, zt), M['alu'])
    profile_between('E_rail', (-1.14, 0.36, 1.2), (1.14, 0.36, 1.2), M['alu'])
    profile_between('E_rail_mid', (-1.14, 0.36, 1.0), (1.14, 0.36, 1.0), M['alu'])
    for x in (-1.16, 1.16):
        for (y, z) in [(-0.36, zt), (0.36, zt), (-0.36, 0.1), (0.36, 0.1)]:
            for d in ((0, 1 if y < 0 else -1), (1 if x < 0 else -1, 0)):
                bx('E_gusset', (0.035, 0.035, 0.035), (x + d[0] * 0.04, y + d[1] * 0.04, z - 0.04), M['alu_dark'], rot=(0, 0, 0), bev=0.002)
    for x in (-0.6, 0.2, 0.9):
        bx('E_bracket', (0.006, 0.22, 0.04), (x, 0.24, 1.035), M['alu_dark'], bev=0.001)
    bx('E_shelf', (2.2, 0.24, 0.004), (0, 0.23, 1.058), M['alu'], bev=0.0008)
    # return
    bx('E_rtop', (RW, RD, t), (RX, RY, H1 - t / 2), M['lam_white'], side=M['black'], bev=0.0012)
    zr = H1 - t - 0.02
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = RX + sx * (RW / 2 - 0.04), RY + sy * (RD / 2 - 0.04)
            profile_between('E_rpost', (x, y, 0.03), (x, y, zr + 0.02), M['alu'])
            foot(x, y, M['black'], h=0.03, r=0.02)
        profile_between('E_rside', (RX + sx * (RW / 2 - 0.04), RY - RD / 2 + 0.06, zr), (RX + sx * (RW / 2 - 0.04), RY + RD / 2 - 0.06, zr), M['alu'])
    for sy in (-1, 1):
        profile_between('E_rlong', (RX - RW / 2 + 0.06, RY + sy * (RD / 2 - 0.04), zr), (RX + RW / 2 - 0.06, RY + sy * (RD / 2 - 0.04), zr), M['alu'])


BUILD = {'A': concept_A, 'B': concept_B, 'C': concept_C, 'D': concept_D, 'E': concept_E, 'BD': lambda: concept_B(lino=True)}


# ------------------------------------------------------------------ label and marking study
def label_study():
    names = ['blanc', 'noir', 'jaune', 'bleu']
    M['floorc'] = mat_pbr('floorc', 'hangar_concrete_floor', 2.0, dark=0.7)
    bx('L_floor', (4.4, 1.6, 0.03), (1.35, 0.1, 0.015), M['floorc'], bev=0.003)
    cable = M['rubber']
    curve_cable('L_cable', [(-0.9, -0.42, 0.037), (0.5, -0.4, 0.037), (1.4, -0.44, 0.037), (2.5, -0.41, 0.037), (3.6, -0.43, 0.037)], 0.007, cable)
    for i, nm in enumerate(names):
        x = i * 0.9
        # small steel pedestal with three drawers
        bx('L_ped', (0.42, 0.5, 0.6), (x, 0.25, 0.33), M['ped'], bev=0.003)
        for k in range(3):
            z = 0.13 + k * 0.18
            bx('L_drawer', (0.4, 0.012, 0.165), (x, -0.003, z + 0.0825 - 0.06), M['ped'], bev=0.003)
            bx('L_pull', (0.16, 0.012, 0.012), (x, -0.016, z + 0.12), M['alu'], bev=0.003)
            w = 0.11
            lm = m_label(f'lab_{nm}_{k}', os.path.join(TEXB, f'etiquette-{nm}-{k}.png'), os.path.join(TEXB, f'etiquette-{nm}-{k}-relief.png'))
            plane('L_label', w, w * 150 / 900, (x - 0.08, -0.0105, z + 0.075), lm, rot=(rad(90), 0, rad(R.uniform(-1.5, 1.5))))
        # floor marking strip in front, and cable tape across the cable
        fm = m_label(f'floor_{nm}', os.path.join(TEXB, f'marquage-{nm}.png'), rough=0.55, alpha=True)
        plane('L_mark', 0.8, 0.05, (x, -0.62, 0.0305), fm, rot=(0, 0, rad(R.uniform(-0.6, 0.6))))
        ct = m_surface(f'tape_{nm}', tuple(c / 255 for c in PAL_RGB[nm]), rough=0.5, var=0.06, grain=600, bump=0.02)
        bx('L_ctape', (0.05, 0.075, 0.0012), (x, -0.42, 0.0378), ct, bev=0.0004)
        bx('L_ctape_wrap', (0.05, 0.02, 0.012), (x, -0.42, 0.039), ct, bev=0.003)


PAL_RGB = {'blanc': (225, 225, 220), 'noir': (24, 24, 26), 'jaune': (226, 182, 24), 'bleu': (36, 86, 168)}


# ------------------------------------------------------------------ studio
def studio(dark=0.06):
    bm = bmesh.new()
    rr, cy = 1.6, 3.0
    prof = [(-7.0, 0.0)] + [(cy + rr * math.sin(math.pi / 2 * i / 16), rr - rr * math.cos(math.pi / 2 * i / 16)) for i in range(17)] + [(cy + rr, 7.0)]
    rows = []
    for x in (-9.0, 9.0):
        rows.append([bm.verts.new((x, y, z)) for (y, z) in prof])
    for j in range(len(prof) - 1):
        bm.faces.new((rows[0][j], rows[1][j], rows[1][j + 1], rows[0][j + 1]))
    me = bpy.data.meshes.new('cyclo')
    bm.to_mesh(me)
    bm.free()
    for f in me.polygons:
        f.use_smooth = True
    o = bpy.data.objects.new('cyclo', me)
    o.location = (0.6, 0, 0)
    me.materials.append(m_surface('cyclo', (dark, dark * 1.02, dark * 1.05), rough=0.8, var=0.02, grain=50, bump=0.0))
    ROOT.objects.link(o)
    bg = next(n for n in SC.world.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs['Color'].default_value = (0.02, 0.021, 0.023, 1)
    bg.inputs['Strength'].default_value = 1.0
    add_light('AREA', 'key', (-3.2, -3.6, 4.2), float(OPT.get('key', 260)), (1.0, 0.95, 0.9), target=(0.4, 0.1, 0.6), size=2.4)
    add_light('AREA', 'fill', (4.6, -3.2, 1.8), float(OPT.get('fill', 50)), (0.9, 0.95, 1.0), target=(0.6, 0, 0.6), size=3.0)
    add_light('AREA', 'rim', (1.4, 3.4, 3.4), float(OPT.get('rim', 320)), (0.95, 0.97, 1.0), target=(0.6, 0, 0.9), size=2.0)
    add_light('AREA', 'top', (0.6, -0.4, 4.6), float(OPT.get('top', 50)), (1.0, 1.0, 1.0), target=(0.6, 0, 0), size=3.5)
    add_light('AREA', 'bgl', (0.9, 1.6, 0.4), float(OPT.get('bgl', 120)), (0.92, 0.95, 1.0), target=(1.2, 4.6, 2.2), size=1.5)


SHOTSPEC = {
    'tq': dict(cam=(-2.45, -3.35, 1.85), target=(0.72, 0.1, 0.58), lens=32, fstop=11, focus=None),
    'face': dict(cam=(0.62, -7.2, 1.0), target=(0.62, 0.0, 0.62), lens=64, fstop=16, focus=None),
    'detail': dict(cam=(-1.78, -1.12, 0.98), target=(-1.12, -0.36, 0.66), lens=70, fstop=3.2, focus=None),
    'etiquettes': dict(cam=(1.35, -3.3, 1.2), target=(1.35, 0.0, 0.28), lens=34, fstop=8, focus=None),
    'etq': dict(cam=(-0.5, -1.45, 0.8), target=(-0.04, -0.2, 0.22), lens=40, fstop=4, focus=None),
}


def main_bureau():
    setup_render()
    SC.view_settings.exposure = float(OPT.get('exposure', 0.0))
    try:
        SC.view_settings.look = 'AgX - Medium High Contrast'
    except TypeError:
        pass
    materials_bureau()
    studio()
    colls = {}
    for k in CONCEPTS:
        c = coll('C_' + k)
        CUR[0] = c
        if k == 'L':
            label_study()
        else:
            BUILD[k]()
        colls[k] = c
    os.makedirs(OUT, exist_ok=True)
    if OPT.get('save') == '1':
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'bureau-prototypes.blend'))
    for k in CONCEPTS:
        for k2, c in colls.items():
            c.hide_render = k2 != k
        shots = ['etiquettes', 'etq-0', 'etq-1', 'etq-2', 'etq-3'] if k == 'L' else SHOTS
        for s in shots:
            spec = dict(SHOTSPEC[s.split('-')[0]])
            if s.startswith('etq-'):
                dx = 0.9 * int(s[-1])
                spec['cam'] = (spec['cam'][0] + dx, spec['cam'][1], spec['cam'][2])
                spec['target'] = (spec['target'][0] + dx, spec['target'][1], spec['target'][2])
            cam = make_camera(spec, f'CAM_{k}_{s}')
            SC.camera = cam
            SC.render.resolution_x = RES
            SC.render.resolution_y = int(RES * 9 / 16)
            SC.render.filepath = os.path.join(OUT, f'{k}-{s}.png')
            print('RENDER', SC.render.filepath, flush=True)
            bpy.ops.render.render(write_still=True)


main_bureau()
