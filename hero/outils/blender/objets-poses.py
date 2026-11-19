
# ================================================================== objects on the desk (step 8), the user's Sketchfab picks
# Rhyzome Plant, Indoor Plant, Soda Cans 3D pack, Paper Cup (Unperfect), Pencil, some eraser, Pen (all CC BY 4.0, see
# hero/credits.md), downloaded by the user into assets/modeles and unzipped into assets/sketchfab/<model>/_archive.
# The Sculpture (Escultura, Museu d'Art Jaume Morera) is prepared here too but goes into the lab decor, not on the desk.
# Every model is brought to its real size, its materials rebuilt (the downloads lose most texture links), and kept as
# a collection in LIB, instanced where it stands. Print: the stamp of an invented café (Pente) on the cup sleeve, from
# papiers-contenus/emballages.py + textures_objets.py (the can prints of the prototypes are still there, not used).
# Built after objets-papiers.py: objects stand on the height field of the papers (CH[0]) and raise it in turn, so they
# never cross a sheet or each other.
# Retained 15/11: prototype B "en cours" without its cans and without the second cup on the plans (default objets=B;
# objets=aucun = none, and in the lab the old placeholders come back). The sculpture waits for the lab decor step.
OBJETS = [OPT.get('objets', 'B')]
SKO = os.path.normpath(os.path.join(HERE, '..', 'assets', 'sketchfab'))
TEXO = os.path.normpath(os.path.join(HERE, '..', 'textures-bureau', 'objets'))
MO = {}
MATS_X = {}       # key -> f(object, slot name, variant) for the models that later modules add to SPECS


def _so(*p):
    return os.path.join(SKO, *p)


SPECS = {
    # key: file, objects to keep (blend), import axes, orientation, size (height or length along y, or a scale)
    'gobelet': dict(f=_so('paper-cup-unperfect', '_archive', 'source', 'UnPerfectCupSketchfab2.fbx'), height=0.122),
    'crayon': dict(f=_so('pencil', '_archive', 'source', 'pencil.fbx'), length=0.172, hexflat=True),
    'gomme': dict(f=_so('some-eraser', '_archive', 'source', 'er2_low.fbx'), scale=1.0),
    'stylo': dict(f=_so('pen', '_archive', 'source', 'Sketchfab_2024_02_02_17_13_02.blend'), names=['pen', 'Tip 1', 'Tip 2', 'low cap', 'Ink tube', 'Cap'],
                  rot=(-90, 0, 0), length=0.149),
    'canette_l': dict(f=_so('soda-cans-3d-pack', '_archive', 'source', 'Cans various types 3d model.blend'), names=['Low poly can (Long)'], scale=0.134 / 4.632),
    'canette_l_ecrasee': dict(f=_so('soda-cans-3d-pack', '_archive', 'source', 'Cans various types 3d model.blend'), names=['BAKED Soda can (Long) crushed (mid)'], scale=0.134 / 4.632),
    'canette_c': dict(f=_so('soda-cans-3d-pack', '_archive', 'source', 'Cans various types 3d model.blend'), names=['Low poly can (short)'], scale=0.115 / 3.511),
    'canette_c_ecrasee': dict(f=_so('soda-cans-3d-pack', '_archive', 'source', 'Cans various types 3d model.blend'), names=['BAKED Soda can (short) crushed (low)'], scale=0.115 / 3.511),
    'plante': dict(f=_so('indoor-plant', 'source', 'indoorplant.obj'), height=float(OPT.get('plante_h', 0.20))),
    'rhyzome': dict(f=_so('rhyzome-plant', '_archive', 'source', 'rhyzome plant.fbx'), height=0.56),
    'sculpture': dict(f=_so('escultura-museu-dart-jaume-morera', '_archive', 'inner', 'MALL1392_LP.obj'), axes=('Y', 'Z'), scale=1.0),
}


# ------------------------------------------------------------------ materials
def _tex(nt, path, noncolor=False, ext='REPEAT'):
    t = nt.nodes.new('ShaderNodeTexImage')
    t.image = img(path, noncolor)
    t.extension = ext
    return t


