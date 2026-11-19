
# ================================================================== the workstation of setup B with the Sketchfab models
# Built after objets-ecrans.py. MacBook Pro (CC-BY, Adreamyouvehadbefore), computer mouse (CC-BY, LagzDesign),
# AirPods 4 (CC-BY, Falah3D), power strip (CC-BY, BlackCube).
# Modelled here: the keyboard (keyboard_mk, layout from hero/outils/clavier_magic.py) and the Mac Studio
# (mac_studio_maison, proportions measured on renders of an earlier model, details from photos of the product).
# Screen contents from hero/outils/ecrans-contenus.
import json, re
SKF = os.path.normpath(os.path.join(HERE, '..', 'assets', 'sketchfab'))
ECR = os.path.normpath(os.path.join(HERE, '..', 'ecrans-contenus'))
TEXB = os.path.normpath(os.path.join(HERE, '..', 'textures-bureau'))


def _new_objects(before):
    return [o for o in bpy.data.objects if o not in before]


def _wrap(new, name, parent, loc, rz=0.0, norm_rot=(0, 0, 0), scale=1.0, lift=None):
    """item empty (desk frame) > norm empty (orientation/scale) > imported top-level objects."""
    item = empty('pst_' + name, loc, (0, 0, rz), parent)
    norm = empty('pst_' + name + '_norm', (0, 0, 0), norm_rot, item)
    norm.scale = (scale, scale, scale)
    for o in new:
        if o.parent is None and o not in (item, norm):
            o.parent = norm
    bpy.context.view_layer.update()
    if lift is not None:
        zs = [(o.matrix_world @ Vector(c)).z for o in new if o.type == 'MESH' for c in o.bound_box]
        if zs:
            item.location.z += lift - min(zs)
    return item


def _link_new(new):
    for o in new:
        if CUR[0] not in o.users_collection:
            for c in list(o.users_collection):
                c.objects.unlink(o)
            CUR[0].objects.link(o)


def import_file(path):
    before = set(bpy.data.objects)
    ext = os.path.splitext(path)[1].lower()
    if ext in ('.glb', '.gltf'):
        bpy.ops.import_scene.gltf(filepath=path)
    elif ext == '.fbx':
        bpy.ops.import_scene.fbx(filepath=path)
    elif ext == '.obj':
        bpy.ops.wm.obj_import(filepath=path)
    elif ext == '.blend':
        with bpy.data.libraries.load(path, link=False) as (src, dst):
            dst.objects = list(src.objects)
        for o in dst.objects:
            if o is not None:
                CUR[0].objects.link(o)
    new = _new_objects(before)
    _link_new(new)
    return new


def drop_missing_textures(objs, recolour=None):
    """Remove image nodes whose file could not be loaded (KTX, missing paths), which render magenta.
    recolour(material, principled) is called for materials that lost a texture."""
    for o in objs:
        for s in (o.data.materials if o.type == 'MESH' else []):
            if not s or not s.use_nodes or s.get('_checked'):
                continue
            s['_checked'] = 1
            lost = False
            for nd in list(s.node_tree.nodes):
                if nd.type == 'TEX_IMAGE' and (nd.image is None or nd.image.size[0] == 0):
                    s.node_tree.nodes.remove(nd)
                    lost = True
            if lost and recolour:
                recolour(s, _bsdf(s))


def _bsdf(m):
    return next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None) if m and m.use_nodes else None


def mat_display(name, path, strength=1.4):
    """Emissive screen behind glossy glass, image on the mesh UVs."""
    m = new_mat(name)
    n, l = m.node_tree.nodes, m.node_tree.links
    p = principled(m)
    t = n.new('ShaderNodeTexImage')
    t.image = img(path)
    p.inputs['Base Color'].default_value = (0, 0, 0, 1)
    l.new(t.outputs['Color'], p.inputs['Emission Color'])
    p.inputs['Emission Strength'].default_value = strength
    p.inputs['Roughness'].default_value = 0.06
    return m


