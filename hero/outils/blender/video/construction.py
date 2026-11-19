
# ================================================================== video: the construction of the desk, step by step
# Built by rendus-video.sh after the complete desk (bureau-complet.py minus its last line) and video/trace.py.
# Every object of the desk gets an animated stage "vid_s" (object custom property, read by its materials):
#   0 hidden · 0→1 its wireframe appears (sweep) · 1→2 it is modelled (wireframe) · 2→3 clay · 3→4 flat colour
#   · 4→5 final texture.
# Every material is wrapped by the node group VID_etapes (transparent → clay → flat colour → final material); the
# wireframe is a twin object (Wireframe modifier) with the emissive line material VID_fil.
# Our own models are "modelled": a face that extrudes, a block that takes its shape, edges that round off, cables that
# grow, sheets that fall and settle. Third-party models (Sketchfab: chair, lamp, MacBook, mouse, AirPods, plants, cup,
# pencils, bin, fan) arrive already modelled; the chair rolls in, the lamp lifts its arm into place and lights up.
import math, random
import numpy as _np
from mathutils import Vector, Matrix, Euler

VID_FPS = int(OPT.get('fps', 24))
VID = dict(bande=0.12, lueur=3.0, grain=0.0, fil=0.0012, fil_col=(0.86, 0.87, 0.9), fil_force=1.4)
VID_STYLES = {
    'balayage': dict(bande=0.3, lueur=2.5, grain=0.0),       # a soft band that climbs the object, a light line
    'coupe': dict(bande=0.02, lueur=0.0, grain=0.0),         # a crisp cut that climbs, no light
    'grain': dict(bande=0.3, lueur=0.0, grain=1.0),          # the object materialises grain by grain
}
VID.update(VID_STYLES.get(OPT.get('style', 'coupe'), {}))           # retained 17/11: the crisp cut


def vid_f(t):
    """Seconds -> frame."""
    return 1 + int(round(t * VID_FPS))


# ------------------------------------------------------------------ the steps, in the physical order of the build
VID_STEPS = [
    ('bureau', lambda t: '/concept_D' in t or '/led_sous_bureau' in t),
    ('rangements', lambda t: '/build_with_desk/place' in t and '/remplir' not in t),
    ('contenus', lambda t: '/remplir' in t),
    ('ecrans', lambda t: '/build_setup/monitor_arm' in t or '/build_setup/ecran' in t),
    ('poste', lambda t: '/build_setup/' in t),
    ('lampe', lambda t: '/lampe_au_bureau' in t),
    ('chaise', lambda t: '/import_mandy' in t),
    ('papiers', lambda t: t.startswith('papiers_bureau')),
    ('objets', lambda t: t.startswith('objets_bureau')),
    ('cables', lambda t: t.startswith('cables_bureau')),
    ('autour', lambda t: t.startswith(('autour_bureau', 'sol_bureau'))),
]
VID_IMPORT = ('import_file', 'import_mandy', 'proto')
VID_EXTRUDE = ('box', 'cyl', 'plane', 'quad', 'tube_between', 'board', 'carcass', 'label', 'disque', 'ring')


def vid_step(o):
    t = o.get('trace', '')
    for k, f in VID_STEPS:
        if f(t):
            return k
    return None


def vid_imported(o):
    return any(k in o.get('trace', '') for k in VID_IMPORT) or o.name.startswith('dk_lampeS')


def vid_piece(o):
    """The unit that is built in one go: an item (c_item, pst_..., the chair, the parts of one placed object),
    otherwise the object itself."""
    if o.get('vid_piece'):                       # a collection instance made real (vid_make_real)
        return o['vid_piece']
    if o.name.startswith('o_') and o.parent is None:
        return o.name.split('_')[1]
    p, best = o.parent, None
    while p:
        if p.name.startswith(('c_item', 'pst_', 'mandy_root', 'grp')):
            best = p
        p = p.parent
    return best


# ------------------------------------------------------------------ node helpers
def _n(nt, kind, x=0, y=0, **kw):
    n = nt.nodes.new(kind)
    n.location = (x, y)
    for k, v in kw.items():
        setattr(n, k, v)
    return n


def _math(nt, op, a, b=None, clamp=False, x=0, y=0):
    m = _n(nt, 'ShaderNodeMath', x, y, operation=op, use_clamp=clamp)
    for i, v in enumerate((a, b)):
        if v is None:
            continue
        if isinstance(v, (int, float)):
            m.inputs[i].default_value = v
        else:
            nt.links.new(v, m.inputs[i])
    return m.outputs[0]


def _vid_core(nt, x0=-1400):
    """Nodes shared by both shaders: the stage s, the sweep coordinate hh, and F(k) = how far transition k has
    climbed at this point (0 before, 1 after, a band of width 'bande' in between)."""
    L = nt.links
    a_s = _n(nt, 'ShaderNodeAttribute', x0, 300, attribute_type='OBJECT', attribute_name='vid_s')
    a_o = _n(nt, 'ShaderNodeAttribute', x0, 100, attribute_type='OBJECT', attribute_name='vid_o')
    a_d = _n(nt, 'ShaderNodeAttribute', x0, -100, attribute_type='OBJECT', attribute_name='vid_d')
    geo = _n(nt, 'ShaderNodeNewGeometry', x0, -300)
    sub = _n(nt, 'ShaderNodeVectorMath', x0 + 200, 0, operation='SUBTRACT')
    L.new(geo.outputs['Position'], sub.inputs[0])
    L.new(a_o.outputs['Vector'], sub.inputs[1])
    dot = _n(nt, 'ShaderNodeVectorMath', x0 + 400, 0, operation='DOT_PRODUCT')
    L.new(sub.outputs[0], dot.inputs[0])
    L.new(a_d.outputs['Vector'], dot.inputs[1])
    noi = _n(nt, 'ShaderNodeTexNoise', x0 + 200, -300)
    noi.inputs['Scale'].default_value = 90.0
    noi.inputs['Detail'].default_value = 1.0
    L.new(geo.outputs['Position'], noi.inputs['Vector'])
    vals = {}
    for i, k in enumerate(('bande', 'lueur', 'grain')):
        v = _n(nt, 'ShaderNodeValue', x0, -500 - 90 * i, label='vid_' + k, name='vid_' + k)
        v.outputs[0].default_value = VID[k]
        vals[k] = v.outputs[0]
    # hh = h + grain * (noise - h)
    dn = _math(nt, 'SUBTRACT', noi.outputs['Fac'], dot.outputs['Value'], x=x0 + 600, y=-200)
    hh = _math(nt, 'MULTIPLY_ADD', dn, vals['grain'], x=x0 + 800, y=-200)
    nt.links.new(dot.outputs['Value'], hh.node.inputs[2])
    one_w = _math(nt, 'ADD', vals['bande'], 1.0, x=x0 + 600, y=-500)

    def F(k, y=0):
        mr = _n(nt, 'ShaderNodeMapRange', x0 + 1000, y, clamp=True)
        L.new(a_s.outputs['Fac'], mr.inputs['Value'])
        mr.inputs['From Min'].default_value, mr.inputs['From Max'].default_value = float(k), float(k + 1)
        x = _math(nt, 'MULTIPLY', mr.outputs['Result'], one_w, x=x0 + 1200, y=y)
        d = _math(nt, 'SUBTRACT', x, hh, x=x0 + 1400, y=y)
        return _math(nt, 'DIVIDE', d, vals['bande'], clamp=True, x=x0 + 1600, y=y)

    def bump(f, y=0):
        # (4 f (1 - f))^8: a thin line in the middle of the band, 0 elsewhere
        inv = _math(nt, 'SUBTRACT', 1.0, f, x=x0 + 1800, y=y)
        m = _math(nt, 'MULTIPLY', f, inv, x=x0 + 2000, y=y)
        m = _math(nt, 'MULTIPLY', m, 4.0, x=x0 + 2200, y=y)
        return _math(nt, 'POWER', m, 8.0, x=x0 + 2400, y=y)

    return F, bump, vals


