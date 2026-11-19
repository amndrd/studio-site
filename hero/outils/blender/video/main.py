
# ================================================================== video: build, animate, cameras, render
# usage (through rendus-video.sh): test=<macstudio|animatique|plan> style=<coupe (retained)|balayage|grain> res=1280 samples=24
#   [moteur=cycles (the final wide and end shots) seuil=0.02] [frames=a-b]
#   out=<dir> [cam=<shot> t=<a-b> (seconds) for test=plan] [liste=f1,f2] [save=<file.blend>] [rendu=0]
#   [boucle=A|B|C (video/boucle.py, the loop after the final shot) frames=boucle (only its frames)]
#   [format=9x16 (the phone version, VID_9x16: res is then the height)]
VID_SHOTS = {
    'macstudio': dict(cam=(0.12, -0.32, 0.98), target=(0.56, 0.27, 0.79), lens=55, fstop=4.0, focus=None),
    'pieds': dict(cam=(-2.0, -1.55, 0.5), target=(-1.05, -0.3, 0.32), lens=26, fstop=5.6, focus=None),
    'clavier': dict(cam=(-0.27, -1.08, 1.1), target=(0.05, -0.17, 0.76), lens=35, fstop=4.0, focus=None),
    'macbook': dict(cam=(1.45, -0.85, 1.05), target=(0.75, -0.02, 0.84), lens=35, fstop=5.6, focus=None),
    'lampe': dict(cam=(-1.95, -0.95, 1.3), target=(-0.98, 0.1, 1.0), lens=40, fstop=5.6, focus=None),
    'chaise': dict(cam=(0.95, -2.75, 0.75), target=(0.1, -0.9, 0.45), lens=32, fstop=8.0, focus=None),
    'papiers': dict(cam=(0.05, -0.85, 2.65), target=(0.05, -0.02, 0.74), lens=28, fstop=8.0, focus=None),
    'cables': dict(cam=(1.75, 1.45, 0.85), target=(1.0, 0.25, 0.22), lens=24, fstop=8.0, focus=None),
    'poste': dict(cam=(-1.75, -2.3, 1.62), target=(0.12, 0.12, 0.98), lens=30, fstop=8.0, focus=None),
    'ensemble': dict(cam=(-2.45, -3.35, 1.85), target=(0.72, 0.1, 0.62), lens=30, fstop=11.0, focus=None),
}
# the sequence shot: (time s, angle deg around the desk, radius, height, target)
VID_SEQ = [   # 17/11: retimed on the faster build; at the lamp and the chair it stays wide (they are seen in the wide shot)
    (0.0, -142, 5.3, 2.6, (0.4, 0.0, 0.4)), (5.2, -127, 4.7, 2.2, (0.2, 0.0, 0.5)), (10.2, -112, 4.5, 2.0, (0.6, 0.0, 0.45)),
    (14.2, -102, 4.3, 1.9, (0.6, 0.0, 0.55)), (20.0, -96, 4.0, 1.8, (0.4, 0.05, 0.75)), (26.0, -92, 3.6, 1.7, (-0.1, 0.05, 0.85)),
    (30.4, -86, 3.7, 1.65, (-0.2, -0.1, 0.75)), (34.2, -76, 3.9, 1.8, (0.2, -0.3, 0.6)), (41.0, -64, 4.0, 2.0, (0.5, 0.0, 0.75)),
    (45.0, -56, 4.1, 1.8, (0.8, 0.0, 0.5)), (51.0, -49, 4.7, 1.9, (0.5, 0.0, 0.6)), (57.4, -41, 5.1, 2.0, (0.6, 0.0, 0.6)),
]
VID_C = Vector((0.6, -0.1, 0.0))
# 18/11, the presentation of the finished desk (the user: a few more shots of the complete desk, from above, close on
# the MacBook, from the side, from behind...), after the wide shot where the LEDs come on and before the final shot of the
# desk set (poste). In the 3D timeline the shots come after the end, the desk standing still; the montage
# (outils/video_montage.py, with montage.json) puts them back before the poste shot. Each one moves slowly (linear),
# crisp cuts between them, wide and close in turn.
# cam / cible: (from, to); roll: a view straight down that turns (degrees); net: the focus point (default: the target);
# sans_bgl: the low light behind the desk off (seen from behind, it lights the floor in front of the camera)
VID_PRES = [
    dict(nom='dessus', L=3.0, cam=((0.45, -0.2, 4.0), (0.45, -0.2, 3.65)), roll=(-4.0, 3.0), lens=28, fstop=11.0),
    # the MacBook (the user's "zoomed on the Mac": the MacBook, not the Mac Studio), from above in three-quarter view as
    # in the user's viewport capture: the Mac Studio behind on the left, the AirPods, the rolls and the papers on the right
    dict(nom='macbook', L=2.8, cam=((1.00, -0.70, 1.31), (0.86, -0.68, 1.28)), cible=((0.86, 0.0, 0.85),) * 2, lens=38,
         fstop=4.0),
    dict(nom='cote', L=2.8, cam=((-3.35, -1.45, 1.35), (-3.05, -1.30, 1.32)), cible=((0.0, 0.0, 0.85), (0.05, 0.0, 0.85)),
         lens=32, fstop=8.0),
    dict(nom='lampe', L=2.6, cam=((-1.85, -1.00, 1.24), (-1.60, -1.18, 1.22)), cible=((-0.92, 0.05, 0.98),) * 2, lens=45,
         fstop=4.0),
    dict(nom='derriere', L=2.8, cam=((1.75, 2.75, 1.55), (0.95, 2.85, 1.55)), cible=((0.55, 0.0, 0.85), (0.35, 0.0, 0.85)),
         lens=35, fstop=8.0, sans_bgl=True),
    dict(nom='rasant', L=2.8, cam=((1.85, -0.72, 0.95), (1.62, -0.66, 0.93)), cible=((-0.6, 0.02, 0.86),) * 2, lens=40,
         fstop=4.0, net=(0.85, -0.05, 0.82)),
]