def _normal(nt, p, path, strength=1.0, directx=False):
    t = _tex(nt, path, True)
    nm = nt.nodes.new('ShaderNodeNormalMap')
    nm.inputs['Strength'].default_value = strength
    if directx:                                    # DirectX normal map: green channel flipped
        sep = nt.nodes.new('ShaderNodeSeparateColor')
        inv = nt.nodes.new('ShaderNodeMath')
        inv.operation = 'SUBTRACT'
        inv.inputs[0].default_value = 1.0
        comb = nt.nodes.new('ShaderNodeCombineColor')
        nt.links.new(t.outputs['Color'], sep.inputs['Color'])
        nt.links.new(sep.outputs[1], inv.inputs[1])
        nt.links.new(sep.outputs[0], comb.inputs[0])
        nt.links.new(inv.outputs[0], comb.inputs[1])
        nt.links.new(sep.outputs[2], comb.inputs[2])
        nt.links.new(comb.outputs['Color'], nm.inputs['Color'])
    else:
        nt.links.new(t.outputs['Color'], nm.inputs['Color'])
    nt.links.new(nm.outputs['Normal'], p.inputs['Normal'])


def m_tex(name, base, rough=0.6, normal=None, rough_map=None, metal_map=None, directx=False, nstr=1.0, metal=0.0):
    key = ('tex', name)
    if key in MO:
        return MO[key]
    m = new_mat('o_' + name)
    nt = m.node_tree
    p = principled(m)
    t = _tex(nt, base)
    nt.links.new(t.outputs['Color'], p.inputs['Base Color'])
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    if rough_map:
        nt.links.new(_tex(nt, rough_map, True).outputs['Color'], p.inputs['Roughness'])
    if metal_map:
        nt.links.new(_tex(nt, metal_map, True).outputs['Color'], p.inputs['Metallic'])
    if normal:
        _normal(nt, p, normal, nstr, directx)
    MO[key] = m
    return m


def m_plain(name, color, rough=0.5, metal=0.0, trans=0.0, ior=1.45, coat=0.0, sss=0.0, alpha=1.0):
    key = ('plain', name)
    if key in MO:
        return MO[key]
    m = mat_color('o_' + name, color, rough, metal)
    p = principled(m)
    p.inputs['Transmission Weight'].default_value = trans
    p.inputs['IOR'].default_value = ior
    p.inputs['Coat Weight'].default_value = coat
    p.inputs['Subsurface Weight'].default_value = sss
    p.inputs['Alpha'].default_value = alpha
    MO[key] = m
    return m


def m_canette(brand):
    """Aluminium can; the print (RGBA page capture) mapped on the side strip of the pack's own UVs:
    u 0.582..2.069 around the can (from the seam, the angle growing), v 0.056..0.917 from bottom to top.
    Where the page is transparent, and on the lid and the base, the metal stays bare."""
    key = ('can', brand)
    if key in MO:
        return MO[key]
    m = new_mat('o_canette_' + brand)
    nt = m.node_tree
    p = principled(m)
    uv = nt.nodes.new('ShaderNodeUVMap')
    uv.uv_map = 'UVMap'
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(uv.outputs['UV'], sep.inputs[0])
    comb = nt.nodes.new('ShaderNodeCombineXYZ')
    for i, (a, b) in enumerate(((0.582, 1.487), (0.056, 0.861))):
        ma = nt.nodes.new('ShaderNodeMath')
        ma.operation = 'MULTIPLY_ADD'
        nt.links.new(sep.outputs[i], ma.inputs[0])
        ma.inputs[1].default_value = 1.0 / b
        ma.inputs[2].default_value = -a / b
        nt.links.new(ma.outputs[0], comb.inputs[i])
    t = _tex(nt, os.path.join(TEXO, f'canette-{brand}.png'), ext='CLIP')
    t.interpolation = 'Cubic'
    nt.links.new(comb.outputs[0], t.inputs['Vector'])
    mix = nt.nodes.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    nt.links.new(t.outputs['Alpha'], mix.inputs[0])
    next(s for s in mix.inputs if s.identifier == 'A_Color').default_value = (0.86, 0.87, 0.88, 1)
    nt.links.new(t.outputs['Color'], next(s for s in mix.inputs if s.identifier == 'B_Color'))
    nt.links.new(next(s for s in mix.outputs if s.identifier == 'Result_Color'), p.inputs['Base Color'])
    for inp, k, c in (('Metallic', -0.72, 1.0), ('Roughness', 0.08, 0.2), ('Coat Weight', 0.6, 0.0)):
        ma = nt.nodes.new('ShaderNodeMath')
        ma.operation = 'MULTIPLY_ADD'
        nt.links.new(t.outputs['Alpha'], ma.inputs[0])
        ma.inputs[1].default_value = k
        ma.inputs[2].default_value = c
        nt.links.new(ma.outputs[0], p.inputs[inp])
    p.inputs['Coat Roughness'].default_value = 0.06
    MO[key] = m
    return m


