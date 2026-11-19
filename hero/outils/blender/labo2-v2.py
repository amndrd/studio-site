

# ====================================================================== V2 : the contemporary lab
# Concatenated after labo2-base.py into labo2.py (see build note at the top of labo2.py).
M = {}

def mat_glass(name, tint=(0.92, 0.96, 0.96), rough=0.02):
    m = new_mat(name)
    p = principled(m)
    p.inputs['Base Color'].default_value = (*tint, 1)
    p.inputs['Transmission Weight'].default_value = 1.0
    p.inputs['Roughness'].default_value = rough
    p.inputs['IOR'].default_value = 1.45
    return m


def mat_alpha_image(path, rough=0.6, emit=0.0):
    key = 'alpha_' + os.path.basename(path)
    if key in bpy.data.materials:
        return bpy.data.materials[key]
    m = new_mat(key)
    nt = m.node_tree
    p = principled(m)
    t = nt.nodes.new('ShaderNodeTexImage')
    t.image = img(path)
    nt.links.new(t.outputs['Color'], p.inputs['Base Color'])
    nt.links.new(t.outputs['Alpha'], p.inputs['Alpha'])
    p.inputs['Roughness'].default_value = rough
    return m


def materials2():
    M['wall'] = mat_pbr('wall', 'concrete_slab_wall', 3.2, dark=0.4, tint=(0.95, 0.97, 1.0))
    M['ceil'] = mat_pbr('ceil', 'concrete_slab_wall', 3.0, dark=0.4)
    M['col'] = mat_pbr('col', 'concrete_slab_wall', 2.2, dark=0.45)
    M['floor'] = mat_pbr('floor', 'brushed_concrete', 3.0, dark=0.55, tint=(0.9, 0.92, 0.95), rough_add=-0.32, bump=0.5)
    M['walnut'] = mat_pbr('walnut', 'black_walnut_veneer_01', 1.4, dark=0.38, tint=(1.0, 0.86, 0.72))
    M['oak'] = mat_pbr('oak', 'oak_veneer_01', 1.4, dark=0.95)
    M['black'] = mat_color('black', (0.016, 0.016, 0.018), rough=0.42, metal=0.3)
    M['black_m'] = mat_color('black_m', (0.022, 0.022, 0.024), rough=0.75)
    M['graphite'] = mat_color('graphite', (0.06, 0.062, 0.066), rough=0.5, metal=0.2)
    M['alu'] = mat_color('alu', (0.72, 0.73, 0.75), rough=0.28, metal=1.0)
    M['steel'] = mat_color('steel', (0.2, 0.2, 0.21), rough=0.35, metal=0.9)
    M['white'] = mat_color('white', (0.78, 0.78, 0.77), rough=0.5)
    M['fan'] = mat_color('fan', (0.6, 0.61, 0.6), rough=0.45)
    M['fabric'] = mat_color('fabric', (0.03, 0.03, 0.034), rough=0.92)
    M['rug'] = mat_color('rug', (0.045, 0.045, 0.05), rough=0.96)
    M['glass'] = mat_glass('glass')
    M['glass_dark'] = mat_glass('glass_dark', (0.5, 0.53, 0.56), 0.04)
    M['rubber'] = mat_color('rubber', (0.012, 0.012, 0.013), rough=0.55)
    M['orange'] = mat_color('orange', (0.85, 0.24, 0.05), rough=0.4)
    M['pot_white'] = mat_color('pot_white', (0.72, 0.71, 0.68), rough=0.6)
    M['pot_concrete'] = mat_pbr('pot_concrete', 'brushed_concrete', 0.6, dark=0.75)
    M['white_hot'] = mat_emit('white_hot', (0.92, 0.96, 1.0), float(OPT.get('hot', 6.0)))
    M['panel'] = mat_emit('panel', (0.93, 0.96, 1.0), float(OPT.get('panel', 3.2)))
    M['table_light'] = mat_emit('table_light', (0.95, 0.97, 1.0), float(OPT.get('tablew', 0.95)))
    M['led_strip'] = mat_emit('led_strip', (0.85, 0.93, 1.0), 25.0)
    M['blue_strip'] = mat_emit('blue_strip', (0.15, 0.45, 1.0), 30.0)
    M['led_red'] = mat_emit('led_red', (1.0, 0.03, 0.01), 160.0)
    M['printer_light'] = mat_emit('printer_light', (1.0, 0.95, 0.88), 12.0)
    M['tube_cold'] = mat_emit('tube_cold', (0.8, 0.92, 1.0), 18.0)


# ------------------------------------------------------------------ fan v2 (turbine)
def turbine_blade(r0, r1, w0, w1, p0, p1, sweep, n=18):
    bm = bmesh.new()
    rows = []
    for i in range(n + 1):
        t = i / n
        r = r0 + (r1 - r0) * t
        w = w0 + (w1 - w0) * math.sin(t * math.pi * 0.62)
        if t > 0.9:
            w *= 1 - ((t - 0.9) / 0.1) ** 2 * 0.35
        p = rad(p0 + (p1 - p0) * t)
        phi = sweep * t ** 1.4
        row = []
        for s in (-0.5, -0.2, 0.2, 0.5):
            camber = 0.05 * w * (1 - (2 * s) ** 2)
            z = s * w * math.cos(p)
            y = s * w * math.sin(p) - camber
            x = r
            xr = x * math.cos(phi) + z * math.sin(phi)
            zr = -x * math.sin(phi) + z * math.cos(phi)
            row.append(bm.verts.new((xr, y, zr)))
        rows.append(row)
    for i in range(n):
        for k in range(3):
            bm.faces.new((rows[i][k], rows[i + 1][k], rows[i + 1][k + 1], rows[i][k + 1]))
    me = bpy.data.meshes.new('tblade')
    bm.to_mesh(me)
    bm.free()
    for f in me.polygons:
        f.use_smooth = True
    return me


def turbine(center, R, n=10, angle=0.0):
    cx, cy, cz = center
    ring('shroud', R - 0.04, R + 0.05, 0.9, (cx, cy + 0.3, cz), M['fan'])
    ring('shroud_lip', R - 0.06, R + 0.12, 0.08, (cx, cy - 0.15, cz), M['fan'])
    me = turbine_blade(0.66, R - 0.07, 0.55, 1.05, float(OPT.get('p0', 66)), float(OPT.get('p1', 50)), rad(26))
    me.materials.append(M['fan'])
    for k in range(n):
        o = bpy.data.objects.new('tblade', me)
        o.location = (cx, cy + 0.25, cz)
        o.rotation_euler = (0, -(angle + 2 * math.pi * k / n), 0)
        sm = o.modifiers.new('solid', 'SOLIDIFY')
        sm.thickness = 0.035
        bv = o.modifiers.new('bev', 'BEVEL')
        bv.width = 0.012
        bv.segments = 2
        link(o)
    # spinner and hub
    sp = bpy.data.objects.new('spinner', bpy.data.meshes.new('spinner'))
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=0.68)
    for v in bm.verts:
        v.co.y = v.co.y * (1.25 if v.co.y < 0 else 0.15)
    bm.to_mesh(sp.data)
    bm.free()
    for f in sp.data.polygons:
        f.use_smooth = True
    sp.data.materials.append(M['fan'])
    sp.location = (cx, cy + 0.2, cz)
    link(sp)
    cyl('hub', 0.68, 0.6, (cx, cy + 0.5, cz), M['fan'], rot=(rad(90), 0, 0), verts=64)
    cyl('motor', 0.55, 1.0, (cx, cy + 1.1, cz), M['graphite'], rot=(rad(90), 0, 0), verts=48)
    for k in range(3):
        a = rad(90 + 120 * k)
        tube_between('stator', (cx + 0.5 * math.cos(a), cy + 1.1, cz + 0.5 * math.sin(a)),
                     (cx + R * math.cos(a), cy + 1.1, cz + R * math.sin(a)), 0.045, M['graphite'], verts=10)


