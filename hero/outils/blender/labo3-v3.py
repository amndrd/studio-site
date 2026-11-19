

# ====================================================================== V3 : the underground creation base
# labo3.py = labo2-base.py + labo2-v2.py (without its last line) + labo3-v3.py  (built by rendus3.sh)

def materials3():
    materials2()
    M['wall'] = mat_pbr('wall3', 'wood_textured_concrete', 2.4, dark=0.55, tint=(0.93, 0.95, 0.97))
    damp(M['wall'])
    M['col'] = mat_pbr('col3', 'concrete_slab_wall', 2.6, dark=0.5)
    damp(M['col'])
    M['ceil'] = mat_pbr('ceil3', 'concrete_wall_008', 3.0, dark=0.42)
    M['floor'] = mat_pbr('floor3', 'hangar_concrete_floor', 3.0, dark=0.66, wet=True)
    for n in M['floor'].node_tree.nodes:
        if n.type == 'VALTORGB':
            n.color_ramp.elements[0].position = float(OPT.get('wet0', 0.6))
            n.color_ramp.elements[1].position = float(OPT.get('wet1', 0.66))
    M['green'] = mat_pbr('green3', 'green_metal_rust', 1.5, dark=0.55, metal=0.4)
    M['steel3'] = mat_pbr('steel3', 'rusty_painted_metal', 1.2, dark=0.5, tint=(0.72, 0.76, 0.76), metal=0.6)
    M['plate'] = mat_pbr('plate3', 'metal_plate', 1.0, dark=0.55, metal=0.9)
    M['blade'] = mat_color('blade3', (0.12, 0.125, 0.13), rough=0.45, metal=0.8)
    M['laminate'] = mat_color('laminate', (0.74, 0.73, 0.70), rough=0.45)
    M['offwhite'] = mat_color('offwhite', (0.8, 0.79, 0.76), rough=0.4, metal=0.1)
    M['tape'] = mat_color('tape', (0.9, 0.42, 0.08), rough=0.55)
    M['scotch'] = mat_color('scotch', (0.018, 0.018, 0.02), rough=0.32, metal=0.0)
    M['etiquette'] = mat_color('etiquette', (0.84, 0.84, 0.81), rough=0.55)
    M['red'] = mat_color('red3', (0.55, 0.04, 0.03), rough=0.35, metal=0.3)
    M['wire'] = mat_color('wire3', (0.03, 0.03, 0.032), rough=0.45, metal=0.9)
    M['grid'] = mat_alpha_image(os.path.join(TEX2, 'grillage.png'), 0.5)
    M['pipe'] = mat_color('pipe3', (0.09, 0.095, 0.1), rough=0.55, metal=0.6)
    M['galva'] = mat_color('galva3', (0.18, 0.185, 0.19), rough=0.5, metal=0.7)
    M['board'] = mat_color('board3', (0.5, 0.5, 0.49), rough=0.7)
    M['white_hot'] = mat_emit('white_hot3', (0.92, 0.96, 1.0), float(OPT.get('hot', 4.0)))
    M['panel'] = mat_emit('panel3', (0.93, 0.96, 1.0), float(OPT.get('panel', 4.0)))


def damp(m):
    """Darker, slightly greenish damp band at the foot of walls and columns."""
    nt = m.node_tree
    p = principled(m)
    src = p.inputs['Base Color'].links[0].from_socket
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(geo.outputs['Position'], sep.inputs[0])
    noise = nt.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 1.2
    noise.inputs['Detail'].default_value = 6
    nt.links.new(geo.outputs['Position'], noise.inputs['Vector'])
    add = nt.nodes.new('ShaderNodeMath')
    add.operation = 'ADD'
    nt.links.new(sep.outputs['Z'], add.inputs[0])
    mul = nt.nodes.new('ShaderNodeMath')
    mul.operation = 'MULTIPLY'
    mul.inputs[1].default_value = 0.9
    nt.links.new(noise.outputs['Fac'], mul.inputs[0])
    nt.links.new(mul.outputs[0], add.inputs[1])
    ramp = nt.nodes.new('ShaderNodeMapRange')
    ramp.inputs['From Min'].default_value = 0.6
    ramp.inputs['From Max'].default_value = 1.9
    ramp.inputs['To Min'].default_value = 1.0
    ramp.inputs['To Max'].default_value = 0.0
    nt.links.new(add.outputs[0], ramp.inputs['Value'])
    mix = nt.nodes.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    mix.blend_type = 'MULTIPLY'
    nt.links.new(ramp.outputs[0], mix.inputs['Factor'])
    nt.links.new(src, mix.inputs[6])
    mix.inputs[7].default_value = (0.5, 0.53, 0.48, 1)
    nt.links.new(mix.outputs[2], p.inputs['Base Color'])


# ------------------------------------------------------------------ fan v1, no guard, with a steel frame on top
def fan_v3(center, R, n_blades=7, angle=0.0, depth=1.1):
    cx, cy, cz = center
    ring('fan_tube', R - 0.02, R + 0.16, depth, (cx, cy + depth / 2 - 0.25, cz), M['green'])
    ring('fan_flange', R - 0.06, R + 0.45, 0.16, (cx, cy - 0.3, cz), M['green'])
    ring('fan_flange_lip', R + 0.36, R + 0.5, 0.24, (cx, cy - 0.32, cz), M['steel3'])
    for i in range(32):
        a = 2 * math.pi * i / 32
        r = R + 0.26
        cyl('bolt', 0.03, 0.08, (cx + r * math.cos(a), cy - 0.41, cz + r * math.sin(a)), M['plate'], rot=(rad(90), 0, 0), verts=8)
    by = cy + 0.15
    cyl('fan_hub', 0.42, 0.45, (cx, by, cz), M['steel3'], rot=(rad(90), 0, 0), verts=48)
    cyl('fan_motor', 0.55, 1.0, (cx, cy + 0.9, cz), M['green'], rot=(rad(90), 0, 0), verts=48)
    for k in range(4):
        a = rad(45 + 90 * k)
        tube_between('strut', (cx + 0.45 * math.cos(a), cy + 0.9, cz + 0.45 * math.sin(a)),
                     (cx + (R + 0.05) * math.cos(a), cy + 0.9, cz + (R + 0.05) * math.sin(a)), 0.06, M['steel3'], verts=10)
    me = blade_mesh('blade', 0.36, R - 0.1, 0.5, 1.15, 40, 14)
    me.materials.append(M['blade'])
    for k in range(n_blades):
        o = bpy.data.objects.new('blade', me)
        o.location = (cx, by - 0.04, cz)
        o.rotation_euler = (0, -(angle + 2 * math.pi * k / n_blades), 0)
        sm = o.modifiers.new('solid', 'SOLIDIFY')
        sm.thickness = 0.03
        bv = o.modifiers.new('bev', 'BEVEL')
        bv.width = 0.008
        bv.segments = 2
        link(o)
    # steel frame: two posts and a cross beam over the top of the disc (like the reference)
    for s_ in (-1, 1):
        box('fan_post', (0.22, 0.25, cz + R + 0.9), (cx + s_ * (R + 0.75), cy - 0.55, (cz + R + 0.9) / 2), M['steel3'])
    box('fan_beam', (2 * R + 1.7, 0.25, 0.3), (cx, cy - 0.55, cz + R * 0.55), M['steel3'])
    box('fan_beam2', (2 * R + 1.7, 0.25, 0.22), (cx, cy - 0.55, cz + R + 0.75), M['steel3'])
    for s_ in (-1, 1):
        tube_between('fan_brace', (cx + s_ * 0.25, cy - 0.55, cz + R * 0.55), (cx + s_ * (R + 0.7), cy - 0.55, cz + R + 0.7), 0.05, M['steel3'], verts=8)


# ------------------------------------------------------------------ hall
def hall3(W, D, H, fc, Rf):
    box('floor', (W + 2, D + 4, 0.2), (0, D / 2, -0.1), M['floor'], c=C_ARCH)
    box('slab', (W + 2, D + 4, 0.4), (0, D / 2, H + 0.2), M['ceil'], c=C_CEIL)
    box('wall_L', (0.5, D + 4, H), (-W / 2 - 0.25, D / 2, H / 2), M['wall'], c=C_ARCH)
    box('wall_R', (0.5, D + 4, H), (W / 2 + 0.25, D / 2, H / 2), M['wall'], c=C_ARCH)
    box('wall_F', (W + 2, 0.5, H), (0, -1.0, H / 2), M['wall'], c=C_ARCH)
    wall_with_hole('wall_B', -W / 2 - 0.5, W / 2 + 0.5, D, D + 1.0, 0, H, fc, Rf + 0.18, M['wall'])
    for y in (6.0, 12.0, 18.0):
        box('beam_x', (W, 0.5, 0.6), (0, y, H - 0.3), M['col'], c=C_CEIL)
        for s in (-1, 1):
            box('column', (0.7, 0.7, H), (s * 4.8, y, H / 2), M['col'], bevel=0.01, c=C_ARCH)
    for s in (-1, 1):
        box('beam_y', (0.5, D, 0.6), (s * 4.8, D / 2, H - 0.3), M['col'], c=C_CEIL)
    # dense services under the slab
    runs = [(-6.6, 0.16, H - 0.85, 'black'), (-6.2, 0.1, H - 0.8, 'steel'), (-5.9, 0.1, H - 0.8, 'steel'),
            (-2.6, 0.38, H - 1.05, 'alu'), (-1.6, 0.09, H - 0.75, 'black'), (1.4, 0.13, H - 0.85, 'black'),
            (1.75, 0.08, H - 0.78, 'steel'), (2.0, 0.08, H - 0.78, 'steel'), (3.2, 0.3, H - 1.0, 'alu'),
            (6.4, 0.14, H - 0.85, 'black'), (6.75, 0.1, H - 0.8, 'steel')]
    remap = {'alu': 'galva', 'steel': 'pipe', 'black': 'black'}
    for (x, r, z, m) in runs:
        cyl('pipe', r, D + 2, (x, D / 2, z), M[remap[m]], rot=(rad(90), 0, 0), verts=20, c=C_CEIL)
    for y in (3.0, 9.0, 15.0, 20.5):
        cyl('pipe_x', 0.09, W, (0, y, H - 0.68), M['black'], rot=(0, rad(90), 0), verts=16, c=C_CEIL)
        for x in (-6.4, -2.6, 1.4, 3.2, 6.4):
            box('hanger', (0.03, 0.03, 0.6), (x, y + 0.6, H - 0.3), M['black'], c=C_CEIL)
    for x in (-7.3, 7.3):
        box('tray', (0.45, D, 0.06), (x, D / 2, H - 1.25), M['steel'], c=C_CEIL)
        for k in range(5):
            cyl('trayc', 0.022, D, (x - 0.16 + 0.08 * k, D / 2, H - 1.2), M['rubber'], rot=(rad(90), 0, 0), verts=8, c=C_CEIL)
    # wall conduits and a few utility boxes
    for (x, y) in [(-7.97, 4.0), (7.97, 5.5), (-7.97, 16.0), (7.97, 16.8)]:
        cyl('conduit', 0.04, H - 1.3, (x + (0.06 if x < 0 else -0.06), y, (H - 1.3) / 2), M['black'], verts=10)
    put('utility_box_02', (3.6, D - 0.3, 0), rz=0)
    put('power_box_01', (-3.8, D - 0.06, 1.6), keep=['power_box_01_box', 'power_box_01_door'])
    put('korean_fire_extinguisher_01', (4.35, 5.6, 0), rz=rad(-90))
    leds([(-7.7, D - 0.05, 5.4), (7.7, D - 0.05, 5.4), (-7.95, 10.0, 4.9), (7.95, 15.0, 4.9), (-3.65, D - 0.1, 2.4)])