# 19/11, the phone version for the site (format=9x16: 1080 x 1920 for res=1920, res is the long side). Sensor fit
# horizontal; z narrows the field of the 16:9 shot (the phone shows 1/z of its width: 1 keeps the whole width, the desk
# then small in a tall empty frame; 3.16 is the plain centre crop of the 16:9 video), s moves the camera back from its
# target, the lens following (lens x z x s); shift (camera shift_y, in frame widths) moves the framing up (+) or down (-);
# roll (degrees, the top view only) turns the view so the desk's length runs up the frame.
_PW, _PC, _PP = dict(z=1.75), dict(z=1.4), dict(z=1.5)      # first pass: the wide shots, the close shots, the presentation
VID_9x16 = dict(
    seq=dict(_PW), ensemble=dict(_PW), poste=dict(_PW),
    pieds=dict(_PC), clavier=dict(_PC), macbook=dict(_PC), lampe=dict(_PC), chaise=dict(_PC), papiers=dict(_PC),
    cables=dict(_PC),
    p_dessus=dict(_PP, roll=90.0), p_macbook=dict(_PP), p_cote=dict(_PP), p_lampe=dict(_PP), p_derriere=dict(_PP),
    p_rasant=dict(_PP),
)


def _vid_9x16_key(cam_name):
    n = cam_name[4:]                                  # CAM_seq, CAM_<shot>, CAM_p_<name>
    return n if n in VID_9x16 else None


def vid_portrait_prep():
    """Before the cameras are made: move each one back from its target by its s (the lens follows in vid_portrait_post)."""
    def back(cam, tgt, s):
        return tuple(t + (c - t) * s for c, t in zip(cam, tgt))
    s = VID_9x16['seq'].get('s', 1.0)
    for i, (t, a, r, h, tg) in enumerate(VID_SEQ):
        loc = VID_C + Vector((r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), h))
        p = Vector(back(loc, tg, s)) - VID_C
        VID_SEQ[i] = (t, math.degrees(math.atan2(p.y, p.x)), math.hypot(p.x, p.y), p.z, tg)
    for k, sp in VID_SHOTS.items():
        sp['cam'] = back(sp['cam'], sp['target'], VID_9x16.get(k, {}).get('s', 1.0))
    for sp in VID_PRES:
        P = VID_9x16.get('p_' + sp['nom'], {})
        s = P.get('s', 1.0)
        if 'roll' in sp:                              # straight down: higher above the desk top (0.75 m)
            sp['cam'] = tuple((c[0], c[1], 0.75 + (c[2] - 0.75) * s) for c in sp['cam'])
            sp['roll'] = tuple(r + P.get('roll', 0.0) for r in sp['roll'])
        else:
            sp['cam'] = tuple(back(c, t, s) for c, t in zip(sp['cam'], sp['cible']))


def vid_portrait_post():
    """Once the cameras are made: horizontal sensor fit, the lens times z x s, the vertical shift."""
    for o in bpy.data.objects:
        if o.type != 'CAMERA':
            continue
        o.data.sensor_fit = 'HORIZONTAL'
        o.data.sensor_width = 36
        k = _vid_9x16_key(o.name)
        if k and o.data.type == 'PERSP':
            o.data.lens *= VID_9x16[k].get('z', 1.0) * VID_9x16[k].get('s', 1.0)
            o.data.shift_y = VID_9x16[k].get('shift', 0.0)