# ------------------------------------------------------------------ architecture v2
def hall(W, D, H, fc, Rf):
    box('floor', (W + 2, D + 4, 0.2), (0, D / 2, -0.1), M['floor'], c=C_ARCH)
    box('slab', (W + 2, D + 4, 0.4), (0, D / 2, H + 0.2), M['ceil'], c=C_CEIL)
    box('wall_L', (0.5, D + 4, H), (-W / 2 - 0.25, D / 2, H / 2), M['wall'], c=C_ARCH)
    box('wall_R', (0.5, D + 4, H), (W / 2 + 0.25, D / 2, H / 2), M['wall'], c=C_ARCH)
    box('wall_F', (W + 2, 0.5, H), (0, -2.25, H / 2), M['wall'], c=C_ARCH)
    wall_with_hole('wall_B', -W / 2 - 0.5, W / 2 + 0.5, D, D + 1.2, 0, H, fc, Rf + 0.22, M['wall'])
    ring('reveal', Rf + 0.2, Rf + 0.24, 1.2, (fc[0], D + 0.6, fc[2]), M['col'], c=C_ARCH)
    # concrete frame: columns, beams across and along
    for y in (5.0, 10.0, 15.0):
        box('beam_x', (W, 0.45, 0.7), (0, y, H - 0.35), M['col'], c=C_CEIL)
        for s in (-1, 1):
            box('column', (0.6, 0.6, H), (s * 5.2, y, H / 2), M['col'], bevel=0.01, c=C_ARCH)
    for s in (-1, 1):
        box('beam_y', (0.45, D, 0.7), (s * 5.2, D / 2, H - 0.35), M['col'], c=C_CEIL)
    # services under the slab: black pipes, a galvanised duct, cable trays
    for (x, r, z) in [(-2.8, 0.11, H - 0.95), (-2.45, 0.07, H - 0.9), (-2.15, 0.07, H - 0.9), (2.4, 0.09, H - 0.92)]:
        cyl('pipe', r, D + 2, (x, D / 2, z), M['black'], rot=(rad(90), 0, 0), verts=20, c=C_CEIL)
    cyl('duct', 0.36, D + 2, (3.3, D / 2, H - 1.2), M['alu'], rot=(rad(90), 0, 0), verts=36, c=C_CEIL)
    for x in (-6.6, 6.6):
        box('tray', (0.4, D, 0.06), (x, D / 2, H - 1.1), M['steel'], c=C_CEIL)
        for k in range(4):
            cyl('trayc', 0.025, D, (x - 0.12 + 0.08 * k, D / 2, H - 1.05), M['rubber'], rot=(rad(90), 0, 0), verts=8, c=C_CEIL)
    for y in [2.5, 7.5, 12.5, 17.5]:
        for x in (-2.8, 3.3):
            box('hanger', (0.03, 0.03, 0.5), (x, y, H - 0.5), M['black'], c=C_CEIL)


def light_ceiling(cx, cy, w, d, z, cell=(1.2, 0.6), name='lc'):
    """Large suspended light box with a grid of panels (the 'bunker' ceiling)."""
    plane(name + '_emit', w, d, (cx, cy, z + 0.02), M['panel'], rot=(rad(180), 0, 0), c=C_FX)
    box(name + '_top', (w + 0.12, d + 0.12, 0.04), (cx, cy, z + 0.12), M['black'])
    for s in (-1, 1):
        box(name + '_side', (w + 0.12, 0.04, 0.16), (cx, cy + s * (d / 2 + 0.04), z + 0.06), M['black'])
        box(name + '_side', (0.04, d + 0.12, 0.16), (cx + s * (w / 2 + 0.04), cy, z + 0.06), M['black'])
    nx, ny = max(1, round(w / cell[0])), max(1, round(d / cell[1]))
    for i in range(1, nx):
        box(name + '_bar', (0.03, d, 0.04), (cx - w / 2 + i * w / nx, cy, z), M['black'])
    for j in range(1, ny):
        box(name + '_bar', (w, 0.03, 0.04), (cx, cy - d / 2 + j * d / ny, z), M['black'])
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(name + '_rod', (0.015, 0.015, 7.0 - z), (cx + sx * (w / 2 - 0.3), cy + sy * (d / 2 - 0.3), (7.0 + z) / 2 + 0.06), M['black'])


# ------------------------------------------------------------------ furniture and tech (modelled)
def monitor(F, lx, ly, lz, w, h, rz, screen, strength=2.0):
    rr = F.r + rz
    box('mon_back', (w + 0.014, 0.025, h + 0.014), F.p(lx, ly, lz), M['black'], rot=(0, 0, rr), bevel=0.004)
    c, s_ = math.cos(rr), math.sin(rr)
    off = Vector((-(-0.0135) * s_, (-0.0135) * c))
    p = F.p(lx, ly, lz) + Vector((off.x, off.y, 0))
    plane('mon_screen', w, h, p, mat_screen(screen, strength), rot=(rad(90), 0, rr), c=C_FX)
    return p