# ------------------------------------------------------------------ clutter helpers
def taped_box(loc, size, rz=0.0, tape=True):
    x, y, z = loc
    w, d, h = size
    box('cbox', (w, d, h), (x, y, z + h / 2), M['offwhite'], rot=(0, 0, rz), bevel=0.004)
    if tape:
        box('cbox_tape', (w + 0.002, 0.05, 0.004), (x, y, z + h + 0.001), M['scotch'], rot=(0, 0, rz))
        box('cbox_label', (0.08, 0.004, 0.05), (x - 0.05 * math.sin(rz) * 0, y - d / 2 - 0.002, z + h * 0.6), M['etiquette'], rot=(0, 0, rz))


def book_stack(loc, n, rz=0.0, seed=1):
    x, y, z = loc
    rng = random.Random(seed)
    cols = [(0.78, 0.77, 0.74), (0.15, 0.16, 0.18), (0.55, 0.57, 0.6), (0.85, 0.45, 0.12), (0.3, 0.36, 0.42)]
    for i in range(n):
        w, d, h = rng.uniform(0.17, 0.26), rng.uniform(0.22, 0.3), rng.uniform(0.018, 0.04)
        key = 'book_%d' % (i % len(cols))
        m = bpy.data.materials.get(key) or mat_color(key, cols[i % len(cols)], 0.6)
        box('book', (w, d, h), (x + rng.uniform(-0.02, 0.02), y + rng.uniform(-0.02, 0.02), z + h / 2), m, rot=(0, 0, rz + rng.uniform(-0.15, 0.15)))
        z += h
    return z


def paper_scatter(F, area, n, z, seed=3, paths=None):
    rng = random.Random(seed)
    paths = paths or PAPERS
    (x0, x1), (y0, y1) = area
    for i in range(n):
        z += 0.0009
        sheet_world(F.p(rng.uniform(x0, x1), rng.uniform(y0, y1), z), F.r + rng.uniform(-0.5, 0.5), rng.choice([0.21, 0.3, 0.3, 0.42]), paths[i % len(paths)])
    return z


def floor_fan(loc, rz):
    x, y = loc
    c, s_ = math.cos(rz), math.sin(rz)
    box('ff_foot', (0.32, 0.22, 0.03), (x, y, 0.015), M['offwhite'], rot=(0, 0, rz), bevel=0.01)
    ring('ff_ring', 0.2, 0.24, 0.12, (x, y, 0.3), M['offwhite'])
    o = bpy.data.objects[-1] if False else None
    for k in range(5):
        a = 2 * math.pi * k / 5
        box('ff_blade', (0.17, 0.006, 0.07), (x + 0.1 * math.cos(a), y, 0.3 + 0.1 * math.sin(a)), M['offwhite'], rot=(0, -a, 0))
    cyl('ff_hub', 0.05, 0.08, (x, y + 0.02, 0.3), M['offwhite'], rot=(rad(90), 0, 0), verts=20)


def architect_lamp(base, head, target, energy=180, color=(1.0, 0.83, 0.62)):
    b, hd = Vector(base), Vector(head)
    cyl('al_base', 0.07, 0.03, b + Vector((0, 0, 0.015)), M['black'], verts=24)
    elbow = (b + hd) / 2 + Vector((0, 0, 0.35))
    tube_between('al_arm1', b + Vector((0, 0, 0.03)), elbow, 0.012, M['black'], verts=8)
    tube_between('al_arm2', elbow, hd, 0.012, M['black'], verts=8)
    d = (Vector(target) - hd).normalized()
    cone = cyl('al_head', 0.075, 0.16, hd + d * 0.04, M['black'], verts=24, caps=False)
    cone.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    add_light('SPOT', 'al_light', hd + d * 0.06, energy, color, target=target, size=0.03, spot=80, blend=0.6)


# ------------------------------------------------------------------ zone 1 : the central desk (Birdcage base, contemporary devices)
def desk_birdcage(F):
    h = 0.75
    W, D = 2.6, 0.85
    box('dk_top', (W, D, 0.03), F.p(0, 0, h - 0.015), M['laminate'], rot=(0, 0, F.r), bevel=0.004)
    for lx in (-0.98, 0.98):
        box('dk_ped', (0.46, 0.62, h - 0.05), F.p(lx, 0.02, (h - 0.05) / 2 + 0.02), M['offwhite'], rot=(0, 0, F.r), bevel=0.004)
        for k in range(3):
            box('dk_dr', (0.42, 0.004, 0.004), F.p(lx, -0.292, 0.18 + k * 0.2), M['graphite'], rot=(0, 0, F.r))
            box('dk_lab', (0.07, 0.003, 0.03), F.p(lx - 0.12, -0.293, 0.24 + k * 0.2), M['tape'], rot=(0, 0, F.r))
    # side table on the right, lower, loaded
    box('dk_side', (1.2, 0.6, 0.03), F.p(1.95, 0.35, 0.66), M['laminate'], rot=(0, 0, F.r + rad(-12)), bevel=0.004)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box('dk_side_leg', (0.035, 0.035, 0.64), F.p(1.95 + sx * 0.53, 0.35 + sy * 0.24, 0.33), M['graphite'], rot=(0, 0, F.r + rad(-12)))
    box('dk_cab', (0.5, 0.5, 0.58), F.p(2.15, -0.45, 0.33), M['offwhite'], rot=(0, 0, F.r + rad(8)), bevel=0.006)
    for k in range(3):
        box('dk_cab_dr', (0.46, 0.004, 0.004), F.p(2.15, -0.703, 0.18 + k * 0.17), M['graphite'], rot=(0, 0, F.r + rad(8)))
    for (lx, ly) in [(1.95, -0.65), (2.35, -0.25)]:
        box('dk_tape', (0.06, 0.003, 0.025), F.p(lx, ly - 0.002, 0.5), M['tape'], rot=(0, 0, F.r + rad(8)))
    # screens: big one, a raised second one, a vertical tablet; computer box
    monitor(F, 0.12, 0.22, h + 0.36, 0.62, 0.35, rad(-4), os.path.join(TEX2, 'ecran-code.jpg'), 2.0)
    cyl('dk_stand', 0.012, 0.3, F.p(0.12, 0.3, h + 0.15), M['alu'], verts=12)
    box('dk_stand_foot', (0.22, 0.16, 0.012), F.p(0.12, 0.28, h + 0.006), M['alu'], rot=(0, 0, F.r))
    zs = book_stack(F.p(-0.66, 0.2, h), 4, F.r + rad(10), 5)
    monitor(F, -0.66, 0.2, zs + 0.18 - F.o.z, 0.48, 0.28, rad(14), os.path.join(TEX2, 'ecran-design.jpg'), 1.8)
    box('dk_mstand', (0.18, 0.14, 0.02), F.p(-0.66, 0.22, zs - F.o.z + 0.01), M['alu'], rot=(0, 0, F.r + rad(14)))
    box('dk_tab', (0.17, 0.012, 0.24), F.p(0.82, 0.18, h + 0.16), M['black'], rot=(rad(-10), 0, F.r + rad(-20)), bevel=0.006)
    plane('dk_tab_scr', 0.155, 0.225, F.p(0.82, 0.172, h + 0.16), mat_screen(os.path.join(TEX2, 'ecran-dashboard.jpg'), 1.4), rot=(rad(80), 0, F.r + rad(-20)), c=C_FX)
    box('dk_pc', (0.2, 0.2, 0.1), F.p(0.5, 0.3, h + 0.05), M['alu'], rot=(0, 0, F.r + rad(5)), bevel=0.02)
    box('dk_kb', (0.36, 0.12, 0.012), F.p(0.1, -0.16, h + 0.006), M['offwhite'], rot=(0, 0, F.r + rad(-3)), bevel=0.003)
    box('dk_mouse', (0.06, 0.1, 0.03), F.p(0.42, -0.16, h + 0.015), M['offwhite'], rot=(0, 0, F.r), bevel=0.012)
    # laptop open on the left half
    lr = F.r + rad(20)
    box('dk_lap', (0.31, 0.22, 0.012), F.p(-0.45, -0.18, h + 0.006), M['alu'], rot=(0, 0, lr), bevel=0.003)
    c, s_ = math.cos(lr), math.sin(lr)
    hinge = F.p(-0.45, -0.18, h + 0.012) + Vector((0.11 * s_, 0.11 * c, 0))
    box('dk_lap_lid', (0.31, 0.006, 0.21), hinge + Vector((0, 0, 0.1)), M['alu'], rot=(rad(-14), 0, lr))
    plane('dk_lap_scr', 0.29, 0.19, hinge + Vector((0.005 * s_ * -1, -0.005 * c, 0.1)), mat_screen(os.path.join(TEX2, 'ecran-3d.jpg'), 1.5), rot=(rad(76), 0, lr), c=C_FX)
    # stacks, boxes with orange tape, papers, mug, phone, headphones, plant
    taped_box(F.p(-1.12, 0.12, h), (0.3, 0.24, 0.18), F.r + rad(-6))
    taped_box(F.p(-1.1, 0.12, h + 0.18), (0.26, 0.2, 0.12), F.r + rad(8))
    book_stack(F.p(-1.12, -0.25, h), 3, F.r + rad(-20), 9)
    paper_scatter(F, ((-0.9, 0.9), (-0.38, 0.05)), 7, h + 0.001, 4)
    cyl('dk_mug', 0.042, 0.095, F.p(0.62, -0.25, h + 0.0475), M['offwhite'], verts=24)
    cyl('dk_cup', 0.04, 0.1, F.p(-0.85, 0.32, h + 0.05), M['graphite'], verts=20)
    for k in range(4):
        tube_between('dk_pen', F.p(-0.85 + 0.01 * k, 0.32, h + 0.06), F.p(-0.86 + 0.02 * k, 0.33 - 0.01 * k, h + 0.18), 0.004, M['tape'] if k == 1 else M['black'], verts=6)
    box('dk_phone', (0.072, 0.15, 0.008), F.p(0.82, -0.28, h + 0.004), M['black'], rot=(0, 0, F.r + rad(-30)), bevel=0.004)
    F.put('potted_plant_04', 1.18, 0.3, h, s=1.0)
    # side table load: printer-like box, boxes, books
    taped_box(F.p(1.75, 0.45, 0.675), (0.42, 0.34, 0.2), F.r + rad(-12))
    taped_box(F.p(2.25, 0.3, 0.675), (0.28, 0.24, 0.14), F.r + rad(-20), tape=False)
    book_stack(F.p(2.3, 0.32, 0.815), 3, F.r, 12)
    paper_scatter(F, ((1.5, 2.4), (0.15, 0.55)), 3, 0.676, 8)
    # lamp over the desk, chair, floor fan, bin, cables, boxes on the floor
    architect_lamp(F.p(-1.05, 0.33, h), F.p(-0.35, 0.05, h + 0.75), F.p(-0.2, -0.15, h), 170)
    office_chair(tuple(F.p(-0.05, -0.78, 0))[:2], F.r + math.pi)
    floor_fan(tuple(F.p(-1.75, -0.35, 0))[:2], F.r + rad(30))
    cyl('dk_bin', 0.15, 0.32, F.p(1.35, -0.55, 0.16), M['graphite'], verts=24, caps=True)
    curve_cable('dk_cable1', [F.p(0.1, 0.4, h - 0.02), F.p(0.15, 0.45, 0.35), F.p(0.3, 0.5, 0.012), F.p(1.2, 1.4, 0.012), F.p(2.5, 2.4, 0.012)], 0.01, M['rubber'])
    curve_cable('dk_cable2', [F.p(-0.6, 0.4, h - 0.02), F.p(-0.65, 0.45, 0.3), F.p(-0.5, 0.6, 0.012), F.p(-1.4, 1.6, 0.012)], 0.009, M['rubber'])
    taped_box(F.p(-1.5, 0.75, 0), (0.45, 0.35, 0.3), F.r + rad(14))
    taped_box(F.p(-1.45, 0.72, 0.3), (0.35, 0.3, 0.2), F.r + rad(-4))
    # light from above, like Birdcage: a narrow cone on the desk
    add_light('SPOT', 'dk_top', F.p(0.0, 0.0, 4.6), float(OPT.get('deskw', 650)), (1.0, 0.9, 0.78), target=F.p(0.0, -0.1, 0), size=0.25, spot=34, blend=0.5)


