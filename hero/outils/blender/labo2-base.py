# Underground lab decor prototypes (hero section).
# blender -b --factory-startup -P labo.py -- piste=A shots=master,table res=960 samples=64 out=<dir> [fog=1] [save=1]
import bpy, bmesh, math, random, os, sys, glob
from mathutils import Vector, Matrix, Euler

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OPT = dict(a.split('=', 1) for a in argv if '=' in a)
PISTE = OPT.get('piste', 'A')
SHOTS = OPT.get('shots', 'master').split(',')
RES = int(OPT.get('res', 960))
SAMPLES = int(OPT.get('samples', 64))
OUT = OPT.get('out', '/tmp/labo')
FOG = OPT.get('fog', '1') == '1'
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.normpath(os.path.join(HERE, '..', 'assets', 'polyhaven'))
TEXG = os.path.normpath(os.path.join(HERE, '..', 'textures'))
TEX2 = os.path.normpath(os.path.join(HERE, '..', 'textures-v2'))
R = random.Random(4)
rad = math.radians

bpy.ops.wm.read_factory_settings(use_empty=True)
SC = bpy.context.scene
ROOT = SC.collection


def coll(name, parent=None):
    c = bpy.data.collections.new(name)
    (parent or ROOT).children.link(c)
    return c


C_LIB = coll('LIB')
C_ARCH = coll('ARCH')
C_PROPS = coll('PROPS')
C_LIGHT = coll('LIGHTS')
C_FX = coll('FX')
C_CEIL = coll('CEILING')
bpy.context.view_layer.layer_collection.children['LIB'].exclude = True
CUR = [C_PROPS]

# ------------------------------------------------------------------ materials
IMGS = {}


def img(path, noncolor=False):
    key = (path, noncolor)
    if key not in IMGS:
        im = bpy.data.images.load(path, check_existing=True)
        if noncolor:
            im.colorspace_settings.name = 'Non-Color'
        IMGS[key] = im
    return IMGS[key]


def principled(mat):
    return next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')


def new_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    return m


def mat_color(name, color, rough=0.6, metal=0.0, spec=0.5):
    m = new_mat(name)
    p = principled(m)
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    return m


def mat_emit(name, color, strength):
    m = new_mat(name)
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type == 'BSDF_PRINCIPLED':
            nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs['Color'].default_value = (*color, 1)
    e.inputs['Strength'].default_value = strength
    nt.links.new(e.outputs[0], out.inputs['Surface'])
    return m