def desk_v2(F):
    """Central desk. The user sits at local -Y and faces +Y; screens face -Y."""
    W, D, h = 2.8, 1.0, 0.74
    box('desk_top', (W, D, 0.035), F.p(0, 0, h - 0.0175), M['walnut'], rot=(0, 0, F.r), bevel=0.004)
    for sx in (-1, 1):
        x = sx * (W / 2 - 0.12)
        for sy in (-1, 1):
            box('desk_leg', (0.06, 0.03, h - 0.035), F.p(x, sy * (D / 2 - 0.06), (h - 0.035) / 2), M['black'], rot=(0, 0, F.r))
        box('desk_foot', (0.06, D - 0.06, 0.03), F.p(x, 0, 0.015), M['black'], rot=(0, 0, F.r))
        box('desk_rail', (0.06, D - 0.06, 0.03), F.p(x, 0, h - 0.05), M['black'], rot=(0, 0, F.r))
    box('desk_tray', (W - 0.6, 0.18, 0.08), F.p(0, 0.3, h - 0.1), M['black'], rot=(0, 0, F.r))
    # screens on a common arm
    cyl('arm_pole', 0.02, 0.5, F.p(0, 0.42, h + 0.25), M['black'], verts=16)
    box('arm_bar', (1.5, 0.03, 0.03), F.p(0, 0.38, h + 0.42), M['black'], rot=(0, 0, F.r))
    monitor(F, 0, 0.33, h + 0.43, 0.72, 0.41, 0, os.path.join(TEX2, 'ecran-code.jpg'), 2.2)
    monitor(F, -0.69, 0.22, h + 0.4, 0.6, 0.34, rad(22), os.path.join(TEX2, 'ecran-design.jpg'), 2.0)
    monitor(F, 0.69, 0.22, h + 0.4, 0.6, 0.34, rad(-22), os.path.join(TEX2, 'ecran-3d.jpg'), 2.0)
    # keyboard (array of keys), mouse, laptop, speakers, phone, notebook, mug, plant, lamp
    kb = box('kb', (0.36, 0.12, 0.012), F.p(0, -0.18, h + 0.006), M['alu'], rot=(0, 0, F.r), bevel=0.003)
    key = box('key', (0.018, 0.018, 0.006), F.p(-0.165, -0.225, h + 0.015), M['graphite'], rot=(0, 0, F.r))
    a1 = key.modifiers.new('ax', 'ARRAY')
    a1.count = 15
    a1.relative_offset_displace = (1.25, 0, 0)
    a2 = key.modifiers.new('ay', 'ARRAY')
    a2.count = 5
    a2.relative_offset_displace = (0, 1.25, 0)
    ms = bpy.data.objects.new('mouse', bpy.data.meshes.new('mouse'))
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=0.5)
    for v in bm.verts:
        v.co = Vector((v.co.x * 0.062, v.co.y * 0.11, max(v.co.z, -0.05) * 0.06))
    bm.to_mesh(ms.data)
    bm.free()
    for f in ms.data.polygons:
        f.use_smooth = True
    ms.data.materials.append(M['graphite'])
    ms.location = F.p(0.33, -0.18, h + 0.003)
    ms.rotation_euler = (0, 0, F.r)
    link(ms)
    plane('deskmat', 0.9, 0.38, F.p(0.08, -0.18, h + 0.001), M['fabric'], rot=(0, 0, F.r))
    # laptop on the right, open, on a stand
    lr = F.r + rad(-28)
    box('lap_base', (0.31, 0.22, 0.012), F.p(1.05, -0.08, h + 0.006), M['alu'], rot=(0, 0, lr), bevel=0.003)
    c, s_ = math.cos(lr), math.sin(lr)
    hinge = F.p(1.05, -0.08, h + 0.012) + Vector((-0.11 * -s_, 0.11 * c, 0))
    lid = box('lap_lid', (0.31, 0.006, 0.21), hinge + Vector((0, 0, 0.1)), M['alu'], rot=(rad(-12), 0, lr))
    plane('lap_screen', 0.29, 0.19, hinge + Vector((-0.005 * -s_, -0.005 * c, 0.1)), mat_screen(os.path.join(TEX2, 'ecran-dashboard.jpg'), 1.6), rot=(rad(90 - 12), 0, lr), c=C_FX)
    for sx in (-1, 1):
        box('speaker', (0.1, 0.1, 0.16), F.p(sx * 1.2, 0.3, h + 0.08), M['graphite'], rot=(0, 0, F.r + sx * rad(-12)), bevel=0.01)
    box('phone', (0.075, 0.155, 0.008), F.p(-0.55, -0.25, h + 0.004), M['black'], rot=(0, 0, F.r + rad(14)), bevel=0.004)
    box('notebook', (0.15, 0.21, 0.014), F.p(-0.85, -0.2, h + 0.007), M['black_m'], rot=(0, 0, F.r + rad(-8)))
    box('pen', (0.14, 0.008, 0.008), F.p(-0.84, -0.2, h + 0.018), M['alu'], rot=(0, 0, F.r + rad(30)))
    cyl('mug', 0.042, 0.095, F.p(-1.12, 0.05, h + 0.0475), M['white'], verts=24)
    F.put('potted_plant_04', -1.25, 0.32, h, s=1.1)
    # minimal LED lamp
    cyl('lamp_base', 0.07, 0.015, F.p(1.25, 0.15, h + 0.008), M['black'], verts=24)
    cyl('lamp_pole', 0.008, 0.48, F.p(1.25, 0.15, h + 0.25), M['black'], verts=10)
    box('lamp_head', (0.42, 0.03, 0.016), F.p(1.06, 0.15, h + 0.49), M['black'], rot=(0, 0, F.r))
    box('lamp_led', (0.38, 0.016, 0.003), F.p(1.06, 0.15, h + 0.481), M['led_strip'], rot=(0, 0, F.r))
    add_light('AREA', 'lamp_light', F.p(1.06, 0.12, h + 0.47), 30, (1.0, 0.82, 0.62), target=F.p(1.0, -0.1, h), size=0.38)
    # cable to the floor box
    curve_cable('desk_cable', [F.p(0, 0.35, h - 0.1), F.p(0.2, 0.45, 0.4), F.p(0.3, 0.6, 0.012), F.p(0.6, 1.4, 0.012)], 0.012, M['rubber'])


def mat_mesh():
    if 'chair_mesh' in bpy.data.materials:
        return bpy.data.materials['chair_mesh']
    m = new_mat('chair_mesh')
    nt = m.node_tree
    p = principled(m)
    p.inputs['Base Color'].default_value = (0.035, 0.035, 0.038, 1)
    p.inputs['Roughness'].default_value = 0.7
    tc = nt.nodes.new('ShaderNodeTexCoord')
    ck = nt.nodes.new('ShaderNodeTexChecker')
    ck.inputs['Scale'].default_value = 90.0
    ck.inputs['Color1'].default_value = (1, 1, 1, 1)
    ck.inputs['Color2'].default_value = (0.35, 0.35, 0.35, 1)
    nt.links.new(tc.outputs['UV'], ck.inputs['Vector'])
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['To Min'].default_value = 0.72
    mr.inputs['To Max'].default_value = 1.0
    nt.links.new(ck.outputs['Fac'], mr.inputs['Value'])
    nt.links.new(mr.outputs[0], p.inputs['Alpha'])
    return m


