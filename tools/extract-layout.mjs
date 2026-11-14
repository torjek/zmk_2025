// One-time extraction (M4 step 2, 2026-11-14): reads the hand-written keymaps and writes the layout
// files in layout/, which are the single source from then on. Kept for the record and for re-checking;
// tools/gen-keymap.mjs is what turns layout/ back into keymap files.
//
//   node tools/extract-layout.mjs [path to the website's src/data/keyboard.ts]
//
// It also proves the condition for the "&lpos" route: every combo of the form "letter key + thumb key"
// fires a macro that holds the thumb key's layer and taps exactly the binding that layer has at the
// letter key's position. A combo that does not fit is listed and kept as it is.
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const ROOT = path.resolve(import.meta.dirname, '..');
const SHIELDS = path.join(ROOT, 'config/boards/shields');
const OUT = path.join(ROOT, 'layout');
const SITE = process.argv[2] ?? path.resolve(ROOT, '../honlap/monotypist-site/src/data/keyboard.ts');

export const ROWS = 6;
export const COLS = 14;
export const LAYERS = ['base', 'blue', 'red', 'orange'];
export const LAYER_NAME = { base: 'BASE', blue: 'BLUE', red: 'RED', orange: 'ORANGE' };
// The thumb keys and the layer each one holds: Enter (red), Space (blue), Delete (orange).
export const THUMBS = { 60: 'red', 61: 'blue', 75: 'orange' };

const norm = (b) => b.trim().replace(/\s+/g, ' ');
// JSON with short arrays (a matrix row, a combo's positions) kept on one line.
export const pretty = (obj) =>
  JSON.stringify(obj, null, 2).replace(/\[\s*((?:"(?:[^"\\]|\\.)*"|-?\d+)(?:,\s*(?:"(?:[^"\\]|\\.)*"|-?\d+))*)\s*\]/g, (_, inner) => '[' + inner.replace(/,\s+/g, ', ') + ']') + '\n';