def mat_pbr(name, tex, scale=1.0, tint=(1, 1, 1), dark=1.0, rough_add=0.0, metal=None, wet=False, bump=1.0):
    d = os.path.join(ASSETS, 'textures', tex)
    m = new_mat(name)
    nt = m.node_tree
    p = principled(m)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (1 / scale, 1 / scale, 1 / scale)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])

    def tex_node(fname, nc):
        t = nt.nodes.new('ShaderNodeTexImage')
        t.image = img(os.path.join(d, fname), nc)
        t.projection = 'BOX'
        t.projection_blend = 0.25
        nt.links.new(mp.outputs['Vector'], t.inputs['Vector'])
        return t

    diff = tex_node('diff.jpg', False)
    mul = nt.nodes.new('ShaderNodeMix')
    mul.data_type = 'RGBA'
    mul.blend_type = 'MULTIPLY'
    mul.inputs['Factor'].default_value = 1.0
    mul.inputs[7].default_value = (tint[0] * dark, tint[1] * dark, tint[2] * dark, 1)
    nt.links.new(diff.outputs['Color'], mul.inputs[6])
    base_out = mul.outputs[2]
    rough = tex_node('rough.jpg', True)
    radd = nt.nodes.new('ShaderNodeMath')
    radd.operation = 'ADD'
    radd.use_clamp = True
    radd.inputs[1].default_value = rough_add
    nt.links.new(rough.outputs['Color'], radd.inputs[0])
    rough_out = radd.outputs[0]
    if wet:
        noise = nt.nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 0.18
        noise.inputs['Detail'].default_value = 6
        noise.inputs['Roughness'].default_value = 0.6
        nt.links.new(tc.outputs['Object'], noise.inputs['Vector'])
        ramp = nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = 0.52
        ramp.color_ramp.elements[1].position = 0.58
        nt.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
        mr = nt.nodes.new('ShaderNodeMix')
        mr.data_type = 'FLOAT'
        nt.links.new(ramp.outputs['Color'], mr.inputs['Factor'])
        nt.links.new(rough_out, mr.inputs[2])
        mr.inputs[3].default_value = 0.03
        rough_out = mr.outputs[0]
        mc = nt.nodes.new('ShaderNodeMix')
        mc.data_type = 'RGBA'
        nt.links.new(ramp.outputs['Color'], mc.inputs['Factor'])
        nt.links.new(base_out, mc.inputs[6])
        dk = nt.nodes.new('ShaderNodeMix')
        dk.data_type = 'RGBA'
        dk.blend_type = 'MULTIPLY'
        dk.inputs['Factor'].default_value = 1
        nt.links.new(base_out, dk.inputs[6])
        dk.inputs[7].default_value = (0.45, 0.47, 0.5, 1)
        nt.links.new(dk.outputs[2], mc.inputs[7])
        base_out = mc.outputs[2]
    nt.links.new(base_out, p.inputs['Base Color'])
    nt.links.new(rough_out, p.inputs['Roughness'])
    nor = tex_node('nor.jpg', True)
    nm = nt.nodes.new('ShaderNodeNormalMap')
    nm.inputs['Strength'].default_value = bump
    nt.links.new(nor.outputs['Color'], nm.inputs['Color'])
    nt.links.new(nm.outputs['Normal'], p.inputs['Normal'])
    if metal is not None:
        p.inputs['Metallic'].default_value = metal
    return m


def mat_paper(path, rough=0.78):
    key = 'paper_' + os.path.basename(path)
    if key in bpy.data.materials:
        return bpy.data.materials[key]
    m = new_mat(key)
    nt = m.node_tree
    p = principled(m)
    t = nt.nodes.new('ShaderNodeTexImage')
    t.image = img(path)
    nt.links.new(t.outputs['Color'], p.inputs['Base Color'])
    p.inputs['Roughness'].default_value = rough
    return m


def mat_screen(path, strength=3.0):
    key = 'screen_' + os.path.basename(path)
    if key in bpy.data.materials:
        return bpy.data.materials[key]
    m = new_mat(key)
    nt = m.node_tree
    p = principled(m)
    t = nt.nodes.new('ShaderNodeTexImage')
    t.image = img(path)
    nt.links.new(t.outputs['Color'], p.inputs['Base Color'])
    nt.links.new(t.outputs['Color'], p.inputs['Emission Color'])
    p.inputs['Emission Strength'].default_value = strength
    p.inputs['Roughness'].default_value = 0.15
    return m


# ------------------------------------------------------------------ mesh helpers
def link(o, c=None):
    (c or CUR[0]).objects.link(o)
    return o


