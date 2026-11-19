# Textures of the desk objects (step 8), from the packaging captures (papiers-contenus/capture-emballages.sh):
#   canette-{ampere,nord,minuit}.png  the can prints, transparent where the aluminium stays bare (mapped by the shader
#                                      in objets-poses.py onto the side strip of the Sketchfab cans' own UVs);
#   manchon-pente.png                  the flat kraft sleeve of the takeaway cup (273 x 42 mm), the Pente stamp printed in
#                                      black ink with the unevenness of a rubber stamp (cylindrical UVs made by objets-poses.py);
#   escultura-diffuse-4k.jpg / -normal-4k.jpg   the sculpture scan textures brought down from 8K (lighter renders).
# usage: python -I textures_objets.py <hero_dir>
import os, sys
import numpy as np
from PIL import Image, ImageFilter

H = os.path.abspath(sys.argv[1])
CAP = os.path.join(H, 'outils', 'papiers-contenus', 'captures')
OUT = os.path.join(H, 'outils', 'textures-bureau', 'objets')
SKF = os.path.join(H, 'outils', 'assets', 'sketchfab')
os.makedirs(OUT, exist_ok=True)
RNG = np.random.default_rng(8)


def noise(h, w, scale, oct=4):
    a = np.zeros((h, w), np.float32)
    amp = 1.0
    for o in range(oct):
        s = max(2, int(scale / (2 ** o)))
        n = RNG.normal(0, 1, (h // s + 2, w // s + 2)).astype(np.float32)
        a += amp * np.asarray(Image.fromarray(n).resize((w, h), Image.BICUBIC))
        amp *= 0.5
    return (a - a.min()) / (np.ptp(a) + 1e-6)


# ------------------------------------------------------------------ cans
for k in ('ampere', 'nord', 'minuit'):
    im = Image.open(os.path.join(CAP, f'emb-{k}.png')).convert('RGBA')
    im.save(os.path.join(OUT, f'canette-{k}.png'), optimize=True)

# ------------------------------------------------------------------ cup sleeve: kraft + stamped ink (the flat sleeve, 273 x 42 mm)
W, Hs = 4096, 630
kraft = np.ones((Hs, W, 3), np.float32) * np.array([164, 120, 80], np.float32)
kraft *= (0.93 + 0.12 * noise(Hs, W, 260)[..., None])
fib = np.clip(RNG.normal(128, 40, (Hs, W)), 0, 255).astype(np.uint8)
fib = (np.asarray(Image.fromarray(fib).filter(ImageFilter.GaussianBlur(0.8))).astype(np.float32) - 128) / 40
kraft *= (1 + 0.035 * fib[..., None])
xx = np.arange(W, dtype=np.float32)
kraft *= (1 + 0.03 * np.sin(xx / W * 2 * np.pi * 240))[None, :, None]          # the fine vertical ribs of the sleeve (1.1 mm)
for _ in range(700):                                                             # darker fibres
    x, y = RNG.integers(0, W), RNG.integers(0, Hs)
    L = RNG.integers(4, 18)
    kraft[y:y + 1, x:x + L] *= RNG.uniform(0.84, 0.93)
st = Image.open(os.path.join(CAP, 'emb-pente.png')).convert('RGBA').resize((W, Hs), Image.LANCZOS)
a = np.asarray(st)[..., 3]
a = np.asarray(Image.fromarray(a).filter(ImageFilter.GaussianBlur(0.8))).astype(np.float32) / 255
cov = 0.62 + 0.38 * noise(Hs, W, 120, 3)                                         # uneven pressure of the stamp
cov = np.clip(cov - (noise(Hs, W, 6, 2) < 0.22) * 0.45, 0, 1)                    # tiny ink dropouts
ink = np.array([34, 28, 24], np.float32)
m = (a * cov)[..., None] * 0.92
kraft = kraft * (1 - m) + (kraft * ink / 255 * 0.9) * m
Image.fromarray(np.clip(kraft, 0, 255).astype(np.uint8)).save(os.path.join(OUT, 'manchon-pente.png'), optimize=True)

# ------------------------------------------------------------------ sculpture scan, 8K -> 4K
src = os.path.join(SKF, 'escultura-museu-dart-jaume-morera', '_archive', 'inner')
for name, out in (('MALL1392_LP_u1_v1_diffuse_3.png', 'escultura-diffuse-4k.jpg'), ('MALL1392_LP_u1_v1_normal.jpg', 'escultura-normal-4k.jpg')):
    p = os.path.join(OUT, out)
    if not os.path.exists(p):
        Image.MAX_IMAGE_PIXELS = None
        Image.open(os.path.join(src, name)).convert('RGB').resize((4096, 4096), Image.LANCZOS).save(p, quality=92)
print('ok', sorted(os.listdir(OUT)))