# ------------------------------------------------------------------ desk prototypes placed in the lab
SHELF = {'A': (1.088, 0.28, -0.85, 1.05), 'B': (1.201, 0.24, -1.15, 1.15), 'BD': (1.2055, 0.24, -1.15, 1.15), 'D': (1.0415, 0.27, -0.85, 1.05), 'E': (1.06, 0.23, -1.1, 1.1)}


def binders(F, x0, y, z, n, rz=0.0, seed=3):
    rng = random.Random(seed)
    cols = [M['offwhite'], M['offwhite'], M['graphite'], M['black'], M['offwhite']]
    x = x0
    for i in range(n):
        w = rng.choice([0.05, 0.075, 0.075])
        lean = rad(rng.uniform(-2, 2)) if i < n - 1 else rad(-14)
        box('dk_binder', (w - 0.004, 0.24, 0.3), F.p(x + w / 2, y, z + 0.15), cols[i % len(cols)], rot=(0, lean, F.r + rz), bevel=0.003)
        box('dk_binder_lab', (w * 0.6, 0.002, 0.06), F.p(x + w / 2, y - 0.121, z + 0.2), M['etiquette'], rot=(0, lean, F.r + rz))
        x += w


def storage_in_lab(p):
    """The storage prototypes (objets-rangements.py) under the desk D, in the desk frame."""
    if 'grey_r' not in M:
        M['grey_r'] = m_powder('grey_r', (0.58, 0.59, 0.585), rough=0.4)
        M['hole'] = mat_color('hole', (0.035, 0.028, 0.02), rough=0.8)
        M['paperw'] = m_surface('paperw', (0.82, 0.82, 0.8), rough=0.75, var=0.02)
    L = look(p)
    place(open_unit, L, -0.895, 0.02)
    place(pedestal, L, 0.55, 0.0)
    place(low_cabinet, L, RX, RY + 0.01)
    place(trolley, L, 2.95, -0.32, rad(-14))


def desk_concept(F, kind):
    """One of the studio desk prototypes (objets-bureau.py), placed in the lab with the same props on it."""
    materials_bureau(keep=True)
    before = set(bpy.data.objects)
    BUILD[kind]()
    if OPT.get('rangements', 'N') in ('N', 'P', 'G'):
        storage_in_lab(OPT.get('rangements', 'N'))
    root = bpy.data.objects.new('dk_frame_' + kind, None)
    root.location = F.o
    root.rotation_euler = (0, 0, F.r)
    link(root)
    for o in set(bpy.data.objects) - before:
        if o.parent is None and o is not root:
            o.parent = root
    h, hr = 0.74, 0.64
    zsh, ysh, xs0, xs1 = SHELF[kind]
    # screens: one of the desk setups (objets-ecrans.py), or the first simple screens
    if 'B2' in SETUP_FN:
        OPT.setdefault('ecrans', 'B2')                # retained workstation (objets-poste.py in the build)
    if OPT.get('ecrans', '') in SETUP_FN:
        build_setup(OPT['ecrans'], F)
    else:
        old_screens(F, h)
    desk_props_rest(F, h, hr, zsh, ysh, xs0)
    if 'sol_bureau' in globals():
        sol_bureau(F, h, hr, before)                  # no floor covering (retained 16/11), the mesh bin (objets-sol.py)
    if 'autour_bureau' in globals():
        autour_bureau(F, h, hr)                       # around the desk: two cartons, the white table fan (objets-autour.py)
    if 'cables_bureau' in globals():
        cables_bureau(F, h, hr)                       # the cables and the power strip under the desk (objets-cables.py)
        if OPT.get('verif') == '1':
            verifier_cables(F)


def old_screens(F, h):
    monitor(F, 0.12, 0.04, h + 0.36, 0.62, 0.35, rad(-4), os.path.join(TEX2, 'ecran-code.jpg'), 2.0)
    cyl('dk_stand', 0.012, 0.3, F.p(0.12, 0.1, h + 0.15), M['alu'], verts=12)
    box('dk_stand_foot', (0.22, 0.16, 0.012), F.p(0.12, 0.09, h + 0.006), M['alu'], rot=(0, 0, F.r))
    zs = book_stack(F.p(-0.6, 0.0, h), 4, F.r + rad(10), 5)
    monitor(F, -0.6, 0.0, zs + 0.18 - F.o.z, 0.48, 0.28, rad(14), os.path.join(TEX2, 'ecran-design.jpg'), 1.8)
    box('dk_mstand', (0.18, 0.14, 0.02), F.p(-0.6, 0.02, zs - F.o.z + 0.01), M['alu'], rot=(0, 0, F.r + rad(14)))
    box('dk_tab', (0.17, 0.012, 0.24), F.p(0.82, 0.08, h + 0.16), M['black'], rot=(rad(-10), 0, F.r + rad(-20)), bevel=0.006)
    plane('dk_tab_scr', 0.155, 0.225, F.p(0.82, 0.072, h + 0.16), mat_screen(os.path.join(TEX2, 'ecran-dashboard.jpg'), 1.4), rot=(rad(80), 0, F.r + rad(-20)), c=C_FX)
    box('dk_pc', (0.2, 0.2, 0.1), F.p(0.5, 0.24, h + 0.05), M['alu'], rot=(0, 0, F.r + rad(5)), bevel=0.02)
    box('dk_kb', (0.36, 0.12, 0.012), F.p(0.1, -0.2, h + 0.006), M['offwhite'], rot=(0, 0, F.r + rad(-3)), bevel=0.003)
    box('dk_mouse', (0.06, 0.1, 0.03), F.p(0.42, -0.2, h + 0.015), M['offwhite'], rot=(0, 0, F.r), bevel=0.012)
    lr = F.r + rad(20)
    box('dk_lap', (0.31, 0.22, 0.012), F.p(-0.42, -0.22, h + 0.006), M['alu'], rot=(0, 0, lr), bevel=0.003)
    c, s_ = math.cos(lr), math.sin(lr)
    hinge = F.p(-0.42, -0.22, h + 0.012) + Vector((0.11 * s_, 0.11 * c, 0))
    box('dk_lap_lid', (0.31, 0.006, 0.21), hinge + Vector((0, 0, 0.1)), M['alu'], rot=(rad(-14), 0, lr))
    plane('dk_lap_scr', 0.29, 0.19, hinge + Vector((0.005 * s_ * -1, -0.005 * c, 0.1)), mat_screen(os.path.join(TEX2, 'ecran-3d.jpg'), 1.5), rot=(rad(76), 0, lr), c=C_FX)