def box(name, size, loc, mat=None, rot=(0, 0, 0), bevel=0.0, c=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    o.location = loc
    o.rotation_euler = rot
    if mat:
        me.materials.append(mat)
    if bevel:
        b = o.modifiers.new('bev', 'BEVEL')
        b.width = bevel
        b.segments = 2
        b.limit_method = 'ANGLE'
    return link(o, c)


def cyl(name, r, depth, loc, mat=None, rot=(0, 0, 0), verts=32, caps=True, c=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False, segments=verts, radius1=r, radius2=r, depth=depth)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for f in me.polygons:
        f.use_smooth = True
    o = bpy.data.objects.new(name, me)
    o.location = loc
    o.rotation_euler = rot
    if mat:
        me.materials.append(mat)
    return link(o, c)


def tube_between(name, a, b, r, mat, verts=12, c=None):
    a, b = Vector(a), Vector(b)
    d = b - a
    o = cyl(name, r, d.length, (a + b) / 2, mat, verts=verts, c=c)
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    return o


def plane(name, w, h, loc, mat=None, rot=(0, 0, 0), c=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata([(-w / 2, -h / 2, 0), (w / 2, -h / 2, 0), (w / 2, h / 2, 0), (-w / 2, h / 2, 0)], [], [(0, 1, 2, 3)])
    me.uv_layers.new()
    for i, uv in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        me.uv_layers[0].data[i].uv = uv
    o = bpy.data.objects.new(name, me)
    o.location = loc
    o.rotation_euler = rot
    if mat:
        me.materials.append(mat)
    return link(o, c)


def curve_cable(name, pts, r=0.012, mat=None, c=None):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = r
    cu.bevel_resolution = 3
    sp = cu.splines.new('BEZIER')
    sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, cu)
    if mat:
        cu.materials.append(mat)
    return link(o, c)


# ------------------------------------------------------------------ asset library (collection instances)
LIB = {}


def lib(aid, keep=None):
    key = (aid, tuple(keep) if keep else None)
    if key in LIB:
        return LIB[key]
    path = glob.glob(os.path.join(ASSETS, 'models', aid, '*.gltf'))[0]
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    for o in new:
        if o.parent:
            mw = o.matrix_world.copy()
            o.parent = None
            o.matrix_world = mw
    meshes = [o for o in new if o.type == 'MESH' and (keep is None or any(o.name.split('.')[0] == k or o.name.startswith(k) for k in keep))]
    for o in new:
        if o not in meshes:
            bpy.data.objects.remove(o, do_unlink=True)
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(cn) for o in meshes for cn in o.bound_box]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    off = Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))
    cl = bpy.data.collections.new('L_' + aid + ('_' + '_'.join(keep) if keep else ''))
    C_LIB.children.link(cl)
    for o in meshes:
        for uc in list(o.users_collection):
            uc.objects.unlink(o)
        cl.objects.link(o)
        o.matrix_world.translation -= off
    LIB[key] = (cl, mx - mn)
    return LIB[key]


def put(aid, loc, rz=0.0, s=1.0, keep=None, rx=0.0, ry=0.0, c=None):
    cl, dims = lib(aid, keep)
    e = bpy.data.objects.new(aid, None)
    e.instance_type = 'COLLECTION'
    e.instance_collection = cl
    e.location = loc
    e.rotation_euler = (rx, ry, rz)
    e.scale = (s, s, s)
    link(e, c)
    return e, dims * s


class Frame:
    """Local frame of a zone: origin + rotation around Z."""

    def __init__(self, x, y, z=0.0, rot=0.0):
        self.o = Vector((x, y, z))
        self.r = rot

    def p(self, lx, ly, lz=0.0):
        c, s = math.cos(self.r), math.sin(self.r)
        return self.o + Vector((lx * c - ly * s, lx * s + ly * c, lz))

    def put(self, aid, lx, ly, lz=0.0, rz=0.0, **kw):
        return put(aid, self.p(lx, ly, lz), self.r + rz, **kw)


# ------------------------------------------------------------------ the fan
def ring(name, r_in, r_out, depth, loc, mat, verts=96, c=None):
    bm = bmesh.new()
    vs = []
    for z in (-depth / 2, depth / 2):
        for r in (r_in, r_out):
            vs.append([bm.verts.new((r * math.cos(2 * math.pi * i / verts), z, r * math.sin(2 * math.pi * i / verts))) for i in range(verts)])
    a_in, a_out, b_in, b_out = vs
    for i in range(verts):
        j = (i + 1) % verts
        bm.faces.new((a_in[i], a_in[j], a_out[j], a_out[i]))
        bm.faces.new((b_in[i], b_out[i], b_out[j], b_in[j]))
        bm.faces.new((a_out[i], a_out[j], b_out[j], b_out[i]))
        bm.faces.new((a_in[i], b_in[i], b_in[j], a_in[j]))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for f in me.polygons:
        f.use_smooth = True
    o = bpy.data.objects.new(name, me)
    o.location = loc
    me.materials.append(mat)
    return link(o, c)


