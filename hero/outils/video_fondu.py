# The construction video as a loop, with a crossfade (retained 19/11 over the three ways of taking the desk away, A B C):
# over the last second of the final shot (the desk set, poste), the image fades into the video's first image, the empty
# light grid. The opening shot starts from rest (the camera still), so fading into its first image held still is
# seamless, and the opening shot then plays whole. The last image of the file is ~96 % the first one, so the loop never
# shows the same image twice. Same length and order as the validated video (montage.json), same encoding.
# Frames: blender/rendus-video.sh final render, folders final-eevee, final-eevee2, final-cycles (the last one wins, as in
# video_montage.py). Output: the looped video in hero/bureau/video/<nom>.mp4; le-raccord.mp4 (the last 3 s, then the
# first 3 s: the seam) and six images of the crossfade in _bruts/video/fondu/<sortie>/, to check. No text on any image.
# usage: python -I video_fondu.py <hero_dir> [n=24 (frames of the crossfade)]
#   [dossiers=final-eevee,final-eevee2,final-cycles (frame folders in animatique, the last one wins)]
#   [sortie=boucle (name of the check folder)] [nom=la-construction-du-bureau-en-boucle]
import os, sys, json, shutil, subprocess, tempfile
from PIL import Image

H = os.path.abspath(sys.argv[1])
OPT = dict(a.split('=', 1) for a in sys.argv[2:])
N = int(OPT.get('n', 24))
A = os.path.join(H, 'outils', 'blender', '_bruts', 'video', 'animatique')
OUT = os.path.join(H, 'bureau', 'video')                                   # the looped video
CHK = os.path.join(A, '..', 'fondu', OPT.get('sortie', 'boucle'))          # the seam and the crossfade, to check
NOM = OPT.get('nom', 'la-construction-du-bureau-en-boucle')
FF = shutil.which('ffmpeg') or '/opt/homebrew/bin/ffmpeg'
FP = shutil.which('ffprobe') or '/opt/homebrew/bin/ffprobe'

frames = {}
for d in OPT.get('dossiers', 'final-eevee,final-eevee2,final-cycles').split(','):
    p = os.path.join(A, d)
    for f in os.listdir(p):
        if f[:4].isdigit() and f.endswith('.png') and os.path.getsize(os.path.join(p, f)) > 0:
            frames[int(f[:4])] = os.path.join(p, f)
order = json.load(open(os.path.join(A, 'montage.json')))['ordre']
seq = [frames[n] for a, b in order for n in range(a, b + 1)]
first = Image.open(seq[0]).convert('RGB')
W, Hh = first.size
os.makedirs(os.path.join(CHK, 'images'), exist_ok=True)


def encode(src_dir, out, crf):
    subprocess.run([FF, '-y', '-loglevel', 'error', '-framerate', '24', '-i', os.path.join(src_dir, '%05d.png'),
                    '-vf', f'scale={W}:{Hh}:flags=lanczos,setsar=1,format=yuv420p', '-r', '24', '-c:v', 'libx264',
                    '-preset', 'slow', '-crf', crf, '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], check=True)


tmp = tempfile.mkdtemp(prefix='fondu-')
loop = list(seq)
for k in range(1, N + 1):                            # the last N images fade into the first one
    i = len(seq) - N + k - 1
    im = Image.blend(Image.open(seq[i]).convert('RGB'), first, k / (N + 1))
    p = os.path.join(tmp, f'fondu-{k:02d}.png')
    im.save(p)
    loop[i] = p
for k, s in enumerate(loop):
    os.symlink(s, os.path.join(tmp, f'{k:05d}.png'))
encode(tmp, os.path.join(OUT, NOM + '.mp4'), '14')

seam = loop[-72:] + loop[:72]                        # the seam: the last 3 s, then the first 3 s
tmp2 = tempfile.mkdtemp(prefix='raccord-')
for k, s in enumerate(seam):
    os.symlink(s, os.path.join(tmp2, f'{k:05d}.png'))
encode(tmp2, os.path.join(CHK, 'le-raccord.mp4'), '16')

for k, i in enumerate([len(seq) - N - 1] + [len(seq) - N - 1 + round(j * N / 4) for j in range(1, 5)] + [0]):
    shutil.copy2(loop[i], os.path.join(CHK, 'images', f'{k + 1}.png'))
shutil.rmtree(tmp)
shutil.rmtree(tmp2)

r = subprocess.run([FP, '-v', 'error', '-select_streams', 'v:0', '-count_frames', '-show_entries',
                    'stream=width,height,nb_read_frames', '-of', 'csv=p=0',
                    os.path.join(OUT, NOM + '.mp4')], capture_output=True, text=True)
w, h, nf = r.stdout.strip().split(',')
print('boucle', f'{w}x{h}', nf, 'images', round(int(nf) / 24, 2), 's ; fondu', N, 'images', round(N / 24, 2), 's')