def office_chair(loc, rz):
    """Contemporary task chair: 5-star base, padded seat, curved mesh back in a black frame, lumbar bar, headrest, T-arms."""
    x, y = loc[0], loc[1]
    c, s_ = math.cos(rz), math.sin(rz)

    def P(lx, ly, lz):
        return Vector((x + lx * c - ly * s_, y + lx * s_ + ly * c, lz))
    for k in range(5):
        a = rad(90 + 72 * k)
        end = Vector((0.33 * math.cos(a), 0.33 * math.sin(a)))
        tube_between('chair_leg', P(0, 0, 0.11), P(end.x, end.y, 0.075), 0.022, M['black'], verts=10)
        cyl('caster', 0.03, 0.035, P(end.x, end.y, 0.032), M['black'], rot=(rad(90), 0, rz + a), verts=16)
    cyl('chair_hub', 0.05, 0.06, P(0, 0, 0.11), M['black'], verts=20)
    cyl('chair_gas', 0.024, 0.32, P(0, 0, 0.29), M['alu'], verts=16)
    box('chair_mech', (0.22, 0.24, 0.05), P(0, 0, 0.45), M['black'], rot=(0, 0, rz), bevel=0.01)
    seat = box('chair_seat', (0.5, 0.48, 0.07), P(0, -0.03, 0.51), M['fabric'], rot=(0, 0, rz), bevel=0.02)
    sm = seat.modifiers.new('sub', 'SUBSURF')
    sm.levels = sm.render_levels = 2
    # back: curved black frame (bevelled curve) + mesh panel
    bw, bh, bz, by = 0.46, 0.6, 0.95, 0.27
    cu = bpy.data.curves.new('chair_frame', 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = 0.016
    cu.bevel_resolution = 3
    sp = cu.splines.new('BEZIER')
    pts = []
    for i in range(16):
        t = 2 * math.pi * i / 16
        lx = bw / 2 * math.copysign(abs(math.cos(t)) ** 0.5, math.cos(t))
        lz = bh / 2 * math.copysign(abs(math.sin(t)) ** 0.5, math.sin(t))
        ly = by + 0.06 * (2 * lx / bw) ** 2 + (lz + bh / 2) * 0.08
        pts.append(P(lx, ly, bz + lz))
    sp.bezier_points.add(len(pts) - 1)
    for bp, pp in zip(sp.bezier_points, pts):
        bp.co = pp
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
    sp.use_cyclic_u = True
    fo = bpy.data.objects.new('chair_frame', cu)
    cu.materials.append(M['black'])
    link(fo)
    bm = bmesh.new()
    nu, nv = 12, 10
    grid = []
    for j in range(nv + 1):
        row = []
        for i in range(nu + 1):
            u, v = i / nu - 0.5, j / nv - 0.5
            lx, lz = u * (bw - 0.02), v * (bh - 0.02)
            ly = by + 0.06 * (2 * lx / bw) ** 2 + (lz + bh / 2) * 0.08 + 0.004
            row.append(bm.verts.new(P(lx, ly, bz + lz)))
        grid.append(row)
    for j in range(nv):
        for i in range(nu):
            bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
    me = bpy.data.meshes.new('chair_mesh')
    bm.to_mesh(me)
    bm.free()
    me.uv_layers.new()
    for poly in me.polygons:
        for li in poly.loop_indices:
            vco = me.vertices[me.loops[li].vertex_index].co
            me.uv_layers[0].data[li].uv = (vco.x * 3 + vco.y * 3, vco.z * 3)
    mo = bpy.data.objects.new('chair_mesh', me)
    me.materials.append(mat_mesh())
    link(mo)
    box('chair_lumbar', (0.4, 0.03, 0.06), P(0, by + 0.035, bz - 0.12), M['black'], rot=(rad(-6), 0, rz), bevel=0.012)
    hr = box('chair_head', (0.28, 0.05, 0.12), P(0, by + 0.09, bz + bh / 2 + 0.11), M['fabric'], rot=(rad(-10), 0, rz), bevel=0.02)
    for sx in (-1, 1):
        tube_between('chair_spine', P(sx * 0.12, 0.12, 0.47), P(sx * 0.2, by + 0.02, bz - bh / 2 + 0.02), 0.016, M['black'], verts=8)
        tube_between('chair_head_post', P(sx * 0.1, by + 0.06, bz + bh / 2 - 0.02), P(sx * 0.1, by + 0.085, bz + bh / 2 + 0.06), 0.008, M['black'], verts=8)
        tube_between('chair_arm_post', P(sx * 0.27, 0.0, 0.47), P(sx * 0.27, 0.0, 0.66), 0.016, M['black'], verts=8)
        tube_between('chair_arm_link', P(sx * 0.2, 0.0, 0.46), P(sx * 0.27, 0.0, 0.47), 0.014, M['black'], verts=8)
        box('chair_arm', (0.08, 0.25, 0.028), P(sx * 0.27, -0.03, 0.675), M['black'], rot=(0, 0, rz), bevel=0.012)


def light_table(F, W=3.0, D=1.6, h=0.92):
    box('lt_glow', (W - 0.08, D - 0.08, 0.02), F.p(0, 0, h - 0.01), M['table_light'], rot=(0, 0, F.r), c=C_FX)
    for s in (-1, 1):
        box('lt_rim', (W, 0.04, 0.08), F.p(0, s * (D / 2 - 0.02), h - 0.03), M['alu'], rot=(0, 0, F.r))
        box('lt_rim', (0.04, D, 0.08), F.p(s * (W / 2 - 0.02), 0, h - 0.03), M['alu'], rot=(0, 0, F.r))
    box('lt_body', (W - 0.1, D - 0.1, 0.12), F.p(0, 0, h - 0.09), M['white'], rot=(0, 0, F.r))
    for sx in (-1, 1):
        for sy in (-1, 1):
            box('lt_leg', (0.05, 0.05, h - 0.2), F.p(sx * (W / 2 - 0.1), sy * (D / 2 - 0.1), (h - 0.2) / 2 + 0.08), M['alu'], rot=(0, 0, F.r))
            cyl('lt_caster', 0.04, 0.04, F.p(sx * (W / 2 - 0.1), sy * (D / 2 - 0.1), 0.04), M['black'], rot=(rad(90), 0, F.r), verts=16)
        box('lt_stretch', (0.04, D - 0.2, 0.04), F.p(sx * (W / 2 - 0.1), 0, 0.22), M['alu'], rot=(0, 0, F.r))
    box('lt_stretch', (W - 0.2, 0.04, 0.04), F.p(0, 0, 0.22), M['alu'], rot=(0, 0, F.r))
    add_light('AREA', 'lt_up', F.p(0, 0, h + 0.02), float(OPT.get('ltw', 45)), (0.95, 0.97, 1.0), target=F.p(0, 0, 3.0), size=2.4)
    # projects laid on the glowing top
    z = h + 0.002
    rng = random.Random(5)
    calques = sorted(glob.glob(os.path.join(TEX2, 'calque-*.png')))
    for i, (lx, ly, w) in enumerate([(-0.85, 0.12, 0.95), (0.05, -0.12, 1.0), (0.9, 0.2, 0.8), (-0.25, 0.4, 0.7), (-1.05, -0.35, 0.6)]):
        z += 0.0015
        pth = calques[i % len(calques)]
        im = img(pth)
        o = plane('calque', w, w * im.size[1] / im.size[0], F.p(lx, ly, z), mat_alpha_image(pth), rot=(0, 0, F.r + rng.uniform(-0.3, 0.3)))
    tirages = sorted(glob.glob(os.path.join(TEX2, 'tirage-*.jpg')))
    for i in range(4):
        z += 0.0012
        sheet_world(F.p(-1.2 + 0.55 * i, -0.5 + rng.uniform(-0.08, 0.08), z), F.r + rng.uniform(-0.25, 0.25), 0.2, tirages[i % len(tirages)])
    # tablets and phone with app screens
    for (lx, ly, scr, rr) in [(0.55, -0.45, 'tablette-menu.jpg', -12), (1.15, -0.4, 'tablette-reservation.jpg', 8)]:
        box('tablet', (0.18, 0.25, 0.008), F.p(lx, ly, z + 0.004), M['black'], rot=(0, 0, F.r + rad(rr)), bevel=0.006)
        plane('tablet_screen', 0.165, 0.235, F.p(lx, ly, z + 0.0085), mat_screen(os.path.join(TEX2, scr), 1.4), rot=(0, 0, F.r + rad(rr)), c=C_FX)
    box('lt_phone', (0.072, 0.15, 0.008), F.p(-0.55, -0.48, z + 0.004), M['black'], rot=(0, 0, F.r + rad(25)), bevel=0.004)
    plane('lt_phone_screen', 0.066, 0.142, F.p(-0.55, -0.48, z + 0.0085), mat_screen(os.path.join(TEX2, 'telephone-projets.jpg'), 1.3), rot=(0, 0, F.r + rad(25)), c=C_FX)
    # white architectural model: a little block town on a base
    box('model_base', (0.6, 0.4, 0.02), F.p(1.0, 0.45, z + 0.01), M['white'], rot=(0, 0, F.r + rad(-6)))
    for k in range(14):
        bw, bd, bh = rng.uniform(0.05, 0.12), rng.uniform(0.05, 0.1), rng.uniform(0.03, 0.16)
        box('model_block', (bw, bd, bh), F.p(0.75 + rng.uniform(0, 0.5), 0.3 + rng.uniform(0, 0.3), z + 0.02 + bh / 2), M['white'], rot=(0, 0, F.r + rad(-6)))
    box('lt_ruler', (0.6, 0.03, 0.004), F.p(-0.3, -0.22, z + 0.004), M['alu'], rot=(0, 0, F.r + rad(10)))
    for (lx, ly) in [(-0.8, -1.05), (0.7, -1.05)]:
        put('metal_stool_01', F.p(lx, ly, 0), F.r + rad(rng.uniform(-30, 30)))


def pinboard(loc, rz, prints, strings=True):
    x, y = loc
    c, s_ = math.cos(rz), math.sin(rz)

    def P(lx, ly, lz):
        return Vector((x + lx * c - ly * s_, y + lx * s_ + ly * c, lz))
    for sx in (-1, 1):
        box('pb_post', (0.035, 0.035, 1.95), P(sx * 0.62, 0, 0.975 + 0.06), M['alu'], rot=(0, 0, rz))
        box('pb_foot', (0.05, 0.5, 0.03), P(sx * 0.62, 0, 0.06), M['alu'], rot=(0, 0, rz))
        for sy in (-1, 1):
            cyl('pb_caster', 0.03, 0.03, P(sx * 0.62, sy * 0.22, 0.03), M['black'], rot=(rad(90), 0, rz), verts=12)
    box('pb_board', (1.2, 0.025, 0.95), P(0, 0, 1.45), M['white'], rot=(0, 0, rz))
    rng = random.Random(int(x * 13 + y * 7))
    pins = []
    for i, pth in enumerate(prints):
        w = 0.26 if 'tirage' in pth else 0.32
        lx, lz = rng.uniform(-0.42, 0.42), rng.uniform(1.12, 1.78)
        o = sheet_world(P(lx, -0.016 - i * 0.001, lz), rz, w, pth, rx=rad(90))
        o.rotation_euler = (rad(90), rng.uniform(-0.08, 0.08), rz)
        pins.append(P(lx, -0.03 - i * 0.001, lz + 0.08))
    if strings:
        for a, b in zip(pins[:-1], pins[1:]):
            tube_between('pb_string', a, b, 0.0025, mat_color('string', (0.7, 0.05, 0.04), 0.6), verts=5)


def rack_v2(loc, rz, h=2.0):
    x, y = loc
    c, s_ = math.cos(rz), math.sin(rz)

    def P(lx, ly, lz):
        return Vector((x + lx * c - ly * s_, y + lx * s_ + ly * c, lz))
    box('rack', (0.6, 1.0, h), P(0, 0, h / 2 + 0.15), M['black'], rot=(0, 0, rz), bevel=0.008)
    box('rack_door', (0.56, 0.01, h - 0.08), P(0, -0.535, h / 2 + 0.15), M['glass_dark'], rot=(0, 0, rz))
    rng = random.Random(int(x * 10 + y))
    cols = [(0.1, 1.0, 0.35), (0.2, 0.55, 1.0), (0.2, 0.55, 1.0), (1.0, 0.6, 0.1)]
    for i in range(18):
        z = 0.3 + i * (h - 0.35) / 18
        box('rack_unit', (0.5, 0.01, 0.07), P(0, -0.505, z), M['graphite'], rot=(0, 0, rz))
        for k in range(rng.randint(5, 12)):
            col = rng.choice(cols)
            key = 'led_%d_%d_%d' % tuple(int(v * 10) for v in col)
            m = bpy.data.materials.get(key) or mat_emit(key, col, 60.0)
            box('rack_led', (0.016, 0.004, 0.01), P(-0.23 + k * 0.038, -0.512, z + 0.02), m, rot=(0, 0, rz), c=C_FX)
    for sx in (-1, 1):
        box('rack_strip', (0.01, 0.006, h - 0.2), P(sx * 0.27, -0.515, h / 2 + 0.15), M['blue_strip'], rot=(0, 0, rz), c=C_FX)


def server_room(x0, x1, y0, y1, H=3.0):
    box('sr_floor', (x1 - x0, y1 - y0, 0.15), ((x0 + x1) / 2, (y0 + y1) / 2, 0.075), M['graphite'], c=C_ARCH)
    box('sr_step', (x1 - x0, 0.4, 0.075), ((x0 + x1) / 2, y0 - 0.2, 0.0375), M['graphite'], c=C_ARCH)
    # glass walls with black mullions
    for (a, b) in [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1))]:
        a, b = Vector(a), Vector(b)
        L = (b - a).length
        n = max(1, round(L / 1.25))
        horiz = abs(b.x - a.x) > abs(b.y - a.y)
        for i in range(n):
            pa = a + (b - a) * (i / n)
            pb = a + (b - a) * ((i + 1) / n)
            m = (pa + pb) / 2
            size = ((pb - pa).length, 0.012, H - 0.2) if horiz else (0.012, (pb - pa).length, H - 0.2)
            box('sr_glass', size, (m.x, m.y, 0.15 + (H - 0.2) / 2), M['glass'], c=C_ARCH)
        for i in range(n + 1):
            p = a + (b - a) * (i / n)
            box('sr_mullion', (0.05, 0.05, H), (p.x, p.y, H / 2 + 0.075), M['black'], c=C_ARCH)
        box('sr_head', ((b - a).length + 0.05, 0.08, 0.1) if horiz else (0.08, (b - a).length + 0.05, 0.1), ((a + b) / 2).to_3d() + Vector((0, 0, H + 0.05)), M['black'], c=C_ARCH)
    box('sr_ceiling', (x1 - x0, y1 - y0, 0.06), ((x0 + x1) / 2, (y0 + y1) / 2, H + 0.1), M['black'], c=C_ARCH)
    plane('sr_light', (x1 - x0) - 0.8, 0.5, ((x0 + x1) / 2, (y0 + y1) / 2, H + 0.06), M['panel'], rot=(rad(180), 0, 0), c=C_FX)
    for (a, b) in [((x0 + 0.1, y0 + 0.05), (x1 - 0.05, y0 + 0.05)), ((x1 - 0.05, y0 + 0.05), (x1 - 0.05, y1))]:
        a, b = Vector(a), Vector(b)
        tube_between('sr_strip', a.to_3d() + Vector((0, 0, 0.16)), b.to_3d() + Vector((0, 0, 0.16)), 0.008, M['blue_strip'], verts=6, c=C_FX)
    n = int((x1 - x0 - 0.6) / 0.66)
    for i in range(n):
        rack_v2((x0 + 0.55 + i * 0.66, y1 - 0.75), 0)
    for i in range(n):
        tube_between('sr_cable', (x0 + 0.55 + i * 0.66, y1 - 0.75, 2.15), (x0 + 0.55 + i * 0.66, y1 - 0.4, H + 0.05), 0.03, M['rubber'], verts=8)
    add_light('AREA', 'sr_fill', ((x0 + x1) / 2, (y0 + y1) / 2, H - 0.1), 220, (0.75, 0.88, 1.0), target=((x0 + x1) / 2, (y0 + y1) / 2, 0), size=2.5)