def desk_props_rest(F, h, hr, zsh, ysh, xs0):
    # retained lamp (2026-11-15): Sketchfab "Desk lamp", original black finish, on three books (S-N, P3).
    # Without objets-lampe.py in the build, the old architect lamp on its box pile is used.
    if 'LAMPES' in globals():
        OPT.setdefault('lampe', 'S-N')
        OPT.setdefault('lpos', 'P3')
    if not OPT.get('lampe', 'old').startswith('S-'):     # the Sketchfab lamp stands without the box pile
        taped_box(F.p(-0.98, 0.1, h), (0.3, 0.24, 0.18), F.r + rad(-6))
        taped_box(F.p(-0.97, 0.1, h + 0.18), (0.26, 0.2, 0.12), F.r + rad(8))
    if OPT.get('lampe', 'old') in globals().get('LAMPES', {}):
        lampe_au_bureau(OPT['lampe'], F, h)          # desk lamp prototypes (objets-lampe.py)
    else:
        architect_lamp(F.p(-0.98, 0.1, h + 0.3), F.p(-0.4, -0.1, h + 0.85), F.p(-0.2, -0.2, h), 210)
    # objects on the desk (objets-poses.py, option objets=A|B|C): they replace the placeholders (grey book pile, mug, pen pot, plant)
    objets = 'objets_bureau' in globals() and globals().get('OBJETS', [''])[0] in globals().get('LAYOUT', {})
    if not objets:
        book_stack(F.p(-1.0, -0.26, h), 3, F.r + rad(-20), 9)
    papiers = globals().get('PAPIERS', [''])[0] == 'M'              # papers on the desk (objets-papiers.py, option papiers=M)
    if papiers:
        papiers_bureau(F, h, hr)
    else:
        paper_scatter(F, ((-0.9, 0.9), (-0.38, -0.02)), 7, h + 0.001, 4)
    if objets:
        objets_bureau(F, h, hr)
    else:
        cyl('dk_mug', 0.042, 0.095, F.p(0.64, -0.27, h + 0.0475), M['offwhite'], verts=24)
        cyl('dk_cup', 0.04, 0.1, F.p(-0.8, -0.05, h + 0.05), M['graphite'], verts=20)
        for k in range(4):
            tube_between('dk_pen', F.p(-0.8 + 0.01 * k, -0.05, h + 0.06), F.p(-0.81 + 0.02 * k, -0.04 - 0.01 * k, h + 0.18), 0.004, M['black'], verts=6)
    if OPT.get('ecrans', '') != 'B2':
        box('dk_phone', (0.072, 0.15, 0.008), F.p(0.84, -0.3, h + 0.004), M['black'], rot=(0, 0, F.r + rad(-30)), bevel=0.004)
    # back shelf: binders and boxes
    if globals().get('CONTENU', [''])[0] in globals().get('FILL', {}):
        remplir_rehausse(F, zsh, ysh, xs0, xs0 + 1.9, h)    # storage contents (objets-contenus.py; retained mix M by default)
        if OPT.get('ledsous', '1') == '1':
            led_sous_bureau(F, h, hr)                     # LED strips under the desk, so the storage reads from the camera
    else:
        binders(F, max(xs0, -0.2) + 0.45, ysh, zsh, 8)
        sx = 0.5 if OPT.get('lampe', 'old').startswith('S-') else 0.25   # leave the left end of the riser to the lamp
        if not (OPT.get('lampe', 'old').startswith('S-') and OPT.get('lpos', 'P3') == 'P2'):   # the lamp stands on the riser instead
            taped_box(F.p(xs0 + sx, ysh, zsh), (0.3, 0.2, 0.16), F.r + rad(-4))
        taped_box(F.p(xs0 + sx + 0.35, ysh, zsh), (0.26, 0.2, 0.12), F.r + rad(5), tape=False)
    # the lower return (with the papers, it holds the plans: the placeholder boxes and books go)
    if not papiers:
        taped_box(F.p(1.62, 0.18, hr), (0.42, 0.34, 0.2), F.r + rad(-10))
        taped_box(F.p(2.12, 0.08, hr), (0.28, 0.24, 0.14), F.r + rad(-18), tape=False)
        book_stack(F.p(2.15, 0.08, hr + 0.14), 3, F.r, 12)
        paper_scatter(F, ((1.4, 2.3), (-0.12, 0.25)), 3, hr + 0.001, 8)
    if not objets:
        F.put('potted_plant_04', 2.3, 0.28, hr, s=0.9)
    # floor: chair, fan, bin, cables, boxes
    if OPT.get('chaise', 'mandy') == 'mandy':
        pc = F.p(-0.05, -0.8, 0)
        import_mandy(OPT.get('mfin', 'graphite'), OPT.get('mvar', 'sans-appui-tete'), (pc.x, pc.y), F.r + math.pi + rad(float(OPT.get('chaise_rot', -15))))
    elif OPT.get('chaise', '') in ('G', 'N', 'A'):
        pc = F.p(-0.05, -0.8, 0)
        place_chair(OPT['chaise'], pc.x, pc.y, F.r + math.pi + rad(float(OPT.get('chaise_rot', -15))))
    else:
        office_chair(tuple(F.p(-0.05, -0.8, 0))[:2], F.r + math.pi)
    autour = globals().get('AUTOUR', ['aucun'])[0] in globals().get('PISTES_AU', ())     # the decor around the desk (objets-autour.py)
    if not autour:
        floor_fan(tuple(F.p(-1.75, -0.35, 0))[:2], F.r + rad(30))
    if 'sol_bureau' not in globals():                 # placeholder; the retained bin comes with objets-sol.py
        cyl('dk_bin', 0.15, 0.32, F.p(1.3, -0.62, 0.16), M['graphite'], verts=24, caps=True)
    curve_cable('dk_cable1', [F.p(0.1, 0.35, h - 0.02), F.p(0.15, 0.42, 0.35), F.p(0.3, 0.5, 0.012), F.p(1.2, 1.4, 0.012), F.p(2.5, 2.4, 0.012)], 0.01, M['rubber'])
    curve_cable('dk_cable2', [F.p(-0.6, 0.35, h - 0.02), F.p(-0.65, 0.42, 0.3), F.p(-0.5, 0.6, 0.012), F.p(-1.4, 1.6, 0.012)], 0.009, M['rubber'])
    if not autour:
        taped_box(F.p(-1.5, 0.75, 0), (0.45, 0.35, 0.3), F.r + rad(14))
        taped_box(F.p(-1.45, 0.72, 0.3), (0.35, 0.3, 0.2), F.r + rad(-4))
    add_light('SPOT', 'dk_top', F.p(0.0, 0.0, 4.6), float(OPT.get('deskw', 650)), (1.0, 0.9, 0.78), target=F.p(0.0, -0.1, 0), size=0.25, spot=34, blend=0.5)


# ------------------------------------------------------------------ zone 2 : the projects corner
def plan_table3(c, w=1.4, d=2.6, h=0.95):
    x, y = c
    box('pt_top', (w, d, 0.05), (x, y, h - 0.025), M['black_m'], bevel=0.005)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box('pt_leg', (0.07, 0.07, h - 0.05), (x + sx * (w / 2 - 0.08), y + sy * (d / 2 - 0.08), (h - 0.05) / 2), M['steel3'])
    box('pt_shelf', (w - 0.2, d - 0.2, 0.03), (x, y, 0.22), M['steel3'])
    F = Frame(x, y, 0, rad(90))
    z = h + 0.001
    rng = random.Random(21)
    blues = sorted(glob.glob(os.path.join(TEXG, 'plan-bleu-*.jpg')))
    others = [p for p in PAPERS if 'bleu' not in p]
    for i, (lx, ly, ww) in enumerate([(-0.75, 0.05, 0.9), (0.35, -0.12, 0.95), (0.95, 0.25, 0.7), (-0.1, 0.35, 0.75), (-1.0, -0.4, 0.6)]):
        z += 0.0012
        sheet_world(F.p(lx, ly, z), F.r + rng.uniform(-0.3, 0.3), ww, blues[i % len(blues)] if i % 3 != 2 else others[i % len(others)])
    for i in range(6):
        z += 0.001
        sheet_world(F.p(rng.uniform(-1.1, 1.1), rng.uniform(-0.55, 0.55), z), F.r + rng.uniform(-1, 1), rng.choice([0.075, 0.21, 0.3]), (POSTITS + PAPERS)[i * 3 % (len(POSTITS) + len(PAPERS))])
    zt = z + 0.002
    for i in range(4):
        r = 0.035 + 0.008 * (i % 2)
        cyl('pt_roll', r, 0.7 - 0.07 * i, F.p(-1.0 + 0.08 * i, 0.5 - 0.04 * i, zt + r), mat_paper(blues[i % len(blues)]), rot=(0, rad(90), F.r + rad(6 * i - 8)), verts=24)
    # white models and printed prototypes
    box('pt_model_base', (0.55, 0.38, 0.02), F.p(0.55, 0.32, zt + 0.01), M['white'], rot=(0, 0, F.r + rad(-5)))
    for k in range(10):
        bw, bd, bh = rng.uniform(0.05, 0.12), rng.uniform(0.05, 0.1), rng.uniform(0.04, 0.2)
        box('pt_block', (bw, bd, bh), F.p(0.35 + rng.uniform(0, 0.4), 0.18 + rng.uniform(0, 0.28), zt + 0.02 + bh / 2), M['white'], rot=(0, 0, F.r + rad(-5)))
    cyl('pt_print', 0.05, 0.11, F.p(-0.25, -0.3, zt + 0.055), mat_color('print_or', (0.85, 0.3, 0.06), 0.4), verts=6)
    box('pt_proto', (0.16, 0.1, 0.06), F.p(-0.5, -0.32, zt + 0.03), M['graphite'], rot=(0, 0, F.r + rad(20)), bevel=0.008)
    box('pt_ruler', (0.6, 0.03, 0.004), F.p(0.0, -0.05, zt + 0.002), M['alu'], rot=(0, 0, F.r + rad(-14)))
    box('pt_tablet', (0.18, 0.25, 0.008), F.p(1.0, -0.35, zt + 0.004), M['black'], rot=(0, 0, F.r + rad(10)), bevel=0.006)
    plane('pt_tablet_scr', 0.165, 0.235, F.p(1.0, -0.35, zt + 0.0085), mat_screen(os.path.join(TEX2, 'tablette-reservation.jpg'), 1.2), rot=(0, 0, F.r + rad(10)), c=C_FX)
    put('metal_stool_01', (x - 0.95, y - 0.6, 0), rz=rad(30))