def vid_group():
    g = bpy.data.node_groups.get('VID_etapes')
    if g:
        return g
    g = bpy.data.node_groups.new('VID_etapes', 'ShaderNodeTree')
    for name, kind, io in (('Final', 'NodeSocketShader', 'INPUT'), ('Couleur', 'NodeSocketColor', 'INPUT'),
                           ('Rugosite', 'NodeSocketFloat', 'INPUT'), ('Metal', 'NodeSocketFloat', 'INPUT'),
                           ('Shader', 'NodeSocketShader', 'OUTPUT')):
        g.interface.new_socket(name=name, in_out=io, socket_type=kind)
    nt, L = g, g.links
    gi = _n(nt, 'NodeGroupInput', -1700, 700)
    go = _n(nt, 'NodeGroupOutput', 1900, 0)
    F, bump, vals = _vid_core(nt)
    f_clay, f_col, f_tex = F(2, 600), F(3, 400), F(4, 200)
    tr = _n(nt, 'ShaderNodeBsdfTransparent', 900, 500)
    clay = _n(nt, 'ShaderNodeBsdfPrincipled', 900, 300)
    clay.inputs['Base Color'].default_value = (0.5, 0.5, 0.5, 1)
    clay.inputs['Roughness'].default_value = 0.62
    col = _n(nt, 'ShaderNodeBsdfPrincipled', 900, -200)
    L.new(gi.outputs['Couleur'], col.inputs['Base Color'])
    L.new(gi.outputs['Rugosite'], col.inputs['Roughness'])
    L.new(gi.outputs['Metal'], col.inputs['Metallic'])
    m1 = _n(nt, 'ShaderNodeMixShader', 1200, 400)
    L.new(f_clay, m1.inputs[0]); L.new(tr.outputs[0], m1.inputs[1]); L.new(clay.outputs[0], m1.inputs[2])
    m2 = _n(nt, 'ShaderNodeMixShader', 1350, 250)
    L.new(f_col, m2.inputs[0]); L.new(m1.outputs[0], m2.inputs[1]); L.new(col.outputs[0], m2.inputs[2])
    m3 = _n(nt, 'ShaderNodeMixShader', 1500, 100)
    L.new(f_tex, m3.inputs[0]); L.new(m2.outputs[0], m3.inputs[1]); L.new(gi.outputs['Final'], m3.inputs[2])
    # the light line at each front
    gsum = _math(nt, 'ADD', bump(f_clay, -800), bump(f_col, -1000), x=900, y=-800)
    gsum = _math(nt, 'ADD', gsum, bump(f_tex, -1200), x=1050, y=-800)
    gstr = _math(nt, 'MULTIPLY', gsum, vals['lueur'], x=1200, y=-800)
    em = _n(nt, 'ShaderNodeEmission', 1350, -600)
    em.inputs['Color'].default_value = (1.0, 0.97, 0.92, 1)
    L.new(gstr, em.inputs['Strength'])
    add = _n(nt, 'ShaderNodeAddShader', 1700, 0)
    L.new(m3.outputs[0], add.inputs[0]); L.new(em.outputs[0], add.inputs[1])
    L.new(add.outputs[0], go.inputs['Shader'])
    return g


def vid_fil_material():
    m = bpy.data.materials.get('VID_fil')
    if m:
        return m
    m = bpy.data.materials.new('VID_fil')
    m.use_nodes = True
    nt, L = m.node_tree, m.node_tree.links
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_MATERIAL':
            nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
    out.location = (1900, 0)
    F, bump, vals = _vid_core(nt)
    f_in, f_clay, f_col = F(0, 600), F(2, 400), F(3, 200)
    # visible once drawn, dimmed over the clay, gone with the colour
    dim = _math(nt, 'MULTIPLY_ADD', f_clay, -0.88, x=900, y=400)
    dim.node.inputs[2].default_value = 1.0
    keep = _math(nt, 'SUBTRACT', 1.0, f_col, x=900, y=200)
    a = _math(nt, 'MULTIPLY', f_in, dim, x=1100, y=500)
    a = _math(nt, 'MULTIPLY', a, keep, x=1250, y=400)
    tr = _n(nt, 'ShaderNodeBsdfTransparent', 1100, 100)
    em = _n(nt, 'ShaderNodeEmission', 1100, -100)
    em.inputs['Color'].default_value = (*VID['fil_col'], 1)
    em.inputs['Strength'].default_value = VID['fil_force']
    mx = _n(nt, 'ShaderNodeMixShader', 1400, 200)
    L.new(a, mx.inputs[0]); L.new(tr.outputs[0], mx.inputs[1]); L.new(em.outputs[0], mx.inputs[2])
    gstr = _math(nt, 'MULTIPLY', bump(f_in, -800), vals['lueur'], x=1200, y=-800)
    eg = _n(nt, 'ShaderNodeEmission', 1400, -400)
    eg.inputs['Color'].default_value = (1.0, 0.97, 0.92, 1)
    L.new(gstr, eg.inputs['Strength'])
    add = _n(nt, 'ShaderNodeAddShader', 1650, 0)
    L.new(mx.outputs[0], add.inputs[0]); L.new(eg.outputs[0], add.inputs[1])
    L.new(add.outputs[0], out.inputs['Surface'])
    _vid_mat_settings(m)
    return m


def _vid_mat_settings(m):
    for k, v in (('surface_render_method', 'DITHERED'), ('use_transparent_shadow', True)):
        try:
            setattr(m, k, v)
        except Exception:
            pass


def vid_set_style(**kw):
    VID.update(kw)
    for nt in [bpy.data.node_groups.get('VID_etapes')] + [m.node_tree for m in bpy.data.materials if m.name == 'VID_fil']:
        if not nt:
            continue
        for k in ('bande', 'lueur', 'grain'):
            n = nt.nodes.get('vid_' + k)
            if n:
                n.outputs[0].default_value = VID[k]


# ------------------------------------------------------------------ the flat colour of each material
_VID_IMG = {}


def _srgb_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _vid_img_mean(im):
    if im.name in _VID_IMG:
        return _VID_IMG[im.name]
    try:
        n = len(im.pixels)
        a = _np.empty(n, dtype=_np.float32)
        im.pixels.foreach_get(a)
        a = a.reshape(-1, 4)
        w = a[:, 3:4] if a.shape[1] == 4 else 1.0
        c = (a[:, :3] * w).sum(axis=0) / max(float(_np.sum(w)), 1.0)
        c = tuple(float(x) for x in c)
        if im.colorspace_settings.name.lower().startswith('srgb') and not im.is_float:
            c = tuple(_srgb_lin(x) for x in c)
    except Exception:
        c = (0.5, 0.5, 0.5)
    _VID_IMG[im.name] = c
    return c


def _vid_col(sock, depth=0):
    if not sock.is_linked:
        v = sock.default_value
        return tuple(v[:3]) if hasattr(v, '__len__') else (v, v, v)
    if depth > 8:
        return (0.5, 0.5, 0.5)
    n = sock.links[0].from_node
    if n.type == 'TEX_IMAGE' and n.image:
        return _vid_img_mean(n.image)
    if n.type == 'RGB':
        return tuple(n.outputs[0].default_value[:3])
    if n.type == 'VALTORGB':
        els = n.color_ramp.elements
        return tuple(sum(e.color[i] for e in els) / len(els) for i in range(3))
    if n.type in ('MIX', 'MIX_RGB'):
        ins = [i for i in n.inputs if i.type == 'RGBA' and i.enabled]
        if len(ins) >= 2:
            a, b = _vid_col(ins[0], depth + 1), _vid_col(ins[1], depth + 1)
            return tuple((x + y) / 2 for x, y in zip(a, b))
    for name in ('Color', 'Color1', 'A', 'Image'):
        if name in n.inputs and n.inputs[name].type == 'RGBA':
            return _vid_col(n.inputs[name], depth + 1)
    return (0.5, 0.5, 0.5)


def _vid_const(m):
    nt = m.node_tree
    if m.name.startswith(('screen_', 'mbp_display')):
        return (0.008, 0.008, 0.009), 0.12, 0.0          # a monitor switched off: black glass
    p = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if p is None:
        e = next((n for n in nt.nodes if n.type in ('BSDF_DIFFUSE', 'EMISSION', 'BSDF_GLOSSY')), None)
        return (_vid_col(e.inputs['Color']) if e else (0.5, 0.5, 0.5)), 0.5, 0.0
    c = _vid_col(p.inputs['Base Color'])
    r = p.inputs['Roughness'].default_value if not p.inputs['Roughness'].is_linked else 0.5
    mt = p.inputs['Metallic'].default_value if not p.inputs['Metallic'].is_linked else 0.0
    return c, r, mt