def printer3d(loc, rz, color=(0.85, 0.24, 0.05)):
    x, y, z = loc
    c, s_ = math.cos(rz), math.sin(rz)

    def P(lx, ly, lz):
        return Vector((x + lx * c - ly * s_, y + lx * s_ + ly * c, z + lz))
    box('p3d_body', (0.4, 0.4, 0.46), P(0, 0, 0.23), M['black'], rot=(0, 0, rz), bevel=0.01)
    box('p3d_door', (0.34, 0.006, 0.36), P(0, -0.203, 0.25), M['glass_dark'], rot=(0, 0, rz))
    box('p3d_light', (0.3, 0.3, 0.008), P(0, 0, 0.44), M['printer_light'], rot=(0, 0, rz), c=C_FX)
    box('p3d_bed', (0.3, 0.3, 0.01), P(0, 0, 0.1), M['graphite'], rot=(0, 0, rz))
    m = mat_color('print_%d' % int(color[0] * 100), color, 0.4)
    cyl('p3d_part', 0.06, 0.12, P(0.02, 0.02, 0.17), m, verts=6)


def robot_arm(loc, rz):
    x, y, z = loc
    cyl('ra_base', 0.09, 0.06, (x, y, z + 0.03), M['white'], verts=32)
    cyl('ra_turret', 0.06, 0.12, (x, y, z + 0.12), M['orange'], verts=32)
    a = Vector((x, y, z + 0.18))
    b = a + Vector((0.08 * math.cos(rz), 0.08 * math.sin(rz), 0.28))
    cc = b + Vector((0.22 * math.cos(rz), 0.22 * math.sin(rz), -0.05))
    tube_between('ra_l1', a, b, 0.04, M['white'], verts=16)
    tube_between('ra_l2', b, cc, 0.032, M['white'], verts=16)
    for p in (a, b):
        o = cyl('ra_joint', 0.05, 0.1, p, M['orange'], rot=(rad(90), 0, rz + rad(90)), verts=24)
    box('ra_grip', (0.05, 0.04, 0.07), cc + Vector((0, 0, -0.04)), M['graphite'], rot=(0, 0, rz))


