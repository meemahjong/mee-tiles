"""MEE 麻将牌面 —— 34 张原创牌，参数化生成。

Every number here was measured, not guessed: the pip drills and bamboo joints
come from a photo of a real Chinese set, re-measured on the output each time.
Rebuilt 2026-10-03 after the previous working copy was lost; the constants are
the ones agreed in the design sessions, listed with the reason they hold.

汉字字形用霞鹜文楷 LXGW WenKai (SIL OFL 1.1). 文鼎 PL 中楷是 Arphic Public
License, 它把 "converting format" 直接列为衍生作品, 不能用于本套 —— 这套牌
的全部意义就是无第三方授权约束。
"""
import math, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ---------------------------------------------------------------- geometry
W, H, SS = 400, 507, 4            # final tile px, 4x supersample
FACE   = (253, 253, 251)
BORDER = (205, 205, 198)
BLUE   = (37, 44, 140)
RED    = (214, 37, 24)
GREEN  = (47, 93, 53)

BACK, BACK_EDGE = (31, 158, 116), (23, 122, 89)   # tile back + its edge


def font_file(name, fallback):
    """A font by file name: $MEE_FONT_DIR, then ./fonts/, then the Linux path
    the set was first built with. Fonts are not committed (see README)."""
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
    for d in (os.environ.get('MEE_FONT_DIR'), here):
        if d and os.path.isfile(os.path.join(d, name)):
            return os.path.join(d, name)
    return fallback


KAI   = font_file('LXGWWenKai-Bold.ttf',
                  '/usr/share/fonts/truetype/lxgw-wenkai/LXGWWenKai-Bold.ttf')
KAI_R = font_file('LXGWWenKai-Regular.ttf',
                  '/usr/share/fonts/truetype/lxgw-wenkai/LXGWWenKai-Regular.ttf')
MING  = (font_file('NotoSerifCJK-Bold.ttc',
                   '/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc'), 3)

FONT_PROFILES = {
    'wenkai': (KAI, 0, 1.000),    # (face, faux-bold dilation @EM=1000, em comp.)
    'ming':   (MING, 0, 1.000),
}
# LXGW WenKai (OFL). The OFL FAQ is explicit that glyph outlines used in a
# design stay yours, so the vector set ships with no font obligation.
FONT, FONT_WEIGHT, FONT_EM = FONT_PROFILES['wenkai']

DRAW_FRAME = True                 # False -> bare symbol, for the LaTeX tiles/
w, h = W*SS, H*SS


