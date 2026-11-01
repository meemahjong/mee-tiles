"""34-tile contact sheet. 饼 / 条 / 万 naming (not 筒/索/萬); names simplified
(五, 万, 东, 发) while the tile ART stays traditional (伍萬, 東, 發).
Dragons sit on the SAME row as the winds, in 白 发 中 order = MPSZ 5z 6z 7z.
Unicode's block is 中发白, reversed; do not follow it."""
import sys, os
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mj34 import font_file
DIR = sys.argv[1] if len(sys.argv) > 1 else 'own_tiles/full'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'own_tiles/sheet34.png'
B = font_file('NotoSansCJK-Bold.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc')
R = font_file('NotoSansCJK-Regular.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
D = font_file('DejaVuSans.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
TITLE, BOLD = ImageFont.truetype(B,25,index=2), ImageFont.truetype(B,23,index=2)
NAME, FOOT  = ImageFont.truetype(B,17,index=2), ImageFont.truetype(R,15,index=2)
CODE = ImageFont.truetype(D,14)
CN = '一二三四五六七八九'
ROWS = [('饼  Dot',       [(f'dot_{i}',    f'{CN[i-1]}饼', f'{i}p') for i in range(1,10)]),
        ('条  Bamboo',    [(f'bamboo_{i}', f'{CN[i-1]}条', f'{i}s') for i in range(1,10)]),
        ('万  Character', [(f'char_{i}',   f'{CN[i-1]}万', f'{i}m') for i in range(1,10)]),
        ('字牌  Honors',  [('wind_east','东','1z'),('wind_south','南','2z'),
                           ('wind_west','西','3z'),('wind_north','北','4z'),
                           ('dragon_white','白','5z'),('dragon_green','发','6z'),
                           ('dragon_red','中','7z')])]
th, gap, pad, labw, rowpad, capg, SEP = 132, 10, 24, 150, 34, 8, 26
load = lambda n: (lambda im: im.resize((round(im.width*th/im.height), th), Image.LANCZOS))(
    Image.open(f'{DIR}/{n}.png').convert('RGBA'))
rows = [(l, [(k, cn, mp, load(k)) for k, cn, mp in it]) for l, it in ROWS]
mx = max(sum(t.width for *_, t in it)+gap*(len(it)-1)+(SEP if l.startswith('字牌') else 0)
         for l, it in rows)
Ht = pad+38+len(rows)*(th+capg+22+rowpad)+30
s = Image.new('RGBA', (labw+mx+pad*2, Ht), (255,255,255,255)); d = ImageDraw.Draw(s)
d.text((pad,8), '34 张原创牌面  ·  © MEE Mahjong, CC BY-NC 4.0',
       fill=(20,20,20,255), font=TITLE)
y = pad+38
for label, items in rows:
    d.text((pad, y+th//2-14), label, fill=(20,20,20,255), font=BOLD)
    x = pad+labw
    for i, (k, cn, mp, t) in enumerate(items):
        if label.startswith('字牌') and i == 4: x += SEP
        s.paste(t, (x, y), t)
        d.text((x+t.width//2, y+th+5), cn, fill=(20,20,20,255), font=NAME, anchor='ma')
        d.text((x+t.width//2, y+th+26), mp, fill=(140,140,140,255), font=CODE, anchor='ma')
        x += t.width+gap
    y += th+capg+22+rowpad
d.text((pad, Ht-26), '三元牌次序 白 发 中（MPSZ 5z 6z 7z）—— 与风牌同排。'
                     'Unicode 区块为 中发白，方向相反，不采用。',
       fill=(110,110,110,255), font=FOOT)
s.convert('RGB').save(OUT); print(OUT, s.size)