def plan_chest(loc, rz=0.0):
    x, y = loc
    box('pc_body', (0.8, 1.1, 0.88), (x, y, 0.44), mat_color('pc_green', (0.16, 0.2, 0.17), 0.5, 0.4), rot=(0, 0, rz), bevel=0.006)
    for k in range(8):
        box('pc_dr', (0.006, 1.02, 0.004), (x - 0.403, y, 0.1 + k * 0.1), M['graphite'], rot=(0, 0, rz))
        box('pc_handle', (0.012, 0.12, 0.012), (x - 0.41, y, 0.14 + k * 0.1), M['alu'], rot=(0, 0, rz))
    blues = sorted(glob.glob(os.path.join(TEXG, 'plan-bleu-*.jpg')))
    for i in range(5):
        cyl('pc_roll', 0.04, 0.9, (x - 0.15 + 0.08 * (i % 3), y - 0.3 + 0.14 * i, 0.92), mat_paper(blues[i % len(blues)]), rot=(rad(90), 0, rz + rad(4 * i)), verts=20)


def planning_wall(x, y0, y1, z0=0.9, z1=2.7):
    """Plans pinned on the right wall, a grid of sheets, post-its and a timeline strip (facing -X)."""
    W = y1 - y0
    plane('pw_board', W, z1 - z0, (x - 0.02, (y0 + y1) / 2, (z0 + z1) / 2), M['board'], rot=(rad(90), 0, rad(90)))
    rng = random.Random(31)
    items = sorted(glob.glob(os.path.join(TEXG, 'plan-*.jpg'))) + sorted(glob.glob(os.path.join(TEXG, 'maquette-*.jpg')))
    k = 0
    for col in range(int(W / 0.55)):
        for row in range(2):
            pth = items[k % len(items)]
            k += 1
            o = sheet_world((x - 0.03 - k * 0.0005, y0 + 0.35 + col * 0.55, z1 - 0.38 - row * 0.5), rad(90), 0.42, pth, rx=rad(90))
            o.rotation_euler = (rad(90), rng.uniform(-0.04, 0.04), rad(90))
    box('pw_line', (0.004, W - 0.3, 0.008), (x - 0.03, (y0 + y1) / 2, z0 + 0.38), M['black'])
    for i in range(int(W / 0.3)):
        cyl('pw_dot', 0.02, 0.006, (x - 0.032, y0 + 0.2 + i * 0.3, z0 + 0.38), M['tape'] if i % 4 == 0 else M['black'], rot=(0, rad(90), 0), verts=12)
        if i % 2 == 0:
            o = sheet_world((x - 0.034, y0 + 0.2 + i * 0.3, z0 + 0.2), rad(90), 0.075, POSTITS[i % len(POSTITS)], rx=rad(90))
            o.rotation_euler = (rad(90), 0, rad(90))


def drafting_board(loc, rz):
    x, y = loc
    c, s_ = math.cos(rz), math.sin(rz)
    for sx in (-1, 1):
        tube_between('db_leg', (x + sx * 0.5 * c, y + sx * 0.5 * s_, 0), (x + sx * 0.45 * c, y + sx * 0.45 * s_, 0.85), 0.02, M['graphite'], verts=8)
    b = box('db_board', (1.2, 0.85, 0.025), (x, y, 1.0), M['offwhite'], rot=(rad(28), 0, rz))
    blues = sorted(glob.glob(os.path.join(TEXG, 'plan-bleu-*.jpg')))
    o = sheet_world((x - 0.0 * s_, y, 1.016), rz, 0.8, sorted(glob.glob(os.path.join(TEXG, 'plan-coupe-*.jpg')))[0], rx=rad(28))
    o.location = Vector((x, y, 1.0)) + Vector((-math.sin(rad(28)) * s_ * 0.0, 0, 0.016))
    box('db_arm', (0.9, 0.02, 0.01), (x, y - 0.1, 1.06), M['alu'], rot=(rad(28), 0, rz + rad(25)))
    box('db_arm2', (0.02, 0.7, 0.01), (x + 0.2, y, 1.04), M['alu'], rot=(rad(28), 0, rz))


def projects_corner():
    light_ceiling(6.25, 11.6, 2.8, 4.0, 3.5, name='lcp')
    plan_table3((6.25, 11.6))
    plan_chest((7.5, 8.4))
    planning_wall(7.98, 9.4, 14.0)
    drafting_board((5.3, 8.6), rad(-30))
    put('metal_stool_01', (5.05, 13.2, 0), rz=rad(-20))
    for i in range(3):
        taped_box((7.45, 14.8 + 0.05 * i, 0.32 * i), (0.5, 0.4, 0.32), rad(4 * i))


# ------------------------------------------------------------------ zone 3 : the workshop
def cnc(loc, rz):
    x, y = loc
    box('cnc_body', (1.3, 1.1, 0.8), (x, y, 0.4), M['graphite'], rot=(0, 0, rz), bevel=0.01)
    box('cnc_hood', (1.3, 1.1, 0.75), (x, y, 1.18), M['glass_dark'], rot=(0, 0, rz))
    box('cnc_frame', (1.32, 0.05, 0.78), (x, y - 0.55, 1.18), M['black'], rot=(0, 0, rz))
    box('cnc_gantry', (1.1, 0.12, 0.12), (x, y, 1.25), M['alu'], rot=(0, 0, rz))
    cyl('cnc_spindle', 0.05, 0.3, (x + 0.2, y, 1.05), M['steel'], verts=16)
    box('cnc_light', (1.0, 0.8, 0.01), (x, y, 1.53), M['printer_light'], rot=(0, 0, rz), c=C_FX)
    box('cnc_panel', (0.3, 0.05, 0.4), (x + 0.75, y - 0.3, 1.0), M['black'], rot=(0, 0, rz))
    plane('cnc_screen', 0.22, 0.16, (x + 0.75, y - 0.33, 1.05), mat_screen(os.path.join(TEX2, 'ecran-dashboard.jpg'), 1.2), rot=(rad(90), 0, rz), c=C_FX)


def prototype_stand(loc):
    x, y = loc
    cyl('ps_base', 0.3, 0.05, (x, y, 0.025), M['black'], verts=32)
    cyl('ps_post', 0.03, 0.9, (x, y, 0.5), M['steel'], verts=12)
    box('ps_plate', (0.5, 0.5, 0.02), (x, y, 0.95), M['steel'])
    for sx in (-1, 1):
        for sy in (-1, 1):
            box('ps_ext', (0.03, 0.03, 0.45), (x + sx * 0.2, y + sy * 0.2, 1.18), M['alu'])
    for z in (0.97, 1.4):
        for (a, b) in [((-0.2, -0.2), (0.2, -0.2)), ((-0.2, 0.2), (0.2, 0.2)), ((-0.2, -0.2), (-0.2, 0.2)), ((0.2, -0.2), (0.2, 0.2))]:
            tube_between('ps_bar', (x + a[0], y + a[1], z), (x + b[0], y + b[1], z), 0.015, M['alu'], verts=6)
    box('ps_board', (0.25, 0.18, 0.02), (x, y, 1.1), mat_color('pcb', (0.05, 0.28, 0.12), 0.5), rot=(0, 0, rad(10)))
    cyl('ps_motor', 0.07, 0.14, (x + 0.08, y - 0.05, 1.25), M['orange'], rot=(rad(90), 0, 0), verts=20)
    cyl('ps_batt', 0.05, 0.22, (x - 0.1, y + 0.08, 1.22), M['black'], rot=(0, rad(90), 0), verts=16)
    curve_cable('ps_wire', [(x - 0.1, y, 1.12), (x, y + 0.12, 1.3), (x + 0.1, y, 1.25), (x + 0.3, y - 0.3, 0.9), (x + 0.6, y - 0.6, 0.01)], 0.006, M['orange'])


