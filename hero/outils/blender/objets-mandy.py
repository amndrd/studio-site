
# ================================================================== desk chair from the Mandy D01 model (Sketchfab, CC-BY, rongphuongbacfurniture / thecity.vn)
# Built by rendus-mandy.sh: labo2-base.py + objets-bureau.py + objets-rangements.py + objets-chaise.py (minus their last lines) + this file.
# The model keeps its technical backrest; we redo every material (finishes) and derive variants
# (without headrest, without arms, polished aluminium base). The FBX faces +x; import_mandy turns it so the seat front faces -y.
MANDY_FBX = os.path.normpath(os.path.join(HERE, '..', 'assets', 'sketchfab', 'mandy-d01', 'source', 'thecity-mandyd01-ppbase-headrest-officechair.FBX'))
ROLE = {'Box1578967125': 'seat', 'Plane4314': 'plastic', 'Box1578967126': 'plastic', 'Object241232888': 'pad', 'Line4576': 'plastic',
        'Shape190': 'mech', 'Plane4316': 'mesh', 'Plane4315': 'plastic', 'Box1578967180': 'plastic', 'Object241233033': 'plastic',
        'Plane4351': 'headpad', 'Plane4352': 'lumbar', 'Layer:KHUNG TEN 003': 'base', 'Object2113136325': 'chrome'}
HEAD = ('Object241233033', 'Plane4351', 'Box1578967180')
ARMS = ('Box1578967126', 'Object241232888', 'Line4576')
FIN_M = {
    'noir': dict(fabric=(0.014, 0.014, 0.015), mesh=(0.012, 0.012, 0.013), label='Noir'),
    'graphite': dict(fabric=(0.05, 0.051, 0.054), mesh=(0.042, 0.043, 0.046), label='Graphite'),
    'gris': dict(fabric=(0.3, 0.3, 0.29), mesh=(0.22, 0.222, 0.225), label='Gris chiné'),
    'bleu': dict(fabric=(0.018, 0.026, 0.055), mesh=(0.014, 0.02, 0.045), label='Bleu nuit'),
}
VAR_M = {
    'complete': dict(head=True, arms=True, alu=False, label='Complète'),
    'sans-appui-tete': dict(head=False, arms=True, alu=False, label='Sans appui-tête'),
    'sans-accoudoirs': dict(head=True, arms=False, alu=False, label='Sans accoudoirs'),
    'alu': dict(head=True, arms=True, alu=True, label='Piètement alu poli'),
    'epure': dict(head=False, arms=False, alu=True, label='Épurée : ni appui-tête ni accoudoirs, piètement alu'),
}


def _mm(n, l, tc_out):
    """Object coordinates of the FBX are in millimetres: bring them to metres."""
    mp = n.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (0.001, 0.001, 0.001)
    l.new(tc_out, mp.inputs['Vector'])
    return mp.outputs['Vector']


def m_plastic(name, color, rough=0.48):
    m = mat_color(name, color, rough=rough, metal=0.0)
    n, l = _nodes(m)
    p = principled(m)
    tc = n.new('ShaderNodeTexCoord')
    v = _mm(n, l, tc.outputs['Object'])
    nz = n.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 1400
    nz.inputs['Detail'].default_value = 2
    l.new(v, nz.inputs['Vector'])
    bp = n.new('ShaderNodeBump')
    bp.inputs['Strength'].default_value = 0.08
    bp.inputs['Distance'].default_value = 0.0002
    l.new(nz.outputs['Fac'], bp.inputs['Height'])
    l.new(bp.outputs['Normal'], p.inputs['Normal'])
    sm = n.new('ShaderNodeTexNoise')
    sm.inputs['Scale'].default_value = 5
    mr = n.new('ShaderNodeMapRange')
    mr.inputs['To Min'].default_value = rough - 0.08
    mr.inputs['To Max'].default_value = rough + 0.1
    l.new(v, sm.inputs['Vector'])
    l.new(sm.outputs['Fac'], mr.inputs['Value'])
    l.new(mr.outputs['Result'], p.inputs['Roughness'])
    return m