def blade_mesh(name, r0, r1, w0, w1, p0, p1, n=14):
    bm = bmesh.new()
    rows = []
    for i in range(n + 1):
        t = i / n
        r = r0 + (r1 - r0) * t
        w = w0 + (w1 - w0) * (t ** 0.7)
        if t > 0.86:
            w *= 1 - ((t - 0.86) / 0.14) ** 2 * 0.5
        p = rad(p0 + (p1 - p0) * t)
        row = []
        for s in (-0.5, -0.17, 0.17, 0.5):
            camber = 0.035 * w * (1 - (2 * s) ** 2)
            z = s * w * math.cos(p)
            y = s * w * math.sin(p) - camber
            row.append(bm.verts.new((r, y, z)))
        rows.append(row)
    for i in range(n):
        for k in range(3):
            bm.faces.new((rows[i][k], rows[i + 1][k], rows[i + 1][k + 1], rows[i][k + 1]))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for f in me.polygons:
        f.use_smooth = True
    return me


def build_fan(center, R_open, depth=1.1, n_blades=7, wall_mat=None, angle=0.0):
    cx, cy, cz = center
    parts = []
    # housing tube + front flange + back ring
    parts.append(ring('fan_tube', R_open - 0.02, R_open + 0.16, depth, (cx, cy + depth / 2 - 0.25, cz), M['green']))
    parts.append(ring('fan_flange', R_open - 0.06, R_open + 0.55, 0.16, (cx, cy - 0.3, cz), M['green']))
    parts.append(ring('fan_flange_lip', R_open + 0.45, R_open + 0.6, 0.26, (cx, cy - 0.32, cz), M['steel']))
    for i in range(36):
        a = 2 * math.pi * i / 36
        r = R_open + 0.32
        parts.append(cyl('bolt', 0.035, 0.08, (cx + r * math.cos(a), cy - 0.41, cz + r * math.sin(a)), M['plate'], rot=(rad(90), 0, 0), verts=8))
    # hub, motor, struts (behind the blades)
    by = cy + 0.25
    parts.append(cyl('fan_hub', 0.5, 0.5, (cx, by, cz), M['steel'], rot=(rad(90), 0, 0), verts=48))
    nose = bpy.data.objects.new('fan_nose', bpy.data.meshes.new('nose'))
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=0.5)
    for v in bm.verts:
        if v.co.y > 0:
            v.co.y *= 0.2
        else:
            v.co.y *= 0.55
    bm.to_mesh(nose.data)
    bm.free()
    for f in nose.data.polygons:
        f.use_smooth = True
    nose.location = (cx, by - 0.25, cz)
    nose.data.materials.append(M['steel'])
    link(nose)
    parts.append(cyl('fan_motor', 0.62, 1.1, (cx, cy + 0.95, cz), M['green'], rot=(rad(90), 0, 0), verts=48))
    for k in range(4):
        a = rad(45 + 90 * k)
        tube_between('strut', (cx + 0.5 * math.cos(a), cy + 0.95, cz + 0.5 * math.sin(a)),
                     (cx + (R_open + 0.05) * math.cos(a), cy + 0.95, cz + (R_open + 0.05) * math.sin(a)), 0.07, M['steel'], verts=10)
    # blades
    me = blade_mesh('blade', 0.42, R_open - 0.12, 0.55, 1.35, 42, 14)
    for k in range(n_blades):
        o = bpy.data.objects.new('blade', me)
        o.location = (cx, by - 0.02, cz)
        o.rotation_euler = (0, -(angle + 2 * math.pi * k / n_blades), 0)
        sm = o.modifiers.new('solid', 'SOLIDIFY')
        sm.thickness = 0.03
        bv = o.modifiers.new('bev', 'BEVEL')
        bv.width = 0.008
        bv.segments = 2
        me.materials.append(M['blade']) if not me.materials else None
        link(o)
    # front guard: rings + spokes, joined into one mesh
    gy = cy - 0.55
    bm = bmesh.new()
    for r in [0.55 + 0.33 * i for i in range(int((R_open - 0.5) / 0.33) + 1)] + [R_open + 0.02]:
        bmesh.ops.create_circle(bm, cap_ends=False, segments=128, radius=r)
    me_g = bpy.data.meshes.new('guard_rings')
    bm.to_mesh(me_g)
    bm.free()
    g = bpy.data.objects.new('guard_rings', me_g)
    g.location = (cx, gy, cz)
    g.rotation_euler = (rad(90), 0, 0)
    sk = g.modifiers.new('skin', 'SKIN')
    for v in me_g.skin_vertices[0].data:
        v.radius = (0.011, 0.011)
    sub = g.modifiers.new('sub', 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 1
    me_g.materials.append(M['wire'])
    link(g)
    for k in range(24):
        a = 2 * math.pi * k / 24
        tube_between('spoke', (cx + 0.55 * math.cos(a), gy, cz + 0.55 * math.sin(a)),
                     (cx + R_open * math.cos(a), gy + 0.02, cz + R_open * math.sin(a)), 0.014, M['wire'], verts=6)
    tube_between('guard_bar_h', (cx - R_open, gy - 0.02, cz), (cx + R_open, gy - 0.02, cz), 0.03, M['wire'], verts=8)
    tube_between('guard_bar_v', (cx, gy - 0.02, cz - R_open), (cx, gy - 0.02, cz + R_open), 0.03, M['wire'], verts=8)


def light_box(center, R_open, wall_back_y, power=1.0, target=None):
    """Bright box behind the fan: emissive back plane + one sharp spot aimed into the room."""
    cx, cy, cz = center
    CUR[0] = C_FX
    plane('hot_plane', R_open * 2.6, R_open * 2.6, (cx, wall_back_y + 2.2, cz), M['white_hot'], rot=(rad(90), 0, 0))
    for s in (-1, 1):
        box('lb_side', (0.1, 2.4, R_open * 3.2), (cx + s * R_open * 1.6, wall_back_y + 1.1, cz), M['black'])
    box('lb_top', (R_open * 3.2, 2.4, 0.1), (cx, wall_back_y + 1.1, cz + R_open * 1.6), M['black'])
    box('lb_bot', (R_open * 3.2, 2.4, 0.1), (cx, wall_back_y + 1.1, cz - R_open * 1.6), M['black'])
    CUR[0] = C_PROPS
    ld = bpy.data.lights.new('fan_spot', 'SPOT')
    ld.energy = float(OPT.get('fanw', 500000)) * power
    ld.color = (0.9, 0.95, 1.0)
    ld.spot_size = rad(float(OPT.get('cone', 54)))
    ld.spot_blend = 0.75
    ld.shadow_soft_size = 0.3
    lo = bpy.data.objects.new('fan_spot', ld)
    lo.location = (cx, wall_back_y + 1.9, cz + 0.8)
    link(lo, C_LIGHT)
    aim(lo, target or (cx, wall_back_y - 10, 0))
    return lo


def aim(o, target):
    d = Vector(target) - o.location
    o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def add_light(kind, name, loc, energy, color, target=None, size=0.1, spot=60, blend=0.5, c=None):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = energy
    ld.color = color
    if kind == 'SPOT':
        ld.spot_size = rad(spot)
        ld.spot_blend = blend
        ld.shadow_soft_size = size
    elif kind == 'POINT':
        ld.shadow_soft_size = size
    elif kind == 'AREA':
        ld.size = size
    o = bpy.data.objects.new(name, ld)
    o.location = loc
    link(o, c or C_LIGHT)
    if target:
        aim(o, target)
    return o


def fog_volume(mn, mx, density=0.016, color=(0.85, 0.9, 0.95)):
    m = new_mat('fog')
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type == 'BSDF_PRINCIPLED':
            nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
    v = nt.nodes.new('ShaderNodeVolumePrincipled')
    v.inputs['Color'].default_value = (*color, 1)
    v.inputs['Anisotropy'].default_value = 0.55
    noise = nt.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 0.35
    noise.inputs['Detail'].default_value = 3
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    nt.links.new(geo.outputs['Position'], noise.inputs['Vector'])
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['To Min'].default_value = density * 0.4
    mr.inputs['To Max'].default_value = density * 1.6
    nt.links.new(noise.outputs['Fac'], mr.inputs['Value'])
    # denser near the floor
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(geo.outputs['Position'], sep.inputs[0])
    fl = nt.nodes.new('ShaderNodeMapRange')
    fl.inputs['From Min'].default_value = 0
    fl.inputs['From Max'].default_value = 2.5
    fl.inputs['To Min'].default_value = 1.8
    fl.inputs['To Max'].default_value = 1.0
    nt.links.new(sep.outputs['Z'], fl.inputs['Value'])
    mul = nt.nodes.new('ShaderNodeMath')
    mul.operation = 'MULTIPLY'
    nt.links.new(mr.outputs[0], mul.inputs[0])
    nt.links.new(fl.outputs[0], mul.inputs[1])
    nt.links.new(mul.outputs[0], v.inputs['Density'])
    nt.links.new(v.outputs['Volume'], out.inputs['Volume'])
    size = [mx[i] - mn[i] for i in range(3)]
    o = box('fog', size, [(mn[i] + mx[i]) / 2 for i in range(3)], m, c=C_FX)
    o.location.z = mn[2] + size[2] / 2
    o.visible_shadow = False
    return o


# ------------------------------------------------------------------ architecture kits
def wall_with_hole(name, x0, x1, y0, y1, z0, z1, hole_c=None, hole_r=0.0, mat=None):
    o = box(name, (x1 - x0, y1 - y0, z1 - z0), ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), mat, c=C_ARCH)
    if hole_r:
        cut = cyl(name + '_cut', hole_r, (y1 - y0) + 1, (hole_c[0], (y0 + y1) / 2, hole_c[2]), None, rot=(rad(90), 0, 0), verts=128, c=C_FX)
        cut.hide_render = True
        cut.display_type = 'WIRE'
        b = o.modifiers.new('hole', 'BOOLEAN')
        b.object = cut
        b.operation = 'DIFFERENCE'
        b.solver = 'EXACT'
    return o