# ------------------------------------------------------------------ models
def macbook_pro(parent, loc, rz=0.0, screen=None):
    new = import_file(os.path.join(SKF, 'macbook-pro-proledxdr-4k', '_archive', 'source', 'MacbookProProledXDR4K.glb'))
    for o in new:
        if o.type != 'MESH':
            continue
        if o.name.startswith('Display'):
            o.name = 'mon_screen_mbp'
            o.data.materials.clear()
            o.data.materials.append(mat_display('mbp_display', screen or os.path.join(ECR, 'ecran-mac-texture.jpg')))
        for s in o.data.materials:
            p = _bsdf(s)
            if s and s.name.startswith('Apple_Logo') and p:
                # 18/11: the model's logo glowed white (emission 6), like the old MacBooks; on this one it is a polished
                # mark, a little darker and shinier than the lid (seen in the video's shot from behind)
                p.inputs['Base Color'].default_value = (0.035, 0.036, 0.04, 1)
                p.inputs['Emission Strength'].default_value = 0.0
                p.inputs['Metallic'].default_value = 1.0
                p.inputs['Roughness'].default_value = 0.12
            if s and s.name.startswith('Trackpad') and p:
                # dark matte trackpad instead of the shiny glass
                p.inputs['Base Color'].default_value = (0.028, 0.029, 0.032, 1)
                p.inputs['Roughness'].default_value = 0.5
                p.inputs['Metallic'].default_value = 0.0
                for k in ('Coat Weight', 'Transmission Weight'):
                    try:
                        p.inputs[k].default_value = 0.0
                    except KeyError:
                        pass
                try:
                    p.inputs['Specular IOR Level'].default_value = 0.3
                except KeyError:
                    pass
    return _wrap(new, 'macbook', parent, loc, rz, lift=DESK_Z)


def _fillet(poly, r, seg=4):
    """Round the right-angle corners of a CCW polygon (x, y). r: radius, or r(convex) -> radius."""
    out, n = [], len(poly)
    for i in range(n):
        P, A, B = Vector((*poly[i], 0)), Vector((*poly[i - 1], 0)), Vector((*poly[(i + 1) % n], 0))
        a, b = (P - A).normalized(), (B - P).normalized()
        rr = r(a.x * b.y - a.y * b.x > 0) if callable(r) else r
        C = P - a * rr + b * rr
        for k in range(seg + 1):
            t = math.pi / 2 * k / seg
            q = C + (-b * math.cos(t) + a * math.sin(t)) * rr
            out.append((q.x, q.y))
    return out


def _offset(poly, d):
    """Offset a CCW right-angle polygon outwards by d."""
    out, n = [], len(poly)
    for i in range(n):
        P, A, B = Vector(poly[i]), Vector(poly[i - 1]), Vector(poly[(i + 1) % n])
        a, b = (P - A).normalized(), (B - P).normalized()
        q = P + d * (Vector((a.y, -a.x)) + Vector((b.y, -b.x)))
        out.append((q.x, q.y))
    return out


