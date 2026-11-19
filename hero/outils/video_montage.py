# The montage of the construction video. 18/11, after the user's review: the two Blender-window scenes are out; the
# presentation of the finished desk (its shots come after the end in the 3D timeline, the desk standing still) is put
# back between the wide shot where the LEDs come on and the final shot of the desk set (poste). The order comes from
# montage.json, written by blender/video/main.py next to the frame folders (_bruts/video/animatique/montage.json):
# {"ordre": [[first, last], ...]} in Blender frame numbers.
# The frames come from one or more folders of NNNN.png at 24 fps (the final render: EEVEE, Cycles, the re-rendered
# frames; for a frame number in several folders, the last folder wins); all are brought to the size of the first.
# usage: python -I video_montage.py <frames_dir[,frames_dir...]> <out.mp4> [crf=16]
import os, sys, json, shutil, subprocess, tempfile
from PIL import Image

DIRS = [os.path.abspath(d) for d in sys.argv[1].split(',')]
OUT = os.path.abspath(sys.argv[2])
CRF = sys.argv[3] if len(sys.argv) > 3 else '16'
FF = shutil.which('ffmpeg') or '/opt/homebrew/bin/ffmpeg'
FP = shutil.which('ffprobe') or '/opt/homebrew/bin/ffprobe'

frames = {}
for d in DIRS:
    for f in os.listdir(d):
        if f[:4].isdigit() and f.endswith('.png') and os.path.getsize(os.path.join(d, f)) > 0:
            frames[int(f[:4])] = os.path.join(d, f)
js = os.path.join(os.path.dirname(DIRS[0]), 'montage.json')
spec = json.load(open(js)) if os.path.exists(js) else {}
order = spec.get('ordre') or [[min(frames), max(frames)]]
seq = [n for a, b in order for n in range(a, b + 1)]
missing = [n for n in seq if n not in frames]
assert not missing, f'{len(missing)} frames missing, from {missing[0]}'

W, H = Image.open(frames[seq[0]]).size
tmp = tempfile.mkdtemp(prefix='montage-')
for k, n in enumerate(seq):
    os.symlink(frames[n], os.path.join(tmp, f'{k:05d}.png'))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
# setsar=1: the PNGs carry a pixel density (SAR 2834:2834)
subprocess.run([FF, '-y', '-loglevel', 'error', '-framerate', '24', '-i', os.path.join(tmp, '%05d.png'),
                '-vf', f'scale={W}:{H}:flags=lanczos,setsar=1,format=yuv420p', '-r', '24', '-c:v', 'libx264',
                '-preset', 'slow', '-crf', CRF, '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OUT], check=True)
shutil.rmtree(tmp)
r = subprocess.run([FP, '-v', 'error', '-select_streams', 'v:0', '-count_frames', '-show_entries',
                    'stream=width,height,nb_read_frames', '-of', 'csv=p=0', OUT], capture_output=True, text=True)
w, h, nf = r.stdout.strip().split(',')
t, pos = 0, []
for a, b in order:                                   # where each segment sits in the video
    pos.append((a, b, round(t / 24, 2), round((t + b - a + 1) / 24, 2)))
    t += b - a + 1
print('montage', OUT, f'{w}x{h}', nf, 'frames', round(int(nf) / 24, 2), 's', pos)