def i_beam(name, x0, x1, y, z_top, mat):
    box(name + '_t', (x1 - x0, 0.3, 0.03), ((x0 + x1) / 2, y, z_top - 0.015), mat, c=C_CEIL)
    box(name + '_w', (x1 - x0, 0.03, 0.42), ((x0 + x1) / 2, y, z_top - 0.24), mat, c=C_CEIL)
    box(name + '_b', (x1 - x0, 0.3, 0.03), ((x0 + x1) / 2, y, z_top - 0.465), mat, c=C_CEIL)


def railing(a, b, h=1.05, post=1.3, c=None):
    a, b = Vector(a), Vector(b)
    L = (b - a).length
    n = max(1, int(L / post))
    for i in range(n + 1):
        p = a + (b - a) * (i / n)
        tube_between('post', p, p + Vector((0, 0, h)), 0.025, M['steel'], verts=8, c=c)
    for zz in (h, h * 0.5):
        tube_between('rail', a + Vector((0, 0, zz)), b + Vector((0, 0, zz)), 0.024, M['steel'], verts=8, c=c)
    box('kick', ((b - a).length if abs((b - a).x) > abs((b - a).y) else 0.01, 0.01 if abs((b - a).x) > abs((b - a).y) else (b - a).length, 0.1), (a + b) / 2 + Vector((0, 0, 0.05)), M['steel'], c=c)