def keyboard_mk(parent, loc, rz=0.0):
    """Wedge-shaped dark aluminium keyboard with numeric keypad (418.7 x 114.9 mm, 4.1 mm at the front, 10.9 mm at the back).
    Black low-profile caps standing 0.9 mm proud of the deck, each in its own cut-out; legends from clavier-legendes.png."""
    L = json.load(open(os.path.join(TEXB, 'clavier-touches.json'), encoding='utf-8'))
    Wmm, Dmm = L['W'], L['D']
    Wm, Dm = Wmm / 1000, Dmm / 1000
    hf, hb = 0.0041, 0.0109
    ang = math.atan((hb - hf) / Dm)
    if 'kbm_alu' not in M:
        M['kbm_alu'] = m_surface('kbm_alu', (0.125, 0.128, 0.136), rough=0.32, var=0.012, grain=2400, bump=0.0025, metal=0.75)
        M['kbm_hole'] = mat_color('kbm_hole', (0.004, 0.004, 0.005), rough=0.75)
        m = new_mat('kbm_keys')
        p = principled(m)
        t = m.node_tree.nodes.new('ShaderNodeTexImage')
        t.image = img(os.path.join(TEXB, 'clavier-legendes.png'))
        t.interpolation = 'Cubic'
        m.node_tree.links.new(t.outputs['Color'], p.inputs['Base Color'])
        p.inputs['Roughness'].default_value = 0.4
        M['kbm_keys'] = m
    E = empty('pst_keyboard', loc, (0, 0, rz), parent)
    body = rrect_mesh('kbm_body', Wm, Dm, hb, 0.0095, M['kbm_alu'], seg=10, bev=0.0016)
    for v in body.data.vertices:
        if v.co.z > 0:
            v.co.z = -hb / 2 + hf + (v.co.y + Dm / 2) / Dm * (hb - hf)
    body.location = (0, 0, DESK_Z + hb / 2)
    under(E, body)
    # plane frame: origin on the deck centre, x along the keyboard, y up the slope, z normal to the deck
    F = empty('kbm_deck', (0, 0, DESK_Z + (hf + hb) / 2), (ang, 0, 0), E)
    cs = math.cos(ang)
    to_f = lambda x, y: (x / 1000 - Wm / 2, (y / 1000 - Dm / 2) / cs)
    bk, bh = bmesh.new(), bmesh.new()
    uvl = bk.loops.layers.uv.new('UVMap')
    zb, zt = -0.0006, 0.0009
    for k in L['keys']:
        ring = _fillet(k['poly'], 1.5)
        vb = [bk.verts.new((*to_f(x, y), zb)) for x, y in ring]
        vt = [bk.verts.new((*to_f(x, y), zt)) for x, y in ring]
        mm = ring + ring
        faces = [bk.faces.new(vt), bk.faces.new(list(reversed(vb)))]
        n = len(ring)
        for i in range(n):
            faces.append(bk.faces.new((vb[i], vb[(i + 1) % n], vt[(i + 1) % n], vt[i])))
        idx = {v: i for i, v in enumerate(vb + vt)}
        for f in faces:
            f.smooth = True
            for lp in f.loops:
                x, y = mm[idx[lp.vert]]
                lp[uvl].uv = (x / Wmm, y / Dmm)
        hole = _fillet(_offset(k['poly'], 0.45), lambda convex: 1.95 if convex else 1.05)
        bh.faces.new([bh.verts.new((*to_f(x, y), 0.00003)) for x, y in hole])
    for nm, b, mat in (('kbm_keys', bk, M['kbm_keys']), ('kbm_holes', bh, M['kbm_hole'])):
        me = bpy.data.meshes.new(nm)
        b.to_mesh(me)
        b.free()
        me.materials.append(mat)
        o = link(bpy.data.objects.new(nm, me))
        o.parent = F
        if nm == 'kbm_keys':
            bv = o.modifiers.new('bev', 'BEVEL')
            bv.width = 0.00042
            bv.segments = 3
            bv.limit_method = 'ANGLE'
            bv.angle_limit = rad(30)
            bv.harden_normals = True
    return E


def mouse_skf(parent, loc, rz=0.0):
    new = import_file(os.path.join(SKF, 'computer-mouse-low-poly', '_archive', 'source', 'mouse.blend'))
    o = next(x for x in new if x.type == 'MESH')
    def dark(m, p):
        if p:
            p.inputs['Base Color'].default_value = (0.022, 0.022, 0.025, 1)
            p.inputs['Roughness'].default_value = 0.42
    drop_missing_textures(new, dark)
    bpy.context.view_layer.update()
    dims = o.dimensions
    s = 0.112 / max(dims)
    for m in o.data.materials:
        p = _bsdf(m)
        if p and m.name in ('Material.001',):
            p.inputs['Base Color'].default_value = (0.022, 0.022, 0.025, 1)
            p.inputs['Roughness'].default_value = 0.42
    o.location = (0, 0, 0)
    return _wrap(new, 'mouse', parent, loc, rz, norm_rot=(0, 0, rad(90)), scale=s, lift=DESK_Z + loc[2])     # loc z: on the desk mat