def drone(loc, rz):
    x, y, z = loc
    box('dr_body', (0.12, 0.18, 0.05), (x, y, z + 0.04), M['graphite'], rot=(0, 0, rz), bevel=0.01)
    for k in range(4):
        a = rz + rad(45 + 90 * k)
        e = Vector((x + 0.2 * math.cos(a), y + 0.2 * math.sin(a), z + 0.05))
        tube_between('dr_arm', (x, y, z + 0.05), e, 0.01, M['black'], verts=8)
        cyl('dr_motor', 0.022, 0.03, e + Vector((0, 0, 0.015)), M['black'], verts=16)
        box('dr_prop', (0.2, 0.018, 0.003), e + Vector((0, 0, 0.034)), M['graphite'], rot=(0, 0, a + rad(30 * k)))


def workshop_v2(F, L=5.0):
    """Workshop along a wall: local +Y is the wall, length along local X."""
    h = 0.92
    n = int(L / 1.0)
    for i in range(n):
        lx = -L / 2 + 0.5 + i * 1.0
        box('ws_cab', (0.96, 0.62, h - 0.06), F.p(lx, 0, (h - 0.06) / 2 + 0.02), M['black'], rot=(0, 0, F.r), bevel=0.004)
        for k in range(4):
            box('ws_drawer', (0.9, 0.005, 0.005), F.p(lx, -0.312, 0.2 + k * 0.18), M['alu'], rot=(0, 0, F.r))
    box('ws_top', (L, 0.66, 0.04), F.p(0, 0, h - 0.02), M['oak'], rot=(0, 0, F.r), bevel=0.003)
    # pegboard and shelf on the wall
    box('ws_peg', (L, 0.02, 1.0), F.p(0, 0.32, h + 0.65), M['black_m'], rot=(0, 0, F.r))
    box('ws_shelf', (L, 0.3, 0.025), F.p(0, 0.18, h + 1.3), M['black'], rot=(0, 0, F.r))
    rng = random.Random(8)
    tools = [('pliers', None), ('combination_wrench', None), ('screwdriver', None), ('tongue_groove_pliers', None), ('adjustable_wrench', None),
             ('screwdrivers_02', None), ('pliers', None), ('combination_wrench', None)]
    for i, (aid, keep) in enumerate(tools):
        F.put(aid, -L / 2 + 0.4 + i * (L - 0.8) / (len(tools) - 1), 0.29, h + 0.45, rx=rad(90), rz=rad(180) + rad(rng.uniform(-6, 6)), keep=keep)
    for i in range(int(L / 0.42)):
        lx = -L / 2 + 0.25 + i * 0.42
        if i % 3 == 2:
            for k in range(3):
                col = [(0.85, 0.24, 0.05), (0.9, 0.9, 0.9), (0.1, 0.1, 0.1), (0.2, 0.45, 0.85)][(i + k) % 4]
                cyl('spool', 0.1, 0.07, F.p(lx - 0.1 + k * 0.1, 0.18, h + 1.43), mat_color('spool_%d' % ((i + k) % 4), col, 0.5), rot=(0, rad(90), F.r), verts=24)
        else:
            box('bin', (0.36, 0.26, 0.2), F.p(lx, 0.18, h + 1.41), M['white'], rot=(0, 0, F.r), bevel=0.01)
    # on the bench: printers, robot arm, drone, electronics
    printer3d(F.p(-L / 2 + 0.4, 0.05, h), F.r)
    printer3d(F.p(-L / 2 + 0.88, 0.05, h), F.r, (0.92, 0.92, 0.92))
    robot_arm(F.p(0.3, 0.0, h), F.r + rad(200))
    drone(F.p(1.3, -0.05, h), F.r + rad(20))
    F.put('circuit_board', 0.85, -0.12, h, s=0.55, rz=rad(15))
    # a laptop, parts trays, a cutting mat
    box('ws_lap', (0.31, 0.22, 0.012), F.p(-0.55, -0.08, h + 0.006), M['alu'], rot=(0, 0, F.r + rad(10)), bevel=0.003)
    box('ws_lap_lid', (0.31, 0.006, 0.21), F.p(-0.55, 0.03, h + 0.11), M['alu'], rot=(rad(-15), 0, F.r + rad(10)))
    plane('ws_lap_screen', 0.29, 0.19, F.p(-0.55, 0.024, h + 0.11), mat_screen(os.path.join(TEX2, 'ecran-3d.jpg'), 1.5), rot=(rad(75), 0, F.r + rad(10) + rad(180)), c=C_FX)
    box('ws_mat', (0.6, 0.45, 0.003), F.p(1.2, -0.08, h + 0.0015), mat_color('cutmat', (0.08, 0.22, 0.17), 0.8), rot=(0, 0, F.r))
    for k in range(3):
        box('ws_tray', (0.22, 0.14, 0.04), F.p(-1.3 + k * 0.25, -0.17, h + 0.02), M['white'], rot=(0, 0, F.r), bevel=0.004)
    F.put('plastic_container', 2.15, 0.05, h, s=0.5, rz=rad(5))
    box('scope', (0.3, 0.16, 0.16), F.p(1.95, 0.1, h + 0.08), M['graphite'], rot=(0, 0, F.r), bevel=0.01)
    plane('scope_screen', 0.16, 0.1, F.p(1.9, 0.1 - 0.081, h + 0.09), mat_screen(os.path.join(TEX2, 'ecran-dashboard.jpg'), 1.5), rot=(rad(90), 0, F.r), c=C_FX)
    # linear LED over the bench
    box('ws_light', (L - 0.4, 0.06, 0.04), F.p(0, 0.05, h + 1.95), M['black'], rot=(0, 0, F.r))
    box('ws_led', (L - 0.5, 0.04, 0.005), F.p(0, 0.05, h + 1.927), M['led_strip'], rot=(0, 0, F.r), c=C_FX)
    add_light('AREA', 'ws_light', F.p(0, -0.05, h + 1.9), 320, (1.0, 0.9, 0.78), target=F.p(0, -0.2, h), size=L - 0.5)
    # tall rolling tool cabinet and a stool
    box('ws_tower', (0.6, 0.48, 1.2), F.p(L / 2 + 0.55, -0.1, 0.62), M['black'], rot=(0, 0, F.r), bevel=0.006)
    for k in range(6):
        box('ws_tower_dr', (0.54, 0.005, 0.006), F.p(L / 2 + 0.55, -0.342, 0.2 + k * 0.18), M['alu'], rot=(0, 0, F.r))
    F.put('metal_stool_01', 0.6, -0.75, 0, rz=rad(30))


