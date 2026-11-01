"""True-vector SVG for all 34 tiles, generated from mj34's own constants so the
SVG and the raster set cannot drift.

Three families, three techniques:
  饼  concentric circles + rotated ellipses (一饼's petals)
  条  rod (stroke 0.65D) + 3 lobes (circles D) + groove (white stroke 0.17D,
      ends pushed out 0.30D). PIL uses BUTT caps -- also the SVG default -- so
      the groove terminates inside the end lobe, as engraved.
  万/字 glyph outlines via fontTools; the faux-bold dilation mj34 does with
      MaxFilter becomes a round stroke of width 2*weight (dilation by a disc
      == Minkowski sum == fill + round stroke).

Optional Latin index, same schemes and placement as the raster set.
"""
import math, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mj34
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.misc.transform import Transform

HEX   = lambda c: '#%02X%02X%02X' % c
GREEN, RED, BLUE = HEX(mj34.GREEN), HEX(mj34.RED), HEX(mj34.BLUE)
FACE, BORDER     = HEX(mj34.FACE), HEX(mj34.BORDER)
W, H, SS = mj34.W, mj34.H, mj34.SS
LW, RAD  = W*0.016, W*0.085
f  = lambda v: ('%.3f' % v).rstrip('0').rstrip('.')
CM = {mj34.GREEN: GREEN, mj34.RED: RED, mj34.BLUE: BLUE}
CN = '一二三四五六七八九'

FRAME = (f'<rect x="{f(LW/2)}" y="{f(LW/2)}" width="{f(W-LW)}" height="{f(H-LW)}" '
         f'rx="{f(RAD)}" fill="{FACE}" stroke="{BORDER}" stroke-width="{f(LW)}"/>')

_FC = {}
def _ft(path, idx=0):
    k = (path, idx)
    if k not in _FC:
        _FC[k] = TTFont(path, fontNumber=idx) if path.endswith('.ttc') else TTFont(path)
    return _FC[k]

_CM = {}
def cmap(ft):
    """Unicode -> glyph name. LXGW WenKai's format-4 subtable is over 64 KB, so
    its 16-bit length field overflows and fontTools cannot decode the cmap
    table; fall back to reading the (3, 10) format-12 subtable directly."""
    if id(ft) not in _CM:
        try:
            _CM[id(ft)] = ft.getBestCmap()
        except IndexError:
            raw = ft.reader['cmap']; order = ft.getGlyphOrder(); m = {}
            for i in range(struct.unpack('>HH', raw[:4])[1]):
                pid, eid, off = struct.unpack('>HHI', raw[4+8*i:12+8*i])
                if (pid, eid) != (3, 10): continue
                for j in range(struct.unpack('>I', raw[off+12:off+16])[0]):
                    a, b, g = struct.unpack('>III', raw[off+16+12*j:off+28+12*j])
                    m.update((c, order[g+c-a]) for c in range(a, b+1))
            assert m, 'no usable cmap'
            _CM[id(ft)] = m
    return _CM[id(ft)]

def glyph(ch, spec):
    """-> (path d in EM=1000 y-down units, ink bbox before dilation)"""
    path, idx = spec if isinstance(spec, tuple) else (spec, 0)
    ft = _ft(path, idx); k = 1000.0/ft['head'].unitsPerEm
    gn = cmap(ft)[ord(ch)]; gs = ft.getGlyphSet()
    p = SVGPathPen(gs); gs[gn].draw(TransformPen(p, Transform(k, 0, 0, -k, 0, 0)))
    b = BoundsPen(gs); gs[gn].draw(b)
    x0, y0, x1, y1 = b.bounds
    return p.getCommands(), (x0*k, -y1*k, x1*k, -y0*k)

def _emit(d, wt, col, tx, ty, sx, sy, ox, oy):
    st = (f' stroke="{col}" stroke-width="{f(2*wt)}" '
          f'stroke-linejoin="round" stroke-linecap="round"') if wt else ''
    return (f'<g transform="translate({f(tx)} {f(ty)}) scale({f(sx)} {f(sy)}) '
            f'translate({f(-ox)} {f(-oy)})"><path d="{d}" fill="{col}"{st}/></g>')

def fit(ch, spec, wt, col, width_frac, y_frac, stretch, anchor='top', max_h_frac=None):
    d, (x0, y0, x1, y1) = glyph(ch, spec)
    ox, oy = x0-wt, y0-wt
    iw, ih = (x1-x0)+2*wt, (y1-y0)+2*wt
    sx = width_frac*W/iw; sy = sx/stretch
    if max_h_frac and ih*sy > max_h_frac*H:
        k = max_h_frac*H/(ih*sy); sx, sy = sx*k, sy*k
    tw, th = iw*sx, ih*sy
    y = y_frac*H if anchor == 'top' else y_frac*H - th/2
    return _emit(d, wt, col, W/2-tw/2, y, sx, sy, ox, oy)