def blank():
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    if not DRAW_FRAME:
        return im
    d = ImageDraw.Draw(im)
    r, lw = int(w*0.085), max(1, int(w*0.016))
    d.rounded_rectangle([lw//2, lw//2, w-1-lw//2, h-1-lw//2],
                        radius=r, fill=FACE+(255,), outline=BORDER+(255,), width=lw)
    return im


# ------------------------------------------------------------------ 饼 pip
PIP_FR = {3: [1.0, 0.70, 0.54, 0.30, 0.14],
          4: [1.0, 0.76, 0.64, 0.50, 0.38, 0.22, 0.10]}


def pip(d, cx, cy, R, color, bands=3):
    """Concentric-ring pip: thick outer band, inner band, small core."""
    for i, f in enumerate(PIP_FR[bands]):
        r = R*f
        d.ellipse([cx-r, cy-r, cx+r, cy+r],
                  fill=(color if i % 2 == 0 else FACE)+(255,))


# Pip radii are quantised the way a tile maker's drill bits are. THREE drills
# total (一 / 二 / 三-九) -- the maker's rule. The reference photo's own 三饼 is
# 18% larger than its 四-九饼, i.e. that set used four sizes; this is a
# deliberate departure from the photo in favour of the rule.
# Each diameter is the measured one less 0.026 tile widths, because engraved
# tiles bleed paint outward: the design underneath has the pips SEPARATE.
PIP_R     = {1: 0.3825, 2: 0.1857}
PIP_R_MIN = 0.1200


def pip_r(n):
    return w*PIP_R.get(n, PIP_R_MIN)


DOTS = {
    2: ([(0.50, 0.300, BLUE), (0.50, 0.700, GREEN)], 4),
    3: ([(0.30, 0.260, BLUE), (0.50, 0.500, RED), (0.70, 0.740, GREEN)], 3),
    4: ([(0.31, 0.320, BLUE), (0.69, 0.320, GREEN),
         (0.31, 0.680, GREEN), (0.69, 0.680, BLUE)], 3),
    5: ([(0.28, 0.270, BLUE), (0.72, 0.270, GREEN), (0.50, 0.500, RED),
         (0.28, 0.730, GREEN), (0.72, 0.730, BLUE)], 3),
}

DOT_DY = 0.000   # was 0.011, fitted to the reference photo's camera tilt;
                 # drawn tile sets centre the group (Shizhao: -0.001 +/- 0.002)

PITCH = 2.167    # centre spacing in units of R: a 0.167R hairline gap


def grid(cols, rows, R, touch, cx=0.5, cy=0.5, spread=(0.0, 0.0)):
    """Pip/stick centres. touch=True -> the design pitch: close, never meeting."""
    sx = PITCH*R if touch else spread[0]
    sy = PITCH*R if touch else spread[1]
    return [(cx*w + (c-(cols-1)/2)*sx, cy*h + (r-(rows-1)/2)*sy)
            for r in range(rows) for c in range(cols)]


def dot_1():
    """一饼: blue double ring, green field with pale lotus petals, red core."""
    im = blank(); d = ImageDraw.Draw(im)
    cx, cy, R = w/2, h/2, w*PIP_R[1]
    for k, c in ((1.000, BLUE), (0.875, FACE), (0.825, BLUE),
                 (0.745, FACE), (0.705, GREEN)):
        r = R*k
        d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=c+(255,))
    for i in range(10):
        a = math.radians(i*36)
        pr, pw, ph = R*0.455, R*0.115, R*0.235
        px, py = cx + pr*math.cos(a), cy + pr*math.sin(a)
        petal = Image.new('RGBA', (int(pw*2)+8, int(ph*2)+8), (0, 0, 0, 0))
        ImageDraw.Draw(petal).ellipse([4, 4, 4+pw*2, 4+ph*2], fill=FACE+(255,))
        petal = petal.rotate(-math.degrees(a)+90, resample=Image.BICUBIC, expand=True)
        im.alpha_composite(petal, (int(px-petal.width/2), int(py-petal.height/2)))
    d = ImageDraw.Draw(im)
    r = R*0.300
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=RED+(255,))
    arm, th = R*0.280, R*0.075
    d.rectangle([cx-arm, cy-th, cx+arm, cy+th], fill=FACE+(255,))
    d.rectangle([cx-th, cy-arm, cx+th, cy+arm], fill=FACE+(255,))
    return im


def dot_tile(n):
    if n == 1:
        return dot_1()
    im = blank(); d = ImageDraw.Draw(im)
    R = pip_r(n)
    if n in DOTS:
        pts, bands = DOTS[n]
        for x, y, c in pts:
            pip(d, x*w, (y+DOT_DY)*h, R, c, bands=bands)
        return im
    if n == 6:                       # group was 0.027 low; recentred
        for p in grid(2, 1, R, True, 0.5, 0.265+DOT_DY):
            pip(d, p[0], p[1], R, GREEN)
        for p in grid(2, 2, R, True, 0.5, 0.631+DOT_DY):
            pip(d, p[0], p[1], R, RED)
        return im
    if n == 7:                       # group was 0.015 high; recentred
        for i in range(3):
            pip(d, w*(0.265+i*0.235), h*(0.201+DOT_DY+i*0.088), R, GREEN)
        for p in grid(2, 2, R, True, 0.5, 0.695+DOT_DY):
            pip(d, p[0], p[1], R, RED)
        return im
    if n == 8:
        for p in grid(2, 4, R, True, 0.5, 0.5+DOT_DY):
            pip(d, p[0], p[1], R, BLUE)
        return im
    if n == 9:
        for r, c in enumerate([BLUE, RED, GREEN]):
            for p in grid(3, 1, R, True, 0.5, 0.5+DOT_DY + (r-1)*0.270):
                pip(d, p[0], p[1], R, c)
        return im


# ----------------------------------------------------------------- 条 stick
JOINTS      = 3                # every bamboo stick in the suit is three joints
STICK_LONG  = (0.372, 0.139)   # (visible length / tile H, lobe diameter / tile W)
STICK_SHORT = (0.240, 0.122)   # 七条/九条 must fit three rows
WAIST       = 0.65             # neck/lobe diameter (measured 0.64-0.66)
EQUAL_EIGHT = True             # 八条: all 8 sticks the same axis length


