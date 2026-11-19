
# ================================================================== video: the loop (19/11)
# The user (19/11, once the final video was validated): make it loop. From the end of the video the desk goes away
# and we come back to the light grid of the start. In the 3D timeline the loop segment comes after the presentation;
# the montage plays it after the final shot. It brings the scene back to its state at frame 1, and its camera lands
# on the sequence shot's first pose with no speed left, the very pose and speed the video starts with.
#   boucle=A  le rembobinage: the whole build rewinds fast, eased, the wide camera with it.
#   boucle=B  la vague: a front crosses the desk from right to left; behind it each piece goes back through its stages
#             (texture, colour, clay, wireframe, nothing) and the concrete turns back into the grid.
#   boucle=C  le retour dans le sol: the finished desk sinks back into the floor it came out of, the lights go out
#             and the grid comes back from the desk outwards.
# usage: rendus-video.sh animatique coupe 1920 48 boucle=B frames=boucle (NOM=boucle-B)
VID_BOUCLE_L = dict(A=6.0, B=None, C=2.7)          # seconds (B: from the size of the desk)


def _bcl_ids():
    """Every datablock with keyframes: objects, shape keys, curves, lights, materials and world (and their trees)."""
    seen, out = set(), []
    for pool in (bpy.data.objects, bpy.data.shape_keys, bpy.data.curves, bpy.data.meshes, bpy.data.lights,
                 bpy.data.materials, bpy.data.worlds, bpy.data.node_groups):
        for i in pool:
            for x in (i, getattr(i, 'node_tree', None)):
                ad = getattr(x, 'animation_data', None) if x is not None else None
                if ad and ad.action and x.as_pointer() not in seen:
                    seen.add(x.as_pointer())
                    out.append(x)
    return out


def _bcl_is_bool(fc):
    return fc.data_path.endswith(('hide_render', 'hide_viewport'))


def _bcl_keys(idb, frames, value, only=None):
    """Appends one key per frame to the F-curves of idb (all, or those whose path contains `only`):
    value(fc, F). F-curves that would stay at their held value are left alone."""
    ad = idb.animation_data
    if not ad or not ad.action:
        return 0
    n = 0
    for fc in _vid_fcurves(ad.action):
        if only and only not in fc.data_path:
            continue
        vals = [value(fc, F) for F in frames]
        hold = fc.evaluate(frames[0] - 1)
        if all(abs(v - hold) < 1e-6 for v in vals):
            continue
        b = _bcl_is_bool(fc)
        if b:
            vals = [float(round(v)) for v in vals]
        frames_k, vals = [frames[0] - 1] + list(frames), [hold] + vals   # held up to the segment: nothing earlier moves
        kp = fc.keyframe_points
        n0 = len(kp)
        kp.add(len(frames_k))
        co = [0.0] * (2 * len(kp))
        kp.foreach_get('co', co)
        for i, (F, v) in enumerate(zip(frames_k, vals)):
            co[2 * (n0 + i)] = float(F)
            co[2 * (n0 + i) + 1] = v
        kp.foreach_set('co', co)
        for i in range(n0, len(kp)):
            p = kp[i]
            p.interpolation = 'CONSTANT' if b else 'LINEAR'
        fc.update()
        n += 1
    return n


def _bcl_mix(idb, frames, m, only=None):
    """From the held value to the value at frame 1 (the start of the video), m[F] in 0..1."""
    return _bcl_keys(idb, frames, lambda fc, F: (1 - m[F]) * fc.evaluate(frames[0] - 1) + m[F] * fc.evaluate(1), only)