def center(ch, spec, wt, em, col, em_frac, max_w_frac, cy_frac):
    d, (x0, y0, x1, y1) = glyph(ch, spec)
    ox, oy = x0-wt, y0-wt
    iw, ih = (x1-x0)+2*wt, (y1-y0)+2*wt
    s = em_frac*em*H/1000.0
    if iw*s > max_w_frac*W: s = max_w_frac*W/iw
    tw, th = iw*s, ih*s
    return _emit(d, wt, col, W/2-tw/2, cy_frac*H-th/2, s, s, ox, oy)

# ------------------------------------------------------------------- index
def index_svg(text, col):
    """Latin index in the top-left, matching mj34.index_label's placement."""
    if not text: return []
    ft = _ft(mj34.INDEX_FONT); k = 1000.0/ft['head'].unitsPerEm
    gs = ft.getGlyphSet(); cm = cmap(ft); hm = ft['hmtx']
    parts = []; adv = 0.0
    minx = miny = 1e9; maxx = maxy = -1e9
    for ch in text:
        gn = cm.get(ord(ch))
        if gn is None: continue
        p = SVGPathPen(gs)
        gs[gn].draw(TransformPen(p, Transform(k, 0, 0, -k, adv, 0)))
        if p.getCommands(): parts.append(p.getCommands())
        b = BoundsPen(gs); gs[gn].draw(b)
        if b.bounds:
            a_, b_, c_, d_ = b.bounds
            minx = min(minx, adv+a_*k); maxx = max(maxx, adv+c_*k)
            miny = min(miny, -d_*k);    maxy = max(maxy, -b_*k)
        adv += hm[gn][0]*k
    if not parts: return []
    iw, ih = maxx-minx, maxy-miny
    ih_, iw_max, ix, icy = mj34.index_geometry()
    s = ih_*H/ih
    if iw*s > iw_max*W: s = iw_max*W/iw
    tx = ix*W; ty = icy*H - ih*s/2
    return [f'<g transform="translate({f(tx)} {f(ty)}) scale({f(s)}) '
            f'translate({f(-minx)} {f(-miny)})">'
            f'<path d="{" ".join(parts)}" fill="{col}"/></g>']

# --------------------------------------------------------------------- 饼
def pip(cx, cy, R, col, bands=3):
    return [f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(R*fr)}" '
            f'fill="{col if i%2==0 else FACE}"/>'
            for i, fr in enumerate(mj34.PIP_FR[bands])]

def grid(cols, rows, R, cx=0.5, cy=0.5):
    sx = sy = mj34.PITCH*R
    return [(cx*W+(c-(cols-1)/2)*sx, cy*H+(r-(rows-1)/2)*sy)
            for r in range(rows) for c in range(cols)]

def rosette():
    R, CX, CY = W*mj34.PIP_R[1], W/2, H/2
    g = [f'<circle cx="{f(CX)}" cy="{f(CY)}" r="{f(R*k)}" fill="{c}"/>'
         for k, c in ((1.0, BLUE), (0.875, FACE), (0.825, BLUE),
                      (0.745, FACE), (0.705, GREEN))]
    pr, pw, ph = R*0.455, R*0.115, R*0.235
    for i in range(10):
        a = math.radians(i*36)
        px, py = CX+pr*math.cos(a), CY+pr*math.sin(a)
        g.append(f'<ellipse cx="{f(px)}" cy="{f(py)}" rx="{f(pw)}" ry="{f(ph)}" '
                 f'fill="{FACE}" transform="rotate({f(i*36-90)} {f(px)} {f(py)})"/>')
    arm, th = R*0.280, R*0.075
    g += [f'<circle cx="{f(CX)}" cy="{f(CY)}" r="{f(R*0.300)}" fill="{RED}"/>',
          f'<rect x="{f(CX-arm)}" y="{f(CY-th)}" width="{f(arm*2)}" height="{f(th*2)}" fill="{FACE}"/>',
          f'<rect x="{f(CX-th)}" y="{f(CY-arm)}" width="{f(th*2)}" height="{f(arm*2)}" fill="{FACE}"/>']
    return g