def workshop3():
    x0, y0, L = -7.45, 8.2, 4.6
    h = 0.92
    F = Frame(x0, y0 + L / 2, 0, rad(90))      # local x along the wall (+Y world), local +Y = towards the wall (-X world)
    box('wb_top', (L, 0.85, 0.06), F.p(0, 0, h - 0.03), M['oak'], rot=(0, 0, F.r), bevel=0.004)
    for lx in (-L / 2 + 0.1, -0.7, 0.7, L / 2 - 0.1):
        for ly in (-0.36, 0.36):
            box('wb_leg', (0.07, 0.07, h - 0.06), F.p(lx, ly, (h - 0.06) / 2), M['steel3'], rot=(0, 0, F.r))
    box('wb_shelf', (L - 0.1, 0.75, 0.03), F.p(0, 0, 0.18), M['steel3'], rot=(0, 0, F.r))
    for i in range(8):
        box('wb_bin', (0.38, 0.5, 0.2), F.p(-L / 2 + 0.35 + i * 0.55, 0.0, 0.3), M['white'] if i % 3 else M['tape'], rot=(0, 0, F.r), bevel=0.01)
    box('wb_peg', (L, 0.02, 1.1), F.p(0, 0.5, h + 0.75), M['black_m'], rot=(0, 0, F.r))
    box('wb_upper', (L, 0.3, 0.025), F.p(0, 0.36, h + 1.4), M['black'], rot=(0, 0, F.r))
    rng = random.Random(14)
    for i in range(int(L / 0.38)):
        lx = -L / 2 + 0.22 + i * 0.38
        if i % 4 == 1:
            for k in range(2):
                cyl('wb_spool', 0.09, 0.07, F.p(lx - 0.05 + k * 0.1, 0.36, h + 1.5), mat_color('spool_w%d' % k, [(0.85, 0.3, 0.06), (0.85, 0.85, 0.85)][k], 0.5), rot=(0, rad(90), F.r), verts=24)
        else:
            box('wb_ubin', (0.3, 0.24, 0.17), F.p(lx, 0.36, h + 1.5), M['white'] if i % 3 else M['tape'], rot=(0, 0, F.r), bevel=0.008)
    tools = ['pliers', 'combination_wrench', 'screwdriver', 'tongue_groove_pliers', 'adjustable_wrench', 'screwdrivers_02', 'pliers', 'combination_wrench', 'screwdriver']
    for i, aid in enumerate(tools):
        F.put(aid, -L / 2 + 0.3 + i * (L - 0.6) / (len(tools) - 1), 0.47, h + 0.55 + 0.25 * (i % 2), rx=rad(90), rz=rad(180) + rad(rng.uniform(-8, 8)))
    # on the bench: cobot arm, printers, parts, a laptop, a vise
    ra = F.p(-0.4, 0.05, h)
    cyl('cb_base', 0.14, 0.08, ra + Vector((0, 0, 0.04)), M['graphite'], verts=32)
    p0 = ra + Vector((0, 0, 0.08))
    p1 = p0 + Vector((0.0, 0.0, 0.32))
    p2 = p1 + Vector((0.35, -0.15, 0.22))
    p3 = p2 + Vector((0.28, -0.05, -0.32))
    for (a, b, r) in [(p0, p1, 0.07), (p1, p2, 0.055), (p2, p3, 0.045)]:
        tube_between('cb_link', a, b, r, M['offwhite'], verts=20)
    for (p, r) in [(p1, 0.085), (p2, 0.07)]:
        o = cyl('cb_joint', r, 0.16, p, M['orange'], verts=24)
        o.rotation_euler = (rad(90), 0, F.r)
    box('cb_tool', (0.08, 0.06, 0.1), p3 + Vector((0, 0, -0.05)), M['graphite'], rot=(0, 0, F.r))
    printer3d(F.p(1.55, 0.1, h), F.r + math.pi)
    printer3d(F.p(2.0, 0.1, h), F.r + math.pi, (0.9, 0.9, 0.9))
    F.put('circuit_board', 0.45, -0.15, h, s=0.6, rz=rad(25))
    box('wb_mat', (0.6, 0.45, 0.003), F.p(0.5, -0.12, h + 0.0015), mat_color('cutmat3', (0.08, 0.22, 0.17), 0.8), rot=(0, 0, F.r))
    for k in range(5):
        box('wb_part', (rng.uniform(0.04, 0.12), rng.uniform(0.04, 0.1), rng.uniform(0.02, 0.06)), F.p(0.2 + rng.uniform(0, 0.7), -0.1 + rng.uniform(-0.2, 0.15), h + 0.03), rng.choice([M['alu'], M['graphite'], M['orange']]), rot=(0, 0, rng.uniform(0, 3)))
    box('wb_lap', (0.31, 0.22, 0.012), F.p(-1.4, -0.12, h + 0.006), M['alu'], rot=(0, 0, F.r + rad(10)), bevel=0.003)
    box('wb_lap_lid', (0.31, 0.006, 0.21), F.p(-1.4, -0.01, h + 0.11), M['alu'], rot=(rad(15), 0, F.r + rad(10)))
    plane('wb_lap_scr', 0.29, 0.19, F.p(-1.4, -0.017, h + 0.11), mat_screen(os.path.join(TEX2, 'ecran-3d.jpg'), 1.4), rot=(rad(105), 0, F.r + rad(10)), c=C_FX)
    F.put('bench_vice_01', -1.95, -0.25, h, keep=['bench_vice_bar', 'bench_vice_clamp', 'bench_vice_dial', 'bench_vice_frame'], rz=rad(180))
    # work lights: cold tube above, two warm clamp lamps
    box('wb_tube', (L - 0.4, 0.06, 0.04), F.p(0, 0.3, h + 1.95), M['black'], rot=(0, 0, F.r))
    box('wb_tube_led', (L - 0.5, 0.04, 0.005), F.p(0, 0.3, h + 1.927), M['tube_cold'], rot=(0, 0, F.r), c=C_FX)
    add_light('AREA', 'ws_tube', F.p(0, 0.2, h + 1.9), float(OPT.get('wsw', 160)), (0.85, 0.92, 1.0), target=F.p(0, -0.2, h), size=L - 0.5)
    architect_lamp(F.p(-0.9, 0.35, h), F.p(-0.6, -0.05, h + 0.6), F.p(-0.5, -0.15, h), 110, (1.0, 0.8, 0.58))
    architect_lamp(F.p(1.0, 0.35, h), F.p(0.7, -0.05, h + 0.55), F.p(0.55, -0.15, h), 90, (1.0, 0.8, 0.58))
    # machines and stands around
    cnc((-6.85, 14.2), 0)
    prototype_stand((-5.75, 11.0))
    box('tc_body', (0.7, 0.48, 1.0), (-5.65, 7.5, 0.55), M['red'], rot=(0, 0, rad(-10)), bevel=0.01)
    for k in range(6):
        box('tc_dr', (0.66, 0.005, 0.006), (-5.65 + 0.24 * math.sin(rad(-10)), 7.5 - 0.243 * math.cos(rad(-10)), 0.2 + k * 0.14), M['alu'], rot=(0, 0, rad(-10)))
    for (sx, sy) in [(-0.3, -0.2), (0.3, -0.2), (-0.3, 0.2), (0.3, 0.2)]:
        cyl('tc_caster', 0.04, 0.03, (-5.65 + sx, 7.5 + sy, 0.04), M['black'], rot=(rad(90), 0, 0), verts=12)
    put('metal_stool_01', (-6.4, 10.2, 0), rz=rad(40))
    put('plastic_container', (-6.6, 7.4, 0), rz=rad(10), s=0.9)
    put('plastic_container', (-6.6, 7.4, 0.3), rz=rad(-5), s=0.8)
    curve_cable('ws_reel', [(-7.6, 12.6, 0.3), (-7.2, 12.8, 0.012), (-6.4, 12.2, 0.012), (-5.9, 11.4, 0.012)], 0.012, M['cable_y'] if 'cable_y' in M else M['orange'])


# ------------------------------------------------------------------ zone 4 : server cage, storage
def server_cage(x0, x1, y0, y1, H=2.6):
    for (a, b) in [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1))]:
        a, b = Vector(a), Vector(b)
        L = (b - a).length
        n = max(1, round(L / 1.1))
        horiz = abs(b.x - a.x) > abs(b.y - a.y)
        for i in range(n):
            pa = a + (b - a) * (i / n)
            pb = a + (b - a) * ((i + 1) / n)
            m = (pa + pb) / 2
            plane('cg_mesh', (pb - pa).length, H - 0.1, (m.x, m.y, (H - 0.1) / 2 + 0.05), M['grid'], rot=(rad(90), 0, 0 if horiz else rad(90)), c=C_ARCH)
        for i in range(n + 1):
            p = a + (b - a) * (i / n)
            box('cg_post', (0.05, 0.05, H), (p.x, p.y, H / 2), M['black'], c=C_ARCH)
        box('cg_head', ((b - a).length + 0.05, 0.05, 0.05) if horiz else (0.05, (b - a).length + 0.05, 0.05), ((a + b) / 2).to_3d() + Vector((0, 0, H)), M['black'], c=C_ARCH)
    n = 3
    for i in range(n):
        rack_v2((x0 + 0.6 + i * 0.72, y1 - 0.65), 0)
        tube_between('cg_cable', (x0 + 0.6 + i * 0.72, y1 - 0.65, 2.15), (x0 + 0.6 + i * 0.72, y1 - 0.3, 5.2), 0.035, M['rubber'], verts=8)
    box('cg_tray', (x1 - x0, 0.35, 0.05), ((x0 + x1) / 2, y1 - 0.4, 2.45), M['steel'])
    add_light('AREA', 'cg_fill', ((x0 + x1) / 2, y1 - 1.3, 2.4), float(OPT.get('srw', 160)), (0.6, 0.8, 1.0), target=((x0 + x1) / 2, y1 - 0.6, 1.0), size=1.5)


def storage3():
    for i in range(2):
        x = 6.0 + i * 1.05
        box('st_frame', (1.0, 0.5, 2.1), (x, 21.3, 1.05), M['black'], bevel=0.004)
        for k in range(4):
            box('st_plank', (0.96, 0.46, 0.02), (x, 21.3, 0.35 + k * 0.5), M['graphite'])
            taped_box((x - 0.2, 21.3, 0.36 + k * 0.5), (0.34, 0.36, 0.22), rad(3 * k), tape=k % 2 == 0)
            taped_box((x + 0.22, 21.3, 0.36 + k * 0.5), (0.3, 0.34, 0.18), rad(-4 * k), tape=k % 2 == 1)
    flight_case((5.6, 19.6, 0), (1.0, 0.6, 0.55), rad(6))
    flight_case((5.62, 19.6, 0.55), (0.8, 0.5, 0.45), rad(-4))
    flight_case((7.1, 19.2, 0), (0.7, 0.7, 0.8), rad(12))
    put('ladder_sectioned_01', (7.75, 17.4, 0), rx=rad(-12), rz=rad(-90), keep=['ladder_section_01'])


# ------------------------------------------------------------------ light groups and look variants
GROUPS = {'fan': ('fan_spot', 'hot_plane'), 'projets': ('lcp_',), 'bureau': ('dk_', 'al_light', 'mon_screen', 'chair'),
          'atelier': ('ws_', 'wb_', 'cnc_', 'p3d_'), 'accents': (), 'ambiant': ()}
VARIANTS = {
    'A': dict(fan=1.0, projets=1.0, bureau=1.0, atelier=1.0, accents=1.0, ambiant=1.0),
    'B': dict(fan=1.35, projets=0.55, bureau=0.75, atelier=0.55, accents=1.0, ambiant=0.4),
    'C': dict(fan=0.7, projets=1.25, bureau=1.5, atelier=1.4, accents=1.3, ambiant=1.0),
    'D': dict(fan=0.4, projets=1.25, bureau=1.5, atelier=1.4, accents=1.3, ambiant=1.0),
}


def setup_lightgroups():
    vl = bpy.context.view_layer
    for g in GROUPS:
        vl.lightgroups.add(name=g)
    vl.cycles.denoising_store_passes = True
    SC.world.lightgroup = 'ambiant'
    for o in bpy.data.objects:
        g = 'accents'
        for name, prefixes in GROUPS.items():
            if any(o.name.startswith(p) for p in prefixes):
                g = name
                break
        if o.name.startswith(('al_light',)):
            # the desk lamp spot vs the workshop clamp lamps: decide by position
            g = 'atelier' if o.location.x < -4.5 else 'bureau'
        if o.name.startswith('fill'):
            g = 'ambiant'
        try:
            o.lightgroup = g
        except Exception:
            pass


