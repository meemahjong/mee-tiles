# Changelog

版本号规则见 README 的"发布新版本"。

## 未发布

- 删除 `svg_tiles_index_mpsz/`（带 `1m–7z` 索引的一套），没有项目使用；`mj34` 仍保留 `mpsz` 索引方案。不影响 npm 包。

## 0.1.0 — 2026-10-31

第一个可按版本引用的版本。

- 34 张牌面 SVG（带框 + 无框），一条（幺鸡）仍是占位图（一根三节竹）。
- 牌背 `back.svg`、`back_question.svg`，从 mee-tile-maker 移入，改由 `svg_tiles.py` 生成。
- npm 包 `@meemahjong/tiles`：`index.js` 按 MPSZ 编号内嵌全部 SVG，附类型 `index.d.ts`；文件路径 `@meemahjong/tiles/svg/*`。
- 授权：牌面美术 CC BY-NC 4.0，代码 MIT。
- 生成脚本的字体路径可配置（`MEE_FONT_DIR` 或 `fonts/`），Windows 上写出的 SVG 统一为 UTF-8、LF。
- `svg_tiles.py` 改为直接读字体的 format 12 cmap：霞鹜文楷的 format 4 子表超过 64 KB，fontTools 解不开。
- 已在 Windows 上验证：用霞鹜文楷 v1.320 / v1.330 Bold 和 DejaVu 2.37 重新生成，204 个 SVG 与提交的逐字节一致；PNG 像素一致。