def airpods(parent, loc, rz=0.0):
    new = import_file(os.path.join(SKF, 'airpods-4', '_archive', 'source', 'AirPods 4.fbx'))
    bpy.context.view_layer.update()
    # keep only the biggest sub-tree (the case); the earbuds stand out of it in the original model
    def top(o):
        while o.parent is not None and o.parent in new:
            if o.parent.parent is None:
                return o
            o = o.parent
        return o
    groups = {}
    for o in new:
        if o.type == 'MESH':
            groups.setdefault(top(o), []).append(o)
    def vol(objs):
        pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
        return (max(p.x for p in pts) - min(p.x for p in pts)) * (max(p.y for p in pts) - min(p.y for p in pts)) * (max(p.z for p in pts) - min(p.z for p in pts))
    if len(groups) > 1:
        best = max(groups, key=lambda g: vol(groups[g]))
        for g, objs in groups.items():
            if g is not best:
                for o in objs:
                    new.remove(o)
                    bpy.data.objects.remove(o)
    # close the lid: reset its hinge, then seat it on the rim of the case (the hinge pivot of the model is offset)
    lid = next((o for o in new if o.name.startswith('nJoEOlgGwcdXBHJ')), None)
    case = next((o for o in new if o.name.startswith('iqLXttIronNPiXb')), None)
    if lid and case:
        def kids(o):
            return [o] + [k for c in o.children for k in kids(c)]
        def box(objs):
            pts = [o.matrix_world @ Vector(c) for o in objs if o.type == 'MESH' for c in o.bound_box]
            return Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)])
        lid.rotation_euler.x = 0.0
        bpy.context.view_layer.update()
        (l0, l1), (c0, c1) = box(kids(lid)), box(kids(case))
        mw = lid.matrix_world.copy()
        mw.translation += Vector(((c0.x + c1.x - l0.x - l1.x) / 2, c0.y - l0.y, c1.z - l0.z))
        lid.matrix_world = mw
        bpy.context.view_layer.update()
    white = mat_color('airpods_white', (0.86, 0.86, 0.85), rough=0.22)
    dark = mat_color('airpods_dark', (0.03, 0.03, 0.03), rough=0.5)
    bpy.context.view_layer.update()
    for o in new:
        if o.type == 'MESH':
            small = max(o.dimensions) < 0.0045
            o.data.materials.clear()
            o.data.materials.append(dark if small else white)
    xs = [(o.matrix_world @ Vector(c)) for o in new if o.type == 'MESH' for c in o.bound_box]
    span = max(max(v.x for v in xs) - min(v.x for v in xs), max(v.y for v in xs) - min(v.y for v in xs), max(v.z for v in xs) - min(v.z for v in xs))
    # hinge side (+y) down on the desk: the front with the status light faces up
    return _wrap(new, 'airpods', parent, loc, rz, norm_rot=(rad(-90), 0, 0), scale=0.05 / max(span, 1e-6), lift=DESK_Z)


def _macstudio_mats():
    """Materials of the Mac Studio (same for both models, so the comparison only shows the geometry)."""
    if 'ms_alu' not in M:
        M['ms_alu'] = m_surface('macstudio_alu', (0.62, 0.63, 0.64), rough=0.34, var=0.012, grain=1800, bump=0.003, metal=1.0)
        M['ms_dark'] = mat_color('macstudio_dark', (0.02, 0.02, 0.022), rough=0.6)
        M['ms_metal'] = mat_color('macstudio_metal', (0.4, 0.41, 0.42), rough=0.3, metal=1.0)
        M['ms_hole'] = mat_color('macstudio_hole', (0.0, 0.0, 0.0), rough=1.0, spec=0.0)
        m = new_mat('macstudio_grille')
        n, l = m.node_tree.nodes, m.node_tree.links
        pr = principled(m)
        tc = n.new('ShaderNodeTexCoord')
        vo = n.new('ShaderNodeTexVoronoi')
        vo.inputs['Scale'].default_value = 52.0          # object space is in dm: holes every ~1.9 mm
        vo.inputs['Randomness'].default_value = 0.0
        l.new(tc.outputs['Object'], vo.inputs['Vector'])
        mr = n.new('ShaderNodeMapRange')
        mr.inputs['From Min'].default_value = 0.26
        mr.inputs['From Max'].default_value = 0.3
        l.new(vo.outputs['Distance'], mr.inputs['Value'])
        mx = n.new('ShaderNodeMix')
        mx.data_type = 'RGBA'
        mx.inputs['A'].default_value = (0.005, 0.005, 0.006, 1)
        mx.inputs['B'].default_value = (0.62, 0.63, 0.64, 1)
        l.new(mr.outputs['Result'], mx.inputs['Factor'])
        l.new(mx.outputs['Result'], pr.inputs['Base Color'])
        l.new(mr.outputs['Result'], pr.inputs['Metallic'])
        pr.inputs['Roughness'].default_value = 0.4
        M['ms_grille'] = m
    return M['ms_alu'], M['ms_dark'], M['ms_metal'], M['ms_grille']