def stairs(x0, x1, y_top, z_top, run_dir=-1, steps=8, c=None):
    rise = z_top / steps
    run = 0.27
    for i in range(steps):
        z = z_top - (i + 1) * rise
        y = y_top + run_dir * (i + 0.5) * run
        box('step', (x1 - x0, run, 0.04), ((x0 + x1) / 2, y, z + rise - 0.02), M['grate'], c=c)
    for x in (x0, x1):
        a = Vector((x, y_top, z_top))
        b = Vector((x, y_top + run_dir * steps * run, 0))
        tube_between('stringer', a, b, 0.05, M['steel'], verts=6, c=c)
        tube_between('hand', a + Vector((0, 0, 1.0)), b + Vector((0, 0, 1.0)), 0.022, M['steel'], verts=8, c=c)
        tube_between('hpost', b, b + Vector((0, 0, 1.0)), 0.022, M['steel'], verts=8, c=c)


def leds(points):
    for p in points:
        o = bpy.data.objects.new('led', bpy.data.meshes.new('led'))
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=0.035)
        bm.to_mesh(o.data)
        bm.free()
        o.data.materials.append(M['led_red'])
        o.location = p
        link(o, C_FX)


def fluo(loc, rot, on=True, c=None):
    e, _ = put('mounted_fluorescent_lights', loc, keep=['mounted_fluorescent_lights_a'], rx=rot[0], ry=rot[1], rz=rot[2], c=c)
    if on:
        t = cyl('fluo_glow', 0.014, 0.86, loc, M['tube_cold'], verts=10, c=C_FX)
        t.rotation_euler = rot
        t.rotation_euler.rotate(Euler((0, rad(90), 0)))
        t.location = Vector(loc) + Vector((0, 0, -0.012))
    return e