def vid_wrap_materials():
    g = vid_group()
    n = 0
    for m in list(bpy.data.materials):
        if not m.use_nodes or m.name.startswith('VID_') or not m.users:
            continue
        nt = m.node_tree
        if any(x.type == 'GROUP' and x.node_tree == g for x in nt.nodes):
            continue
        c, r, mt = _vid_const(m)
        for out in [x for x in nt.nodes if x.type == 'OUTPUT_MATERIAL']:
            s = out.inputs['Surface']
            if not s.is_linked:
                continue
            src = s.links[0].from_socket
            gn = nt.nodes.new('ShaderNodeGroup')
            gn.node_tree = g
            gn.location = (out.location.x - 220, out.location.y)
            out.location.x += 120
            nt.links.new(src, gn.inputs['Final'])
            nt.links.new(gn.outputs['Shader'], s)
            gn.inputs['Couleur'].default_value = (*c, 1)
            gn.inputs['Rugosite'].default_value = r
            gn.inputs['Metal'].default_value = mt
        _vid_mat_settings(m)
        n += 1
    print('VID materials', n, flush=True)


def vid_screens_power():
    """Monitors (materials screen_*): an 'on' factor per object (vid_on): 0 black glass, 0→0.3 the backlight rises,
    0.3→1 the picture fades in."""
    for m in bpy.data.materials:
        if not m.name.startswith(('screen_', 'mbp_display')) or not m.use_nodes:
            continue
        nt, L = m.node_tree, m.node_tree.links
        p = principled(m)
        if p.get('vid_on'):
            continue
        p['vid_on'] = 1
        tex = p.inputs['Base Color'].links[0].from_socket if p.inputs['Base Color'].is_linked else None
        strength = p.inputs['Emission Strength'].default_value
        on = _n(nt, 'ShaderNodeAttribute', -900, -600, attribute_type='OBJECT', attribute_name='vid_on')
        a = _n(nt, 'ShaderNodeMapRange', -700, -500, clamp=True)
        L.new(on.outputs['Fac'], a.inputs['Value']); a.inputs['From Max'].default_value = 0.3
        b = _n(nt, 'ShaderNodeMapRange', -700, -750, clamp=True)
        L.new(on.outputs['Fac'], b.inputs['Value']); b.inputs['From Min'].default_value = 0.3
        if tex is not None:
            base = _n(nt, 'ShaderNodeMix', -450, -300, data_type='RGBA')
            L.new(b.outputs['Result'], base.inputs[0]); base.inputs[6].default_value = (0.0, 0.0, 0.0, 1)
            L.new(tex, base.inputs[7])
            L.new(base.outputs[2], p.inputs['Base Color'])
            emc = _n(nt, 'ShaderNodeMix', -450, -550, data_type='RGBA')
            L.new(b.outputs['Result'], emc.inputs[0]); emc.inputs[6].default_value = (0.05, 0.055, 0.065, 1)
            L.new(tex, emc.inputs[7])
            L.new(emc.outputs[2], p.inputs['Emission Color'])
        st = _math(nt, 'MULTIPLY', a.outputs['Result'], strength, x=-450, y=-800)
        L.new(st, p.inputs['Emission Strength'])


# ------------------------------------------------------------------ keyframes
def _key(o, prop, frame, value):
    o[prop] = value
    o.keyframe_insert(data_path=f'["{prop}"]', frame=frame)


def _key_attr(owner, attr, frame, value):
    setattr(owner, attr, value)
    owner.keyframe_insert(data_path=attr, frame=frame)


def _vid_interp(o, kind='LINEAR', only=None):
    ad = o.animation_data
    if not ad or not ad.action:
        return
    for fc in _vid_fcurves(ad.action):
        if only and only not in fc.data_path:
            continue
        for kp in fc.keyframe_points:
            kp.interpolation = kind


def _vid_fcurves(act):
    try:
        return list(act.fcurves)
    except AttributeError:                       # layered actions (4.4+)
        out = []
        for lay in act.layers:
            for st in lay.strips:
                for cb in st.channelbags:
                    out += list(cb.fcurves)
        return out


def _vid_const_interp(o, path):
    ad = o.animation_data
    if ad and ad.action:
        for fc in _vid_fcurves(ad.action):
            if fc.data_path == path:
                for kp in fc.keyframe_points:
                    kp.interpolation = 'CONSTANT'


# ------------------------------------------------------------------ wireframe twins and modelling
def vid_twin(o):
    if o.type != 'MESH' or not o.material_slots:
        return None
    t = o.copy()
    t.name = o.name + '.fil'
    for c in o.users_collection:
        c.objects.link(t)
    fil = vid_fil_material()
    for sl in t.material_slots:
        sl.link = 'OBJECT'
        sl.material = fil
    # world size / mesh size: the scale actually applied to the mesh (imported models nest their own scales)
    loc = [Vector(c) for c in o.bound_box]
    wor = [o.matrix_world @ v for v in loc]
    dl = (Vector([max(v[i] for v in loc) for i in range(3)]) - Vector([min(v[i] for v in loc) for i in range(3)])).length
    dw = (Vector([max(v[i] for v in wor) for i in range(3)]) - Vector([min(v[i] for v in wor) for i in range(3)])).length
    sc = dw / dl if dl > 1e-9 else 1.0
    n = len(o.data.polygons)
    if n > 6000:                                     # dense meshes: fewer, cleaner lines
        dm = t.modifiers.new('vid_simple', 'DECIMATE')
        dm.ratio = max(0.04, 6000 / n)
    w = t.modifiers.new('vid_fil', 'WIREFRAME')
    w.thickness = VID['fil'] / max(sc, 1e-6)
    w.use_replace, w.use_even_offset, w.use_boundary, w.use_relative_offset = True, False, True, False
    for k in ('visible_shadow', 'visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_volume_scatter'):
        try:
            setattr(t, k, False)
        except Exception:
            pass
    t['vid_twin'] = o.name
    return t


def vid_morph(o, kind):
    me = o.data
    if me.shape_keys or len(me.vertices) < 4:
        return None
    if me.users > 1:
        o.data = me = me.copy()
    co = [v.co.copy() for v in me.vertices]
    mn = Vector([min(c[i] for c in co) for i in range(3)])
    mx = Vector([max(c[i] for c in co) for i in range(3)])
    sz = mx - mn
    if kind == 'extrude':
        ax = 2 if sz.z >= 0.35 * max(sz.x, sz.y) else (0 if sz.x >= sz.y else 1)
        start = lambda c: Vector([mn[i] + (c[i] - mn[i]) * 0.015 if i == ax else c[i] for i in range(3)])
    elif kind == 'nappe':
        start = lambda c: Vector((c.x, c.y, mx.z))
    else:                                    # bloc: everything near a face of the bounding box goes onto it
        def start(c):
            r = c.copy()
            for i in range(3):
                m = 0.22 * sz[i]
                if c[i] - mn[i] < m:
                    r[i] = mn[i]
                elif mx[i] - c[i] < m:
                    r[i] = mx[i]
            return r
    o.shape_key_add(name='Basis', from_mix=False)
    k = o.shape_key_add(name='vid_bloc', from_mix=False)
    for i, c in enumerate(co):
        k.data[i].co = start(c)
    return k


# ------------------------------------------------------------------ the schedule
VID_D = dict(appear=0.5, model=1.3, clay=0.55, colour=0.45, texture=0.55)


def vid_bbox(objs):
    pts = []
    for o in objs:
        if o.type in ('MESH', 'CURVE'):
            pts += [o.matrix_world @ Vector(c) for c in o.bound_box]
    if not pts:
        return Vector(), Vector((0, 0, 1))
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    return mn, mx


def vid_sweep_axis(mn, mx):
    sz = mx - mn
    if sz.z >= 0.35 * max(sz.x, sz.y):
        ax = Vector((0, 0, 1))
    else:
        ax = Vector((1, 0, 0)) if sz.x >= sz.y else Vector((0, 1, 0))
    L = max(ax.dot(sz), 1e-3)
    return ax / L