def maquette_table(c, w, d, h=0.55):
    """Large white scale model on a low platform, in the path of the fan beams."""
    x, y = c
    box('mq_base', (w, d, h), (x, y, h / 2), M['black'], bevel=0.01)
    box('mq_top', (w - 0.06, d - 0.06, 0.03), (x, y, h + 0.015), M['white'])
    rng = random.Random(12)
    for i in range(70):
        bw, bd = rng.uniform(0.12, 0.38), rng.uniform(0.12, 0.32)
        bh = rng.choice([0.08, 0.12, 0.18, 0.25, 0.35, 0.5]) * rng.uniform(0.7, 1.2)
        bx, by = x + rng.uniform(-w / 2 + 0.25, w / 2 - 0.25), y + rng.uniform(-d / 2 + 0.2, d / 2 - 0.2)
        if abs(by - y) < 0.12:
            continue
        box('mq_block', (bw, bd, bh), (bx, by, h + 0.03 + bh / 2), M['white'], rot=(0, 0, rad(rng.choice([0, 0, 90, 15]))))
    for k in range(6):
        px = x - w / 2 + 0.4 + k * (w - 0.8) / 5
        cone = cyl('mq_tree', 0.05, 0.16, (px, y + rng.choice([-1, 1]) * rng.uniform(0.2, 0.9), h + 0.11), M['white'], verts=12)
    box('mq_road', (w - 0.1, 0.12, 0.004), (x, y, h + 0.032), M['graphite'])


def plant_pot(loc, kind='white', size=1.0, plant=('fern_02', ['fern_02_a']), s=1.0, rz=0.0):
    x, y = loc
    r, hgt = 0.2 * size, 0.42 * size
    mat = M['pot_white'] if kind == 'white' else (M['pot_concrete'] if kind == 'concrete' else M['black_m'])
    cyl('pot', r, hgt, (x, y, hgt / 2), mat, verts=40)
    cyl('soil', r * 0.94, 0.02, (x, y, hgt - 0.02), M['rubber'], verts=40)
    aid, keep = plant
    put(aid, (x, y, hgt - 0.03), rz, s=s, keep=keep)


def lockers(x0, y, n, rz=0.0):
    for i in range(n):
        x = x0 + i * 0.52
        box('locker', (0.5, 0.5, 1.9), (x, y, 0.95), M['black'], rot=(0, 0, rz), bevel=0.004)
        box('locker_vent', (0.3, 0.005, 0.12), (x, y - 0.252, 1.65), M['graphite'], rot=(0, 0, rz))
        box('locker_handle', (0.02, 0.01, 0.12), (x + 0.18, y - 0.255, 1.0), M['alu'], rot=(0, 0, rz))


def flight_case(loc, size, rz=0.0):
    x, y, z = loc
    w, d, h = size
    box('fc', (w, d, h), (x, y, z + h / 2), M['black_m'], rot=(0, 0, rz), bevel=0.01)
    for sz in (-1, 1):
        box('fc_edge', (w + 0.01, d + 0.01, 0.02), (x, y, z + h / 2 + sz * (h / 2 - 0.01)), M['alu'], rot=(0, 0, rz))
    box('fc_latch', (0.08, 0.01, 0.05), (x, y - d / 2 - 0.005, z + h * 0.7), M['alu'], rot=(0, 0, rz))


