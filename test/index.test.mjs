// Checks index.js against the SVG files and the package's public paths.
// Run: node --test
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import * as pkg from '@meemahjong/tiles';

const root = new URL('../', import.meta.url);
const read = (path) => readFileSync(new URL(path, root), 'utf8');
const inline = (raw) => raw.trim().replace(/>\s+</g, '><');
const manifest = JSON.parse(read('package.json'));

test('34 MPSZ codes, 5z 6z 7z = 白 发 中', () => {
  const { TILE_CODES } = pkg;
  assert.equal(TILE_CODES.length, 34);
  assert.equal(new Set(TILE_CODES).size, 34);
  assert.deepEqual(TILE_CODES.slice(0, 2), ['1m', '2m']);
  assert.deepEqual(TILE_CODES.slice(-3), ['5z', '6z', '7z']);
  assert.match(pkg.symbols['5z'], /<title>白 \/ 5z<\/title>/);
  assert.match(pkg.symbols['6z'], /<title>发 \/ 6z<\/title>/);
  assert.match(pkg.symbols['7z'], /<title>中 \/ 7z<\/title>/);
});

test('isTileCode', () => {
  assert.ok(pkg.isTileCode('9s'));
  assert.ok(pkg.isTileCode('7z'));
  for (const s of ['8z', '0m', 'm1', '1x', '', 'x']) assert.ok(!pkg.isTileCode(s), s);
});

test('inlined strings match the SVG files', () => {
  for (const code of pkg.TILE_CODES) {
    assert.equal(pkg.symbols[code], inline(read(`svg_tiles/${code}_symbol.svg`)), code);
    assert.equal(pkg.tiles[code], inline(read(`svg_tiles/${code}.svg`)), code);
  }
  assert.equal(pkg.backs.plain, inline(read('svg_tiles/back.svg')));
  assert.equal(pkg.backs.question, inline(read('svg_tiles/back_question.svg')));
  assert.deepEqual(Object.keys(pkg.symbols), [...pkg.TILE_CODES]);
  assert.deepEqual(Object.keys(pkg.tiles), [...pkg.TILE_CODES]);
});

test('every SVG is standalone, 400×507, and safe to inline', () => {
  const all = [...Object.values(pkg.symbols), ...Object.values(pkg.tiles), ...Object.values(pkg.backs)];
  for (const s of all) {
    assert.ok(s.startsWith('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 507"'));
    assert.ok(!/\sid=/.test(s), 'ids would collide when several tiles share a page');
    assert.ok(!/<text|<image|href=/.test(s), 'no fonts or external resources');
  }
  assert.deepEqual(pkg.TILE_SIZE, { width: 400, height: 507 });
  assert.ok(pkg.tiles['1m'].includes(pkg.FACE_COLOR));
});

test('VERSION follows package.json', () => {
  assert.equal(pkg.VERSION, manifest.version);
});

test('public file paths resolve through exports', () => {
  for (const name of ['1m.svg', '1m_symbol.svg', '7z_symbol.svg', 'back.svg', 'back_question.svg']) {
    const path = fileURLToPath(import.meta.resolve(`@meemahjong/tiles/svg/${name}`));
    assert.ok(existsSync(path), name);
  }
});