def vid_schedule_piece(objs, t0, imported, scale=1.0, motion=None):
    """Keys the stages of one piece (a list of objects built together) from t0 (s). Returns the end time."""
    d = {k: v * scale for k, v in VID_D.items()}
    if imported:
        d['model'] = 0.45 * scale
    mn, mx = vid_bbox(objs)
    dv = vid_sweep_axis(mn, mx)
    ta = t0 + d['appear']
    tm = ta + d['model']
    tc = tm + d['clay']
    tk = tc + d['colour']
    tt = tk + d['texture']
    fr = [vid_f(x) for x in (t0, ta, tm, tc, tk, tt)]
    for o in objs:
        if o.type not in ('MESH', 'CURVE'):
            continue
        o['vid_o'] = list(mn)
        o['vid_d'] = list(dv)
        own = not imported
        if o.type == 'CURVE':
            # cables grow along their path, straight in clay
            for f, v in ((0, 0.0), (fr[0] - 1, 0.0), (fr[0], 3.0), (fr[2], 3.0), (fr[4], 4.0), (fr[5], 5.0)):
                if f >= 0:
                    _key(o, 'vid_s', max(f, 0), v)
            o.data.bevel_factor_end = 0.0
            o.data.keyframe_insert('bevel_factor_end', frame=fr[0])
            o.data.bevel_factor_end = 1.0
            o.data.keyframe_insert('bevel_factor_end', frame=fr[2])
            _key_attr(o, 'hide_render', 0, True)
            _key_attr(o, 'hide_render', fr[0], False)
            _vid_const_interp(o, 'hide_render')
            continue
        for f, v in ((0, 0.0), (fr[0], 0.0), (fr[1], 1.0), (fr[2], 2.0), (fr[3], 3.0), (fr[4], 4.0), (fr[5], 5.0)):
            _key(o, 'vid_s', f, v)
        _key_attr(o, 'hide_render', 0, True)
        _key_attr(o, 'hide_render', max(fr[2] - 1, 1), False)
        _vid_const_interp(o, 'hide_render')
        # modelling of our own meshes
        if own and o.get('vid_kind'):
            kb = o.data.shape_keys.key_blocks.get('vid_bloc') if o.data.shape_keys else None
            if kb:
                kb.value = 1.0
                kb.keyframe_insert('value', frame=fr[1])
                kb.value = 0.0
                kb.keyframe_insert('value', frame=fr[1] + int((fr[2] - fr[1]) * 0.7))
            bev = o.get('vid_bev') or {}
            for tw in [o] + [x for x in [bpy.data.objects.get(o.name + '.fil')] if x]:
                for m in tw.modifiers:
                    if m.type == 'BEVEL' and m.name in bev:
                        m.width = 0.0
                        m.keyframe_insert('width', frame=fr[1] + int((fr[2] - fr[1]) * 0.55))
                        m.width = bev[m.name]
                        m.keyframe_insert('width', frame=fr[2])
        tw = bpy.data.objects.get(o.name + '.fil')
        if tw:
            for f, v in ((0, 0.0), (fr[0], 0.0), (fr[1], 1.0), (fr[2], 2.0), (fr[3], 3.0), (fr[4], 4.0), (fr[5], 5.0)):
                _key(tw, 'vid_s', f, v)
            tw['vid_o'], tw['vid_d'] = list(mn), list(dv)
            _key_attr(tw, 'hide_render', 0, True)
            _key_attr(tw, 'hide_render', max(fr[0], 1), False)
            _key_attr(tw, 'hide_render', fr[4] + 1, True)
            _vid_const_interp(tw, 'hide_render')
    return tt


def vid_prepare(objs):
    """Morph keys, twins and default props for the animated objects."""
    bpy.context.view_layer.update()
    for o in objs:
        if o.type not in ('MESH', 'CURVE'):
            continue
        if o.type == 'MESH' and not vid_imported(o) and len(o.data.polygons) < 60000:
            leaf = o.get('trace', '').split('/')[-1]
            kind = 'extrude' if leaf in VID_EXTRUDE else ('nappe' if leaf == 'grid_mesh' else 'bloc')
            if vid_morph(o, kind):
                o['vid_kind'] = kind
            bev = {m.name: m.width for m in o.modifiers if m.type == 'BEVEL'}
            if bev:
                o['vid_bev'] = bev
        if o.type == 'MESH':
            vid_twin(o)


def vid_defaults():
    for o in bpy.data.objects:
        if o.type in ('MESH', 'CURVE'):
            o['vid_s'] = 5.0
            o['vid_on'] = 1.0
            o['vid_o'] = [0.0, 0.0, 0.0]
            o['vid_d'] = [0.0, 0.0, 0.0]


# ------------------------------------------------------------------ collection instances made real
def vid_make_real():
    """The Sketchfab objects placed through collection instances (the fan, the plants, the pencils, the pen, the cup,
    the eraser, the bin and its paper balls) become real objects, one piece per instance. The stages are swept in world
    space from the piece's own box, which an instance cannot follow: before (17/11) the fan and the plants stayed in
    clay. The prototypes (LIB, at the origin) are marked and left out of the build."""
    n = 0
    for inst in [o for o in bpy.data.objects if o.type == 'EMPTY' and o.instance_type == 'COLLECTION' and o.instance_collection]:
        coll = inst.instance_collection
        off = Matrix.Translation(-coll.instance_offset)
        dest = inst.users_collection[0]
        for ob in coll.all_objects:
            ob['vid_proto'] = True
            if ob.type not in ('MESH', 'CURVE'):
                continue
            c = ob.copy()
            dest.objects.link(c)
            c.parent = None
            c.matrix_world = inst.matrix_world @ off @ ob.matrix_world
            c['vid_piece'] = inst.name
            del c['vid_proto']
            n += 1
        inst.instance_type = 'NONE'
    bpy.context.view_layer.update()
    print('REAL', n, 'objects', flush=True)


# ------------------------------------------------------------------ the backdrop: prototypes A, B, C (17/11)
# The studio cyclorama shows its edge in the wide shots (it is 18 m wide). Option fond=:
#   A  the infinite cove: a floor that curves up into a round wall all around the desk, no edge nor horizon whichever
#      way the camera turns; satin floor that softly reflects the desk; the far wall sinks into the dark.
#   B  Blender's grid: an endless dark floor with the viewport grid (10 cm and 1 m lines, the red X and green Y axes),
#      fading with the distance; once everything is built (with the LEDs) the grid fades and the floor becomes the lab's
#      concrete: from the software to the real thing.
#   C  the plinth: the desk corner stands on a slab of the lab's concrete floating in a dark void; the slab is the first
#      thing built (a face that extrudes).
VID_FOND = OPT.get('fond', 'B')                 # retained 18/11: Blender's grid, light (fondv=3); A, C: Trash; fond=0: old cyclo


def _vid_spin(name, prof, seg=144):
    """A surface of revolution about the vertical axis through VID_C; prof = [(r, z), ...] from the centre outwards."""
    import bmesh as _bm
    bm = _bm.new()
    vs = [bm.verts.new((r, 0.0, z)) for r, z in prof]
    es = [bm.edges.new((vs[i], vs[i + 1])) for i in range(len(vs) - 1)]
    _bm.ops.spin(bm, geom=vs + es, cent=(0, 0, 0), axis=(0, 0, 1), angle=2 * math.pi, steps=seg, use_merge=True)
    _bm.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for f in me.polygons:
        f.use_smooth = True
    o = bpy.data.objects.new(name, me)
    o.location = (VID_C.x, VID_C.y, 0.0)
    ROOT.objects.link(o)
    return o


# B's variants (18/11, the user found B too dark around a black desk): floor and line tones, the line glow, the final
# concrete, and a horizon that brightens with the distance (colour, from, to, colour of the sky above) seen by the camera
VID_GRILLE = {
    # beton: the concrete texture (hangar_concrete_floor) is very dark, about 3 % linear: the factor brings it to the
    # grid's own tone, so the floor keeps its value when the grid fades; the horizon starts just outside the lit area
    '0': dict(base=0.026, minor=0.065, major=0.12, glow=0.9, beton=0.95, horizon=None, world=0.006),           # B as first shown
    '1': dict(base=0.075, minor=0.118, major=0.185, glow=0.5, beton=2.5, horizon=(0.075, 3.0, 22.0, 0.06), world=0.03),  # Blender's grey
    '2': dict(base=0.045, minor=0.09, major=0.15, glow=0.6, beton=1.5, horizon=(0.3, 2.5, 16.0, 0.15), world=0.03),     # light horizon
    # retained 18/11: the light grid; its concrete is the stained hangar floor brought to the grid's tone (the user
    # likes its stains; a clean brushed concrete was tried and declined)
    '3': dict(base=0.42, minor=0.27, major=0.17, glow=0.0, beton=14.0, horizon=(0.5, 3.0, 18.0, 0.38), world=0.05),
}
VID_FOND_V = VID_GRILLE.get(OPT.get('fondv', '3'), VID_GRILLE['3'])    # 3 retained 18/11 (0, 1, 2: Trash)