def compositor3(variants_out):
    SC.use_nodes = True
    nt = SC.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    rl = nt.nodes.new('CompositorNodeRLayers')
    comp = nt.nodes.new('CompositorNodeComposite')
    fo = nt.nodes.new('CompositorNodeOutputFile')
    fo.base_path = variants_out
    fo.format.file_format = 'PNG'
    fo.file_slots.clear()
    first = True
    for vname, w in VARIANTS.items():
        acc = None
        for g, k in w.items():
            mul = nt.nodes.new('CompositorNodeMixRGB')
            mul.blend_type = 'MULTIPLY'
            mul.inputs['Fac'].default_value = 1.0
            nt.links.new(rl.outputs['Combined_' + g], mul.inputs[1])
            mul.inputs[2].default_value = (k, k, k, 1)
            if acc is None:
                acc = mul.outputs[0]
            else:
                add = nt.nodes.new('CompositorNodeMixRGB')
                add.blend_type = 'ADD'
                add.inputs['Fac'].default_value = 1.0
                nt.links.new(acc, add.inputs[1])
                nt.links.new(mul.outputs[0], add.inputs[2])
                acc = add.outputs[0]
        dn = nt.nodes.new('CompositorNodeDenoise')
        nt.links.new(acc, dn.inputs['Image'])
        nt.links.new(rl.outputs['Denoising Normal'], dn.inputs['Normal'])
        nt.links.new(rl.outputs['Denoising Albedo'], dn.inputs['Albedo'])
        gl = nt.nodes.new('CompositorNodeGlare')
        gl.glare_type = 'FOG_GLOW'
        try:
            gl.quality = 'HIGH'
            gl.inputs['Threshold'].default_value = 1.2
            gl.inputs['Strength'].default_value = 0.28
        except Exception as e:
            print('glare', e)
        nt.links.new(dn.outputs[0], gl.inputs['Image'])
        fo.file_slots.new(vname + '_')
        nt.links.new(gl.outputs['Image'], fo.inputs[vname + '_'])
        if vname == OPT.get('main', 'D'):
            nt.links.new(gl.outputs['Image'], comp.inputs['Image'])
            first = False


# ------------------------------------------------------------------ layout v3
def shell(W, D, H, fc, Rf, wall_mat=None):
    wm = wall_mat or M['wall']
    box('floor', (W + 2, D + 4, 0.2), (0, D / 2, -0.1), M['floor'], c=C_ARCH)
    box('wall_L', (0.5, D + 4, H), (-W / 2 - 0.25, D / 2, H / 2), wm, c=C_ARCH)
    box('wall_R', (0.5, D + 4, H), (W / 2 + 0.25, D / 2, H / 2), wm, c=C_ARCH)
    box('wall_F', (W + 2, 0.5, H), (0, -1.0, H / 2), wm, c=C_ARCH)
    wall_with_hole('wall_B', -W / 2 - 0.5, W / 2 + 0.5, D, D + 1.0, 0, H, fc, Rf + 0.18, wm)


def services(W, D, H, dense=True, sides_only=False):
    runs = [(-6.6, 0.16, 'black'), (-6.2, 0.1, 'pipe'), (-2.6, 0.38, 'galva'), (1.4, 0.13, 'black'), (1.75, 0.08, 'pipe'), (3.2, 0.3, 'galva'), (6.4, 0.14, 'black')]
    if sides_only:
        runs = [(-6.6, 0.16, 'black'), (-6.2, 0.1, 'pipe'), (-5.85, 0.22, 'galva'), (6.4, 0.14, 'black'), (6.05, 0.22, 'galva'), (6.75, 0.1, 'pipe')]
    if dense:
        runs += [(-5.9, 0.1, 'pipe'), (-1.6, 0.09, 'black'), (2.0, 0.08, 'pipe'), (6.75, 0.1, 'pipe')]
    for (x, r, m) in runs:
        cyl('pipe', r, D + 2, (x, D / 2, H - 0.75 - r), M[m], rot=(rad(90), 0, 0), verts=20, c=C_CEIL)
    for x in (-7.3, 7.3):
        box('tray', (0.45, D, 0.06), (x, D / 2, H - 1.25), M['steel'], c=C_CEIL)


def fittings(D):
    put('utility_box_02', (3.6, D - 0.3, 0), rz=0)
    put('power_box_01', (-3.8, D - 0.06, 1.6), keep=['power_box_01_box', 'power_box_01_door'])
    put('korean_fire_extinguisher_01', (4.35, 5.6, 0), rz=rad(-90))


def hall_variant(kind, W, D, fc, Rf):
    """Architecture variants around the same furniture. Returns the ceiling height."""
    cols = [(x, y) for y in (6.0, 12.0, 18.0) for x in (-4.8, 4.8)]
    if kind == 'actuel':
        hall3(W, D, 6.5, fc, Rf)
        return 6.5
    if kind == 'champignons':
        H = 6.5
        shell(W, D, H, fc, Rf)
        box('slab', (W + 2, D + 4, 0.4), (0, D / 2, H + 0.2), M['ceil'], c=C_CEIL)
        for (x, y) in cols:
            cyl('mush_col', 0.32, H - 1.35, (x, y, (H - 1.35) / 2), M['col'], verts=48, c=C_ARCH)
            bm = bmesh.new()
            bmesh.ops.create_cone(bm, cap_ends=True, segments=48, radius1=0.32, radius2=1.5, depth=1.1)
            me = bpy.data.meshes.new('cap')
            bm.to_mesh(me)
            bm.free()
            for f in me.polygons:
                f.use_smooth = True
            o = bpy.data.objects.new('mush_cap', me)
            o.location = (x, y, H - 0.25 - 0.55)
            me.materials.append(M['col'])
            link(o, C_ARCH)
            cyl('mush_drop', 1.7, 0.25, (x, y, H - 0.125), M['col'], verts=48, c=C_CEIL)
        services(W, D, H, dense=False)
        fittings(D)
        leds([(-7.7, D - 0.05, 5.4), (7.7, D - 0.05, 5.4), (-7.95, 10.0, 4.9), (7.95, 15.0, 4.9)])
        return H
    if kind == 'charpente':
        H = 8.5
        shell(W, D, H, fc, Rf)
        box('deck', (W + 2, D + 4, 0.15), (0, D / 2, H + 0.08), M['steel3'], c=C_CEIL)
        for k in range(int((D + 2) / 0.6)):
            box('deck_rib', (W + 2, 0.08, 0.12), (0, -1 + k * 0.6, H - 0.06), M['steel3'], c=C_CEIL)
        for (x, y) in cols:
            box('hcol_web', (0.04, 0.4, H), (x, y, H / 2), M['steel3'], c=C_ARCH)
            for s_ in (-1, 1):
                box('hcol_fl', (0.4, 0.04, H), (x, y + s_ * 0.2, H / 2), M['steel3'], c=C_ARCH)
        for y in (6.0, 12.0, 18.0):
            zb, zt = H - 2.2, H - 0.3
            box('tr_bot', (W, 0.25, 0.25), (0, y, zb), M['steel3'], c=C_CEIL)
            box('tr_top', (W, 0.25, 0.25), (0, y, zt), M['steel3'], c=C_CEIL)
            n = 12
            for i in range(n + 1):
                x = -W / 2 + i * W / n
                box('tr_v', (0.12, 0.12, zt - zb), (x, y, (zb + zt) / 2), M['steel3'], c=C_CEIL)
                if i < n:
                    a, b = (x, y, zb if i % 2 == 0 else zt), (x + W / n, y, zt if i % 2 == 0 else zb)
                    tube_between('tr_d', a, b, 0.05, M['steel3'], verts=6, c=C_CEIL)
        for y in (3.0, 9.0, 15.0):
            put('caged_hanging_light', (0, y, H - 3.2))
            add_light('POINT', 'acc_cage', (0, y, H - 3.15), 40, (1.0, 0.78, 0.55), size=0.12)
        services(W, D, H - 1.6, dense=False)
        fittings(D)
        leds([(-7.7, D - 0.05, 7.4), (7.7, D - 0.05, 7.4), (-4.8, 6.25, 6.6), (4.8, 12.25, 6.6)])
        return H
    if kind == 'caissons':
        H = 6.8
        shell(W, D, H, fc, Rf)
        box('slab', (W + 2, D + 4, 0.4), (0, D / 2, H + 0.2), M['ceil'], c=C_CEIL)
        for i in range(11):
            box('waffle_x', (0.28, D + 2, 0.55), (-W / 2 + i * 1.6, D / 2, H - 0.275), M['col'], c=C_CEIL)
        for j in range(12):
            box('waffle_y', (W, 0.28, 0.55), (0, j * 2.0, H - 0.275), M['col'], c=C_CEIL)
        for (x, y) in cols:
            box('column', (0.7, 0.7, H), (x, y, H / 2), M['col'], bevel=0.01, c=C_ARCH)
        services(W, D, H - 0.4, dense=False, sides_only=True)
        fittings(D)
        leds([(-7.7, D - 0.05, 5.6), (7.7, D - 0.05, 5.6), (-7.95, 10.0, 5.0), (7.95, 15.0, 5.0)])
        return H
    if kind == 'passerelles':
        H = 10.0
        shell(W, D, H, fc, Rf)
        box('slab', (W + 2, D + 4, 0.4), (0, D / 2, H + 0.2), M['ceil'], c=C_CEIL)
        for (x, y) in cols:
            box('column', (0.6, 0.6, H), (x, y, H / 2), M['col'], bevel=0.01, c=C_ARCH)
        for y in (6.0, 12.0, 18.0):
            box('beam_x', (W, 0.5, 0.7), (0, y, H - 0.35), M['col'], c=C_CEIL)
        M['grate'] = mat_pbr('grate3', 'metal_grate_rusty', 1.0, dark=0.6, metal=0.7)
        zc = 4.2
        y0 = 5.0
        for s_ in (-1, 1):
            x = s_ * (W / 2 - 0.8)
            box('cw_side', (1.6, D - y0, 0.08), (x, (D + y0) / 2, zc), M['grate'], c=C_ARCH)
            box('cw_side_beam', (0.12, D - y0, 0.3), (x - s_ * 0.8, (D + y0) / 2, zc - 0.19), M['steel3'], c=C_ARCH)
            railing((x - s_ * 0.8, y0, zc), (x - s_ * 0.8, D - 0.1, zc), c=C_ARCH)
            for y in (6.0, 10.0, 14.0, 18.0, 21.5):
                box('cw_bracket', (1.6, 0.1, 0.1), (x, y, zc - 0.25), M['steel3'], c=C_ARCH)
        box('cw_back', (W - 3.2, 1.4, 0.08), (0, D - 0.7, 6.0), M['grate'], c=C_ARCH)
        railing((-W / 2 + 1.6, D - 1.4, 6.0), (W / 2 - 1.6, D - 1.4, 6.0), c=C_ARCH)
        stairs(-W / 2 + 0.4, -W / 2 + 1.5, y0, zc, -1, steps=14, c=C_ARCH)
        for x in (-W / 2 + 1.6, W / 2 - 1.6):
            for y in (D - 0.1, D - 1.4):
                box('cw_hanger', (0.05, 0.05, H - 6.0), (x, y, (H + 6.0) / 2), M['steel3'], c=C_ARCH)
        services(W, D, H, dense=True)
        fittings(D)
        leds([(-7.7, D - 0.05, 8.4), (7.7, D - 0.05, 8.4), (-7.95, 10.0, 7.0), (7.95, 15.0, 7.0), (0, D - 0.1, 6.6)])
        return H
    if kind == 'roche':
        H = 7.0
        M['rockw'] = mat_pbr('rock3', 'rock_wall_08', 3.2, dark=0.5, bump=1.6)
        box('floor', (W + 4, D + 4, 0.2), (0, D / 2, -0.1), M['floor'], c=C_ARCH)
        wall_with_hole('wall_B', -W / 2 - 1.4, W / 2 + 1.4, D, D + 1.0, 0, H + 0.3, fc, Rf + 0.18, M['col'])
        tx = bpy.data.textures.new('rock_noise', 'CLOUDS')
        tx.noise_scale = 2.0
        tx.noise_depth = 4

        tx2 = bpy.data.textures.new('rock_fine', 'VORONOI')
        tx2.noise_scale = 0.45
        tx2.distance_metric = 'DISTANCE'

        def rock(name, size, loc, rot, strength=1.0):
            o = plane(name, size[0], size[1], loc, M['rockw'], rot=rot, c=C_ARCH)
            sub = o.modifiers.new('sub', 'SUBSURF')
            sub.subdivision_type = 'SIMPLE'
            sub.levels = sub.render_levels = 8
            for (t, st) in ((tx, strength), (tx2, 0.18)):
                dm = o.modifiers.new('disp', 'DISPLACE')
                dm.texture = t
                dm.strength = st
                dm.texture_coords = 'GLOBAL'
            o.modifiers.new('smooth', 'SMOOTH').iterations = 2
            for f in o.data.polygons:
                f.use_smooth = True
            return o
        rock('rock_L', (D + 4, H + 2.5), (-W / 2 - 0.75, D / 2, H / 2), (rad(90), 0, rad(90)))
        rock('rock_R', (D + 4, H + 2.5), (W / 2 + 0.75, D / 2, H / 2), (rad(90), 0, rad(-90)))
        rock('rock_F', (W + 3, H + 2.5), (0, -1.6, H / 2), (rad(90), 0, 0))
        rock('rock_C', (W + 3, D + 4), (0, D / 2, H + 0.8), (rad(180), 0, 0), 1.5)
        for (x, y) in cols:
            box('column', (0.7, 0.7, H + 0.6), (x, y, (H + 0.6) / 2), M['col'], bevel=0.01, c=C_ARCH)
        for y in (6.0, 12.0, 18.0):
            box('ibeam', (W, 0.3, 0.45), (0, y, H - 0.4), M['steel3'], c=C_CEIL)
        services(W, D, H - 0.6, dense=False, sides_only=True)
        fittings(D)
        leds([(-6.8, D - 0.05, 5.4), (6.8, D - 0.05, 5.4), (-4.8, 6.4, 4.9), (4.8, 15.4, 4.9)])
        return H
    raise ValueError(kind)