# ------------------------------------------------------------------ the v2 layout
def labo_v2():
    W, D, H = 15.0, 18.0, 7.2
    Rf = 3.0
    fc = (0.0, D, 3.5)
    hall(W, D, H, fc, Rf)
    turbine(fc, Rf, n=int(OPT.get('blades', 10)), angle=rad(6))
    light_box(fc, Rf, D + 1.2, power=float(OPT.get('fanp', 1.8)), target=(0.0, float(OPT.get('aimy', 12.0)), 0))
    # central desk under the large light ceiling
    desk_v2(Frame(0.0, 9.8, 0, 0))
    office_chair((0.15, 9.1), rad(8))
    box('rug', (4.2, 3.0, 0.012), (0.0, 9.5, 0.006), M['rug'], c=C_ARCH)
    light_ceiling(0.0, 9.3, 6.0, 4.2, 4.7)
    # light table, front left, with mobile boards
    light_table(Frame(-3.3, 5.4, 0, rad(4)))
    tir = sorted(glob.glob(os.path.join(TEX2, 'tirage-*.jpg')))
    pinboard((-6.0, 6.5), rad(-70), tir[:4] + PAPERS[:3])
    pinboard((-5.9, 3.9), rad(-95), tir[4:8] + PAPERS[3:6], strings=False)
    # workshop along the right wall
    workshop_v2(Frame(6.65, 7.4, 0, rad(-90)), L=5.0)
    box('ws_shelves', (0.5, 1.6, 2.1), (6.95, 11.2, 1.05), M['black'], c=C_ARCH)
    for k in range(4):
        box('ws_shelf_plank', (0.48, 1.56, 0.02), (6.95, 11.2, 0.45 + k * 0.5), M['graphite'])
        for j in range(3):
            put('plastic_container', (6.95, 10.7 + j * 0.5, 0.47 + k * 0.5), rz=rad(90), s=0.55)
    # glass server room, back left
    server_room(-7.45, -2.9, 15.45, 17.95)
    # storage back right: lockers and flight cases
    lockers(4.4, 17.6, 6)
    flight_case((4.9, 15.7, 0), (1.0, 0.6, 0.55), rad(4))
    flight_case((4.95, 15.7, 0.55), (0.8, 0.5, 0.45), rad(-3))
    flight_case((6.3, 15.6, 0), (0.7, 0.7, 0.8), rad(10))
    # lounge corner, front right
    put('mid_century_lounge_chair', (4.5, 3.2, 0), rz=rad(-150))
    cyl('side_table', 0.25, 0.02, (5.2, 3.8, 0.5), M['black'], verts=32)
    cyl('side_table_leg', 0.012, 0.5, (5.2, 3.8, 0.25), M['black'], verts=10)
    # plants, discreet and scattered
    plant_pot((1.95, 10.6), 'white', 1.0, ('fern_02', ['fern_02_b']), 0.9)
    plant_pot((-5.75, 10.6), 'concrete', 1.3, ('pachira_aquatica_01', ['pachira_aquatica_01_bark_c', 'pachira_aquatica_01_leaves_c']), 1.0)
    plant_pot((5.75, 10.0), 'concrete', 1.1, ('calathea_orbifolia_01', ['calathea_orbifolia_01_a']), 1.2)
    plant_pot((5.6, 4.2), 'white', 0.9, ('anthurium_botany_01', ['anthurium_botany_01_b']), 1.0)
    plant_pot((-2.5, 15.0), 'black', 0.8, ('fern_02', ['fern_02_c']), 0.8)
    plant_pot((6.8, 14.4), 'white', 1.2, ('pachira_aquatica_01', ['pachira_aquatica_01_bark_b', 'pachira_aquatica_01_leaves_b']), 1.0)
    F_ = Frame(6.65, 7.4, 0, rad(-90))
    F_.put('anthurium_botany_01', 2.35, 0.1, 0.92 + 1.31, keep=['anthurium_botany_05_e'])
    if OPT.get('maquette') == '1':
        maquette_table((0.0, 14.0), 4.6, 2.6)
    # details: security camera, red LEDs, cables
    put('security_camera_02', (-5.2, 14.65, 5.2), rz=rad(200), s=0.9)
    leds([(-7.2, 17.95, 6.4), (7.2, 17.95, 6.4), (-7.45, 8.0, 5.8), (7.45, 12.0, 5.8)])
    curve_cable('floor_run', [(-3.7, 14.4, 0.15), (-2.8, 13.0, 0.012), (-1.0, 11.8, 0.012), (0.3, 11.2, 0.012)], 0.02, M['rubber'])
    fog = fog_volume((-W / 2, -1.5, 0), (W / 2, D - 0.05, H), density=float(OPT.get('fogd', 0.0045))) if FOG else None
    add_light('AREA', 'fill', (0, 6, H - 0.6), float(OPT.get('fill', 0)), (0.8, 0.88, 1.0), target=(0, 6, 0), size=10)
    return {
        'master': dict(cam=(0.0, 0.6, 1.8), target=(0.0, D, 2.9), lens=24, fstop=8, focus=9.5),
        'desk': dict(cam=(1.25, 6.95, 1.72), target=(-0.05, 10.05, 1.12), lens=28, fstop=2.8, focus=None),
        'table': dict(cam=(-1.6, 3.55, 2.3), target=(-3.25, 5.45, 0.92), lens=30, fstop=2.8, focus=None),
        'atelier': dict(cam=(2.6, 6.5, 1.6), target=(6.7, 7.9, 1.2), lens=26, fstop=2.8, focus=None),
        'serveur': dict(cam=(-3.6, 12.2, 1.5), target=(-5.1, 17.4, 1.25), lens=30, fstop=4, focus=None),
        'master_haut': dict(cam=(0.0, 0.4, 2.3), target=(0.0, D, 2.5), lens=24, fstop=8, focus=10.0),
        'fan': dict(cam=(0.9, 12.3, 0.6), target=(0.0, D, 4.0), lens=20, fstop=5.6, focus=5.5),
        'plan': dict(ortho=True, cam=(0, D / 2, 30), target=(0, D / 2, 0), scale=D + 1.5, portrait=True),
        'pass1': dict(cam=(0.35, 14.6, 3.0), target=(0.2, D, 3.5), lens=24, fstop=4, focus=3.6),
        'pass2': dict(cam=(1.55, 17.7, 4.05), target=(2.0, D + 3, 4.6), lens=18, fstop=2.8, focus=0.8),
        'pass2b': dict(cam=(-1.6, 17.7, 2.9), target=(-2.1, D + 3, 2.5), lens=18, fstop=2.8, focus=0.8),
    }


def main2():
    setup_render()
    SC.view_settings.exposure = float(OPT.get('exposure', -0.35))
    if OPT.get('look', 'High Contrast'):
        lk0 = OPT.get('look', 'High Contrast')
        for lk in ('AgX - ' + lk0, lk0):
            try:
                SC.view_settings.look = lk
                break
            except TypeError:
                continue
    M.clear()
    materials2()
    shots = labo_v2()
    compositor()
    os.makedirs(OUT, exist_ok=True)
    if OPT.get('save') == '1':
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'labo-v2.blend'))
    for s in SHOTS:
        spec = shots[s]
        cam = make_camera(spec, 'CAM_' + s)
        SC.camera = cam
        fog = bpy.data.objects.get('fog')
        ceil_coll = bpy.context.view_layer.layer_collection.children['CEILING']
        so = None
        if spec.get('ortho'):
            if fog:
                fog.hide_render = True
            ceil_coll.exclude = True
            for o in bpy.data.objects:
                if o.name.startswith(('lc_', 'lc')) and o.type == 'MESH':
                    o.hide_render = True
            SC.render.resolution_x = int(RES * 0.75)
            SC.render.resolution_y = RES
            sun = bpy.data.lights.new('plan_sun', 'SUN')
            sun.energy = 4.0
            sun.angle = rad(12)
            so = bpy.data.objects.new('plan_sun', sun)
            so.rotation_euler = (rad(20), rad(10), rad(30))
            ROOT.objects.link(so)
        else:
            SC.render.resolution_x = RES
            SC.render.resolution_y = int(RES * (16 / 9 if spec.get('vertical') else 9 / 16))
        tag = OPT.get('tag', '')
        SC.render.filepath = os.path.join(OUT, f'V2-{s}{tag}.png')
        print('RENDER', SC.render.filepath, flush=True)
        bpy.ops.render.render(write_still=True)
        if so:
            bpy.data.objects.remove(so)
            if fog:
                fog.hide_render = False
            ceil_coll.exclude = False


main2()