def bamboo_path(im, pts, D, color):
    """Bamboo along a polyline, in pixels. `pts` are the END-JOINT centres and
    `D` the lobe diameter. Each straight stroke gets exactly JOINTS lobes, the
    necks are pinched to WAIST, and the engraved groove is ONE continuous slot
    for the whole path."""
    d = ImageDraw.Draw(im)
    d.line(pts, fill=color+(255,), width=int(D*WAIST), joint='curve')
    for a, b in zip(pts, pts[1:]):
        for i in range(JOINTS):
            t = i/(JOINTS-1)
            cx, cy = a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t
            d.ellipse([cx-D/2, cy-D/2, cx+D/2, cy+D/2], fill=color+(255,))
    e = D*0.30
    def push(p, q):
        L = math.hypot(q[0]-p[0], q[1]-p[1]) or 1.0
        return (p[0]+(p[0]-q[0])/L*e, p[1]+(p[1]-q[1])/L*e)
    g = [push(pts[0], pts[1])] + list(pts[1:-1]) + [push(pts[-1], pts[-2])]
    d.line(g, fill=FACE+(255,), width=max(2, int(D*0.17)), joint='curve')


def bamboo(im, p0, p1, D, color):
    bamboo_path(im, [p0, p1], D, color)


def stick_dims(size):
    """(axis length between end joints, lobe diameter) in px."""
    lv, dw = STICK_LONG if size == 'long' else STICK_SHORT
    D = dw*w
    return lv*h - D, D


def vbamboo(im, xf, yf, size, color):
    A, D = stick_dims(size)
    bamboo(im, (xf*w, yf*h - A/2), (xf*w, yf*h + A/2), D, color)


BAMBOO = {
    2: ('long',  [(0.50, 0.280, GREEN), (0.50, 0.720, GREEN)]),
    3: ('long',  [(0.50, 0.270, GREEN), (0.32, 0.730, GREEN), (0.68, 0.730, GREEN)]),
    4: ('long',  [(0.30, 0.280, GREEN), (0.70, 0.280, GREEN),
                  (0.30, 0.720, GREEN), (0.70, 0.720, GREEN)]),
    5: ('long',  [(0.27, 0.270, GREEN), (0.73, 0.270, GREEN), (0.50, 0.500, RED),
                  (0.27, 0.730, GREEN), (0.73, 0.730, GREEN)]),
    6: ('long',  [(x, y, GREEN) for y in (0.280, 0.720) for x in (0.26, 0.50, 0.74)]),
    # 七条/九条: rows recentred (pitch unchanged at 0.2745 / 0.2735)
    7: ('short', [(0.50, 0.2255, RED)] +
                 [(x, y, GREEN) for y in (0.5000, 0.7745) for x in (0.26, 0.50, 0.74)]),
    9: ('short', [(x, y, c) for y in (0.2265, 0.5000, 0.7735)
                  for x, c in ((0.26, GREEN), (0.50, RED), (0.74, GREEN))]),
}

BAM_DY = 0.000   # was 0.019, the same camera-tilt artefact as DOT_DY.
                 # Applied by EVERY bamboo tile now, 八索 included.


def bamboo_1_placeholder():
    """一条 —— PLACEHOLDER: a single three-joint stick, which is literally what
    一条 means and what plainer sets actually draw. The 幺鸡 bird is being drawn
    by hand separately; drop it in here when it arrives. Deliberately NOT a
    half-finished bird: a wrong bird would ship unnoticed, this cannot."""
    im = blank()
    vbamboo(im, 0.50, 0.500+BAM_DY, 'long', GREEN)
    return im


def bamboo_8():
    """八条: eight discrete three-joint sticks -- four forming a W, four an M.
    The outer stroke of each letter is upright, the inner pair slants up to a
    centre apex. All eight share the long stick's axis length (verified against
    the photo: upright and slant are equal axis-to-axis, 133px vs 137px)."""
    im = blank()
    A, D = stick_dims('long')
    run = 0.70*A
    rise = math.sqrt(A*A - run*run)
    x1, x2 = w*0.50 - run, w*0.50 + run
    top = h*(0.095 + BAM_DY) + D/2
    bot = top + A
    apex = bot - rise
    pts = [(x1, top), (x1, bot), (w*0.50, apex), (x2, bot), (x2, top)]
    for path in (pts, [(x, h-y) for x, y in pts]):
        bamboo_path(im, path, D, GREEN)
    return im


def bamboo_tile(n):
    if n == 1:
        return bamboo_1_placeholder()
    if n == 8:
        return bamboo_8()
    im = blank()
    size, pts = BAMBOO[n]
    for x, y, c in pts:
        vbamboo(im, x, y+BAM_DY, size, c)
    return im