def labo_v3():
    W, D, H = 16.0, 22.0, 6.5
    Rf = 2.25
    fc = (0.0, D, 3.0)
    H = hall_variant(OPT.get('archi', 'charpente'), W, D, fc, Rf)
    fan_v3(fc, Rf, n_blades=int(OPT.get('blades', 7)), angle=rad(9))
    light_box(fc, Rf, D + 1.0, power=float(OPT.get('fanp', 1.0)), target=(0.0, float(OPT.get('aimy', 12.0)), 0))
    if OPT.get('bureau', 'D') in BUILD:
        desk_concept(Frame(-0.4, 8.0, 0, rad(-8)), OPT.get('bureau', 'D'))
    else:
        desk_birdcage(Frame(-0.4, 8.0, 0, rad(-8)))
    projects_corner()
    workshop3()
    server_cage(-7.95, -5.0, 18.3, 21.75)
    storage3()
    for (x, y, kind, sz, pl, sc_) in [(-2.5, 9.0, 'white', 0.9, ('fern_02', ['fern_02_b']), 0.8), (4.25, 12.6, 'concrete', 1.2, ('pachira_aquatica_01', ['pachira_aquatica_01_bark_c', 'pachira_aquatica_01_leaves_c']), 0.9),
                                      (-4.25, 13.2, 'black', 1.0, ('calathea_orbifolia_01', ['calathea_orbifolia_01_a']), 1.1), (4.3, 17.3, 'white', 0.8, ('anthurium_botany_01', ['anthurium_botany_01_b']), 0.9),
                                      (-4.3, 17.0, 'concrete', 0.8, ('fern_02', ['fern_02_c']), 0.8), (2.6, 4.4, 'black', 1.1, ('pachira_aquatica_01', ['pachira_aquatica_01_bark_b', 'pachira_aquatica_01_leaves_b']), 0.9)]:
        if (x, y) == (-2.5, 9.0) and globals().get('AUTOUR', ['aucun'])[0] in globals().get('PISTES_AU', ()):
            continue                                  # the fern left of the desk gives way to the decor around the desk
        plant_pot((x, y), kind, sz, pl, sc_)
    if 'verifier_autour' in globals() and OPT.get('verif') == '1':
        verifier_autour(AU_NEWS, [o for o in bpy.data.objects if o not in AU_NEWS])
    if FOG:
        fog_volume((-W / 2, -0.8, 0), (W / 2, D - 0.05, H), density=float(OPT.get('fogd', 0.006)))
    add_light('AREA', 'fill', (0, 9, H - 0.5), float(OPT.get('fill', 0)), (0.75, 0.85, 1.0), target=(0, 9, 0), size=9)
    return {
        'c34': dict(cam=(-3.3, 3.4, 1.6), target=(0.7, 18.0, 2.3), lens=24, fstop=5.6, focus=5.4),
        'axe': dict(cam=(0.35, 2.5, 1.35), target=(0.0, D, 2.5), lens=24, fstop=5.6, focus=5.6),
        'bureau': dict(cam=(-2.7, 5.3, 1.55), target=(-0.15, 8.35, 1.0), lens=30, fstop=2.8, focus=None),
        'lampe': dict(cam=(-2.35, 6.8, 1.42), target=(-1.1, 8.2, 1.06), lens=36, fstop=2.8, focus=None),
        'rangements': dict(cam=(-2.05, 6.85, 0.82), target=(-0.75, 8.1, 0.34), lens=30, fstop=4, focus=None),
        'corbeille': dict(cam=(1.5, 6.15, 0.46), target=(0.5, 7.75, 0.24), lens=36, fstop=4, focus=None),   # the bin on the concrete
        'projets': dict(cam=(6.0, 14.6, 2.2), target=(6.8, 11.0, 0.95), lens=28, fstop=2.8, focus=None),
        'atelier': dict(cam=(-3.4, 8.4, 1.6), target=(-7.3, 11.0, 1.1), lens=26, fstop=2.8, focus=None),
        'serveurs': dict(cam=(-5.7, 15.4, 1.6), target=(-6.5, 21.2, 1.2), lens=28, fstop=4, focus=None),
        'ventilo': dict(cam=(0.9, 16.0, 0.5), target=(0.0, D, 3.4), lens=22, fstop=5.6, focus=6.0),
        'plan': dict(ortho=True, cam=(0, D / 2, 30), target=(0, D / 2, 0), scale=D + 1.5, portrait=True),
    }


def main3():
    setup_render()
    SC.view_settings.exposure = float(OPT.get('exposure', -0.15))
    M.clear()
    materials3()
    shots = labo_v3()
    setup_lightgroups()
    os.makedirs(OUT, exist_ok=True)
    if OPT.get('save') == '1':
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'labo-v3.blend'))
    for s in SHOTS:
        spec = shots[s]
        cam = make_camera(spec, 'CAM_' + s)
        SC.camera = cam
        compositor3(os.path.join(OUT, 'variantes', s + OPT.get('tag', '')))
        fog = bpy.data.objects.get('fog')
        ceil_coll = bpy.context.view_layer.layer_collection.children['CEILING']
        so = None
        if spec.get('ortho'):
            if fog:
                fog.hide_render = True
            ceil_coll.exclude = True
            for o in bpy.data.objects:
                if o.name.startswith('lcp') and o.type == 'MESH':
                    o.hide_render = True
            SC.render.resolution_x = int(RES * 0.75)
            SC.render.resolution_y = RES
            sun = bpy.data.lights.new('plan_sun', 'SUN')
            sun.energy = 4.0
            so = bpy.data.objects.new('plan_sun', sun)
            so.rotation_euler = (rad(5), rad(3), rad(30))
            ROOT.objects.link(so)
            so.lightgroup = 'ambiant'
        else:
            SC.render.resolution_x = RES
            SC.render.resolution_y = int(RES * 9 / 16)
        SC.render.filepath = os.path.join(OUT, f'V3-{s}{OPT.get("tag", "")}.png')
        print('RENDER', SC.render.filepath, flush=True)
        bpy.ops.render.render(write_still=True)
        if so:
            bpy.data.objects.remove(so)
            if fog:
                fog.hide_render = False
            ceil_coll.exclude = False


main3()