const rows = (list) => Array.from({ length: ROWS }, (_, r) => list.slice(r * COLS, (r + 1) * COLS));
// "&kp A &mt RGUI O" -> ["&kp A", "&mt RGUI O"]; some bindings touch ("&kp LEFT_BRACKET&kp SEMI").
export const splitBindings = (text) => text.split('&').map((s) => s.trim()).filter(Boolean).map((s) => norm('&' + s));
const stripComments = (s) => s.replace(/\/\*[\s\S]*?\*\//g, '').replace(/\/\/.*$/gm, '');

export function parseKeymap(text) {
  const src = stripComments(text);
  const layers = {};
  const simple = {};
  let sensor = null;
  for (const name of LAYERS) {
    const m = src.match(new RegExp(`${name}_layer\\s*\\{([\\s\\S]*?)>;\\s*\\};`));
    if (!m) throw new Error(`no ${name}_layer`);
    const body = m[1];
    const s = body.match(/sensor-bindings\s*=\s*<([^>]*)>/);
    if (s && name === 'base') sensor = norm(s[1]);
    const inner = body.slice(body.indexOf('bindings = <', s ? body.indexOf('>;') : 0) + 'bindings = <'.length);
    // SIMPLE_MODE: "#if SIMPLE_MODE == 1 / #else / #endif" chooses a row; keep both.
    const normal = [];
    const simpleList = [];
    let mode = 'both';
    for (const line of inner.split('\n')) {
      const t = line.trim();
      if (/^#if\s+SIMPLE_MODE\s*==\s*1/.test(t)) { mode = 'simple'; continue; }
      if (/^#else/.test(t)) { mode = 'normal'; continue; }
      if (/^#endif/.test(t)) { mode = 'both'; continue; }
      const b = splitBindings(t);
      if (mode !== 'simple') normal.push(...b);
      if (mode !== 'normal') simpleList.push(...b);
    }
    if (normal.length !== ROWS * COLS) throw new Error(`${name}: ${normal.length} bindings, not ${ROWS * COLS}`);
    layers[name] = normal;
    if (simpleList.length === normal.length) {
      const diff = {};
      simpleList.forEach((b, i) => { if (b !== normal[i]) diff[i] = b; });
      if (Object.keys(diff).length) simple[name] = diff;
    }
  }

  const combosBlock = src.match(/combos\s*\{\s*compatible\s*=\s*"zmk,combos";([\s\S]*?)\n\s*\};/);
  const combos = [];
  for (const m of combosBlock[1].matchAll(/(combo_\w+)\s*\{([^}]*)\}\s*;/g)) {
    const props = m[2];
    const get = (k) => props.match(new RegExp(`${k}\\s*=\\s*<([^>]*)>`))?.[1].trim();
    combos.push({
      name: m[1],
      positions: get('key-positions').split(/\s+/).map(Number),
      timeoutMs: Number(get('timeout-ms')),
      slowRelease: /\bslow-release\b/.test(props),
      binding: norm(get('bindings')),
      // anything else this combo sets, kept word for word
      other: props.split(';').map((p) => p.trim()).filter((p) => p && !/^(key-positions|timeout-ms|bindings|slow-release)\b/.test(p)),
    });
  }

  const macros = {};
  for (const m of src.matchAll(/(\w+):\s*\w+\s*\{\s*compatible\s*=\s*"zmk,behavior-macro";([\s\S]*?)\};/g)) {
    const b = m[2].match(/bindings\s*=\s*([\s\S]*?);/)?.[1] ?? '';
    macros[m[1]] = [...b.matchAll(/<([^>]*)>/g)].map((x) => norm(x[1]));
  }
  return { layers, simple, sensor, combos, macros };
}

// What a combo sends, when it has the "&lpos" shape: { layer, position } of the key it taps.
export function comboTarget(c, km) {
  const thumb = c.positions.find((p) => THUMBS[p]);
  const key = c.positions.find((p) => !THUMBS[p]);
  if (c.positions.length !== 2 || thumb === undefined || key === undefined) return { why: 'not one key and one thumb key' };
  const layer = THUMBS[thumb];
  const lp = c.binding.match(/^&lpos (\w+) (\d+)$/);
  if (lp) {
    if (lp[1] !== LAYER_NAME[layer] || Number(lp[2]) !== key) return { why: `&lpos ${lp[1]} ${lp[2]} does not match the keys` };
    return { layer, position: key };
  }
  const macro = c.binding.match(/^&(\w+)$/)?.[1];
  const steps = macro && km.macros[macro];
  if (!steps) return { why: `binding ${c.binding} is not a macro` };
  const want = [`&macro_press &mo ${LAYER_NAME[layer]}`, null, '&macro_pause_for_release', `&macro_release &mo ${LAYER_NAME[layer]}`];
  if (steps.length !== 4 || steps[0] !== want[0] || steps[2] !== want[2] || steps[3] !== want[3] || !steps[1].startsWith('&macro_tap ')) {
    return { why: `macro ${macro} has another shape: ${steps.join(', ')}` };
  }
  const tapped = norm(steps[1].slice('&macro_tap '.length));
  const held = km.layers[layer][key];
  if (tapped !== held) return { why: `macro ${macro} taps ${tapped}, but ${layer} has ${held} at ${key}` };
  return { layer, position: key, macro };
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const site = await import(pathToFileURL(SITE).href);
  fs.mkdirSync(OUT, { recursive: true });

  // The physical keys: matrix position <-> the website's key names.
  const keyboard = {
    about: 'MonoTypist left hand: the ZMK matrix is 6 rows by 14 columns (row * 14 + column); the left half uses columns 0 to 6.',
    rows: ROWS,
    cols: COLS,
    layers: LAYERS.map((id, i) => ({ id, index: i, name: LAYER_NAME[id] })),
    thumbs: Object.entries(THUMBS).map(([p, layer]) => ({ position: Number(p), id: { red: 'enter', blue: 'space', orange: 'delete' }[layer], layer })),
    // The website's block keys k0..k23 (4 rows of 6) at their matrix positions.
    block: Array.from({ length: 24 }, (_, k) => ({ site: `k${k}`, position: Math.floor(k / 6) * COLS + (k % 6) })),
    other: [
      { id: 'ctrl', position: 57 }, { id: 'alt', position: 58 },
      { id: 'five-way-up', position: 6 }, { id: 'five-way-down', position: 20 }, { id: 'five-way-right', position: 34 }, { id: 'five-way-left', position: 48 },
    ],
  };
  fs.writeFileSync(path.join(OUT, 'keyboard.json'), pretty(keyboard));

  const report = [];
  for (const lang of ['hu', 'da']) {
    const file = path.join(SHIELDS, `v4_2_${lang}`, `v4_2_${lang}.keymap`);
    const km = parseKeymap(fs.readFileSync(file, 'utf8'));
    const combos = km.combos.map((c) => {
      const t = comboTarget(c, km);
      const out = { name: c.name, positions: c.positions, timeoutMs: c.timeoutMs, slowRelease: c.slowRelease };
      if (c.other.length) out.other = c.other;
      if (t.why) { out.binding = c.binding; report.push(`${lang} ${c.name}: kept as it is (${t.why})`); }
      return out;
    });
    const fit = combos.filter((c) => !c.binding).length;
    report.push(`${lang}: ${fit} of ${combos.length} combos have the "&lpos" shape`);
    // The printed legend of each block key, per layer, from the website's layout data.
    const legends = Object.fromEntries(LAYERS.map((l) => [l, Object.fromEntries(keyboard.block.map(({ site: s, position }) => [position, site.legends[lang][l][Number(s.slice(1))] ?? '']).filter(([, v]) => v))]));
    const data = {
      language: lang,
      source: `config/boards/shields/v4_2_${lang}/v4_2_${lang}.keymap, extracted on 2026-11-14 by tools/extract-layout.mjs`,
      sensor: km.sensor,
      // Each layer as 6 rows of 14 bindings, in matrix order.
      layers: Object.fromEntries(LAYERS.map((l) => [l, rows(km.layers[l])])),
      simple: km.simple,
      combos,
      legends,
    };
    fs.writeFileSync(path.join(OUT, `${lang}.json`), pretty(data));
  }
  console.log(report.join('\n'));
}