# Apple logo outline (public-domain silhouette, Wikimedia Commons "Apple_logo_black.svg", 814 x 1000)
APPLE_LOGO = ('M788.1 340.9c-5.8 4.5-108.2 62.2-108.2 190.5 0 148.4 130.3 200.9 134.2 202.2-.6 3.2-20.7 71.9-68.7 141.9-42.8 61.6-87.5 123.1-155.5 123.1'
              's-85.5-39.5-164-39.5c-76.5 0-103.7 40.8-165.9 40.8s-105.6-57-155.5-127C46.7 790.7 0 663 0 541.8c0-194.4 126.4-297.5 250.8-297.5 66.1 0 121.2 43.4 162.7 43.4'
              ' 39.5 0 101.1-46 176.3-46 28.5 0 130.9 2.6 198.3 99.2zm-234-181.5c31.1-36.9 53.1-88.1 53.1-139.3 0-7.1-.6-14.3-1.9-20.1-50.6 1.9-110.8 33.7-147.1 75.8'
              '-28.5 32.4-55.1 83.6-55.1 135.5 0 7.8 1.3 15.6 1.9 18.1 3.2.6 8.4 1.3 13.6 1.3 45.4 0 102.5-30.4 135.5-71.3z')


def _svg_polys(d, samples=10):
    """Minimal SVG path reader (M L H V C S Z, absolute and relative) -> list of polygons [(x, y), ...]."""
    toks = re.findall(r'[MmLlHhVvCcSsZz]|-?(?:\d+\.?\d*|\.\d+)(?:[eE]-?\d+)?', d)
    polys, cur = [], []
    pos = start = Vector((0.0, 0.0))
    ctrl, cmd, i = None, None, 0
    def nums(k):
        nonlocal i
        v = [float(t) for t in toks[i:i + k]]
        i += k
        return v
    def bez(p0, p1, p2, p3):
        for k in range(1, samples + 1):
            t = k / samples
            u = 1 - t
            cur.append(tuple(p0 * u ** 3 + p1 * 3 * u * u * t + p2 * 3 * u * t * t + p3 * t ** 3))
    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]
            i += 1
            if cmd in 'Zz':
                if cur:
                    polys.append(cur)
                cur, pos, ctrl = [], start, None
                continue
        rel = cmd.islower()
        C = cmd.upper()
        base = pos if rel else Vector((0.0, 0.0))
        if C == 'M':
            x, y = nums(2)
            if cur:
                polys.append(cur)
            pos = start = base + Vector((x, y))
            cur, ctrl = [tuple(pos)], None
            cmd = 'l' if rel else 'L'
        elif C == 'L':
            x, y = nums(2)
            pos, ctrl = base + Vector((x, y)), None
            cur.append(tuple(pos))
        elif C == 'H':
            x, = nums(1)
            pos, ctrl = Vector(((pos.x if rel else 0.0) + x, pos.y)), None
            cur.append(tuple(pos))
        elif C == 'V':
            y, = nums(1)
            pos, ctrl = Vector((pos.x, (pos.y if rel else 0.0) + y)), None
            cur.append(tuple(pos))
        elif C == 'C':
            v = nums(6)
            c1, c2, p = base + Vector(v[0:2]), base + Vector(v[2:4]), base + Vector(v[4:6])
            bez(pos, c1, c2, p)
            pos, ctrl = p, c2
        elif C == 'S':
            v = nums(4)
            c1 = pos * 2 - ctrl if ctrl is not None else pos
            c2, p = base + Vector(v[0:2]), base + Vector(v[2:4])
            bez(pos, c1, c2, p)
            pos, ctrl = p, c2
    if cur:
        polys.append(cur)
    return polys