def _smooth(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def _bcl_profile(n, up=0.15, down=0.4):
    """n positions from 0 to 1: the speed rises smoothly over the first `up` of the time, holds, and falls smoothly to
    zero over the last `down`."""
    v = []
    for i in range(n):
        u = i / (n - 1)
        v.append(min(_smooth(u / up) if up else 1.0, _smooth((1 - u) / down) if down else 1.0))
    c, out = 0.0, []
    for x in v:
        out.append(c)
        c += x
    return [x / out[-1] for x in out]


def _bcl_floor_end(floor, a, b):
    """The front sets the floor before the segment (none) and, on the last frame, the grid everywhere (frame 1)."""
    for F, v in ((a - 1, -1000.0),):
        _key(floor, 'vid_front', F, v)
    _key(floor, 'vid_grille', b - 1, 0.0)
    _key(floor, 'vid_grille', b, 1.0)


def _bcl_camera(a, b):
    """A camera like the sequence shot's (lens, depth of field), which turns into the first pose of the video: it
    lands there at frame b + 1, with no speed, as the video's own camera starts from rest."""
    cd = bpy.data.cameras.new('CAM_boucle')
    cam = bpy.data.objects.new('CAM_boucle', cd)
    ROOT.objects.link(cam)
    tg = bpy.data.objects.new('CAM_boucle_cible', None)
    ROOT.objects.link(tg)
    c = cam.constraints.new('TRACK_TO')
    c.target, c.track_axis, c.up_axis = tg, 'TRACK_NEGATIVE_Z', 'UP_Y'
    cd.lens, cd.sensor_width, cd.clip_end = 30, 36, 200
    cd.dof.use_dof = True
    cd.dof.aperture_fstop = 11.0
    cd.dof.focus_object = tg
    t0, a0, r0, h0, tgt = VID_SEQ[0]
    tg.location = tgt
    for F in range(a, b + 2):
        u = 1 - (1 - (F - a) / (b + 1 - a)) ** 2          # eased out: still at the end, moving at the cut in
        ang, r, h = a0 - 18 * (1 - u), r0 + 0.25 * (1 - u), h0 + 0.2 * (1 - u)
        cam.location = VID_C + Vector((r * math.cos(math.radians(ang)), r * math.sin(math.radians(ang)), h))
        cam.keyframe_insert('location', frame=F)
    _vid_interp(cam, 'LINEAR')
    return cam


def _bcl_floor_front(kind, centre, direction=(-1.0, 0.0, 0.0), band=0.06):
    """The concrete turns back into the grid behind a front: on the floor's material, the grid mix (vid_grille) becomes
    max(vid_grille, the area the front has passed). The front is the object property vid_front of the floor, in
    metres: a line moving along `direction` (plan) or a circle growing from `centre` (cercle)."""
    o = bpy.data.objects.get('fond_grille')
    if not o:
        return None
    nt = o.material_slots[0].material.node_tree
    g = next(n for n in nt.nodes if n.type == 'ATTRIBUTE' and n.attribute_name == 'vid_grille')
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    fr = nt.nodes.new('ShaderNodeAttribute')
    fr.attribute_type, fr.attribute_name = 'OBJECT', 'vid_front'
    L = nt.links
    if kind == 'plan':
        dp = nt.nodes.new('ShaderNodeVectorMath')
        dp.operation = 'DOT_PRODUCT'
        L.new(geo.outputs['Position'], dp.inputs[0])
        dp.inputs[1].default_value = direction
        d = dp.outputs['Value']
    else:
        sb = nt.nodes.new('ShaderNodeVectorMath')
        sb.operation = 'SUBTRACT'
        L.new(geo.outputs['Position'], sb.inputs[0])
        sb.inputs[1].default_value = (centre.x, centre.y, 0.0)
        fl = nt.nodes.new('ShaderNodeVectorMath')
        fl.operation = 'MULTIPLY'
        L.new(sb.outputs[0], fl.inputs[0])
        fl.inputs[1].default_value = (1.0, 1.0, 0.0)
        ln = nt.nodes.new('ShaderNodeVectorMath')
        ln.operation = 'LENGTH'
        L.new(fl.outputs[0], ln.inputs[0])
        d = ln.outputs['Value']
    df = _math(nt, 'SUBTRACT', fr.outputs['Fac'], d)
    sc = _math(nt, 'DIVIDE', df, band, clamp=True)
    mx = nt.nodes.new('ShaderNodeMath')
    mx.operation = 'MAXIMUM'
    outs = [(lk.to_socket) for lk in L if lk.from_socket == g.outputs['Fac']]
    L.new(g.outputs['Fac'], mx.inputs[0])
    L.new(sc, mx.inputs[1])
    for s in outs:
        L.new(mx.outputs[0], s)
    o['vid_front'] = -1000.0
    _key(o, 'vid_front', 0, -1000.0)
    return o


def _bcl_pieces(groups):
    pieces = []
    for st, items in groups.items():
        for k, objs in items:
            ids, seen = [], set()
            for o in objs:
                tw = bpy.data.objects.get(o.name + '.fil')
                for x in (o, tw, o.data if o.type == 'CURVE' else None,
                          o.data.shape_keys if o.type == 'MESH' else None,
                          tw.data.shape_keys if tw is not None and tw.type == 'MESH' else None):
                    if x is not None and x.as_pointer() not in seen:
                        seen.add(x.as_pointer())
                        ids.append(x)
            mn, mx = vid_bbox(objs)
            pieces.append(dict(k=k, st=st, objs=objs, ids=ids, mn=mn, mx=mx))
    return pieces


def _bcl_assign(pieces, skip):
    """The animated datablocks that are not a piece's own (the lamp's pivots, the chair's root, the lights, the
    animated materials) go with a piece: through their children, their parents, their users, or the nearest one."""
    own = {i.as_pointer() for p in pieces for i in p['ids']}
    of_obj = {o.name: p for p in pieces for o in p['objs']}

    def by_obj(o):
        st = list(o.children)
        while st:
            c = st.pop()
            if c.name in of_obj:
                return of_obj[c.name]
            st += list(c.children)
        a = o.parent
        while a:
            if a.name in of_obj:
                return of_obj[a.name]
            a = a.parent
        if o.name in of_obj:
            return of_obj[o.name]
        loc = o.matrix_world.translation
        return min(pieces, key=lambda p: ((p['mn'] + p['mx']) / 2 - loc).length)
    extra = []
    for i in _bcl_ids():
        if i.as_pointer() in own or skip(i):
            continue
        p = None
        if isinstance(i, bpy.types.Object):
            p = by_obj(i)
        elif isinstance(i, bpy.types.Light):
            u = next((o for o in bpy.data.objects if o.data == i), None)
            p = by_obj(u) if u else None
        elif isinstance(i, (bpy.types.ShaderNodeTree, bpy.types.Material)):
            for o in bpy.data.objects:
                if o.name in of_obj and any(sl.material and (sl.material == i or sl.material.node_tree == i)
                                            for sl in o.material_slots):
                    p = of_obj[o.name]
                    break
        if p:
            p['ids'].append(i)
            extra.append((i.name, p['k']))
    print('BOUCLE assigned', len(extra), [e for e in extra if 'light' in e[0].lower() or 'lamp' in e[0].lower()
                                          or 'led' in e[0].lower() or 'mandy' in e[0].lower()][:20], flush=True)


def _bcl_intervals(ids, f_max):
    """The frames where a piece is changing (its keys that move), merged: the idle time between its build and, say,
    its LEDs coming on is skipped."""
    iv = []
    for i in ids:
        ad = i.animation_data
        if not ad or not ad.action:
            continue
        for fc in _vid_fcurves(ad.action):
            kp = sorted((p.co.x, p.co.y, p.interpolation) for p in fc.keyframe_points)
            for (x0, y0, it), (x1, y1, _) in zip(kp, kp[1:]):
                if x1 > f_max + 0.5 or abs(y1 - y0) < 1e-6:
                    continue
                iv.append((x1 - 1, x1) if it == 'CONSTANT' else (x0, x1))
    iv.sort()
    out = []
    for a, b in iv:
        if out and a <= out[-1][1] + 1e-6:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def _bcl_rewind_map(iv):
    """u in 0..1 -> source frame: 0 the end of the piece's last change, 1 the start of its first one."""
    total = sum(b - a for a, b in iv)

    def W(u):
        s = min(max(u, 0.0), 1.0) * total
        for a, b in reversed(iv):
            if s <= b - a:
                return b - s
            s -= b - a
        return iv[0][0]
    return W


def vid_boucle(kind, groups, seq, pres):
    """Keys the loop segment after the presentation. Returns (first, last) frame."""
    a = pres[-1][2] + 1
    f_fin = vid_f(VID_T['fin'])
    cams = lambda i: isinstance(i, (bpy.types.Object, bpy.types.Camera)) and i.name.startswith('CAM_')
    if kind == 'A':
        b = a + round(VID_BOUCLE_L['A'] * VID_FPS) - 1
        frames = list(range(a, b + 1))
        n = len(frames)
        # the build backwards, eased: it sets off from the finished desk and slows down onto frame 2, so the video's
        # frame 1 follows as the turning point
        P = _bcl_profile(n, up=0.12, down=0.45)
        W = {F: f_fin - (f_fin - 2) * P[i] for i, F in enumerate(frames)}
        k = 0
        for i in _bcl_ids():
            if cams(i) and i.name not in ('CAM_seq', 'CAM_seq_cible'):
                continue
            k += _bcl_keys(i, frames, lambda fc, F: fc.evaluate(W[F]))
        m = SC.timeline_markers.new('boucle', frame=a)
        m.camera = seq
        print('BOUCLE A', a, b, k, 'curves', flush=True)
        return a, b
    pieces = _bcl_pieces(groups)
    floor = bpy.data.objects.get('fond_grille')
    bgl = bpy.data.objects.get('bgl')
    skip = lambda i: cams(i) or i == floor or (bgl and (i == bgl or i == bgl.data)) or isinstance(i, bpy.types.World) \
        or (bpy.data.worlds and i == SC.world.node_tree)
    if bgl:
        _bcl_keys(bgl.data, list(range(a, a + 2)), lambda fc, F: fc.evaluate(1))
    allmn = Vector([min(p['mn'][j] for p in pieces) for j in range(3)])
    allmx = Vector([max(p['mx'][j] for p in pieces) for j in range(3)])
    centre = (allmn + allmx) / 2
    if kind == 'B':
        _bcl_assign(pieces, skip)
        V = 2.6                                       # m/s across the desk
        xh, xl = allmx.x + 0.25, allmn.x - 0.25
        T_pre, T_post, t_hold = 0.7, 0.8, 0.35
        td0 = t_hold + T_pre
        td1 = td0 + (xh - xl) / V
        for p in pieces:
            p['s'] = td0 + (xh - p['mx'].x) / V
            p['D'] = max(0.6, (p['mx'].x - p['mn'].x) / V)
        L = max(td1 + T_post, max(p['s'] + p['D'] for p in pieces)) + 0.4
        b = a + round(L * VID_FPS) - 1
        frames = list(range(a, b + 1))
        T = {F: (F - a) / VID_FPS for F in frames}
        k = 0
        for p in pieces:
            iv = _bcl_intervals(p['ids'], f_fin)
            if not iv:
                continue
            Wm = _bcl_rewind_map(iv)
            Wk = {F: Wm(_smooth((T[F] - p['s']) / p['D'])) for F in frames}
            for i in p['ids']:
                k += _bcl_keys(i, frames, lambda fc, F: fc.evaluate(Wk[F]))
        # the floor: the front runs fast up to the desk, crosses it with the pieces, then runs off past the camera
        if _bcl_floor_front('plan', centre):
            for F in frames:
                t = T[F]
                if t < t_hold:
                    x = xh + 9.0
                elif t < td0:
                    x = xh + 9.0 * (1 - (t - t_hold) / T_pre)
                elif t < td1:
                    x = xh - V * (t - td0)
                else:
                    x = xl - 6.0 * min(1.0, (t - td1) / T_post)
                floor['vid_front'] = -x
                floor.keyframe_insert('["vid_front"]', frame=F)
            _bcl_floor_end(floor, a, b)
        print('BOUCLE B', a, b, round(L, 2), 's', k, 'curves', 'x', round(xl, 2), round(xh, 2), flush=True)
    else:
        L = VID_BOUCLE_L['C']
        b = a + round(L * VID_FPS) - 1
        frames = list(range(a, b + 1))
        T = {F: (F - a) / VID_FPS for F in frames}
        # the lights go out first: the screens, the lamp, the LEDs, the low light behind the desk
        off = {F: _smooth((T[F] - 0.15) / 0.55) for F in frames}
        for i in _bcl_ids():
            if (isinstance(i, (bpy.types.Light, bpy.types.ShaderNodeTree)) and not skip(i)
                    and not (SC.world and i == SC.world.node_tree)):
                _bcl_mix(i, frames, off)
        for o in bpy.data.objects:
            if o.get('vid_on') is not None:
                _bcl_mix(o, frames, off, only='vid_on')
        # then the whole desk goes down into the floor, in one piece, like on a lift
        roots, objs = set(), [o for p in pieces for o in p['objs']]
        objs += [t for t in (bpy.data.objects.get(o.name + '.fil') for o in objs) if t]
        for o in objs:
            r = o
            while r.parent:
                r = r.parent
            roots.add(r.name)
        H = allmx.z + 0.15
        fa, fb = a + round(0.5 * VID_FPS), a + round(2.9 * VID_FPS)
        for nm in roots:
            r = bpy.data.objects[nm]
            r.delta_location = (0.0, 0.0, 0.0)
            r.keyframe_insert('delta_location', index=2, frame=fa)
            r.delta_location = (0.0, 0.0, -H)
            r.keyframe_insert('delta_location', index=2, frame=fb)
        for o in objs:
            _key_attr(o, 'hide_render', b, True)
            _vid_const_interp(o, 'hide_render')
        # the grid comes back from under the desk outwards
        if _bcl_floor_front('cercle', centre):
            for F in frames:
                floor['vid_front'] = -0.2 + 16.0 * _ease_io((T[F] - 0.6) / 2.4)
                floor.keyframe_insert('["vid_front"]', frame=F)
            _bcl_floor_end(floor, a, b)
        print('BOUCLE C', a, b, len(roots), 'roots, sink', round(H, 2), 'm', flush=True)
    cam = _bcl_camera(a, b)
    m = SC.timeline_markers.new('boucle', frame=a)
    m.camera = cam
    return a, b