def vid_presentation():
    """The presentation shots, one after another from the frame after the end. Returns [(name, first, last)]."""
    f = vid_f(VID_T['fin']) + 1
    out = []
    for s in VID_PRES:
        a = f
        b = a + round(s['L'] * VID_FPS) - 1
        cd = bpy.data.cameras.new('CAM_p_' + s['nom'])
        cam = bpy.data.objects.new(cd.name, cd)
        ROOT.objects.link(cam)
        cd.lens, cd.sensor_width, cd.clip_end = s['lens'], 36, 200
        cd.dof.use_dof = True
        cd.dof.aperture_fstop = s['fstop']
        if 'roll' in s:                              # straight down, the frame's top towards the back of the desk
            for fr, p, r in ((a, s['cam'][0], s['roll'][0]), (b, s['cam'][1], s['roll'][1])):
                cam.location = p
                cam.rotation_euler = (0.0, 0.0, math.radians(r))
                cam.keyframe_insert('location', frame=fr)
                cam.keyframe_insert('rotation_euler', frame=fr)
                cd.dof.focus_distance = p[2] - 0.75
                cd.dof.keyframe_insert('focus_distance', frame=fr)
        else:
            tg = bpy.data.objects.new(cam.name + '_cible', None)
            ROOT.objects.link(tg)
            c = cam.constraints.new('TRACK_TO')
            c.target, c.track_axis, c.up_axis = tg, 'TRACK_NEGATIVE_Z', 'UP_Y'
            for fr, p, t in ((a, s['cam'][0], s['cible'][0]), (b, s['cam'][1], s['cible'][1])):
                cam.location = p
                cam.keyframe_insert('location', frame=fr)
                tg.location = t
                tg.keyframe_insert('location', frame=fr)
            _vid_interp(tg, 'LINEAR')
            if s.get('net'):
                fo = bpy.data.objects.new(cam.name + '_net', None)
                ROOT.objects.link(fo)
                fo.location = s['net']
                cd.dof.focus_object = fo
            else:
                cd.dof.focus_object = tg
        _vid_interp(cam, 'LINEAR')
        m = SC.timeline_markers.new(cam.name, frame=a)
        m.camera = cam
        li = bpy.data.objects.get('bgl')
        if s.get('sans_bgl') and li and VID_T.get('bgl'):
            v = VID_T['bgl'][1]
            for fr, k in ((a - 1, 1.0), (a, 0.0), (b, 0.0), (b + 1, 1.0)):
                li.data.energy = v * k
                li.data.keyframe_insert('energy', frame=fr)
        out.append((s['nom'], a, b))
        f = b + 1
    print('PRES', out, flush=True)
    return out


def vid_cycles_setup(samples):
    """18/11, the final render: Cycles for the wide shot and the final shots, once every piece is finished (EEVEE
    blotches the brushed aluminium of the Mac Studio). The wireframe twins are all gone by then: hidden outright."""
    SC.render.engine = 'CYCLES'
    c = SC.cycles
    try:
        pr = bpy.context.preferences.addons['cycles'].preferences
        pr.compute_device_type = 'METAL'
        # 18/11: the background specialisation of the Metal kernels crashed Blender (abort in
        # ccl::MetalKernelPipeline::compile, path_cache_get) on the first frame of the animation: off
        pr.kernel_optimization_level = 'OFF'
        pr.get_devices()
        for d in pr.devices:
            d.use = True
        c.device = 'GPU'
    except Exception as ex:
        print('cycles device', ex)
    c.samples = samples
    c.use_adaptive_sampling = True
    c.adaptive_threshold = float(OPT.get('seuil', 0.02))
    c.use_denoising = True
    try:
        c.denoiser = 'OPENIMAGEDENOISE'
        c.denoising_use_gpu = True
    except Exception:
        pass
    c.max_bounces, c.diffuse_bounces, c.glossy_bounces, c.transparent_max_bounces = 8, 3, 4, 16
    c.caustics_reflective = c.caustics_refractive = False
    c.blur_glossy = 1.0
    for o in bpy.data.objects:
        if o.type == 'LIGHT':
            o.visible_camera = False                # the presentation's shots look towards some lights: never seen
        if o.get('vid_twin'):
            o.animation_data_clear()
            o.hide_render = True


def vid_render_setup(res, samples):
    if OPT.get('moteur') == 'cycles':
        vid_cycles_setup(samples)
    else:
        vid_eevee_setup(samples)
    vid_output_setup(res)


