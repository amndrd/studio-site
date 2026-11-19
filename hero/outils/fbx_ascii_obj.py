# Converts an ASCII FBX (which Blender cannot import) into OBJ + MTL: meshes, UVs, per-polygon materials (colour, opacity).
# Written for the Sketchfab "Indoor Plant" (SketchUp export, no transforms on the models). Y-up as in the file.
# usage: python -I fbx_ascii_obj.py <in.fbx> <out.obj>
import re, sys, os

src, out = sys.argv[1], sys.argv[2]
txt = open(src, encoding='utf-8', errors='replace').read()


def arr(block, key):
    m = re.search(key + r': \*\d+ \{\s*a: ([^}]*)\}', block)
    return [float(v) for v in m.group(1).replace('\n', '').split(',')] if m else []


def blocks(kind):
    """Top-level objects of a kind: (id, name, body)."""
    res = []
    for m in re.finditer(r'\n\t' + kind + r': (\d+), "' + kind + r'::([^"]*)", "[^"]*" \{', txt):
        i, depth = m.end(), 1
        while depth:
            c = txt[i]
            depth += (c == '{') - (c == '}')
            i += 1
        res.append((m.group(1), m.group(2), txt[m.end():i - 1]))
    return res


geos = {i: b for i, _, b in blocks('Geometry')}
models = {i: n for i, n, _ in blocks('Model')}
mats = {i: (n, b) for i, n, b in blocks('Material')}
conn = re.findall(r'C: "OO",(\d+),(\d+)', txt)
geo_model = {g: m for g, m in conn if g in geos}
model_mats = {}
for a, b in conn:                      # material order on a model = order of the connections
    if a in mats and b in models:
        model_mats.setdefault(b, []).append(a)

mtl = os.path.splitext(out)[0] + '.mtl'
with open(mtl, 'w') as f:
    for i, (n, b) in mats.items():
        col = re.search(r'P: "DiffuseColor", "Color", "", "A",([\d.e-]+),([\d.e-]+),([\d.e-]+)', b)
        op = re.search(r'P: "Opacity", "double", "Number", "",([\d.e-]+)', b)
        f.write(f'newmtl {n}\nKd {col.group(1)} {col.group(2)} {col.group(3)}\nd {op.group(1) if op else 1}\n\n')

lines = [f'mtllib {os.path.basename(mtl)}']
vo = to = 0
for gid, body in geos.items():
    mid = geo_model[gid]
    names = [mats[x][0] for x in model_mats.get(mid, [])]
    V, P = arr(body, 'Vertices'), [int(v) for v in arr(body, 'PolygonVertexIndex')]
    UV, UVI = arr(body, 'UV'), [int(v) for v in arr(body, 'UVIndex')]
    MI = [int(v) for v in arr(body, 'Materials')]
    lines.append(f'o {models[mid]}')
    lines += [f'v {V[k]:.6f} {V[k + 1]:.6f} {V[k + 2]:.6f}' for k in range(0, len(V), 3)]
    lines += [f'vt {UV[k]:.6f} {UV[k + 1]:.6f}' for k in range(0, len(UV), 2)]
    poly, pv, cur = 0, 0, None
    face = []
    for k, idx in enumerate(P):
        end = idx < 0
        vi = (-idx - 1) if end else idx
        face.append(f'{vi + 1 + vo}/{UVI[k] + 1 + to}' if UVI else f'{vi + 1 + vo}')
        if end:
            m = names[MI[poly] if len(MI) > 1 else (MI[0] if MI else 0)] if names else None
            if m != cur:
                lines.append(f'usemtl {m}')
                cur = m
            lines.append('f ' + ' '.join(face))
            face, poly = [], poly + 1
    vo += len(V) // 3
    to += len(UV) // 2
    print(models[mid], len(V) // 3, 'verts', poly, 'polys', names)
open(out, 'w').write('\n'.join(lines) + '\n')
print('ok', out)