# --------------------------------------------------------------- 万 / 字牌
def _ink(ch, font):
    """Render a glyph at a reference em and return its inked mask. FONT_WEIGHT
    thickens the strokes so a delicate Kai face still carries on a projector.
    The mask is cropped before dilating, which keeps it fast."""
    EM = 1000
    f = (ImageFont.truetype(font[0], EM, index=font[1])
         if isinstance(font, tuple) else ImageFont.truetype(font, EM))
    lay = Image.new('L', (EM*2, EM*2), 0)
    ImageDraw.Draw(lay).text((EM, EM), ch, font=f, fill=255, anchor='mm')
    bb = lay.getbbox()
    if not FONT_WEIGHT:
        return lay.crop(bb)
    k = 1 + 2*int(round(FONT_WEIGHT))
    pad = k//2 + 2
    bb = (max(0, bb[0]-pad), max(0, bb[1]-pad),
          min(lay.width, bb[2]+pad), min(lay.height, bb[3]+pad))
    small = lay.crop(bb).filter(ImageFilter.MaxFilter(k))
    return small.crop(small.getbbox())


def _place(im, mask, color, size, xy):
    col = Image.new('RGBA', size, color+(0,))
    col.putalpha(mask.resize(size, Image.LANCZOS))
    im.alpha_composite(col, xy)


def glyph_fit(im, ch, color, width_frac, y_frac, stretch=1.10, anchor='top',
              max_h_frac=None, font=None):
    """Set a glyph to a FIXED INK WIDTH -- the way the reference tiles are laid
    out (numeral and 萬 each keep a constant width, their heights following the
    character). `stretch` widens the glyph relative to its height, matching the
    squat brush proportions of painted tiles."""
    ink = _ink(ch, font or FONT)
    iw, ih = ink.size
    sx = width_frac*w/iw
    sy = sx/stretch
    if max_h_frac and ih*sy > max_h_frac*h:
        k = max_h_frac*h/(ih*sy)
        sx, sy = sx*k, sy*k
    tw_, th_ = max(1, round(iw*sx)), max(1, round(ih*sy))
    y = round(y_frac*h) if anchor == 'top' else round(y_frac*h - th_/2)
    _place(im, ink, color, (tw_, th_), (round(w/2 - tw_/2), y))


def glyph_center(im, ch, color, em_frac, max_w_frac, cy_frac, font=None):
    """Centred glyph sized by em, scaled down if it would exceed max width."""
    ink = _ink(ch, font or FONT)
    iw, ih = ink.size
    s = em_frac*FONT_EM*h/1000.0
    if iw*s > max_w_frac*w:
        s = max_w_frac*w/iw
    tw_, th_ = max(1, round(iw*s)), max(1, round(ih*s))
    _place(im, ink, color, (tw_, th_),
           (round(w/2 - tw_/2), round(cy_frac*h - th_/2)))