def vid_eevee_setup(samples):
    SC.render.engine = 'BLENDER_EEVEE_NEXT'
    e = SC.eevee
    e.taa_render_samples = samples
    for k, v in (('use_raytracing', True), ('use_shadows', True), ('use_gtao', True)):
        try:
            setattr(e, k, v)
        except Exception:
            pass
    try:
        e.ray_tracing_method = 'SCREEN'
        o = e.ray_tracing_options
        o.resolution_scale = '1' if int(OPT.get('res', 1280)) >= 1280 else '2'
        o.use_denoise = True
        for k in ('denoise_spatial', 'denoise_temporal', 'denoise_bilateral'):
            setattr(o, k, True)
        o.trace_max_roughness = 0.5
        e.shadow_resolution_scale = 1.0
        e.shadow_ray_count = 2
        e.shadow_step_count = 12
        for li in bpy.data.lights:
            if li.type == 'AREA':
                li.use_shadow_jitter = True
    except Exception as ex:
        print('eevee opts', ex)


def vid_output_setup(res):
    SC.render.resolution_x = int(res * 9 / 16) if OPT.get('format') == '9x16' else res
    SC.render.resolution_y = res if OPT.get('format') == '9x16' else int(res * 9 / 16)
    SC.render.resolution_percentage = 100
    SC.render.fps = VID_FPS
    SC.render.image_settings.file_format = 'PNG'


def vid_seq_camera():
    cd = bpy.data.cameras.new('CAM_seq')
    cam = bpy.data.objects.new('CAM_seq', cd)
    ROOT.objects.link(cam)
    tg = bpy.data.objects.new('CAM_seq_cible', None)
    ROOT.objects.link(tg)
    c = cam.constraints.new('TRACK_TO')
    c.target, c.track_axis, c.up_axis = tg, 'TRACK_NEGATIVE_Z', 'UP_Y'
    cd.lens, cd.sensor_width, cd.clip_end = 30, 36, 200
    cd.dof.use_dof = True
    cd.dof.aperture_fstop = 11.0
    cd.dof.focus_object = tg
    for t, a, r, h, target in VID_SEQ:
        f = vid_f(t)
        cam.location = VID_C + Vector((r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), h))
        cam.keyframe_insert('location', frame=f)
        tg.location = target
        tg.keyframe_insert('location', frame=f)
    return cam


def vid_cuts(times, seq):
    """Close shots cut into the sequence shot: (camera, start s, end s). 17/11: each one lasts until its object is
    complete (textured); the lamp and the chair are seen in the wide shot; the MacBook replaces the Mac Studio."""
    def span(*keys, a=0.0, b=0.0):
        ks = [x for x in times if x.startswith(keys)]
        return (min(times[k][0] for k in ks) + a, max(times[k][1] for k in ks) + b) if ks else None
    P = {st: (t0, L) for st, t0, L, sc in VID_PLAN}
    mb = span('pst_macbook', a=0.1)
    cuts = []
    for shot, w in (('pieds', span('D_leg', 'foot', a=0.15, b=0.5)), ('clavier', span('pst_keyboard', a=0.1, b=0.45)),
                    ('macbook', (mb[0], VID_T['ecrans_on'] + 1.2) if mb else None),
                    ('papiers', (P['papiers'][0] + 0.2, sum(P['papiers']) + 0.2)),
                    ('cables', (P['cables'][0] + 1.2, sum(P['cables']) + 0.4)),
                    ('poste', (VID_T['fin'] - 3.8, VID_T['fin']))):
        if not w:
            continue
        cam = make_camera(dict(VID_SHOTS[shot]), 'CAM_' + shot)
        # a slow push along the view axis
        d = (Vector(VID_SHOTS[shot]['target']) - Vector(VID_SHOTS[shot]['cam'])) * 0.06
        cam.location = Vector(VID_SHOTS[shot]['cam']) - d
        cam.keyframe_insert('location', frame=vid_f(w[0]))
        cam.location = Vector(VID_SHOTS[shot]['cam']) + d
        cam.keyframe_insert('location', frame=vid_f(w[1]))
        _vid_interp(cam, 'LINEAR')
        cuts.append((cam, w[0], w[1]))
    cuts.sort(key=lambda c: c[1])
    print('CUTS', [(c.name, round(a, 2), round(b, 2)) for c, a, b in cuts], flush=True)
    SC.timeline_markers.clear()
    m = SC.timeline_markers.new('seq', frame=1)
    m.camera = seq
    for i, (cam, a, b) in enumerate(cuts):
        m = SC.timeline_markers.new(cam.name, frame=vid_f(a))
        m.camera = cam
        nxt = cuts[i + 1][1] if i + 1 < len(cuts) else 1e9
        if b < nxt - 0.05 and b < VID_T['fin'] - 0.05:  # back to the sequence shot, unless a close shot follows or it ends
            m = SC.timeline_markers.new('seq', frame=vid_f(b))
            m.camera = seq
    SC.camera = seq
    return cuts