def _mats(key, o, brand=None):
    """Material of each slot of an imported part, by model."""
    A = lambda *p: _so(*p)
    out = []
    for s in o.data.materials:
        n = s.name if s else ''
        if key == 'gobelet':
            if 'Label' in o.name:
                m = m_tex('manchon_pente', os.path.join(TEXO, 'manchon-pente.png'), 0.82)
            elif 'Lid' in o.name:
                m = m_tex('couvercle_kraft', A('paper-cup-unperfect', '_archive', 'textures', 'BrownPaperTexture.jpg'), 0.8)
            else:
                m = m_tex('gobelet_papier', A('paper-cup-unperfect', '_archive', 'textures', 'PaperCupTexture.jpg'), 0.5)
        elif key == 'crayon':
            t = A('pencil', '_archive', 'textures')
            m = m_tex('crayon', os.path.join(t, 'Pencil_Albedo.tga.png'), 0.42, os.path.join(t, 'Pencil_Normal.tga.png'),
                      metal_map=os.path.join(t, 'Pencil_Metallic.tga.png'))
        elif key == 'gomme':
            t = A('some-eraser', '_archive', 'textures')
            m = m_tex('gomme', os.path.join(t, 'Eraser2_Base_color.jpg'), 0.7, os.path.join(t, 'Eraser2_Normal_DirectX.jpg'),
                      rough_map=os.path.join(t, 'Eraser2_Roughness.jpg'), directx=True)
        elif key == 'stylo':
            m = {'Acrylic': lambda: m_plain('stylo_corps', (0.96, 0.97, 0.97), 0.04, trans=1.0, ior=1.49),
                 'Ink': lambda: m_plain('stylo_encre', (0.012, 0.012, 0.014), 0.22, coat=0.4),
                 'Blue plastic': lambda: m_plain('stylo_capuchon', (0.014, 0.014, 0.016), 0.28, coat=0.3),
                 'Beige plastic': lambda: m_plain('stylo_pointe', (0.82, 0.8, 0.75), 0.35, sss=0.2),
                 'Copper': lambda: m_plain('stylo_bille', (0.8, 0.64, 0.38), 0.25, metal=1.0)}.get(n, lambda: m_plain('stylo_encre', (0.012, 0.012, 0.014), 0.22))()
        elif key.startswith('canette'):
            m = m_canette(brand or 'ampere')
        elif key == 'plante':
            m = {'FrontColor': lambda: m_plain('plante_pot', (0.78, 0.77, 0.74), 0.32, coat=0.3),
                 '_Color_E04_1': lambda: m_plain('plante_panache', (0.62, 0.66, 0.38), 0.42, sss=0.08),
                 'Color_F11': lambda: m_plain('plante_feuille', (0.05, 0.17, 0.035), 0.4, sss=0.05, coat=0.15),
                 'Translucent_Glass_Gray': lambda: m_plain('plante_soucoupe', (0.7, 0.71, 0.7), 0.1, trans=0.9),
                 'Groundcover_Gravel_1inch': lambda: m_plain('plante_terre', (0.06, 0.045, 0.035), 0.95)}.get(n, lambda: m_plain('plante_feuille', (0.05, 0.17, 0.035), 0.4))()
        elif key == 'rhyzome':
            t = A('rhyzome-plant', '_archive', 'textures')
            if 'pot' in o.name:
                m = m_tex('rhyzome_pot', os.path.join(t, 'brushed_concrete texture.jpeg'), 0.85)
            else:
                m = m_tex('rhyzome_feuille', os.path.join(t, 'leaf texture.jpeg'), 0.45)
        elif key in MATS_X:                               # models added by later modules (objets-sol.py, objets-autour.py)
            m = MATS_X[key](o, n, brand)
        elif key == 'sculpture':
            m = m_tex('sculpture', os.path.join(TEXO, 'escultura-diffuse-4k.jpg'), 0.85, os.path.join(TEXO, 'escultura-normal-4k.jpg'), nstr=0.8)
        else:
            m = s
        out.append(m)
    return out


