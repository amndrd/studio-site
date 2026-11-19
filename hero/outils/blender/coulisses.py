# ================================================================== behind the scenes: captures of the Blender scene (17/11)
# Retained 17/11: piste A (the Blender window as it is) and piste C (the same shot from wireframe to render, without
# interface), for the six views below, in 16:9 (site) and 4:5 (Instagram). Piste B (window on a backdrop with captions)
# went to the Trash; no text is added on any image.
# Runs in a Blender WITH its interface (a second instance; the user's own Blender is never touched), on the complete desk
# scene hero/bureau/scene/bureau-complet.blend, driven by a timer: no click needed, the window closes itself at the end.
#   job=ui  : screenshots of the whole window (screen.screenshot), for each view: wireframe, clay, material preview and
#             rendered shading in the Layout workspace (an object of the view selected, its properties shown; nothing
#             selected in the rendered one, the render settings shown), then the Shading workspace on the material of
#             that object. Extras (empties, lights, cameras), 3D cursor and floor grid hidden; no file path ever shown
#             (it holds the user's name). The user view's lens is 2 x the camera lens (zoom factor of the user view).
#   job=net : the same views from cameras, without interface: wireframe, clay, material preview (render.opengl) and the
#             final Cycles render.
# The rendered viewport and the material preview are captured once they are stable (two successive captures agree;
# EEVEE never settles completely, so its wait is capped).
# Nothing is saved: the scene file stays as it is (the session ends with os._exit).
# usage (see rendus-coulisses.sh):
#   Blender --factory-startup <scene.blend> --window-geometry 0 0 <w> <h> --python coulisses.py -- job=ui|net format=169|45 out=<dir> [vues=a,b]
import bpy, os, sys, time, traceback
import numpy as np
from mathutils import Vector, Matrix

ARGV = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OPT = dict(a.split('=', 1) for a in ARGV if '=' in a)
OUT = OPT['out']
JOB = OPT.get('job', 'ui')
FMT = OPT.get('format', '169')
os.makedirs(OUT, exist_ok=True)
LOG = open(os.path.join(OUT, f'log-{JOB}-{FMT}.txt'), 'w')

# the six views: for each, the 16:9 camera and the 4:5 one (position, target, lens, image up)
VUES = {
    'ensemble': {'169': dict(cam=(-1.45, -4.4, 2.0), target=(0.45, 0.05, 0.6), lens=33),
                 '45': dict(cam=(-2.75, -2.85, 2.2), target=(0.0, 0.05, 0.6), lens=34)},
    'poste': {'169': dict(cam=(-1.75, -2.3, 1.62), target=(0.12, 0.12, 0.98), lens=30),
              '45': dict(cam=(-1.6, -2.45, 1.5), target=(0.05, 0.05, 0.86), lens=30)},
    'arriere': {'169': dict(cam=(0.75, 2.05, 1.3), target=(0.25, 0.38, 0.72), lens=28),
                '45': dict(cam=(0.4, 1.85, 1.45), target=(0.1, 0.32, 0.7), lens=28)},
    'dessus': {'169': dict(cam=(0.05, 0.0, 3.55), target=(0.05, 0.02, 0.74), lens=35, up=(0, 1, 0)),
               '45': dict(cam=(-0.45, 0.02, 2.75), target=(-0.45, 0.02, 0.74), lens=32, up=(-1, 0, 0))},
    'lampe': {'169': dict(cam=(-1.95, -0.95, 1.3), target=(-0.98, 0.1, 1.0), lens=42),
              '45': dict(cam=(-1.8, -1.05, 1.25), target=(-1.0, 0.1, 1.02), lens=40)},
    'cables': {'169': dict(cam=(1.5, 1.15, 0.75), target=(1.0, 0.25, 0.2), lens=30),
               '45': dict(cam=(1.4, 1.05, 0.85), target=(1.02, 0.25, 0.25), lens=28)},
}
ORDRE = ['ensemble', 'poste', 'arriere', 'dessus', 'lampe', 'cables']
# per view: the selection in the interface (names, or mat:<material>), its active object, the properties tab, and the
# selection for the Shading workspace (whose active object's material is shown in the node editor)
SEL = {
    'ensemble': (['root:mandy_root'], 'Box1578967125', 'OBJECT', ['root:mandy_root']),   # the chair, whole in the frame
    'poste': (['mat:macstudio_alu'], None, 'MATERIAL', ['mat:macstudio_alu']),
    'arriere': (['cb_ventilo'], 'cb_ventilo', 'DATA', ['cb_ventilo']),
    'dessus': (['mon_screen_left'], 'mon_screen_left', 'MATERIAL', ['mon_screen_left']),
    'lampe': (['mat:dl_N'], None, 'MATERIAL', ['mat:dl_N']),
    'cables': (['cb_'], 'cb_ecran_right_alim', 'DATA', ['mat:cb_gaine_noire']),
}
STAGES = [('1-fil-de-fer', 'WIREFRAME'), ('2-argile', 'SOLID'), ('3-materiaux', 'MATERIAL'), ('4-rendu', 'RENDERED')]