# ------------------------------------------------------------------ zone kits
PAPERS = sorted(glob.glob(os.path.join(TEXG, 'plan-*.jpg'))) + sorted(glob.glob(os.path.join(TEXG, 'maquette-*.jpg'))) + \
    sorted(glob.glob(os.path.join(TEXG, 'carte-*.jpg'))) + sorted(glob.glob(os.path.join(TEXG, 'croquis-*.jpg'))) + \
    [os.path.join(TEXG, 'listing-1.jpg'), os.path.join(TEXG, 'dossier-kraft.jpg')]
POSTITS = sorted(glob.glob(os.path.join(TEXG, 'postit-*.jpg')))
PHOTOS = sorted(glob.glob(os.path.join(TEXG, 'photo-*.jpg')))


def sheet_world(loc, rz, w, path, curl=0.0, rx=0.0):
    im = img(path)
    h = w * im.size[1] / im.size[0]
    o = plane('sheet', w, h, loc, mat_paper(path), rot=(rx, 0, rz))
    if curl:
        me = o.data
        sub = o.modifiers.new('sub', 'SUBSURF')
        sub.subdivision_type = 'SIMPLE'
        sub.levels = sub.render_levels = 4
        sd = o.modifiers.new('bend', 'SIMPLE_DEFORM')
        sd.deform_method = 'BEND'
        sd.angle = curl
        sd.deform_axis = 'X'
    return o


