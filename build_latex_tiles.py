"""Drop-in tiles/ for the CTAN `mahjong` package -- ALL 41 files true vector,
straight from svg_tiles/*_symbol.svg. No second source of truth, no raster, and
no font obligation (glyphs are LXGW WenKai, OFL).

The package composites a BARE SYMBOL onto its own Front, so these carry no
frame; pass scale 1 (`\\mahjong[<height>][1]{...}`) because they are drawn at
full tile size while the package default is 0.75.

MPSZ naming, with the dragon order every engine relies on: 5z=白 6z=發 7z=中.
"""
import os, shutil, sys, cairosvg
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mj34
SVG, OUT = 'svg_tiles', 'latex_tiles/tiles'
W, H = mj34.W, mj34.H
HEX = lambda c: '#%02X%02X%02X' % c
f = lambda v: ('%.3f' % v).rstrip('0').rstrip('.')
LW, RAD = W*0.016, W*0.085

def shell(fill, stroke, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'width="{W}" height="{H}"><title>{title}</title>'
            f'<rect x="{f(LW/2)}" y="{f(LW/2)}" width="{f(W-LW)}" height="{f(H-LW)}" '
            f'rx="{f(RAD)}" fill="{fill}" stroke="{stroke}" stroke-width="{f(LW)}"/></svg>')

if __name__ == '__main__':
    if os.path.isdir(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    n = 0
    for suit in ('p','s','m'):
        for i in range(1,10):
            src = f'{SVG}/{i}{suit}_symbol.svg'
            # Every tile must have a vector source. A missing one is a build
            # error, not something to paper over: an earlier version silently
            # fell back and wrote 五条 into the 5m slot.
            assert os.path.exists(src), f'no vector for {i}{suit}'
            cairosvg.svg2pdf(url=src, write_to=f'{OUT}/mahjong-{i}{suit}.pdf'); n += 1
    for i in range(1,8):
        src = f'{SVG}/{i}z_symbol.svg'
        assert os.path.exists(src), src
        cairosvg.svg2pdf(url=src, write_to=f'{OUT}/mahjong-{i}z.pdf'); n += 1
    for red, normal in (('0m','5m'), ('0p','5p'), ('0s','5s')):
        shutil.copy(f'{OUT}/mahjong-{normal}.pdf', f'{OUT}/mahjong-{red}.pdf'); n += 1
    for nm, body in (('Front', shell(HEX(mj34.FACE), HEX(mj34.BORDER), 'Front')),
                     ('Blank', shell(HEX(mj34.FACE), HEX(mj34.BORDER), 'Blank')),
                     ('Back',  shell(HEX(mj34.BACK), HEX(mj34.BACK_EDGE), 'Back')),
                     ('Space', f'<svg xmlns="http://www.w3.org/2000/svg" '
                               f'viewBox="0 0 {W} {H}" width="{W}" height="{H}"/>')):
        cairosvg.svg2pdf(bytestring=body.encode(), write_to=f'{OUT}/mahjong-{nm}.pdf'); n += 1
    tot = sum(os.path.getsize(f'{OUT}/{x}') for x in os.listdir(OUT))
    print('%d pdfs -> %s   全部真矢量   共 %.0f KB' % (n, OUT, tot/1024))