def dot_sym(n):
    if n == 1: return rosette()
    R = W*mj34.PIP_R.get(n, mj34.PIP_R_MIN); DY = mj34.DOT_DY; g = []
    if n in mj34.DOTS:
        pts, bands = mj34.DOTS[n]
        for x, y, c in pts: g += pip(x*W, (y+DY)*H, R, CM[c], bands)
    elif n == 6:
        for p in grid(2, 1, R, 0.5, 0.265+DY): g += pip(*p, R, GREEN)
        for p in grid(2, 2, R, 0.5, 0.631+DY): g += pip(*p, R, RED)
    elif n == 7:
        for i in range(3): g += pip(W*(0.265+i*0.235), H*(0.201+DY+i*0.088), R, GREEN)
        for p in grid(2, 2, R, 0.5, 0.695+DY): g += pip(*p, R, RED)
    elif n == 8:
        for p in grid(2, 4, R, 0.5, 0.5+DY): g += pip(*p, R, BLUE)
    elif n == 9:
        for r, c in enumerate([BLUE, RED, GREEN]):
            for p in grid(3, 1, R, 0.5, 0.5+DY+(r-1)*0.270): g += pip(*p, R, c)
    return g

# --------------------------------------------------------------------- 条
def stick_dims(size):
    lv, dw = mj34.STICK_LONG if size == 'long' else mj34.STICK_SHORT
    D = dw*W
    return lv*H - D, D

def pathd(pts): return 'M'+' L'.join(f'{f(x)},{f(y)}' for x, y in pts)

def bamboo_path(pts, D, col):
    g = []
    neck = int(D*SS*mj34.WAIST)/SS          # int() parity with the raster
    g.append(f'<path d="{pathd(pts)}" fill="none" stroke="{col}" '
             f'stroke-width="{f(neck)}" stroke-linejoin="round" stroke-linecap="butt"/>')
    for a, b in zip(pts, pts[1:]):
        for i in range(mj34.JOINTS):
            t = i/(mj34.JOINTS-1)
            cx, cy = a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t
            g.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(D/2)}" fill="{col}"/>')
    e = D*0.30
    def push(p, q):
        L = math.hypot(q[0]-p[0], q[1]-p[1]) or 1.0
        return (p[0]+(p[0]-q[0])/L*e, p[1]+(p[1]-q[1])/L*e)
    gp = [push(pts[0], pts[1])]+list(pts[1:-1])+[push(pts[-1], pts[-2])]
    gw = max(2, int(D*SS*0.17))/SS
    g.append(f'<path d="{pathd(gp)}" fill="none" stroke="{FACE}" '
             f'stroke-width="{f(gw)}" stroke-linejoin="round" stroke-linecap="butt"/>')
    return g

def vbamboo(xf, yf, size, col):
    A, D = stick_dims(size)
    return bamboo_path([(xf*W, yf*H-A/2), (xf*W, yf*H+A/2)], D, col)

def bamboo_sym(n):
    DY = mj34.BAM_DY
    if n == 1:                               # placeholder: one 3-joint stick
        return vbamboo(0.50, 0.500+DY, 'long', GREEN)
    if n == 8:
        g = []; A, D = stick_dims('long')
        run = 0.70*A; rise = math.sqrt(A*A-run*run)
        x1, x2 = W*0.50-run, W*0.50+run
        top = H*(0.095+DY)+D/2; bot = top+A; apex = bot-rise
        pts = [(x1, top), (x1, bot), (W*0.50, apex), (x2, bot), (x2, top)]
        for path in (pts, [(x, H-y) for x, y in pts]): g += bamboo_path(path, D, GREEN)
        return g
    size, pts = mj34.BAMBOO[n]; g = []
    for x, y, c in pts: g += vbamboo(x, y+DY, size, CM[c])
    return g

# ----------------------------------------------------------------- 万 / 字
def white_frame():
    g = []; lw = max(2, W*0.038)
    x0, y0, x1, y1 = W*0.185, H*0.115, W*0.815, H*0.885
    # PIL draws its outline INSIDE the box; SVG centres the stroke on the path,
    # so every rect is inset by half the stroke width to land in the same place.
    h1 = lw/2
    g.append(f'<rect x="{f(x0+h1)}" y="{f(y0+h1)}" width="{f(x1-x0-lw)}" '
             f'height="{f(y1-y0-lw)}" rx="{f(max(0,W*0.030-h1))}" fill="none" '
             f'stroke="{BLUE}" stroke-width="{f(lw)}"/>')
    ins = W*0.062; lw2 = max(1, lw*0.45); h2 = lw2/2
    g.append(f'<rect x="{f(x0+ins+h2)}" y="{f(y0+ins+h2)}" width="{f(x1-x0-2*ins-lw2)}" '
             f'height="{f(y1-y0-2*ins-lw2)}" rx="{f(max(0,W*0.022-h2))}" fill="none" '
             f'stroke="{BLUE}" stroke-width="{f(lw2)}"/>')
    t = W*0.072
    for ax, ay, sx, sy in ((x0+ins, y0+ins, 1, 1), (x1-ins, y0+ins, -1, 1),
                           (x0+ins, y1-ins, 1, -1), (x1-ins, y1-ins, -1, -1)):
        g.append(f'<polygon points="{f(ax)},{f(ay)} {f(ax+sx*t)},{f(ay)} '
                 f'{f(ax)},{f(ay+sy*t)}" fill="{BLUE}"/>')
    return g

