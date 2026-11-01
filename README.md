# MEE 麻将牌面 — 34 张原创牌

Mahjong (Education Edition) · 麻将（教育版）

重建于 2026-10-03。全部图案自主设计，不含任何第三方美术素材。
这个仓库是牌面的唯一源头，各项目按版本号引用，不再各自拷贝。

授权：牌面美术 **CC BY-NC 4.0**（非商业使用免费，须署名；商用请联系），代码 **MIT**。
详见 [`LICENSE-ART.md`](LICENSE-ART.md) 和 [`LICENSE`](LICENSE)。

---

## 在项目里使用

在 `package.json` 里按标签引用（需要本机装有 git）：

    "dependencies": {
      "@meemahjong/tiles": "github:meemahjong/mee-tiles#v0.1.0"
    }

```ts
import { TILE_CODES, symbols, tiles, backs, isTileCode } from '@meemahjong/tiles';

symbols['5z'];   // 白板，无框透明的完整 <svg> 字符串
tiles['1m'];     // 一万，带牌框
backs.plain;     // 牌背；backs.question 是带问号的牌背
```

- 牌面以字符串形式编进应用，**运行时不联网**，离线可用。
- 也可以直接引用文件：`@meemahjong/tiles/svg/1m_symbol.svg`（对应仓库里的 `svg_tiles/`）。
- 编号是 MPSZ：`1m–9m` 万、`1p–9p` 饼、`1s–9s` 条、`1z–7z` = 东 南 西 北 白 发 中。`TILE_CODES` 按 m → p → s → z 排列；理牌时怎么排由应用决定。
- 所有 SVG 的 viewBox 都是 `0 0 400 507`，不含 `id`、字体或外部资源，同一页面放多张不会冲突。
- 牌底色是 `FACE_COLOR`（`#FDFDFB`），替换它可以换牌底颜色。
- 使用者不需要 Python 和字体：生成好的 SVG 和 `index.js` 都已提交。

## 目录

| 路径 | 内容 |
|---|---|
| `mj34.py` | **源头**。所有牌面的参数化定义，34 张栅格由此生成 |
| `svg_tiles.py` | 真矢量 SVG 生成器（读 `mj34` 的常数，不另立一套），也生成牌背和 `index.js` |
| `build_index.py` | 把 `svg_tiles/` 里的 SVG 内嵌成 `index.js` |
| `index.js` / `index.d.ts` | npm 包的入口（生成）/ 类型（手写） |
| `test/` | `node --test`：检查 `index.js` 和 SVG 一致、对外路径可用 |
| `sheet34.py` | 34 张对照表 |
| `build_latex_tiles.py` | 生成 CTAN `mahjong` 宏包的 drop-in `tiles/` |
| `own_tiles/full/` | 34 张 PNG（400×507） |
| `svg_tiles/` | 34 张 SVG ×2（带框 + `_symbol` 无框透明），加牌背 `back.svg`、`back_question.svg` |
| `svg_tiles_index_plain/` | 同上，带 `1-9 / E S W N / R G Wh` 索引（打印用，不进 npm 包） |
| `svg_tiles_index_mpsz/` | 同上，带 `1m-9m / 1z-7z` 索引（打印用，不进 npm 包） |
| `latex_tiles/tiles/` | 41 个 PDF，**全部真矢量**，104 KB |

## 重新生成

使用者不需要做这一步，只有改牌面时才需要。