def _vid_grid(m):
    """Blender's viewport grid on top of the material m (world position, in metres): 10 cm lines near the desk, 1 m lines
    further, the X (red) and Y (green) axes; mixed in by the object attribute vid_grille (1 grid, 0 the real floor)."""
    nt, L = m.node_tree, m.node_tree.links
    p = principled(m)
    geo = _n(nt, 'ShaderNodeNewGeometry', -2400, 600)
    sep = _n(nt, 'ShaderNodeSeparateXYZ', -2200, 600)
    L.new(geo.outputs['Position'], sep.inputs[0])
    X, Y = sep.outputs['X'], sep.outputs['Y']

    def line(c, step, w, y):
        if step:
            f = _math(nt, 'FRACT', _math(nt, 'ADD', _math(nt, 'DIVIDE', c, step, x=-2000, y=y), 0.5, x=-1850, y=y), None, x=-1700, y=y)
            d = _math(nt, 'MULTIPLY', _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', f, 0.5, x=-1550, y=y), None, x=-1400, y=y), step, x=-1250, y=y)
        else:
            d = _math(nt, 'ABSOLUTE', c, None, x=-1400, y=y)
        r = _n(nt, 'ShaderNodeMapRange', -1100, y, clamp=True)
        L.new(d, r.inputs['Value'])
        r.inputs['From Min'].default_value, r.inputs['From Max'].default_value = w * 0.4, w * 1.6
        r.inputs['To Min'].default_value, r.inputs['To Max'].default_value = 1.0, 0.0
        return r.outputs['Result']

    def fade(a, b, y):
        dx = _math(nt, 'SUBTRACT', X, VID_C.x, x=-2000, y=y)
        dy = _math(nt, 'SUBTRACT', Y, VID_C.y, x=-2000, y=y - 60)
        dist = _math(nt, 'SQRT', _math(nt, 'ADD', _math(nt, 'MULTIPLY', dx, dx, x=-1850, y=y), _math(nt, 'MULTIPLY', dy, dy, x=-1850, y=y - 60), x=-1700, y=y), None, x=-1550, y=y)
        r = _n(nt, 'ShaderNodeMapRange', -1100, y, clamp=True)
        L.new(dist, r.inputs['Value'])
        r.inputs['From Min'].default_value, r.inputs['From Max'].default_value = a, b
        r.inputs['To Min'].default_value, r.inputs['To Max'].default_value = 1.0, 0.0
        return r.outputs['Result']

    minor = _math(nt, 'MULTIPLY', _math(nt, 'MAXIMUM', line(X, 0.1, 0.0024, 500), line(Y, 0.1, 0.0024, 400), x=-900, y=450), fade(2.0, 6.5, 300), x=-750, y=450)
    major = _math(nt, 'MULTIPLY', _math(nt, 'MAXIMUM', line(X, 1.0, 0.0055, 200), line(Y, 1.0, 0.0055, 100), x=-900, y=150), fade(5.0, 24.0, 0), x=-750, y=150)
    fa = fade(8.0, 40.0, -100)
    ax_x = _math(nt, 'MULTIPLY', line(Y, 0.0, 0.009, -200), fa, x=-750, y=-200)     # the X axis is the line y = 0
    ax_y = _math(nt, 'MULTIPLY', line(X, 0.0, 0.009, -300), fa, x=-750, y=-300)
    P = VID_FOND_V
    tone = lambda v: (v, v * 1.02, v * 1.07, 1)
    col = tone(P['base'])
    prev = None
    for k, (mask, c) in enumerate(((minor, tone(P['minor'])), (major, tone(P['major'])),
                                   (ax_x, (0.62, 0.11, 0.13, 1)), (ax_y, (0.3, 0.58, 0.1, 1)))):
        mx = _n(nt, 'ShaderNodeMix', -550 + k * 120, 300 - k * 80, data_type='RGBA')
        L.new(mask, mx.inputs[0])
        if prev is None:
            mx.inputs[6].default_value = col
        else:
            L.new(prev, mx.inputs[6])
        mx.inputs[7].default_value = c
        prev = mx.outputs[2]
    lines = _math(nt, 'MAXIMUM', _math(nt, 'MAXIMUM', minor, major, x=-550, y=-450), _math(nt, 'MAXIMUM', ax_x, ax_y, x=-550, y=-520), x=-400, y=-480)
    g = _n(nt, 'ShaderNodeAttribute', -550, -650, attribute_type='OBJECT', attribute_name='vid_grille')
    base_src = p.inputs['Base Color'].links[0].from_socket if p.inputs['Base Color'].is_linked else None
    bm_ = _n(nt, 'ShaderNodeMix', 0, 300, data_type='RGBA')
    L.new(g.outputs['Fac'], bm_.inputs[0])
    if base_src is not None:
        L.new(base_src, bm_.inputs[6])
    else:
        bm_.inputs[6].default_value = p.inputs['Base Color'].default_value
    L.new(prev, bm_.inputs[7])
    # the horizon: far away the floor turns into the sky's colour (it glows, so it matches the background exactly)
    if P['horizon']:
        hc, ha, hb, _ = P['horizon']
        fh = fade(ha, hb, -900)                     # 1 near the desk, 0 at the horizon
        fh = _math(nt, 'SUBTRACT', 1.0, fh, x=-900, y=-900)
    else:
        fh, hc = None, 0.0
    if fh is not None:
        dark = _n(nt, 'ShaderNodeMix', 150, 300, data_type='RGBA')
        L.new(fh, dark.inputs[0])
        L.new(bm_.outputs[2], dark.inputs[6])
        dark.inputs[7].default_value = (0, 0, 0, 1)
        L.new(dark.outputs[2], p.inputs['Base Color'])
    else:
        L.new(bm_.outputs[2], p.inputs['Base Color'])
    rsrc = p.inputs['Roughness'].links[0].from_socket if p.inputs['Roughness'].is_linked else None
    rm = _n(nt, 'ShaderNodeMix', 0, 0, data_type='FLOAT')
    L.new(g.outputs['Fac'], rm.inputs['Factor'])
    if rsrc is not None:
        L.new(rsrc, rm.inputs[2])
    else:
        rm.inputs[2].default_value = p.inputs['Roughness'].default_value
    rm.inputs[3].default_value = 0.85
    L.new(rm.outputs[0], p.inputs['Roughness'])
    # the lines glow a little, so the grid reads in the shadows like in the viewport: s1 * lines + fh * horizon
    s1 = _math(nt, 'MULTIPLY', _math(nt, 'MULTIPLY', lines, g.outputs['Fac'], x=-250, y=-500), P['glow'], x=-100, y=-500)
    if fh is None:
        L.new(prev, p.inputs['Emission Color'])
        L.new(s1, p.inputs['Emission Strength'])
    else:
        s1 = _math(nt, 'MULTIPLY', s1, _math(nt, 'SUBTRACT', 1.0, fh, x=-100, y=-700), x=50, y=-500)
        tot = _math(nt, 'ADD', s1, fh, x=200, y=-600)
        w = _math(nt, 'DIVIDE', fh, _math(nt, 'ADD', tot, 1e-4, x=300, y=-700), x=400, y=-650)
        ec = _n(nt, 'ShaderNodeMix', 500, -500, data_type='RGBA')
        L.new(w, ec.inputs[0])
        L.new(prev, ec.inputs[6])
        ec.inputs[7].default_value = tone(hc)
        L.new(ec.outputs[2], p.inputs['Emission Color'])
        L.new(tot, p.inputs['Emission Strength'])


def _vid_world_horizon():
    """The sky seen by the camera: the horizon's colour, a little darker upwards; the light it gives stays low."""
    P = VID_FOND_V
    w = SC.world
    nt, L = w.node_tree, w.node_tree.links
    bg = next(n for n in nt.nodes if n.type == 'BACKGROUND')
    tone = lambda v: (v, v * 1.02, v * 1.07, 1)
    if not P['horizon']:
        bg.inputs['Color'].default_value = tone(P['world'])
        return
    hc, _, _, top = P['horizon']
    tc = _n(nt, 'ShaderNodeTexCoord', -900, 300)
    sep = _n(nt, 'ShaderNodeSeparateXYZ', -700, 300)
    L.new(tc.outputs['Generated'], sep.inputs[0])
    r = _n(nt, 'ShaderNodeMapRange', -500, 300, clamp=True, interpolation_type='SMOOTHSTEP')
    L.new(sep.outputs['Z'], r.inputs['Value'])
    r.inputs['From Min'].default_value, r.inputs['From Max'].default_value = 0.0, 0.7
    sky = _n(nt, 'ShaderNodeMix', -300, 300, data_type='RGBA')
    L.new(r.outputs['Result'], sky.inputs[0])
    sky.inputs[6].default_value, sky.inputs[7].default_value = tone(hc), tone(top)
    lp = _n(nt, 'ShaderNodeLightPath', -300, 550)
    mx = _n(nt, 'ShaderNodeMix', -100, 350, data_type='RGBA')
    L.new(lp.outputs['Is Camera Ray'], mx.inputs[0])
    mx.inputs[6].default_value = tone(P['world'])
    L.new(sky.outputs[2], mx.inputs[7])
    L.new(mx.outputs[2], bg.inputs['Color'])


def vid_fond(kind):
    cy = bpy.data.objects.get('cyclo')
    if kind not in ('A', 'B', 'C') or not cy:
        return
    bg = next(n for n in SC.world.node_tree.nodes if n.type == 'BACKGROUND')
    bpy.data.objects.remove(cy, do_unlink=True)
    if kind == 'A':
        R0, rc, H = 4.2, 3.2, 12.0                      # close enough for the studio lights to draw a gradient on the wall
        prof = [(0.0, 0.0), (2.0, 0.0), (R0, 0.0)] + \
            [(R0 + rc * math.sin(math.pi / 2 * i / 16), rc - rc * math.cos(math.pi / 2 * i / 16)) for i in range(1, 17)] + [(R0 + rc, H)]
        o = _vid_spin('fond_cyclo', prof)
        o.data.materials.append(m_surface('fond_cyclo', (0.06, 0.061, 0.064), rough=0.42, var=0.015, grain=50, bump=0.0))
        bg.inputs['Color'].default_value = (0.005, 0.0052, 0.0056, 1)
    elif kind == 'B':
        S = 150.0
        me = bpy.data.meshes.new('fond_grille')
        me.from_pydata([(-S, -S, 0), (S, -S, 0), (S, S, 0), (-S, S, 0)], [], [(0, 1, 2, 3)])
        o = bpy.data.objects.new('fond_grille', me)
        ROOT.objects.link(o)
        P = VID_FOND_V                          # the real floor under the grid (wet: sparkling puddles in EEVEE)
        m = mat_pbr('fond_beton', P.get('tex', 'hangar_concrete_floor'), 3.0, tint=P.get('tint', (1, 1, 1)), dark=P['beton'],
                    rough_add=P.get('rough', 0.08))
        _vid_grid(m)
        o.data.materials.append(m)
        o['vid_grille'] = 1.0
        _vid_world_horizon()
    else:
        pts = []
        for x in bpy.data.objects:
            if x.type == 'MESH' and x.get('trace') and not x.get('vid_proto') and not x.get('vid_twin'):
                pts += [x.matrix_world @ Vector(c) for c in x.bound_box]
        mn = Vector((min(p.x for p in pts), min(p.y for p in pts)))
        mx = Vector((max(p.x for p in pts), max(p.y for p in pts)))
        mg = 0.7
        w, d = mx.x - mn.x + 2 * mg, mx.y - mn.y + 2 * mg
        o = box('fond_socle', (w, d, 0.24), ((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, -0.12),
                mat_pbr('fond_socle', 'hangar_concrete_floor', 2.0, dark=1.1, rough_add=0.12))
        bv = o.modifiers.new('bev', 'BEVEL')
        bv.width, bv.segments = 0.012, 3
        o['trace'] = 'socle/box'
        print('SOCLE', round(w, 2), 'x', round(d, 2), flush=True)
        bg.inputs['Color'].default_value = (0.0035, 0.0037, 0.004, 1)
    print('FOND', kind, flush=True)


def vid_fond_anim(kind):
    if kind == 'B':
        o = bpy.data.objects.get('fond_grille')
        t = VID_T['leds']
        for f, v in ((0, 1.0), (vid_f(t - 0.2), 1.0), (vid_f(t + 2.4), 0.0)):
            _key(o, 'vid_grille', f, v)
    elif kind == 'C':
        o = bpy.data.objects.get('fond_socle')
        if o:
            vid_prepare([o])
            vid_schedule_piece([o], 0.15, False, scale=0.5)


# ------------------------------------------------------------------ groups by step
def vid_groups():
    """{step: [(piece_name, [objects]), ...]} in build order."""
    steps = {k: {} for k, _ in VID_STEPS}
    for o in bpy.data.objects:
        if o.type not in ('MESH', 'CURVE') or o.get('vid_twin') or o.get('vid_proto'):
            continue
        st = vid_step(o)
        if not st:
            continue
        p = vid_piece(o)
        key = p if isinstance(p, str) else (p.name if p else o.name)
        steps[st].setdefault(key, []).append(o)
    out = {}
    for st, d in steps.items():
        items = []
        for k, objs in d.items():
            mn, mx = vid_bbox(objs)
            items.append((k, objs, mn, mx))
        if st in ('bureau', 'ecrans', 'lampe'):
            items.sort(key=lambda it: (round(it[2].z / 0.05), it[2].x))
        else:
            items.sort(key=lambda it: (it[2].x, it[2].z))
        out[st] = [(k, objs) for k, objs, mn, mx in items]
    return out


def vid_report(groups):
    for st, items in groups.items():
        n = sum(len(o) for _, o in items)
        print('STEP', st, len(items), 'pieces', n, 'objects', [k for k, _ in items[:12]], flush=True)


# ------------------------------------------------------------------ easing
def _ease_io(u):
    u = min(max(u, 0.0), 1.0)
    return 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2


def _ease_out_back(u, k=1.4):
    u = min(max(u, 0.0), 1.0)
    return 1 + (k + 1) * (u - 1) ** 3 + k * (u - 1) ** 2


def _ease_out(u):
    u = min(max(u, 0.0), 1.0)
    return 1 - (1 - u) ** 3


# ------------------------------------------------------------------ the lamp: cut into its articulated parts
# Sketchfab "Desk lamp": one mesh in loose parts, Y up in mesh space (the object turns it upright). A double
# parallelogram: the two rods of each arm turn by the same angle about their own pins, so the elbow plate and the head
# bracket only translate; the head turns about its swivel pin; the whole arm turns on the base.
LAMP_PINS = dict(P1=(-0.141, 0.69), P2=(0.128, 0.609), Q1=(-1.256, 1.753), Q2=(-1.432, 1.963),
                 E=(-1.575, 1.759), J=(0.11, 2.87), H=(0.19, 3.12), S=(-0.02, 0.0))
LAMP = {}
LAMP_BULB = Vector((0.657, 3.319, -0.109))          # the bulb, in mesh space (the module's constant, Y up)


def _lamp_class(c, n):
    x, y = c.x, c.y
    if y < 0.75:
        return 'B'
    if y < 1.5 and x > -1.1:
        return 'L2' if (n == 144 and abs(x + 0.59) < 0.05) else 'L1'
    if x < -1.1 and y < 2.05:
        return 'E'
    if y < 2.75:
        return 'U1' if (n == 144 and abs(x + 0.576) < 0.05) else 'U2'
    return 'Hh' if x > 0.15 else 'Hb'


def vid_lamp_rig():
    lamp = bpy.data.objects.get('dk_lampeS')
    if not lamp:
        return None
    tete = float(lamp.get('dl_tete', 0.0))          # the head's turn already applied by the decor (objets-lampe.py, 17/11)
    import bmesh as _bm
    bm = _bm.new()
    bm.from_mesh(lamp.data)
    bm.verts.ensure_lookup_table()
    cls = [None] * len(bm.verts)
    shade_n, shade_pts = [0], []
    seen = set()
    for v in bm.verts:
        if v.index in seen:
            continue
        st, comp = [v], []
        seen.add(v.index)
        while st:
            x = st.pop()
            comp.append(x)
            for e in x.link_edges:
                w = e.other_vert(x)
                if w.index not in seen:
                    seen.add(w.index)
                    st.append(w)
        c = sum((x.co for x in comp), Vector()) / len(comp)
        k = _lamp_class(c, len(comp))
        for x in comp:
            cls[x.index] = k
        if k == 'Hh' and len(comp) > shade_n[0]:
            shade_n[0] = len(comp)
            shade_pts[:] = [x.co.copy() for x in comp]
    bm.free()
    parts = {}
    for k in ('B', 'L1', 'L2', 'E', 'U1', 'U2', 'Hb', 'Hh'):
        o = lamp.copy()
        o.data = lamp.data.copy()
        o.name = 'dk_lampeS_' + k
        for c in lamp.users_collection:
            c.objects.link(o)
        b2 = _bm.new()
        b2.from_mesh(o.data)
        b2.verts.ensure_lookup_table()
        _bm.ops.delete(b2, geom=[v for v in b2.verts if cls[v.index] != k], context='VERTS')
        b2.to_mesh(o.data)
        b2.free()
        parts[k] = o
    coll = lamp.users_collection[0]
    norm = lamp.parent
    bpy.data.objects.remove(lamp, do_unlink=True)
    base_basis = parts['B'].matrix_basis.copy()

    def empty(name, parent, at, rel_to=(0.0, 0.0)):
        e = bpy.data.objects.new(name, None)
        e.empty_display_size = 0.02
        coll.objects.link(e)
        e.parent = parent
        if parent is norm:
            e.matrix_basis = base_basis @ Matrix.Translation((at[0], at[1], 0.0))
        else:
            e.matrix_basis = Matrix.Translation((at[0] - rel_to[0], at[1] - rel_to[1], 0.0))
        return e

    P = LAMP_PINS
    sw0 = empty('vidl_cadre', norm, P['S'])                # the lamp's own frame (it stands the Y-up mesh upright)
    sw = empty('vidl_pivot', sw0, P['S'], P['S'])          # the swivel on the base, about the mesh Y axis
    l1 = empty('vidl_L1', sw, P['P1'], P['S'])
    l2 = empty('vidl_L2', sw, P['P2'], P['S'])
    er = empty('vidl_coude', sw, P['S'], P['S'])
    u1 = empty('vidl_U1', er, P['Q1'], P['S'])
    u2 = empty('vidl_U2', er, P['Q2'], P['S'])
    hr = empty('vidl_tete', er, P['S'], P['S'])
    hh = empty('vidl_rotule', hr, P['H'], P['S'])
    bpy.context.view_layer.update()

    def adopt(o, parent):
        mw = o.matrix_world.copy()
        o.parent = parent
        o.matrix_parent_inverse = Matrix.Identity(4)
        o.matrix_world = mw

    for k, par in (('L1', l1), ('L2', l2), ('E', er), ('U1', u1), ('U2', u2), ('Hb', hr), ('Hh', hh)):
        adopt(parts[k], par)
    for f in [o for o in bpy.data.objects if o.name.startswith('dk_lampeS_fil')]:
        z = max((f.matrix_world @ Vector(c)).z for c in f.bound_box)
        adopt(f, er if z < 1.15 else hr)
    li = bpy.data.objects.get('al_light_S')
    LAMP['final'] = (0.0, 0.0)
    if li and shade_pts:
        # The head was meant to be turned so the shade looks at the lit spot (the module's swivel never applied: the
        # mesh is Y up), and the spot sat apart from the lamp. Here the head and the base swivel are turned so the
        # shade aims at the point the original spot was aimed at, and the spot sits in the bulb, along the shade.
        mw0 = li.matrix_world.copy()
        p0, d0 = mw0.translation, -(mw0.to_3x3() @ Vector((0, 0, 1))).normalized()
        zd = float(globals().get('H0', 0.74))
        T = p0 + d0 * ((zd - p0.z) / d0.z) if d0.z < -0.05 else p0 + Vector((0.3, -0.2, zd - p0.z))
        piv = Vector((0.19, 3.12, -0.03))
        B = piv + Matrix.Rotation(tete, 3, 'Z') @ (LAMP_BULB - piv)
        # the shade is a dome: the centre of its box lies along its axis, in front of the bulb (as in the module)
        R = (Vector([min(v[i] for v in shade_pts) for i in range(3)]) + Vector([max(v[i] for v in shade_pts) for i in range(3)])) / 2
        Msw, Mhh, Mhead = sw.matrix_world.copy(), hh.matrix_world.copy(), parts['Hh'].matrix_world.copy()
        head_in_hh = Mhh.inverted() @ Mhead

        def aim(psi, t3):
            Mh = Msw @ Matrix.Rotation(psi, 4, 'Y') @ Msw.inverted() @ Mhh @ Matrix.Rotation(t3, 4, 'Z') @ head_in_hh
            bw, rw = Mh @ B, Mh @ R
            return bw, (rw - bw).normalized()

        best = None
        for i in range(-28, 29):
            for j in range(-40, 41):
                psi, t3 = i * 0.025, j * 0.03
                bw, ax = aim(psi, t3)
                cost = ax.angle((T - bw).normalized()) + 0.2 * abs(psi)
                if best is None or cost < best[0]:
                    best = (cost, psi, t3)
        _, psi, t3 = best
        LAMP['final'] = (psi, t3)
        bw, ax = aim(psi, t3)
        print('LAMP aim', round(psi, 3), round(t3, 3), 'target', [round(x, 2) for x in T], 'err', round(best[0], 3), flush=True)
        sw.rotation_euler = (0.0, psi, 0.0)
        hh.rotation_euler = (0.0, 0.0, t3)
        bpy.context.view_layer.update()
        li.parent = None
        li.matrix_world = Matrix.Translation(bw + ax * 0.06) @ ax.to_track_quat('-Z', 'Y').to_matrix().to_4x4()
        adopt(li, hh)
    elif li:
        adopt(li, hh)
    LAMP.update(parts=parts, sw=sw, l1=l1, l2=l2, er=er, u1=u1, u2=u2, hr=hr, hh=hh, light=li,
                energy=li.data.energy if li else 0.0)
    bpy.context.view_layer.update()
    return parts


LAMP_START = dict(psi=0.3, t1=0.22, t2=-0.36, t3=-0.32)   # half folded, the head bowed (17/11: was too low)


def _lamp_pose(psi, t1, t2, t3):
    P = LAMP_PINS
    L1 = Vector((P['E'][0] - P['P1'][0], P['E'][1] - P['P1'][1], 0.0))
    L2 = Vector((P['J'][0] - P['Q1'][0], P['J'][1] - P['Q1'][1], 0.0))
    d1 = Matrix.Rotation(t1, 3, 'Z') @ L1 - L1
    d2 = Matrix.Rotation(t2, 3, 'Z') @ L2 - L2
    S = LAMP_PINS['S']
    return dict(sw_rot=(0.0, psi, 0.0), l_rot=(0.0, 0.0, t1), er_loc=Vector((d1.x, d1.y, 0.0)),
                u_rot=(0.0, 0.0, t2), hr_loc=Vector((d2.x, d2.y, 0.0)), hh_rot=(0.0, 0.0, t3))


def vid_lamp_motion(t_move, dur, t_on):
    """Half folded until t_move; over dur seconds (while it goes from wireframe to texture) the arm lifts smoothly
    into place, the lower arm first, then the upper one and the head, with no bounce; lights up at t_on."""
    if not LAMP:
        return
    P = LAMP_PINS
    base = {k: LAMP[k].location.copy() for k in ('l1', 'l2', 'u1', 'u2', 'er', 'hr', 'hh', 'sw')}
    st = LAMP_START
    f0, f1 = vid_f(t_move) - 1, vid_f(t_move + dur) + 1
    for f in [0] + list(range(f0, f1 + 1)):
        u = max((f - 1) / VID_FPS - t_move, 0.0) / dur
        us = _ease_io(u / 0.8)
        u1 = _ease_io(u / 0.8)
        u2 = _ease_io((u - 0.12) / 0.8)
        uh = _ease_io((u - 0.3) / 0.7)
        pf, hf = LAMP.get('final', (0.0, 0.0))
        pose = _lamp_pose(pf + st['psi'] * (1 - us), st['t1'] * (1 - u1), st['t2'] * (1 - u2), hf + st['t3'] * (1 - uh))
        for key, rot in (('sw', 'sw_rot'), ('l1', 'l_rot'), ('l2', 'l_rot'), ('u1', 'u_rot'), ('u2', 'u_rot'), ('hh', 'hh_rot')):
            o = LAMP[key]
            o.rotation_euler = pose[rot]
            o.keyframe_insert('rotation_euler', frame=f)
        for key, loc in (('er', 'er_loc'), ('hr', 'hr_loc')):
            o = LAMP[key]
            o.location = base[key] + pose[loc]
            o.keyframe_insert('location', frame=f)
    # switching on: the spot and the bulb
    li = LAMP.get('light')
    m = bpy.data.materials.get('dl_N')
    p = principled(m) if m else None
    em = p.inputs['Emission Strength'].default_value if p else 0.0
    fo = vid_f(t_on)
    for f, k in ((0, 0.0), (fo - 1, 0.0), (fo + 1, 0.55), (fo + 2, 0.25), (fo + 4, 1.0)):
        if li:
            li.data.energy = LAMP['energy'] * k
            li.data.keyframe_insert('energy', frame=f)
        if p:
            p.inputs['Emission Strength'].default_value = em * k
            p.inputs['Emission Strength'].keyframe_insert('default_value', frame=f)


# ------------------------------------------------------------------ the chair rolls in
def vid_chair_roll(t0, dur):
    r = bpy.data.objects.get('mandy_root')
    if not r:
        return
    end_loc, end_rot = r.location.copy(), r.rotation_euler.z
    start = end_loc + Vector((-1.85, -0.5, 0.0))           # comes in from the left, in front of the desk
    ctrl = end_loc + Vector((-0.8, -0.55, 0.0))
    for f in range(0, vid_f(t0 + dur) + 1):
        u = _ease_out(((f - 1) / VID_FPS - t0) / dur)
        a = (1 - u) ** 2 * start + 2 * (1 - u) * u * ctrl + u ** 2 * end_loc
        r.location = a
        r.rotation_euler.z = end_rot + math.radians(55) * (1 - u) ** 1.5 - math.radians(6) * math.sin(math.pi * u) * (1 - u)
        r.keyframe_insert('location', frame=f)
        r.keyframe_insert('rotation_euler', index=2, frame=f)
        if f < vid_f(t0) - 1:
            continue


# ------------------------------------------------------------------ screens, LEDs
def vid_power(objs, t_on, dur=0.9):
    for o in objs:
        _key(o, 'vid_on', 0, 0.0)
        _key(o, 'vid_on', vid_f(t_on), 0.0)
        _key(o, 'vid_on', vid_f(t_on + dur), 1.0)
        _vid_interp(o, 'LINEAR')


def vid_leds(t_on):
    m = bpy.data.materials.get('c_led_strip')
    if m:
        e = next((n for n in m.node_tree.nodes if n.type == 'EMISSION'), None)
        if e:
            v = e.inputs['Strength'].default_value
            for f, k in ((0, 0.0), (vid_f(t_on), 0.0), (vid_f(t_on + 0.6), 1.0)):
                e.inputs['Strength'].default_value = v * k
                e.inputs['Strength'].keyframe_insert('default_value', frame=f)
    for o in bpy.data.objects:
        if o.type == 'LIGHT' and o.name.startswith('al_light_sous'):
            v = o.data.energy
            for f, k in ((0, 0.0), (vid_f(t_on), 0.0), (vid_f(t_on + 0.6), 1.0)):
                o.data.energy = v * k
                o.data.keyframe_insert('energy', frame=f)


# ------------------------------------------------------------------ the whole schedule
VID_PLAN = [  # step, start (s), length (s), stage scale
    # 17/11: the steps overlap (the next one starts while the last pieces of the previous are still being coloured) so
    # the build flows faster without speeding the stages up; the cables come last, once everything else is there
    ('bureau', 1.0, 6.0, 0.85), ('rangements', 5.6, 6.0, 0.6), ('contenus', 10.2, 5.5, 0.55),
    ('ecrans', 14.2, 4.0, 0.8), ('poste', 17.2, 9.0, 1.0), ('lampe', 26.0, 4.2, 0.9), ('chaise', 30.5, 3.6, 1.0),
    ('papiers', 33.4, 5.0, 0.7), ('objets', 37.4, 4.0, 0.8), ('autour', 40.4, 4.5, 0.9), ('cables', 44.4, 5.0, 0.7),
]
# the desk set, piece by piece (offset from the step's start): the Mac Studio is modelled in the wide shot, then two close
# shots follow each other, the keyboard then the MacBook, whose screen wakes up with the monitors once it is there
VID_POSTE = (('deskmat', 0.0), ('macstudio', 0.2), ('mouse', 0.8), ('airpods', 1.2), ('keyboard', 1.8), ('macbook', 5.2))
VID_T = dict(leds=49.8, fin=57.4)


def vid_schedule_all(groups):
    times = {}
    for st, t0, L, sc in VID_PLAN:
        items = groups.get(st, [])
        if not items:
            continue
        if st == 'chaise':
            # it rolls in from the left in the wide shot and goes from wireframe to texture on the way
            k, objs = items[0]
            vid_prepare(objs)
            end = vid_schedule_piece(objs, t0, True, scale=dur_scale(L))
            vid_chair_roll(t0 - 0.1, L)
            times[k] = (t0, end)
            continue
        if st == 'lampe':
            # the books, then the lamp, half folded: its arm lifts while it is modelled, then it lights up
            lamp_items = [it for it in items if it[0].startswith('pst_lampeS')]
            books = [it for it in items if not it[0].startswith('pst_lampeS')]
            for i, (k, objs) in enumerate(books):
                vid_prepare(objs)
                times[k] = (t0 + i * 0.35, vid_schedule_piece(objs, t0 + i * 0.35, False, scale=sc))
            for k, objs in lamp_items:
                vid_prepare(objs)
                tl = t0 + 1.0
                end = vid_schedule_piece(objs, tl, True, scale=sc)
                times[k] = (tl, end)
                t_move, dur = tl + 0.4, 2.6
                VID_T['lampe_on'] = max(end, t_move + dur) + 0.2
                vid_lamp_motion(t_move, dur, VID_T['lampe_on'])
            continue
        if st == 'poste':
            for k, objs in items:
                off = next((o for n, o in VID_POSTE if n in k), 0.0)
                vid_prepare(objs)
                times[k] = (t0 + off, vid_schedule_piece(objs, t0 + off, vid_imported(objs[0]), scale=sc))
            continue
        n = len(items)
        d_piece = sum(VID_D.values()) * sc
        gap = 0.0 if n < 2 else max(0.03, min(1.1, (L - d_piece) / (n - 1)))
        bbs = {k: vid_bbox(objs) for k, objs in items}
        tm = {}
        for i, (k, objs) in enumerate(items):
            vid_prepare(objs)
            ts = t0 + i * gap
            imp = vid_imported(objs[0])
            # 18/11: a piece standing on another one of its step (the fan on its boxes) starts once its support is
            # modelled, so the build still climbs from the bottom up (an imported piece is modelled faster: the fan
            # was solid while its boxes were still in wireframe). Only in the step around the desk: elsewhere it would
            # retime the build the user approved (the trays, the papers, the cables...)
            sup = vid_support(k, bbs) if st == 'autour' else None
            if sup in tm:
                ts = max(ts, tm[sup] + 0.1 - VID_D['appear'] * sc)
                print('SUPPORT', st, k, 'on', sup, round(ts, 2), flush=True)
            tm[k] = ts + (VID_D['appear'] + (0.45 if imp else VID_D['model'])) * sc
            times[k] = (ts, vid_schedule_piece(objs, ts, imp, scale=sc))
    # the screens wake up once the MacBook is there (the Mac Studio is already), the LEDs at the end
    mb = next((v for k, v in times.items() if 'macbook' in k), None)
    VID_T['ecrans_on'] = (mb[1] + 0.25) if mb else 25.0
    screens = [o for o in bpy.data.objects if o.type == 'MESH' and not o.get('vid_twin')
               and any(m and m.name.startswith(('screen_', 'mbp_display')) for m in o.data.materials)]
    vid_power(screens, VID_T['ecrans_on'])
    vid_leds(VID_T['leds'])
    vid_bgl(times)
    return times


def vid_support(k, bbs):
    """The piece of the same step that piece k stands on: its bottom on that piece's top, its centre over it."""
    mn, mx = bbs[k]
    if mn.z < 0.05:
        return None
    c = (mn + mx) / 2
    for j, (a, b) in bbs.items():
        if j != k and abs(mn.z - b.z) < 0.04 and a.x - 0.02 <= c.x <= b.x + 0.02 and a.y - 0.02 <= c.y <= b.y + 0.02:
            return j
    return None


def vid_bgl(times):
    """18/11: the low background light behind the desk (bgl, aimed at the wall) lit the empty grid at the start: a
    bright patch with a hard edge. Off until the close shot of the feet ends; back in the wide shot, the desk top
    hides the floor it lights."""
    li = bpy.data.objects.get('bgl')
    ks = [k for k in times if k.startswith(('D_leg', 'foot'))]
    if not li or not ks:
        return
    f = vid_f(max(times[k][1] for k in ks) + 0.5)    # the cut back to the wide shot (main.py, vid_cuts: 'pieds')
    v = li.data.energy
    for fr, k in ((0, 0.0), (f - 1, 0.0), (f, 1.0)):
        li.data.energy = v * k
        li.data.keyframe_insert('energy', frame=fr)
    VID_T['bgl'] = (f, v)


def dur_scale(L):
    return min(1.0, L / sum(VID_D.values()))
