
# ================================================================== the floor of the desk corner (step 9, retained 16/11)
# No floor covering: the desk corner stands directly on the lab's wet concrete (hangar_concrete_floor, unchanged).
# What stays from the step is the bin, under the right side of the desk top, in front of the drawer unit.
# Since 16/11 (evening) it is the user's models (assets/newmodels, unzipped into assets/sketchfab/<model>/_archive):
#   Paper Waste Bin (ellieharrodine, CC BY 4.0): a black steel mesh bin, 30 cm high;
#   Crumpled Paper (osamamon, CC BY 4.0): the paper balls, lined notebook paper, about 7 cm.
# A few balls are stacked inside without touching each other or the mesh, one missed on the floor beside it.
# It replaces the lab's grey placeholder cylinder (dk_bin in labo3-v3.py). Option corbeille=0 removes it.
# Placed by labo3-v3.py (desk_concept) and bureau-complet.py through sol_bureau(); proto() comes from objets-poses.py.
CORBEILLE = (0.99, -0.18)        # desk frame, under the right side of the desk top, in front of the drawer unit
H_CORBEILLE = 0.30               # height of the bin; the model's wall goes from r 0.305 H at the foot to r 0.49 H at the rim
H_BOULETTE = 0.062               # height of a paper ball (about 7 cm across)
SPECS['corbeille'] = dict(f=_so('paper-waste-bin', '_archive', 'source', 'Bin.fbx'), height=H_CORBEILLE)
SPECS['boulette'] = dict(f=_so('crumpled-paper', '_archive', 'source', 'CrumpledPaper.glb'), height=H_BOULETTE)
MATS_X['corbeille'] = lambda o, n, v: m_plain('corbeille_fil', (0.017, 0.017, 0.019), 0.4, metal=0.45)
MATS_X['boulette'] = lambda o, n, v: m_tex('boulette', _so('crumpled-paper', '_archive', 'textures',
                                                           'notebook-paper-background-lined-notebook-paper-crumpled-pape.png'), 0.74)
# balls inside the bin, in the bin's frame (x, y, z of the centre): three at the bottom, two above, crossing nothing
# (centres at least 7 cm apart, at least 3.6 cm inside the mesh)
BOULES_DEDANS = [(0.045, 0.0, 0.034), (-0.0225, 0.039, 0.034), (-0.0225, -0.039, 0.034),
                 (0.025, 0.043, 0.094), (-0.05, 0.0, 0.094)]
BOULES_SOL = [(-0.03, -0.25)]    # on the floor, beside the bin (desk frame offset from the bin)


def _inst(key, loc, rot, s=1.0, variant=None, name=None):
    """An instance of a prepared model (objets-poses.py proto) at a world position, without touching the papers' field."""
    c, size = proto(key, variant)
    e = bpy.data.objects.new(name or f'o_{key}', None)
    e.instance_type = 'COLLECTION'
    e.instance_collection = c
    e.location = loc
    e.rotation_euler = rot
    e.scale = (s, s, s)
    return link(e), size


def corbeille(F, x, y, z0=0.0, dedans=BOULES_DEDANS, sol=BOULES_SOL, seed=77):
    """The mesh bin standing at (x, y) of the desk frame, paper balls inside and on the floor."""
    rng = random.Random(seed)
    _inst('corbeille', F.p(x, y, z0), (0, 0, F.r + rad(rng.uniform(0, 360))), name='sol_corbeille')
    _, (bw, bd, bh) = proto('boulette')
    for (dx, dy, dz) in dedans:                # tumbled about its own centre (the model's origin is at its base)
        e = Euler((rng.uniform(0, 6.28), rng.uniform(0, 6.28), rng.uniform(0, 6.28)))
        s = rng.uniform(0.92, 1.04)
        c = F.p(x + dx, y + dy, z0 + 0.003 + dz)
        _inst('boulette', Vector(c) - e.to_matrix() @ Vector((0, 0, bh / 2 * s)), e, s=s, name='sol_boule')
    for (dx, dy) in sol:                       # resting on the floor: base of the model down, turned around z only
        _inst('boulette', F.p(x + dx, y + dy, z0), (0, 0, rng.uniform(0, 6.28)), s=rng.uniform(0.95, 1.05), name='sol_boule')


def sol_bureau(F, h=0.74, hr=0.64, before=None):
    """The retained floor: nothing under the corner (the lab's concrete), only the bin on it."""
    if OPT.get('corbeille', '1') != '0':
        corbeille(F, CORBEILLE[0], CORBEILLE[1], 0.0)
    return []


# (no main: sol_bureau is called by labo3-v3.py and bureau-complet.py; this last line is dropped by the builds)