def m_fabric(name, color, heather=0.22):
    """Knitted upholstery: heathered colour, fine knit relief, sheen."""
    m = mat_color(name, color, rough=0.92)
    n, l = _nodes(m)
    p = principled(m)
    for k, v in (('Sheen Weight', 0.12), ('Sheen Roughness', 0.6), ('Specular IOR Level', 0.15)):
        try:
            p.inputs[k].default_value = v
        except KeyError:
            pass
    tc = n.new('ShaderNodeTexCoord')
    v = _mm(n, l, tc.outputs['Object'])
    nz = n.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 1100
    nz.inputs['Detail'].default_value = 3
    l.new(v, nz.inputs['Vector'])
    mix = n.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    mix.inputs['A'].default_value = (*[c * (1 - heather) for c in color], 1)
    mix.inputs['B'].default_value = (*[min(1, c * (1 + heather * 1.6)) for c in color], 1)
    l.new(nz.outputs['Fac'], mix.inputs['Factor'])
    l.new(mix.outputs['Result'], p.inputs['Base Color'])
    vo = n.new('ShaderNodeTexVoronoi')
    vo.inputs['Scale'].default_value = 520
    l.new(v, vo.inputs['Vector'])
    seam = n.new('ShaderNodeMix')
    seam.data_type = 'RGBA'
    seam.blend_type = 'MULTIPLY'
    cr = n.new('ShaderNodeValToRGB')
    cr.color_ramp.elements[0].position = 0.0
    cr.color_ramp.elements[0].color = (0.55, 0.55, 0.55, 1)
    cr.color_ramp.elements[1].position = 0.35
    cr.color_ramp.elements[1].color = (1, 1, 1, 1)
    l.new(vo.outputs['Distance'], cr.inputs['Fac'])
    seam.inputs['Factor'].default_value = 1.0
    l.new(mix.outputs['Result'], seam.inputs['A'])
    l.new(cr.outputs['Color'], seam.inputs['B'])
    l.new(seam.outputs['Result'], p.inputs['Base Color'])
    bp = n.new('ShaderNodeBump')
    bp.inputs['Strength'].default_value = 0.7
    bp.inputs['Distance'].default_value = 0.002
    l.new(vo.outputs['Distance'], bp.inputs['Height'])
    l.new(bp.outputs['Normal'], p.inputs['Normal'])
    return m


def m_techmesh(name, color, scale=360.0, mortar=0.13):
    """Technical woven mesh of the backrest: staggered openings (brick pattern on the model's UVs), transparent between strands."""
    m = mat_color(name, color, rough=0.5)
    n, l = _nodes(m)
    p = principled(m)
    try:
        p.inputs['Sheen Weight'].default_value = 0.4
    except KeyError:
        pass
    out = next(x for x in n if x.type == 'OUTPUT_MATERIAL')
    tc = n.new('ShaderNodeTexCoord')
    # projected in the chair's own space (width y, height z of the FBX, in metres): the backrest UVs are distorted
    v = _mm(n, l, tc.outputs['Object'])
    sp = n.new('ShaderNodeSeparateXYZ')
    l.new(v, sp.inputs['Vector'])
    cb = n.new('ShaderNodeCombineXYZ')
    l.new(sp.outputs['Y'], cb.inputs['X'])
    l.new(sp.outputs['Z'], cb.inputs['Y'])
    br = n.new('ShaderNodeTexBrick')
    br.offset = 0.5
    br.inputs['Scale'].default_value = scale
    br.inputs['Mortar Size'].default_value = mortar
    br.inputs['Mortar Smooth'].default_value = 0.85
    br.inputs['Brick Width'].default_value = 0.5
    br.inputs['Row Height'].default_value = 0.25
    l.new(cb.outputs['Vector'], br.inputs['Vector'])
    tr = n.new('ShaderNodeBsdfTransparent')
    mix = n.new('ShaderNodeMixShader')
    l.new(br.outputs['Fac'], mix.inputs['Fac'])
    l.new(tr.outputs[0], mix.inputs[1])
    l.new(p.outputs[0], mix.inputs[2])
    l.new(mix.outputs[0], out.inputs['Surface'])
    return m


def mandy_mats(fin, alu):
    key = f'mandy_{fin}_{alu}'
    if key in M:
        return M[key]
    f = FIN_M[fin]
    plastic = M.get('mandy_plastic') or m_plastic('mandy_plastic', (0.018, 0.018, 0.02))
    M['mandy_plastic'] = plastic
    d = dict(plastic=plastic, mech=plastic, lumbar=plastic,
             pad=M.get('mandy_pad') or m_plastic('mandy_pad', (0.014, 0.014, 0.015), rough=0.62),
             seat=m_fabric(f'mandy_fabric_{fin}', f['fabric']), headpad=None,
             mesh=m_techmesh(f'mandy_mesh_{fin}', f['mesh']),
             chrome=M.get('mandy_chrome') or mat_color('mandy_chrome', (0.9, 0.9, 0.9), rough=0.08, metal=1.0),
             metal=M.get('mandy_metal') or mat_color('mandy_metal', (0.35, 0.36, 0.37), rough=0.3, metal=1.0))
    M['mandy_pad'], M['mandy_chrome'], M['mandy_metal'] = d['pad'], d['chrome'], d['metal']
    d['headpad'] = d['seat']
    d['base'] = mat_color('mandy_alu', (0.86, 0.865, 0.87), rough=0.13, metal=1.0) if alu else plastic
    M[key] = d
    return d