# ------------------------------------------------------------------ preparing the models (real size, origin at the base centre)
def _import(spec):
    before = set(bpy.data.objects)
    f = spec['f']
    if f.endswith('.fbx'):
        bpy.ops.import_scene.fbx(filepath=f)
    elif f.endswith('.glb'):
        bpy.ops.import_scene.gltf(filepath=f)
    elif f.endswith('.obj'):
        fw, up = spec.get('axes', ('NEGATIVE_Z', 'Y'))
        bpy.ops.wm.obj_import(filepath=f, forward_axis=fw, up_axis=up)
    else:
        with bpy.data.libraries.load(f, link=False) as (src, dst):
            dst.objects = [n for n in src.objects if n in spec['names']]
        for o in dst.objects:
            SC.collection.objects.link(o)
    bpy.context.view_layer.update()
    return [o for o in bpy.data.objects if o not in before]


def proto(key, brand=None):
    """Collection (in LIB) holding the model at real size, base centred on the origin; and its size (w, d, h)."""
    ck = (key, brand)
    if ck in MO:
        return MO[ck]
    spec = SPECS[key]
    base = MO.get(('parts', key))
    if base is None:
        new = _import(spec)
        if spec.get('prep'):                            # model-specific clean-up before the meshes are taken
            spec['prep'](new)
        if spec.get('evaluate'):                        # rigged or modified models: the evaluated mesh (pose, auto smooth)
            dg = bpy.context.evaluated_depsgraph_get()
            parts = [(o.name, bpy.data.meshes.new_from_object(o.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg),
                      o.matrix_world.copy()) for o in new if o.type == 'MESH']
        else:
            parts = [(o.name, o.data.copy(), o.matrix_world.copy()) for o in new if o.type == 'MESH']
        for o in new:
            bpy.data.objects.remove(o, do_unlink=True)
        R_ = Euler([rad(a) for a in spec.get('rot', (0, 0, 0))]).to_matrix().to_4x4()
        for _, me, mw in parts:
            me.transform(R_ @ mw)
        if spec.get('hexflat'):                         # the pencil rests on a flat face of its hexagon
            vs = [v.co for _, me, _ in parts for v in me.vertices]
            ym = sum(v.y for v in vs) / len(vs)
            mid = [v for v in vs if abs(v.y - ym) < 0.5]
            rmax = max(math.hypot(v.x, v.z) for v in mid)
            phi = [math.degrees(math.atan2(v.z, v.x)) % 60 for v in mid if math.hypot(v.x, v.z) > 0.97 * rmax]
            a = phi[0]
            for _, me, _ in parts:
                me.transform(Matrix.Rotation(rad(a), 4, 'Y'))
            vs = [v.co for _, me, _ in parts for v in me.vertices]
            mid = [v for v in vs if abs(v.y - ym) < 0.5]
            rmax = max(math.hypot(v.x, v.z) for v in mid)
            phi = [math.degrees(math.atan2(v.z, v.x)) % 60 for v in mid if math.hypot(v.x, v.z) > 0.97 * rmax]
            if min(phi[0], 60 - phi[0]) > 3:            # wrong way round: turn back twice
                for _, me, _ in parts:
                    me.transform(Matrix.Rotation(rad(-2 * a), 4, 'Y'))
        vs = [v.co for _, me, _ in parts for v in me.vertices]
        mn = Vector([min(v[i] for v in vs) for i in range(3)])
        mx = Vector([max(v[i] for v in vs) for i in range(3)])
        dims = mx - mn
        if 'height' in spec:
            s = spec['height'] / dims.z
        elif 'length' in spec:
            s = spec['length'] / dims.y
        else:
            s = spec['scale']
        T = Matrix.Diagonal((s, s, s, 1)) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z)))
        for name, me, _ in parts:
            me.transform(T)
            if key == 'gobelet' and name in ('Label', 'Cup'):
                _uv_cylindre(me, 0.0 if name == 'Label' else rad(256))      # the paper seam of the cup goes behind the stamp
            if key.startswith('canette') or key in ('stylo', 'gobelet'):
                me.shade_smooth()
                me.set_sharp_from_angle(angle=rad(38))
        base = (parts, dims * s)
        MO[('parts', key)] = base
    parts, size = base
    c = coll(f'o_{key}' + (f'_{brand}' if brand else ''), C_LIB)
    for name, me, _ in parts:
        o = bpy.data.objects.new(f'o_{key}_{name}', me)
        o['_src'] = name
        c.objects.link(o)
        mats = _mats(key, o, brand)
        for i, m in enumerate(mats):
            if i < len(o.material_slots):
                o.material_slots[i].link = 'OBJECT'
                o.material_slots[i].material = m
    MO[ck] = (c, tuple(size))
    return MO[ck]