def log(*a):
    print(*a, file=LOG, flush=True)


def win():
    return bpy.context.window_manager.windows[0]


def area(kind):
    return next((a for a in win().screen.areas if a.type == kind), None)


def region(a, kind='WINDOW'):
    return next(r for r in a.regions if r.type == kind)


def screenshot(path, zone=False):
    w, a = win(), area('VIEW_3D')
    if not zone:                                      # the pointer in the middle of the view: no hover hint anywhere
        try:
            w.cursor_warp(a.x + a.width // 2, a.y + a.height // 2)
        except Exception:
            pass
    with bpy.context.temp_override(window=w, area=a, region=region(a)):
        if zone:
            bpy.ops.screen.screenshot_area(filepath=path, check_existing=False)
        else:
            bpy.ops.screen.screenshot(filepath=path, check_existing=False)
    return path


def pixels(path):
    im = bpy.data.images.load(path, check_existing=False)
    a = np.empty(im.size[0] * im.size[1] * im.channels, np.float32)
    im.pixels.foreach_get(a)
    bpy.data.images.remove(im)
    return a


def stable(min_wait=2.0, max_wait=240.0, tol=0.0008):
    """Generator: waits until the 3D viewport stops changing (two captures 6 s apart agree), at most max_wait."""
    t0 = time.time()
    yield min_wait
    prev = None
    tmp = os.path.join(OUT, '_stable.png')
    while True:
        cur = pixels(screenshot(tmp, zone=True))
        if prev is not None and prev.shape == cur.shape:
            d = float(np.abs(cur - prev).mean())
            if d < tol or time.time() - t0 > max_wait:
                log('  stable', round(time.time() - t0), 's', round(d, 5))
                os.remove(tmp)
                return
        prev = cur
        yield 6.0


def orient(spec):
    """Rotation looking from spec cam to spec target, the image's up along spec up (world Z by default)."""
    c, t = Vector(spec['cam']), Vector(spec['target'])
    z = -(t - c).normalized()
    up = Vector(spec.get('up', (0, 0, 1)))
    y = (up - z * up.dot(z)).normalized()
    x = y.cross(z)
    return Matrix((x, y, z)).transposed().to_quaternion()


def look(spec, a):
    """Aligns the 3D view on a camera position (user perspective, not the camera view)."""
    sp = a.spaces.active
    r3 = sp.region_3d
    c, t = Vector(spec['cam']), Vector(spec['target'])
    r3.view_perspective = 'PERSP'
    r3.view_rotation = orient(spec)
    r3.view_distance = (t - c).length
    r3.view_location = t
    sp.lens = spec['lens'] * 2
    sp.clip_start, sp.clip_end = 0.01, 200


def tidy(a, stats=True):
    sp = a.spaces.active
    ov = sp.overlay
    ov.show_extras = False
    ov.show_relationship_lines = False
    ov.show_cursor = False
    ov.show_floor = False
    ov.show_axis_x = ov.show_axis_y = False
    ov.show_stats = stats
    ov.show_text = True
    ov.show_overlays = True
    ov.show_look_dev = False
    sp.show_region_toolbar = True
    sp.show_region_header = True
    sp.show_region_ui = False
    sp.show_gizmo = True


def shading(kind, a):
    s = a.spaces.active.shading
    s.type = kind
    if kind == 'SOLID':                                   # clay: one light grey, studio light, cavity, soft shadow
        s.light = 'STUDIO'
        s.color_type = 'SINGLE'
        s.single_color = (0.78, 0.78, 0.78)
        s.show_cavity = True
        s.cavity_type = 'BOTH'
        s.cavity_ridge_factor, s.cavity_valley_factor = 1.0, 1.2
        s.show_shadows = True
        s.shadow_intensity = 0.4
        s.show_specular_highlight = True
    elif kind == 'WIREFRAME':
        s.wireframe_color_type = 'THEME'
        s.show_xray_wireframe = False
        a.spaces.active.overlay.wireframe_threshold = 1.0
    elif kind == 'MATERIAL':                              # neutral studio HDRI plus the scene's lights
        s.use_scene_lights = True
        s.use_scene_world = False
        try:
            s.studio_light = 'studio.exr'
        except TypeError:
            log('  studio.exr absent')
        s.studiolight_intensity = 0.55
        s.studiolight_background_alpha = 0.0
        a.spaces.active.overlay.show_look_dev = False
    a.spaces.active.overlay.show_text = kind != 'RENDERED'   # the render status text lags behind the image


def under(o, root):
    p = o.parent
    while p:
        if p == root:
            return True
        p = p.parent
    return False


def select(names, active=None):
    """Selects the objects whose name starts with one of names, (mat:<name>) that use that material, or (root:<name>)
    the meshes under that empty (an imported model with meaningless names: the chair)."""
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    mats = [n[4:] for n in names if n.startswith('mat:')]
    roots = [bpy.data.objects.get(n[5:]) for n in names if n.startswith('root:')]
    pref = tuple(n for n in names if not n.startswith(('mat:', 'root:')))
    objs = [o for o in bpy.context.view_layer.objects if (pref and o.name.startswith(pref))
            or (o.type in ('MESH', 'CURVE') and any(m and m.name in mats for m in o.data.materials))
            or (o.type == 'MESH' and any(r and under(o, r) for r in roots))]
    for o in objs:
        o.select_set(True)
    act = bpy.data.objects.get(active) if active else (objs[0] if objs else None)
    bpy.context.view_layer.objects.active = act
    return objs


def outliner(show_active=False):
    w = win()
    for a in w.screen.areas:
        if a.type != 'OUTLINER':
            continue
        with bpy.context.temp_override(window=w, area=a, region=region(a)):
            for _ in range(4):
                bpy.ops.outliner.show_one_level(open=False)
            bpy.ops.outliner.show_one_level(open=True)
            if show_active:
                bpy.ops.outliner.show_active()


def properties(ctx):
    for a in win().screen.areas:
        if a.type == 'PROPERTIES':
            try:
                a.spaces.active.context = ctx
            except TypeError:
                log('  properties: no tab', ctx)


def ranger_noeuds(nt):
    """Lays a node tree out in columns from the output (only in this session, nothing is saved)."""
    nodes = [n for n in nt.nodes if n.type not in ('FRAME', 'REROUTE')]
    out = next((n for n in nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output), None) or \
        next((n for n in nodes if n.type == 'OUTPUT_MATERIAL'), None)
    if not out:
        return
    depth = {out: 0}
    for _ in range(len(nodes)):
        changed = False
        for l in nt.links:
            if l.to_node in depth and l.from_node.type not in ('FRAME', 'REROUTE'):
                d = depth[l.to_node] + 1
                if depth.get(l.from_node, -1) < d:
                    depth[l.from_node] = d
                    changed = True
        if not changed:
            break
    for n in nodes:
        n.parent = None
    cols = {}
    for n, d in depth.items():
        cols.setdefault(d, []).append(n)
    x = 0.0
    for d in sorted(cols):
        col = sorted(cols[d], key=lambda n: -n.location.y)
        w = max(n.width for n in col)
        hs = [max(n.dimensions.y / max(n.dimensions.x / n.width, 1e-3), 60.0) if n.dimensions.x else 160.0 for n in col]
        y = sum(hs) / 2 + 30 * (len(col) - 1) / 2
        for n, h in zip(col, hs):
            n.location = (x - n.width, y)
            y -= h + 30
        x -= w + 90
    for n in nodes:
        if n not in depth:
            n.hide = True


def setup():
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'
    prefs.get_devices()
    for d in prefs.devices:
        d.use = True
    sc = bpy.context.scene
    sc.cycles.device = 'GPU'
    sc.cycles.preview_samples = 64
    sc.cycles.use_preview_denoising = True
    sc.render.preview_pixel_size = '1'
    sc.eevee.taa_samples = 32
    log('setup', [d.name for d in prefs.devices], win().width, win().height)


def vues():
    return [v for v in ORDRE if not OPT.get('vues') or v in OPT['vues'].split(',')]


# ------------------------------------------------------------------ A: the interface
def job_ui():
    sfx = '' if FMT == '169' else '-45'
    shading_ready = False
    for vue in vues():
        spec = VUES[vue][FMT]
        sel, act, tab, sel_nodes = SEL[vue]
        win().workspace = bpy.data.workspaces['Layout']
        yield 1.5
        a = area('VIEW_3D')
        tidy(a)
        look(spec, a)
        for k, (st, shade) in enumerate(STAGES, 1):
            log(vue, st)
            if shade == 'RENDERED':
                select([])
            else:
                select(sel, act)
            shading(shade, a)
            outliner(show_active=shade != 'RENDERED')
            yield 1.0
            properties('RENDER' if shade == 'RENDERED' else tab)
            yield from stable(min_wait=35.0 if shade == 'RENDERED' else (15.0 if shade == 'MATERIAL' else 3.0),
                              max_wait=45.0 if shade == 'MATERIAL' else 240.0)
            screenshot(os.path.join(OUT, f'ui-{vue}-{st}{sfx}.png'))
        # the Shading workspace on the material of the view's object
        log(vue, '5-noeuds')
        win().workspace = bpy.data.workspaces['Shading']
        yield 1.5
        w = win()
        if not shading_ready:
            for o in list(w.screen.areas):
                if o.type == 'FILE_BROWSER':          # never show a file path (it holds the user's name)
                    o.type = 'IMAGE_EDITOR'
            yield 0.5
            if FMT == '45':                           # no room in the portrait window: the left column goes
                for o in [o for o in w.screen.areas if o.type == 'IMAGE_EDITOR']:
                    with bpy.context.temp_override(window=w, area=o, region=region(o)):
                        bpy.ops.screen.area_close()
                    yield 0.5
            shading_ready = True
        imgs = []                                    # the screens' contents: the code, the Figma board
        for mn in ('screen_ecran-gauche-code.png', 'screen_ecran-droite-figma.png'):
            m = bpy.data.materials.get(mn)
            im = next((nd.image for nd in m.node_tree.nodes if nd.type == 'TEX_IMAGE' and nd.image), None) if m else None
            if im:
                imgs.append(im)
        k = 0
        for o in w.screen.areas:
            if o.type == 'IMAGE_EDITOR' and imgs:
                o.spaces.active.image = imgs[k % len(imgs)]
                k += 1
                with bpy.context.temp_override(window=w, area=o, region=region(o)):
                    bpy.ops.image.view_all(fit_view=True)
        a = area('VIEW_3D')
        tidy(a)
        look(spec, a)
        shading('MATERIAL', a)
        select(sel_nodes, act if (act in sel_nodes or sel_nodes == sel) else None)
        outliner(show_active=True)
        ob = bpy.context.view_layer.objects.active
        nt = ob.active_material.node_tree if ob and ob.active_material and ob.active_material.use_nodes else None
        if nt:                                       # laid out in columns, unconnected sockets hidden (ctrl+H)
            for n in nt.nodes:
                for so in list(n.inputs) + list(n.outputs):
                    if not so.is_linked:
                        so.hide = True
            yield 0.8
            ranger_noeuds(nt)
        yield 1.0
        properties('MATERIAL')
        ne = area('NODE_EDITOR')
        if ne:
            with bpy.context.temp_override(window=w, area=ne, region=region(ne)):
                bpy.ops.node.view_all()
                for _ in range(2):
                    bpy.ops.view2d.zoom_in()
        yield from stable(min_wait=15.0, max_wait=45.0)
        screenshot(os.path.join(OUT, f'ui-{vue}-5-noeuds{sfx}.png'))
        log('  ok', vue)


# ------------------------------------------------------------------ C: without interface
def camera(spec, name):
    cd = bpy.data.cameras.new(name)
    co = bpy.data.objects.new(name, cd)
    bpy.context.scene.collection.objects.link(co)
    c, t = Vector(spec['cam']), Vector(spec['target'])
    co.location = c
    co.rotation_mode = 'QUATERNION'
    co.rotation_quaternion = orient(spec)
    cd.lens = spec['lens']
    cd.sensor_width = 36
    cd.sensor_fit = 'AUTO'
    cd.clip_end = 200
    cd.dof.use_dof = True
    cd.dof.aperture_fstop = 11
    cd.dof.focus_distance = (t - c).length
    return co


def job_net():
    sc = bpy.context.scene
    rx, ry = (2160, 2700) if FMT == '45' else (3840, 2160)
    for vue in vues():
        cam = camera(VUES[vue][FMT], f'CAM_net_{vue}_{FMT}')
        sc.camera = cam
        sc.render.resolution_x, sc.render.resolution_y = rx, ry
        sc.render.resolution_percentage = 100
        sc.render.film_transparent = False
        sc.render.engine = 'CYCLES'
        a = area('VIEW_3D')
        sp = a.spaces.active
        tidy(a, stats=False)
        sp.show_region_toolbar = False
        sp.show_region_header = False
        sp.show_gizmo = False
        sp.region_3d.view_perspective = 'CAMERA'
        select([])
        for st, shade in STAGES[:3]:
            shading(shade, a)
            ov = sp.overlay
            if shade == 'WIREFRAME':                  # wireframe shading draws its lines as an overlay
                ov.show_overlays = True
                for attr in ('show_text', 'show_stats', 'show_annotation', 'show_bones', 'show_outline_selected', 'show_object_origins'):
                    if hasattr(ov, attr):
                        setattr(ov, attr, False)
            else:
                ov.show_overlays = False
            yield from stable(min_wait=15.0 if shade == 'MATERIAL' else 3.0, max_wait=45.0)
            sc.render.filepath = os.path.join(OUT, f'net-{vue}-{FMT}-{st}.png')
            with bpy.context.temp_override(window=win(), area=a, region=region(a)):
                bpy.ops.render.opengl(write_still=True, view_context=True)
            log('  opengl', vue, st)
            yield 1.0
        sc.cycles.samples = int(OPT.get('samples', 160))
        sc.cycles.use_denoising = True
        sc.render.filepath = os.path.join(OUT, f'net-{vue}-{FMT}-4-rendu.png')
        shading('SOLID', a)
        yield 1.0
        t0 = time.time()
        bpy.ops.render.render(write_still=True)
        log('  cycles', vue, round(time.time() - t0), 's')
        yield 1.0


def run():
    yield 4.0
    setup()
    yield 2.0
    if JOB == 'ui':
        yield from job_ui()
    else:
        yield from job_net()
    log('fin')


GEN = run()


def tick():
    try:
        return next(GEN)
    except StopIteration:
        LOG.close()
        os._exit(0)
    except Exception:
        log(traceback.format_exc())
        LOG.close()
        os._exit(1)


bpy.app.timers.register(tick, first_interval=3.0)