def _ms_outline(A, E, d, n=2.4, seg=22):
    """Plan outline of the Mac Studio body: square of half-side A with continuous (superellipse) corners of extent E,
    offset inwards by d. CCW."""
    c, e, pts = A - E, E - d, []
    sp = lambda v: math.copysign(abs(v) ** (2 / n), v)
    for q in range(4):
        mid = q * math.pi / 2 + math.pi / 4
        cx, cy = math.copysign(c, math.cos(mid)), math.copysign(c, math.sin(mid))
        for k in range(seg + 1):
            t = q * math.pi / 2 + math.pi / 2 * k / seg
            pts.append((cx + e * sp(math.cos(t)), cy + e * sp(math.sin(t))))
    return pts


def mac_studio_maison(parent, loc, rz=0.0):
    """Mac Studio modelled from Apple's product photos, at the size the previous scene showed it (195.6 x 195.6 x 100.7 mm).
    Built in decimetres and wrapped at scale 0.1, like the comparison model, so the object-space aluminium grain matches.
    Shape parameters (corner extent E, edge radii, base height) were tuned on side-by-side renders."""
    alu, dark, metal, grille = _macstudio_mats()
    A, E, H = 0.09765, 0.0355, 0.1007              # half-side, corner extent (continuous corner, exponent 2.4), height
    z0, rb = 0.0096, 0.0006                        # underside of the body, bottom edge radius (the top edge is sharp)
    sq = 2.4
    prof = [(rb * (1 - math.sin(math.radians(a))), z0 + rb * (1 - math.cos(math.radians(a)))) for a in range(0, 91, 10)]
    prof += [(0.0, H)]
    bm = bmesh.new()
    rings = [[bm.verts.new((x, y, z)) for x, y in _ms_outline(A, E, d, sq)] for d, z in prof]
    nv = len(rings[0])
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(nv):
            bm.faces.new((r0[k], r0[(k + 1) % nv], r1[(k + 1) % nv], r1[k]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    top_ring = set(rings[-1])
    for e in bm.edges:
        if e.verts[0] in top_ring and e.verts[1] in top_ring:
            e.smooth = False                        # crisp top edge
    # circular base: a 1 mm ring (r 72.9 mm) flaring into a cone up to r 85 mm under the body
    nb = 96
    ring = lambda r, z: [bm.verts.new((r * math.cos(2 * math.pi * k / nb), r * math.sin(2 * math.pi * k / nb), z)) for k in range(nb)]
    b0, b1, b2 = ring(0.073, 0.0), ring(0.073, 0.001), ring(0.0854, z0 + 0.0003)
    bm.faces.new(list(reversed(b0)))
    for lo, hi in ((b0, b1), (b1, b2)):
        for k in range(nb):
            f = bm.faces.new((lo[k], lo[(k + 1) % nb], hi[(k + 1) % nb], hi[k]))
            f.material_index = 2
    for f in bm.faces:
        f.smooth = True
    me = bpy.data.meshes.new('ms_body')
    bm.to_mesh(me)
    bm.free()
    for m in (alu, dark, metal):
        me.materials.append(m)
    body = link(bpy.data.objects.new('ms_body', me))
    hole = M['ms_hole']

    # flat details: front ports, card slot, light, rear grille and ports, top logo (each a face 0.03 mm proud)
    det = bmesh.new()
    eps = 0.00003
    def shape(pts2, plane, mi):
        if plane in ('front', 'front2'):           # front2: on top of a front detail (the USB-C tongue)
            vs = [det.verts.new((u, -A - eps * (2 if plane == 'front2' else 1), v)) for u, v in pts2]
            want = Vector((0, -1, 0))
        elif plane == 'back':
            vs = [det.verts.new((u, A + eps, v)) for u, v in pts2]
            want = Vector((0, 1, 0))
        else:
            vs = [det.verts.new((u, v, H + eps)) for u, v in pts2]
            want = Vector((0, 0, 1))
        f = det.faces.new(vs)
        f.normal_update()
        if f.normal.dot(want) < 0:
            f.normal_flip()
        f.material_index = mi
    def stadium(cx, cz, w, h, seg=8):
        r = min(w, h) / 2
        pts = []
        if h >= w:
            for k in range(seg + 1):
                a = math.pi * k / seg
                pts.append((cx + r * math.cos(a), cz + h / 2 - r + r * math.sin(a)))
            for k in range(seg + 1):
                a = math.pi + math.pi * k / seg
                pts.append((cx + r * math.cos(a), cz - h / 2 + r + r * math.sin(a)))
        else:
            for k in range(seg + 1):
                a = -math.pi / 2 + math.pi * k / seg
                pts.append((cx + w / 2 - r + r * math.cos(a), cz + r * math.sin(a)))
            for k in range(seg + 1):
                a = math.pi / 2 + math.pi * k / seg
                pts.append((cx - w / 2 + r + r * math.cos(a), cz + r * math.sin(a)))
        return pts
    def disc(cx, cz, r, seg=20):
        return [(cx + r * math.cos(2 * math.pi * k / seg), cz + r * math.sin(2 * math.pi * k / seg)) for k in range(seg)]
    def rbox(cx, cz, w, h, r=0.0008):
        return _fillet([[cx - w / 2, cz - h / 2], [cx + w / 2, cz - h / 2], [cx + w / 2, cz + h / 2], [cx - w / 2, cz + h / 2]], r, 3)
    zp = 0.0271
    # front: two USB-C (vertical) and the SDXC slot, as dark openings; the status light stays off and unseen
    for x in (-0.0657, -0.0509):
        shape(stadium(x, zp, 0.0023, 0.0086), 'front', 4)
        shape([(x - 0.00026, zp - 0.0031), (x + 0.00026, zp - 0.0031), (x + 0.00026, zp + 0.0031), (x - 0.00026, zp + 0.0031)], 'front2', 2)
    shape(stadium(-0.0241, zp, 0.0268, 0.0025), 'front', 4)
    # back (never seen in the scene, simplified): perforated grille, 4 Thunderbolt, Ethernet, power, 2 USB-A, HDMI, jack, power button
    shape(rbox(0.0, 0.061, 0.142, 0.052, 0.002), 'back', 3)
    for x in (-0.0652, -0.0559, -0.0466, -0.0371):
        shape(stadium(x, zp, 0.0025, 0.0074), 'back', 1)
    shape(rbox(-0.0258, zp, 0.010, 0.0085), 'back', 1)
    shape(disc(0.0005, zp, 0.0068, 32), 'back', 1)
    for x in (0.0215, 0.0338):
        shape(rbox(x, zp, 0.0055, 0.0125), 'back', 1)
    shape(rbox(0.0514, zp, 0.0145, 0.0046), 'back', 1)
    shape(disc(0.0640, zp, 0.0018, 16), 'back', 1)
    shape(disc(0.0702, zp, 0.0042, 24), 'back', 2)
    # top: logo, 49.2 mm wide, 5 mm behind the centre, leaf towards the back
    sc = 0.0492 / 814
    for poly in _svg_polys(APPLE_LOGO):
        pts = [((x - 407) * sc + 0.0008, (500 - y) * sc + 0.0051) for x, y in poly]
        if len(pts) > 3 and (pts[0][0] - pts[-1][0]) ** 2 + (pts[0][1] - pts[-1][1]) ** 2 < 1e-12:
            pts = pts[:-1]
        shape(pts, 'top', int(OPT.get('ms_logo', 1)))
    me2 = bpy.data.meshes.new('ms_details')
    det.to_mesh(me2)
    det.free()
    for m in (alu, dark, metal, grille, hole):
        me2.materials.append(m)
    details = link(bpy.data.objects.new('ms_details', me2))
    for o in (body, details):
        o.data.transform(Matrix.Scale(10.0, 4))
    return _wrap([body, details], 'macstudio', parent, loc, rz, scale=0.1, lift=DESK_Z)


def power_strip(parent, loc, rz=0.0):
    new = import_file(os.path.join(SKF, 'power-plug-outlet-adapter-connector-strip', '_archive', 'inner', 'untitled4.fbx'))
    keep = [o for o in new if o.type != 'MESH' or o.name.startswith(('connector strip', 'switch', 'power plug 3', 'power plug 2', 'power plug 1'))]
    for o in [o for o in new if o not in keep]:
        bpy.data.objects.remove(o)
    new = keep
    black = mat_color('strip_black', (0.018, 0.018, 0.02), rough=0.55)
    for o in new:
        if o.type == 'MESH':
            for i, s in enumerate(o.data.materials):
                if s and s.name in ('white', 'gray'):
                    o.data.materials[i] = black
    return _wrap(new, 'strip', parent, loc, rz, lift=0.0)


# ------------------------------------------------------------------ setup B, final version
TAPIS_EP = 0.003      # thickness of the desk mat (objets-ecrans.py, desk_mat): the keyboard and the mouse rest on it


def setup_B2(root):
    """Two 27" on a dual arm (code / Figma), MacBook Pro showing GitHub, keyboard with keypad, mouse, AirPods, Mac Studio."""
    _, a = ecran(root, 'left', 0.597, 0.336, os.path.join(ECR, 'ecran-gauche-code.png'), (-0.2, 0.06, 1.12), rz=rad(9), stand='none', strength=1.5)
    _, b = ecran(root, 'right', 0.597, 0.336, os.path.join(ECR, 'ecran-droite-figma.png'), (0.42, 0.06, 1.12), rz=rad(-9), stand='none', strength=1.5)
    monitor_arm(root, (0.11, 0.33), [a, b])
    desk_mat(root, (0.1, -0.2))
    macbook_pro(root, (0.86, -0.06, 0), rz=rad(-22))
    keyboard_mk(root, (0.02, -0.215, TAPIS_EP), rz=rad(-1.5))     # both stand on the desk mat, not in it
    mouse_skf(root, (0.33, -0.205, TAPIS_EP), rz=rad(-1.5))
    airpods(root, (0.585, -0.035, 0), rz=rad(-26))
    mac_studio_maison(root, (0.56, 0.27, 0), rz=0.0)
    power_strip(root, (0.25, 0.32, 0), rz=rad(4))
    for k, (x, y, z) in enumerate([(0.11, 0.35, 1.0), (0.12, 0.35, 0.95)]):
        under(root, curve_cable(f'pst_cable{k}', [(0.6, 0.38, DESK_Z + 0.05), (0.45, 0.42, DESK_Z + 0.02), (0.2, 0.4, DESK_Z + 0.01), (x + 0.02 * k, 0.36, z - 0.2), (x, y, z)], 0.003, M['cable_e']))
    under(root, curve_cable('pst_power', [(0.62, 0.38, DESK_Z + 0.02), (0.66, 0.43, DESK_Z - 0.04), (0.6, 0.45, 0.3), (0.35, 0.36, 0.02), (0.28, 0.33, 0.02)], 0.0035, M['cable_e']))
    under(root, curve_cable('pst_mbp', [(0.97, 0.03, DESK_Z + 0.006), (1.02, 0.2, DESK_Z + 0.004), (0.98, 0.38, DESK_Z + 0.003), (0.92, 0.43, DESK_Z - 0.05), (0.7, 0.44, 0.2), (0.3, 0.34, 0.02)], 0.0025, M['cable_e']))


SETUP_FN['B2'] = setup_B2
SETUP_NAMES['B2'] = 'Deux 27 pouces sur bras, MacBook Pro, clavier pavé numérique, Mac Studio'
SHOT_E['mac'] = dict(cam=(0.5, -0.78, 1.0), target=(0.86, -0.02, 0.86), lens=42, fstop=4, focus=None)
SHOT_E['objets'] = dict(cam=(0.3, -0.86, 0.98), target=(0.56, -0.06, 0.76), lens=50, fstop=3.2, focus=None)
SHOT_E['ms_tq'] = dict(cam=(0.31, -0.1, 0.96), target=(0.56, 0.27, 0.79), lens=62, fstop=8, focus=None)
SHOT_E['ms_face'] = dict(cam=(0.56, -0.3, 0.805), target=(0.56, 0.27, 0.79), lens=72, fstop=8, focus=None)
SHOT_E['ms_haut'] = dict(cam=(0.95, 0.04, 1.1), target=(0.56, 0.27, 0.8), lens=55, fstop=8, focus=None)
SHOT_E['ms_det'] = dict(cam=(0.55, -0.12, 0.79), target=(0.55, 0.1715, 0.758), lens=80, fstop=8, focus=None)
SHOT_E['clavier'] = dict(cam=(-0.36, -0.56, 0.86), target=(0.0, -0.205, 0.748), lens=55, fstop=5.6, focus=None)