def _uv_cylindre(me, a0=0.0):
    """Own UVs for the cup sleeve (the download's are degenerate on the sides) and the cup: u around the cup from
    angle a0, growing with the angle, v from the bottom to the top. The sleeve texture is the flat sleeve print."""
    bm = bmesh.new()
    bm.from_mesh(me)
    uvl = bm.loops.layers.uv.active or bm.loops.layers.uv.new()
    zs = [v.co.z for v in bm.verts]
    z0, z1 = min(zs), max(zs)
    for f in bm.faces:
        us = [((math.atan2(l.vert.co.y, l.vert.co.x) - a0) / (2 * math.pi)) % 1.0 for l in f.loops]
        if max(us) - min(us) > 0.5:
            us = [u + 1 if u < 0.5 else u for u in us]
        for l, u in zip(f.loops, us):
            l[uvl].uv = (u, (l.vert.co.z - z0) / (z1 - z0))
    bm.to_mesh(me)
    bm.free()


# ------------------------------------------------------------------ placing
def poser(F, key, x, y, rz, z=None, brand=None, along=False):
    """An instance of a model on the desk frame. Without z, it stands on the height field (papers, desk, return) under
    its footprint; with along=True (pencil, pen), it lies along its length, tilted to rest on the highest supports."""
    c, (w, d, h) = proto(key, brand)
    rx = 0.0
    if z is None and CH[0]:
        if along:
            cs, sn = math.cos(rz), math.sin(rz)
            pts = []
            for t in (-0.42, 0.0, 0.42):
                px, py = x - sn * t * d, y + cs * t * d
                pts.append((t * d, CH[0].footprint(px, py, rz, w, d * 0.16)))
            slope = (pts[2][1] - pts[0][1]) / (pts[2][0] - pts[0][0])
            z = max(zz - slope * tt for tt, zz in pts)
            rx = math.atan(slope)
        else:
            z = CH[0].footprint(x, y, rz, w, d)
    elif z is None:
        z = H0
    e = bpy.data.objects.new(f'o_{key}', None)
    e.instance_type = 'COLLECTION'
    e.instance_collection = c
    e.location = F.p(x, y, z)
    e.rotation_euler = (rx, 0, F.r + rz)
    link(e)
    if CH[0]:
        CH[0].footprint(x, y, rz, w, d, z + h)
    return e


FRONT = {'canette': -1.374, 'gobelet': rad(76)}        # angle of the front of the print in the model: middle of the can page;
                                                       # the first Pente stamp of the sleeve (u 0.21 of the page, u = angle / 360°)


def face(x, y, cam, key='canette'):
    """Turn (rz) that brings the front of a print towards a camera position."""
    return math.atan2(cam[1] - y, cam[0] - x) - FRONT['gobelet' if key == 'gobelet' else 'canette']


CAM_PRINC = (-2.45, -3.35)                      # the "ensemble" view, close to the hero camera
LAYOUT = {
    # (key, x, y, rz or None = face the main view, brand, along)
    'B': [('gobelet', -0.94, -0.21, None, None, False), ('crayon', 1.52, 0.03, rad(32), None, True),
          ('crayon', -0.43, -0.31, rad(-12), None, True), ('gomme', 1.71, -0.11, rad(-18), None, False),
          ('stylo', -0.61, -0.07, rad(64), None, True)],
}


def objets_bureau(F, h=0.74, hr=0.64, k=None):
    k = k or OBJETS[0]
    if k not in LAYOUT:
        return
    for key, x, y, rz, brand, along in LAYOUT[k]:
        if rz is None:
            rz = face(x, y, CAM_PRINC, key)
        poser(F, key, x, y, rz, brand=brand, along=along)
    poser(F, 'plante', float(OPT.get('plante_x', 0.765)), 0.27, rad(float(OPT.get('plante_rz', 80))), z=h + 0.3015)         # on the riser, between the books and the NAS
    poser(F, 'rhyzome', 2.36, 0.305, rad(-30))                                            # on the corner of the plans table


