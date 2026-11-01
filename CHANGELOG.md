# Changelog

版本号规则见 README 的"发布新版本"。

## 0.1.0 — 2026-10-31

第一个可按版本引用的版本。

- 34 张牌面 SVG（带框 + 无框），一条（幺鸡）仍是占位图（一根三节竹）。
- 牌背 `back.svg`、`back_question.svg`，从 mee-tile-maker 移入，改由 `svg_tiles.py` 生成。
- npm 包 `@meemahjong/tiles`：`index.js` 按 MPSZ 编号内嵌全部 SVG，附类型 `index.d.ts`；文件路径 `@meemahjong/tiles/svg/*`。
- 授权：牌面美术 CC BY-NC 4.0，代码 MIT。
- 生成脚本的字体路径可配置（`MEE_FONT_DIR` 或 `fonts/`），Windows 上写出的 SVG 统一为 UTF-8、LF。