# -------------------------------------------------------------------- build
# ------------------------------------------------------------------- backs
# Backs are complete tiles with their own plate, so they have no _symbol twin.
BACK_FRAME = FRAME.replace(FACE, HEX(mj34.BACK)).replace(BORDER, HEX(mj34.BACK_EDGE))
QUESTION = [f'<path d="M138 188 C138 138 172 106 206 106 C244 106 270 132 270 168 '
            f'C270 204 242 218 224 238 C210 253 206 266 206 292" fill="none" '
            f'stroke="{FACE}" stroke-width="36" stroke-linecap="round" '
            f'stroke-linejoin="round"/>',
            f'<circle cx="206" cy="372" r="23" fill="{FACE}"/>']

def wrap(title, body, frame=True):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'width="{W}" height="{H}">\n  <title>{title}</title>\n  '
            + '\n  '.join(([FRAME] if frame else [])+body) + '\n</svg>\n')

def write(path, text):
    # UTF-8 and LF on every platform: Windows would otherwise pick its ANSI
    # code page (the titles are Chinese) and CRLF.
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(text)

def build_backs(outdir='svg_tiles'):
    os.makedirs(outdir, exist_ok=True)
    write(f'{outdir}/back.svg', wrap('牌背 / back', [BACK_FRAME], False))
    write(f'{outdir}/back_question.svg',
          wrap('问号牌背 / back with question mark', [BACK_FRAME]+QUESTION, False))

def build(outdir='svg_tiles', profile='wenkai', index=None):
    spec, wt, em = mj34.FONT_PROFILES[profile]
    mj34.INDEX_SCHEME = index
    os.makedirs(outdir, exist_ok=True)
    def put(key, title, body):
        write(f'{outdir}/{key}.svg', wrap(title, body, True))
        write(f'{outdir}/{key}_symbol.svg', wrap(title, body, False))
    for n in range(1, 10):
        put(f'{n}p', f'{CN[n-1]}饼 / {n}p',
            dot_sym(n) + index_svg(mj34._idx('p', n-1), BLUE))
        put(f'{n}s', f'{CN[n-1]}条 / {n}s',
            bamboo_sym(n) + index_svg(mj34._idx('s', n-1), GREEN))
        put(f'{n}m', f'{CN[n-1]}万 / {n}m',
            [fit(mj34.NUMERALS[n-1], spec, wt, BLUE, 0.442, 0.285, 1.165, 'center', 0.300),
             fit('萬', spec, wt, RED, 0.504, 0.480, 1.13, 'top', 0.425)]
            + index_svg(mj34._idx('m', n-1), BLUE))
    for i, ch in enumerate('東南西北'):
        put(f'{i+1}z', f'{ch} / {i+1}z',
            [center(ch, spec, wt, em, BLUE, 0.620, 1.000, 0.500)]
            + index_svg(mj34._idx('wind', i), BLUE))
    put('5z', '白 / 5z', white_frame() + index_svg(mj34._idx('white'), BLUE))
    put('6z', '发 / 6z', [center('發', spec, wt, em, GREEN, 0.620, 1.000, 0.500)]
        + index_svg(mj34._idx('green'), GREEN))
    put('7z', '中 / 7z', [center('中', spec, wt, em, RED, 0.660, 1.000, 0.500)]
        + index_svg(mj34._idx('red'), RED))
    mj34.INDEX_SCHEME = None
    n = len([x for x in os.listdir(outdir) if x.endswith('.svg')])
    tot = sum(os.path.getsize(f'{outdir}/{x}') for x in os.listdir(outdir))
    return n, tot

if __name__ == '__main__':
    for out, idx in (('svg_tiles', None),
                     ('svg_tiles_index_plain', 'plain'),
                     ('svg_tiles_index_learner', 'learner')):
        n, t = build(out, index=idx)
        print('%-24s %2d files, %.0f KB' % (out, n, t/1024))
    build_backs('svg_tiles')
    import build_index
    build_index.main()