# ------------------------------------------------------------------ check: nothing crosses
def verifier(c, tol=0.0015):
    """Prints every placed object (collection c) whose vertices enter the box of another mesh of the scene (papers
    excepted: the height field keeps them apart), or of another placed object. Option verif=1."""
    others = [o for o in bpy.data.objects if o.type == 'MESH' and not o.name.startswith(('p_', 'o_', 'cyclo')) and
              not any(cc.name == 'LIB' for cc in o.users_collection) and o.visible_get() is not None]
    insts = [e for e in c.objects if e.instance_type == 'COLLECTION']
    boxes = []
    for o in others:
        mn = Vector([min(v[i] for v in o.bound_box) for i in range(3)])
        mx = Vector([max(v[i] for v in o.bound_box) for i in range(3)])
        boxes.append((o.name, o.matrix_world.inverted(), mn, mx, o.matrix_world.translation))
    for e in insts:
        pts = []
        for o in e.instance_collection.objects:
            M = e.matrix_world @ o.matrix_world
            me = o.data
            step = max(1, len(me.vertices) // 20000)
            pts += [M @ me.vertices[i].co for i in range(0, len(me.vertices), step)]
        cx = sum((p for p in pts), Vector()) / len(pts)
        for name, inv, mn, mx, t in boxes:
            if (t - cx).length > 1.5:
                continue
            n = 0
            for p in pts:
                q = inv @ p
                if all(mn[i] + tol < q[i] < mx[i] - tol for i in range(3)):
                    n += 1
            if n:
                print('CROISE', e.name, name, n, flush=True)
    print('VERIF ok', len(insts), 'objets', flush=True)


# ------------------------------------------------------------------ studio prototypes
SHOT_OB = {
    'ensemble': dict(cam=(-2.45, -3.35, 1.85), target=(0.72, 0.1, 0.62), lens=30, fstop=11, focus=None),
    'dessus': dict(cam=(0.62, -0.42, 3.55), target=(0.62, 0.02, 0.7), lens=24, fstop=11, focus=None),
    'lampe': dict(cam=(-1.0, -1.15, 1.32), target=(-0.6, -0.08, 0.76), lens=35, fstop=5.6, focus=None),
    'mac': dict(cam=(0.12, -0.98, 1.16), target=(0.72, 0.02, 0.9), lens=38, fstop=5.6, focus=None),
    'retour': dict(cam=(1.15, -1.25, 1.42), target=(1.82, 0.1, 0.66), lens=32, fstop=6.3, focus=None),
    'plante': dict(cam=(1.3, -0.5, 1.32), target=(0.74, 0.25, 1.12), lens=45, fstop=4, focus=None),
}


def packshot():
    """The objects on a plain plinth in the studio: the three cans, the cup, the pencil, the eraser, the pen, the plants."""
    setup_render()
    try:
        SC.view_settings.look = 'AgX - Medium High Contrast'
    except TypeError:
        pass
    materials_bureau()
    studio()
    m = mat_color('o_socle', (0.5, 0.5, 0.49), rough=0.6)
    bx('o_socle', (1.6, 0.7, 0.74), (0.0, 0.0, 0.37), m, bev=0.004)
    F = _F0
    for key, x, y, br in (('canette_l', -0.3, 0.05, 'ampere'), ('canette_c', -0.16, 0.07, 'nord'), ('canette_l', -0.02, 0.05, 'minuit'),
                          ('canette_l_ecrasee', 0.11, 0.09, 'minuit'), ('gobelet', 0.27, 0.06, None)):
        poser(F, key, x, y, face(x, y, (0.0, -2.0), key), z=0.74, brand=br)
    poser(F, 'crayon', -0.12, -0.17, rad(80), z=0.74)
    poser(F, 'stylo', 0.06, -0.19, rad(96), z=0.74)
    poser(F, 'gomme', 0.24, -0.16, rad(12), z=0.74)
    poser(F, 'plante', -0.6, 0.12, 0.0, z=0.74)
    poser(F, 'rhyzome', 0.6, 0.14, 0.0, z=0.74)


def sculpture_studio():
    """The sculpture alone on a museum plinth (it goes into the lab decor, not on the desk; a click will show its notice)."""
    setup_render()
    try:
        SC.view_settings.look = 'AgX - Medium High Contrast'
    except TypeError:
        pass
    materials_bureau()
    studio()
    m = mat_color('o_socle_musee', (0.8, 0.8, 0.78), rough=0.55)
    bx('o_socle', (0.42, 0.42, 0.9), (0.0, 0.0, 0.45), m, bev=0.003)
    poser(_F0, 'sculpture', 0.0, 0.0, rad(float(OPT.get('sc_rz', 0))), z=0.9)


SHOT_PK = {
    'packshot': dict(cam=(0.0, -2.0, 1.12), target=(0.0, 0.02, 0.86), lens=45, fstop=8, focus=None),
    'canettes': dict(cam=(-0.12, -0.75, 0.86), target=(-0.12, 0.05, 0.8), lens=60, fstop=5.6, focus=None),
    'gobelet': dict(cam=(0.22, -0.55, 0.9), target=(0.25, 0.04, 0.8), lens=70, fstop=5.6, focus=None),
    'sculpture': dict(cam=(-1.25, -2.3, 1.55), target=(0.0, 0.0, 1.18), lens=55, fstop=8, focus=None),
    'sculpture-face': dict(cam=(0.0, -2.7, 1.32), target=(0.0, 0.0, 1.24), lens=50, fstop=8, focus=None),
    'sculpture-cote': dict(cam=(2.5, -1.0, 1.38), target=(0.0, 0.0, 1.24), lens=50, fstop=8, focus=None),
}


def main_objets():
    os.makedirs(OUT, exist_ok=True)
    if OPT.get('mode') in ('packshot', 'sculpture'):
        (packshot if OPT['mode'] == 'packshot' else sculpture_studio)()
        shots, keys = SHOT_PK, ['P' if OPT['mode'] == 'packshot' else 'S']
        vues = OPT.get('vues', 'packshot,canettes,gobelet').split(',')
        colls = {}
    else:
        build_bureau_complet()
        CUR[0] = coll('PAPIERS')
        papiers_bureau(_F0, H0, H1)
        shots = SHOT_OB
        keys = OPT.get('pistes', 'B').split(',')
        vues = OPT.get('vues', 'ensemble,dessus,lampe,mac,retour,plante').split(',')
        base = CH[0]
        snap = [row[:] for row in base.z]
        colls = {}
        for k in keys:
            base.z = [row[:] for row in snap]            # each prototype starts from the papers alone
            c = coll('O_' + k)
            CUR[0] = c
            objets_bureau(_F0, H0, H1, k)
            colls[k] = c
            if OPT.get('verif') == '1':
                bpy.context.view_layer.update()
                verifier(c)
    if OPT.get('save'):
        # a .blend to open in Blender: the first prototype shown, the others hidden (eye icon in the outliner), one camera
        # per view (the first one active). save=1 -> OUT/objets.blend, save=<path.blend> -> that file; rendu=0 skips the renders.
        path = OPT['save'] if OPT['save'].endswith('.blend') else os.path.join(OUT, 'objets.blend')
        for k2, c in colls.items():
            c.hide_render = k2 != keys[0]
            bpy.context.view_layer.layer_collection.children[c.name].hide_viewport = k2 != keys[0]
        cams = [make_camera(dict(shots[v]), f'CAM_{v}') for v in vues]
        SC.camera = cams[0]
        SC.render.resolution_x = RES
        SC.render.resolution_y = int(RES * 9 / 16)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=path)
        print('SAVED', path, flush=True)
        if OPT.get('rendu', '1') == '0':
            return
        for c in cams:
            bpy.data.objects.remove(c, do_unlink=True)
        for c in colls.values():
            bpy.context.view_layer.layer_collection.children[c.name].hide_viewport = False
    for k in keys:
        for k2, c in colls.items():
            c.hide_render = k2 != k
        for v in vues:
            SC.camera = make_camera(dict(shots[v]), f'CAM_{k}_{v}')
            SC.render.resolution_x = RES
            SC.render.resolution_y = int(RES * 9 / 16)
            SC.render.filepath = os.path.join(OUT, f'{k}-{v}.png')
            print('RENDER', SC.render.filepath, flush=True)
            bpy.ops.render.render(write_still=True)


main_objets()