def vid_main():
    trace_install()
    trace_build()
    vid_make_real()
    vid_fond(VID_FOND)
    vid_defaults()
    vid_lamp_rig()
    vid_defaults()
    vid_screens_power()
    vid_wrap_materials()
    groups = vid_groups()
    vid_report(groups)
    test = OPT.get('test', 'macstudio')
    if test == 'macstudio':
        piece = next(objs for k, objs in groups['poste'] if k.startswith('pst_macstudio'))
        vid_prepare(piece)
        end = vid_schedule_piece(piece, 0.4, False)
        SC.camera = make_camera(dict(VID_SHOTS['macstudio']), 'CAM_test')
        SC.frame_start, SC.frame_end = 1, vid_f(end + 0.8)
    else:
        times = vid_schedule_all(groups)
        vid_fond_anim(VID_FOND)
        print('TIMES', {k: (round(a, 2), round(b, 2)) for k, (a, b) in list(times.items())[:8]}, flush=True)
        print('BUILT', round(max(b for a, b in times.values()), 2), 's (Cycles only after this)', flush=True)
        if OPT.get('format') == '9x16':
            vid_portrait_prep()
        seq = vid_seq_camera()
        if test == 'animatique':
            cuts = vid_cuts(times, seq)
            pres = vid_presentation()
            # 19/11, the loop (video/boucle.py): after the presentation in the 3D timeline, after the final shot in the
            # montage; its own montage file, the validated video's montage.json stays as it is
            seg = vid_boucle(OPT['boucle'], groups, seq, pres) if OPT.get('boucle') else None
            SC.frame_start, SC.frame_end = 1, seg[1] if seg else pres[-1][2]
            # the montage's order: the build, the presentation, then the final shot of the desk set
            fp = next(vid_f(a) for c, a, b in cuts if c.name == 'CAM_poste')
            order = [[1, fp - 1], [pres[0][1], pres[-1][2]], [fp, vid_f(VID_T['fin'])]]
            if seg:
                VID_T['boucle'] = seg
                order.append(list(seg))
            js = os.path.join(os.path.dirname(OPT.get('out', '/tmp/vid').rstrip('/')),
                              f"montage-boucle-{OPT['boucle']}.json" if seg else 'montage.json')
            _json.dump(dict(ordre=order, plans=pres, **(dict(boucle=list(seg)) if seg else {})), open(js, "w"))
            print('MONTAGE', order, flush=True)
        else:                                            # plan: one camera over a time range
            name = OPT.get('cam', 'seq')
            SC.camera = seq if name == 'seq' else make_camera(dict(VID_SHOTS[name]), 'CAM_' + name)
            a, b = map(float, OPT.get('t', '0-74').split('-'))
            SC.frame_start, SC.frame_end = vid_f(a), vid_f(b)
    if OPT.get('format') == '9x16':
        vid_portrait_post()
    vid_render_setup(int(OPT.get('res', 1280)), int(OPT.get('samples', 24)))
    if OPT.get('save'):
        bpy.ops.wm.save_as_mainfile(filepath=OPT['save'])
        print('SAVED', OPT['save'], flush=True)
    if OPT.get('rendu', '1') == '0':
        return
    out = OPT.get('out', '/tmp/vid')
    os.makedirs(out, exist_ok=True)
    if OPT.get('liste'):
        for f in map(int, OPT['liste'].split(',')):
            SC.frame_set(f)
            SC.render.filepath = os.path.join(out, f'f{f:04d}.png')
            bpy.ops.render.render(write_still=True)
            print('STILL', f, flush=True)
        return
    SC.frame_step = int(OPT.get('pas', 1))
    fr = OPT.get('frames')
    if fr:
        a, b = VID_T['boucle'] if fr == 'boucle' else map(int, fr.split('-'))
        SC.frame_start, SC.frame_end = a, b
    SC.render.filepath = os.path.join(out, '')
    SC.render.use_overwrite = False                 # resumable: a rerun skips the frames already there
    SC.render.use_placeholder = True
    print('RENDER', SC.frame_start, SC.frame_end, out, flush=True)
    bpy.ops.render.render(animation=True)
    print('DONE', flush=True)


vid_main()