1. 装依赖：`pip install -r requirements.txt`
2. 准备字体（不提交进仓库）：放进 `fonts/`，或用环境变量 `MEE_FONT_DIR` 指向字体所在目录。找不到时退回 Linux 的系统路径。
   - `LXGWWenKai-Bold.ttf`：[霞鹜文楷](https://github.com/lxgw/LxgwWenKai)，牌面汉字。**v1.330 是最后一个有 Bold 的版本**（v1.500 起改名为 Medium，字形不同，不要用）。v1.320 和 v1.330 生成的 SVG 都和仓库里的逐字节一致。
   - `DejaVuSans-Bold.ttf`：带索引的两套 SVG，[DejaVu 2.37](https://github.com/dejavu-fonts/dejavu-fonts/releases)
   - `NotoSansCJK-Bold.ttc`、`NotoSansCJK-Regular.ttc`、`DejaVuSans.ttf`：只有对照表 `sheet34.py` 用
3. 运行（Windows 上把 `python3` 换成 `py`）：

        python3 -c "import mj34; mj34.build()"
        python3 svg_tiles.py          # 同时生成牌背和 index.js
        python3 sheet34.py
        python3 build_latex_tiles.py  # 需要 Cairo 库
        node --test

只手改了 SVG 时，运行 `python3 build_index.py` 重新生成 `index.js`。

注意：换了字体版本，字形轮廓可能变化。重新生成后用 `git diff` 检查 SVG，只应该在改动的牌上有差异。

## 发布新版本

1. 改脚本 → 重新生成（见上）→ `node --test` 通过。
2. 改 `package.json` 的 `version`，再运行一次 `python3 build_index.py`（`index.js` 里的 `VERSION` 跟着变）。
3. 在 `CHANGELOG.md` 记下改了什么。
4. 提交，打标签，推送：

        git tag v0.2.0
        git push origin main --tags

5. 各项目把依赖里的 `#v0.1.0` 改成新标签，重新安装。

版本号规则：只改画面（例如换上幺鸡）或新增导出 → 升 minor；修错 → 升 patch；改文件名、删除导出 → 升 major。

## LaTeX 用法

把 `latex_tiles/tiles/` 拷到 .tex 同级目录下，命名为 `tiles/`，宏包会优先用它。

    \usepackage{mahjong}
    \mahjong[1.4cm][1]{123456789m}

**必须传 scale = 1**：宏包默认 0.75，而这些符号是按整张牌的尺寸画的。

## 设计决定（都是量出来的，不是拍脑袋）

**三个钻头** — 一饼 / 二饼 / 三至九饼，共三种圆。实测 42 个圆落在
0.2437–0.2462 牌宽，离散 0.0025（4× 超采样的一个像素，取整极限）。
参考实物照片里三饼比四–九饼大 18%，即那副牌用了四种尺寸；这里**有意
偏离照片**，采用制作逻辑上的三钻头规则。

**颜料溢出** — 照片里圆是相接的，但那是上色时溢出。设计上它们分离。
每个直径都减去了 0.026 牌宽（实物每侧约 0.13 mm 的溢出）。
校验方式：连通块数必须等于圆数。

**图案居中** — `DOT_DY` 与 `BAM_DY` 曾是 0.011 / 0.019，是从照片里拟合
出来的。但照片五行全部呈同向偏差，是相机俯视立体牌的产物。Shizhao 的
矢量图（非拍摄）实测居中到 −0.001 ± 0.002。故二者归零，34 张的上下边距
全部为 0。

**竹** — 每根 = 竹杆（线宽 0.65D）+ 3 个鼓包（直径 D）+ 白色凹槽
（线宽 0.17D，两端外推 0.30D）。PIL 用平头帽，SVG 默认同样是平头，
所以凹槽收在端部鼓包内侧。八条是同样三步套在 W / M 两条 5 点折线上，
八根等长。

**字体** — 霞鹜文楷 LXGW WenKai Bold，**SIL OFL 1.1**。OFL FAQ 明确：
把字形转成轮廓用在设计里，作品著作权仍属作者，不需署名、不需以 OFL 发布。
**文鼎 PL 中楷（Arphic Public License）不可用** — APL 把 "converting
format" 直接列为衍生作品，没有针对美术作品的例外。

**三元牌次序** 白 发 中 = MPSZ `5z 6z 7z`。Unicode 区块是 中发白，
方向相反，**不采用** —— 打牌逻辑（宝牌指示牌的循环）依赖这个次序。

**命名** 饼 / 条 / 万（不用筒 / 索）。标注用简体（五、万、东、发），
牌面刻繁体（伍萬、東、發）。

**牌背** — 绿色 `#1F9E74`，边框 `#177A59`，和 LaTeX 的 `Back` 同色。
牌背是完整的牌（自带底板），没有 `_symbol` 版本。

## 待办

**一条（幺鸡）目前是占位图** — 一根三节竹。这正是"一条"的字面意思，
朴素的牌也确实这么画，所以它能用、不会出错。手绘的幺鸡到了之后替换
`mj34.bamboo_1_placeholder()` 和 `svg_tiles.bamboo_sym(1)` 即可，
其余 33 张不受影响。换好后按上面的流程发布新版本（升 minor）。

**向画师要的交付**：Plain SVG，描边转轮廓，画布 400×507，只画鸟不画牌框，
背景透明，鸟占画布高 62–70%、宽 ≤75%，上下留白相等，
配色 `#2F5D35` / `#D62518` / `#252C8C`，最细部件 ≥10 单位（0.33 mm）。
**并书面确认著作权转让给 MEE Mahjong、且非描摹图标库**，否则不能按本仓库的授权发布。

## 尺寸参考

牌面 400 × 507 单位（横宽比 0.789）。讲义上实印 13.3 × 16.9 mm。
最细实心部件下限 0.025 牌宽 = 10 单位 = 0.33 mm。

调色：`#2F5D35` 绿 · `#D62518` 红 · `#252C8C` 蓝 · `#FDFDFB` 牌面 · `#CDCDC6` 边框
