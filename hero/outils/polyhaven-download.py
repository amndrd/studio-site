# Download Poly Haven (CC0) models (glTF) and textures into hero/outils/assets/polyhaven.
# usage: python -I polyhaven-download.py <assets_dir> models:id,id,... [models2k:id,...] [textures:id,...]
import json, os, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor

UA = {'User-Agent': 'studio-reference-fetch/1.0'}
root = sys.argv[1]


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def save(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = get(url)
    with open(path, 'wb') as f:
        f.write(data)


def model(aid, res):
    files = json.loads(get(f'https://api.polyhaven.com/files/{aid}'))
    g = files['gltf']
    r = res if res in g else sorted(g.keys())[0]
    entry = g[r]['gltf']
    d = os.path.join(root, 'models', aid)
    save(entry['url'], os.path.join(d, os.path.basename(entry['url'])))
    for rel, inc in entry.get('include', {}).items():
        save(inc['url'], os.path.join(d, rel))
    return f'{aid} ({r})'


def texture(aid, res='2k'):
    files = json.loads(get(f'https://api.polyhaven.com/files/{aid}'))
    d = os.path.join(root, 'textures', aid)
    got = []
    for key, name in [('Diffuse', 'diff'), ('nor_gl', 'nor'), ('Rough', 'rough'), ('Displacement', 'disp'), ('AO', 'ao'), ('Metal', 'metal')]:
        if key in files and res in files[key]:
            fmt = 'jpg' if 'jpg' in files[key][res] else ('png' if 'png' in files[key][res] else list(files[key][res])[0])
            save(files[key][res][fmt]['url'], os.path.join(d, f'{name}.{fmt}'))
            got.append(name)
    return f'{aid}: {",".join(got)}'


jobs = []
for arg in sys.argv[2:]:
    kind, ids = arg.split(':', 1)
    for aid in [i for i in ids.split(',') if i]:
        if kind == 'models':
            jobs.append((model, aid, '1k'))
        elif kind == 'models2k':
            jobs.append((model, aid, '2k'))
        elif kind == 'textures':
            jobs.append((texture, aid, '2k'))


def run(job):
    fn, aid, res = job
    try:
        return fn(aid, res)
    except Exception as e:
        return f'{aid} ERROR {e}'


with ThreadPoolExecutor(8) as ex:
    for line in ex.map(run, jobs):
        print(line, flush=True)
