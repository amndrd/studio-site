
# ================================================================== video: which build call creates each object
# Wraps every function of the concatenated build so each new object records the chain of calls that created it
# (custom property "trace"); trace_build() then builds the complete desk exactly like bureau-complet.py (no render).
import types as _types, json as _json
_VT_STACK = []


def _vt_wrap(name, f):
    def w(*a, **k):
        before = set(bpy.data.objects.keys())
        _VT_STACK.append(name)
        try:
            return f(*a, **k)
        finally:
            path = '/'.join(_VT_STACK)
            _VT_STACK.pop()
            for n in set(bpy.data.objects.keys()) - before:
                o = bpy.data.objects.get(n)
                if o is not None and 'trace' not in o:
                    o['trace'] = path
    w.__name__ = name
    w.__wrapped__ = f
    return w


def trace_install():
    g = globals()
    for k, v in list(g.items()):
        if isinstance(v, _types.FunctionType) and v.__module__ == '__main__' and not k.startswith(('_vt_', 'trace_', 'vid_', '_vid')):
            g[k] = _vt_wrap(k, v)


def trace_build():
    build_bureau_complet()
    for fn in ('papiers_bureau', 'objets_bureau', 'sol_bureau', 'autour_bureau', 'cables_bureau'):
        if fn in globals():
            globals()[fn](_F0, H0, H1)


def trace_dump(path):
    from mathutils import Vector
    rows = []
    for o in bpy.data.objects:
        r = dict(name=o.name, type=o.type, trace=o.get('trace', ''), parent=o.parent.name if o.parent else '',
                 coll=[c.name for c in o.users_collection], hidden=o.hide_render)
        if o.type in ('MESH', 'CURVE'):
            bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
            r['min'] = [round(min(v[i] for v in bb), 3) for i in range(3)]
            r['max'] = [round(max(v[i] for v in bb), 3) for i in range(3)]
            r['mats'] = [m.name for m in o.data.materials if m]
            r['users'] = o.data.users
            r['mods'] = [m.type for m in o.modifiers]
            if o.type == 'MESH':
                r['polys'] = len(o.data.polygons)
        rows.append(r)
    _json.dump(rows, open(path, 'w'), indent=0)
    print('DUMP', len(rows), path, flush=True)