# ------------------------------------------------------------------- index
# A Latin index in the top-left corner, for players who do not read Chinese.
INDEX_SCHEME = None                 # None | 'plain' | 'mpsz' | 'learner'
INDEX_FONT   = font_file('DejaVuSans-Bold.ttf',
                         '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
INDEX_H      = 0.070                # cap height / tile height
INDEX_W_MAX  = 0.125
INDEX_X      = 0.048
INDEX_CY     = 0.090

# Schemes drawn at another size: (INDEX_H, INDEX_W_MAX, INDEX_X, INDEX_CY).
# 'learner' is for screens, where a tile can be 40 px wide: bigger than print.
INDEX_GEOMETRY = {'learner': (0.160, 0.210, 0.048, 0.120)}


def index_geometry():
    return INDEX_GEOMETRY.get(INDEX_SCHEME, (INDEX_H, INDEX_W_MAX, INDEX_X, INDEX_CY))


# A kind missing from a scheme gets no index.
IDX = {
    'plain': {'m': [str(i) for i in range(1, 10)],
              'p': [str(i) for i in range(1, 10)],
              's': [str(i) for i in range(1, 10)],
              'wind': ['E', 'S', 'W', 'N'],
              'red': 'R', 'green': 'G', 'white': 'Wh'},
    'mpsz':  {'m': [f'{i}m' for i in range(1, 10)],
              'p': [f'{i}p' for i in range(1, 10)],
              's': [f'{i}s' for i in range(1, 10)],
              'wind': ['1z', '2z', '3z', '4z'],
              'red': '7z', 'green': '6z', 'white': '5z'},
    # On screen for players who do not read Chinese: only the tiles they
    # cannot tell apart by sight. 饼 and 条 can be counted; the dragons differ
    # in colour.
    'learner': {'m': [str(i) for i in range(1, 10)],
                'wind': ['E', 'S', 'W', 'N']},
}


def _idx(kind, i=None):
    if not INDEX_SCHEME:
        return None
    t = IDX[INDEX_SCHEME].get(kind)
    return t[i] if isinstance(t, list) else t


def index_label(im, text, color):
    if not text:
        return
    ih_, iw_max, ix, icy = index_geometry()
    ink = _ink_plain(text, INDEX_FONT)
    iw, ih = ink.size
    s = ih_*h/ih
    if iw*s > iw_max*w:
        s = iw_max*w/iw
    tw_, th_ = max(1, round(iw*s)), max(1, round(ih*s))
    _place(im, ink, color, (tw_, th_),
           (round(ix*w), round(icy*h - th_/2)))


def _ink_plain(text, font_path):
    EM = 400
    f = ImageFont.truetype(font_path, EM)
    lay = Image.new('L', (EM*len(text)*2, EM*3), 0)
    ImageDraw.Draw(lay).text((EM, EM), text, font=f, fill=255, anchor='lt')
    return lay.crop(lay.getbbox())


# -------------------------------------------------------------------- 万子
NUMERALS = '一二三四伍六七八九'      # the tile FACE carries 伍; names use 五


def char_tile(n, font=None):
    im = blank()
    glyph_fit(im, NUMERALS[n-1], BLUE, 0.442, 0.285, stretch=1.165,
              anchor='center', max_h_frac=0.300, font=font)
    glyph_fit(im, '萬',          RED,  0.504, 0.480, stretch=1.13,
              max_h_frac=0.425, font=font)
    index_label(im, _idx('m', n-1), BLUE)
    return im


WINDS = '東南西北'


def wind_tile(ch, font=None):
    im = blank()
    glyph_center(im, ch, BLUE, 0.620, 1.000, 0.500, font)
    index_label(im, _idx('wind', WINDS.index(ch)), BLUE)
    return im


def dragon_red(font=None):
    im = blank()
    glyph_center(im, '中', RED, 0.660, 1.000, 0.500, font)
    index_label(im, _idx('red'), RED)
    return im


def dragon_green(font=None):
    im = blank()
    glyph_center(im, '發', GREEN, 0.620, 1.000, 0.500, font)
    index_label(im, _idx('green'), GREEN)
    return im


def dragon_white():
    """白板: blue double frame with four inner corner accents."""
    im = blank()
    index_label(im, _idx('white'), BLUE)
    d = ImageDraw.Draw(im)
    lw = max(2, int(w*0.038))
    x0, y0, x1, y1 = w*0.185, h*0.115, w*0.815, h*0.885
    d.rounded_rectangle([x0, y0, x1, y1], radius=w*0.030,
                        outline=BLUE+(255,), width=lw)
    ins = w*0.062
    d.rounded_rectangle([x0+ins, y0+ins, x1-ins, y1-ins], radius=w*0.022,
                        outline=BLUE+(255,), width=max(1, int(lw*0.45)))
    t = w*0.072
    for (ax, ay, sx, sy) in ((x0+ins, y0+ins, 1, 1), (x1-ins, y0+ins, -1, 1),
                             (x0+ins, y1-ins, 1, -1), (x1-ins, y1-ins, -1, -1)):
        d.polygon([(ax, ay), (ax+sx*t, ay), (ax, ay+sy*t)], fill=BLUE+(255,))
    return im


# -------------------------------------------------------------------- build
def build(profile='wenkai', outdir='own_tiles/full', index=None):
    global FONT, FONT_WEIGHT, FONT_EM, INDEX_SCHEME
    FONT, FONT_WEIGHT, FONT_EM = FONT_PROFILES[profile]
    INDEX_SCHEME = index
    os.makedirs(outdir, exist_ok=True)
    tiles = {}
    for i in range(1, 10):
        tiles[f'dot_{i}']    = dot_tile(i)
        tiles[f'bamboo_{i}'] = bamboo_tile(i)
        tiles[f'char_{i}']   = char_tile(i)
    for ch, nm in zip(WINDS, ('east', 'south', 'west', 'north')):
        tiles[f'wind_{nm}'] = wind_tile(ch)
    tiles['dragon_red']   = dragon_red()
    tiles['dragon_green'] = dragon_green()
    tiles['dragon_white'] = dragon_white()
    for name, im in tiles.items():
        im.resize((W, H), Image.LANCZOS).save(f'{outdir}/{name}.png')
    INDEX_SCHEME = None
    return len(tiles)