def import_mandy(fin, var, loc=(0.0, 0.0), rz=0.0, coll=None):
    V = VAR_M[var]
    mats = mandy_mats(fin, V['alu'])
    if coll is not None:
        lc = next(c for c in bpy.context.view_layer.layer_collection.children if c.collection == coll)
        bpy.context.view_layer.active_layer_collection = lc
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=MANDY_FBX)
    new = [o for o in bpy.data.objects if o not in before]
    for o in list(new):
        if (not V['head'] and o.name.split('.')[0] in HEAD) or (not V['arms'] and o.name.split('.')[0] in ARMS):
            new.remove(o)
            bpy.data.objects.remove(o)
            continue
        if o.type != 'MESH':
            continue
        role = ROLE.get(o.name.split('.')[0], 'plastic')
        if role == 'mesh':
            # the backrest mesh comes as a soup of loose triangles with mixed winding: weld and re-orient it
            bm = bmesh.new()
            bm.from_mesh(o.data)
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.05)
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            bm.to_mesh(o.data)
            bm.free()
            if hasattr(o.data, 'has_custom_normals') and o.data.has_custom_normals:
                try:
                    o.data.free_normals_split()
                except Exception:
                    pass
                try:
                    bpy.context.view_layer.objects.active = o
                    bpy.ops.mesh.customdata_custom_splitnormals_clear()
                except Exception:
                    pass
        for i, slot in enumerate(o.data.materials):
            r = role
            if role == 'mech':
                nm = slot.name if slot else ''
                r = 'metal' if ('INOX' in nm or 'Default22' in nm) else 'plastic'
            o.data.materials[i] = mats[r]
        for p in o.data.polygons:
            p.use_smooth = True
    root = bpy.data.objects.new('mandy_root', None)
    (coll or bpy.context.view_layer.active_layer_collection.collection).objects.link(root)
    for o in new:
        if o.parent is None:
            o.parent = root
    root.location = (loc[0], loc[1], 0)
    root.rotation_euler = (0, 0, rz - math.pi / 2)
    return root


SHOT_M = {
    'tq': dict(cam=(-1.55, -2.35, 1.35), target=(0.0, 0.02, 0.6), lens=45, fstop=8, focus=None),
    'dos': dict(cam=(1.35, 2.35, 1.45), target=(0.0, 0.08, 0.64), lens=45, fstop=8, focus=None),
    'detail': dict(cam=(-0.46, -0.52, 0.98), target=(0.0, 0.12, 0.62), lens=60, fstop=3.2, focus=None),
}
JOBS_M = [(f, 'complete', ('tq', 'dos', 'detail')) for f in ('noir', 'graphite', 'gris', 'bleu')] + \
         [('graphite', v, ('tq', 'dos')) for v in ('sans-appui-tete', 'sans-accoudoirs', 'alu', 'epure')]


def main_mandy():
    setup_render()
    try:
        SC.view_settings.look = 'AgX - Medium High Contrast'
    except TypeError:
        pass
    materials_bureau()
    studio()
    jobs = JOBS_M
    if OPT.get('jobs'):
        want = OPT['jobs'].split(',')
        jobs = [j for j in jobs if f'{j[0]}:{j[1]}' in want]
    colls = {}
    for f, v, _ in jobs:
        c = coll(f'M_{f}_{v}')
        import_mandy(f, v, coll=c)
        colls[(f, v)] = c
    os.makedirs(OUT, exist_ok=True)
    if OPT.get('save') == '1':
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'mandy-prototypes.blend'))
    for f, v, views in jobs:
        for k, c in colls.items():
            c.hide_render = k != (f, v)
        for s in views:
            if OPT.get('vues') and s not in OPT['vues'].split(','):
                continue
            SC.camera = make_camera(dict(SHOT_M[s]), f'CAM_{f}_{v}_{s}')
            SC.render.resolution_x = RES
            SC.render.resolution_y = int(RES * 9 / 16)
            SC.render.filepath = os.path.join(OUT, f'{f}-{v}-{s}.png')
            print('RENDER', SC.render.filepath, flush=True)
            bpy.ops.render.render(write_still=True)


main_mandy()