# ------------------------------------------------------------------ render
def setup_render():
    try:
        SC.render.engine = 'CYCLES'
    except TypeError:
        pass
    prefs = bpy.context.preferences.addons['cycles'].preferences
    try:
        prefs.compute_device_type = 'METAL'
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
        SC.cycles.device = 'GPU'
    except Exception as e:
        print('GPU indisponible', e)
    SC.cycles.samples = SAMPLES
    SC.cycles.use_denoising = True
    SC.cycles.max_bounces = 8
    SC.cycles.diffuse_bounces = 3
    SC.cycles.glossy_bounces = 3
    SC.cycles.transmission_bounces = 4
    SC.cycles.volume_bounces = 1
    SC.cycles.transparent_max_bounces = 16
    SC.cycles.volume_step_rate = 1.5
    SC.cycles.volume_max_steps = 256
    SC.cycles.caustics_reflective = False
    SC.cycles.caustics_refractive = False
    SC.cycles.blur_glossy = 1.0
    SC.cycles.sample_clamp_indirect = 6.0
    SC.render.resolution_x = RES
    SC.render.resolution_y = int(RES * 9 / 16)
    SC.render.resolution_percentage = 100
    try:
        SC.view_settings.view_transform = 'AgX'
    except TypeError:
        pass
    for lk in ('AgX - Medium High Contrast', 'Medium High Contrast'):
        try:
            SC.view_settings.look = lk
            break
        except TypeError:
            continue
    SC.view_settings.exposure = float(OPT.get('exposure', 0.0))
    SC.render.image_settings.file_format = 'PNG'
    w = bpy.data.worlds.new('w')
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs['Color'].default_value = (0.004, 0.005, 0.007, 1)
    bg.inputs['Strength'].default_value = 1.0
    SC.world = w


def make_camera(spec, name):
    cd = bpy.data.cameras.new(name)
    co = bpy.data.objects.new(name, cd)
    ROOT.objects.link(co)
    co.location = spec['cam']
    aim(co, spec['target'])
    cd.sensor_width = 36
    cd.clip_end = 200
    if spec.get('ortho'):
        cd.type = 'ORTHO'
        cd.ortho_scale = spec['scale']
    else:
        cd.lens = spec['lens']
        cd.dof.use_dof = True
        cd.dof.aperture_fstop = spec['fstop']
        cd.dof.focus_distance = spec['focus'] or (Vector(spec['target']) - Vector(spec['cam'])).length
    return co


def compositor():
    SC.use_nodes = True
    nt = SC.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    rl = nt.nodes.new('CompositorNodeRLayers')
    gl = nt.nodes.new('CompositorNodeGlare')
    gl.glare_type = 'FOG_GLOW'
    try:
        gl.quality = 'HIGH'
        gl.mix = -0.72
        gl.threshold = 1.2
        gl.size = 8
    except Exception as e:
        print('glare opts', e)
    ld = nt.nodes.new('CompositorNodeLensdist')
    try:
        ld.inputs['Dispersion'].default_value = 0.012
        ld.inputs['Distortion'].default_value = -0.008
    except Exception as e:
        print('lens', e)
    comp = nt.nodes.new('CompositorNodeComposite')
    nt.links.new(rl.outputs['Image'], gl.inputs['Image'])
    nt.links.new(gl.outputs['Image'], ld.inputs['Image'])
    nt.links.new(ld.outputs['Image'], comp.inputs['Image'])


def apply_state(state):
    """0 = power off (only red LEDs + faint daylight behind the fan), 1 = tubes and lamps on, fan stopped, 2 = everything on."""
    if state >= 2:
        return
    fan = bpy.data.objects.get('fan_spot')
    hot = bpy.data.materials.get('white_hot')
    e = next(n for n in hot.node_tree.nodes if n.type == 'EMISSION')
    if state == 0:
        e.inputs['Strength'].default_value = 0.35
        if fan:
            fan.data.energy *= 0.03
        for o in bpy.data.objects:
            if o.type == 'LIGHT' and o.name not in ('fan_spot',):
                o.hide_render = True
        for m in bpy.data.materials:
            if m.name.startswith(('screen_', 'tube_cold', 'grow', 'bulb')) or m.name.startswith('led_') and m.name != 'led_red':
                for n in m.node_tree.nodes:
                    if n.type == 'EMISSION':
                        n.inputs['Strength'].default_value = 0.0
                    if n.type == 'BSDF_PRINCIPLED':
                        n.inputs['Emission Strength'].default_value = 0.0
    elif state == 1:
        e.inputs['Strength'].default_value = 1.2
        if fan:
            fan.data.energy *= 0.12


