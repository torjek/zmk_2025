// One-time (M4 step 6, 2026-11-14): writes layout/us.json, the English (US) MonoTypist, which never had a
// hand-written keymap.
//
//   node tools/make-us-layout.mjs [path to the website's src/data/keyboard.ts]
//
// - Base and blue: the same key codes as the Hungarian keymap. They are key positions; a computer set to
//   English types the English legends from them (Z stays Z, the blue ; ' / . , stay themselves).
// - Red and orange: each of the 24 block keys sends the character its English keycap prints (the
//   website's `us` legends), named for a computer set to US English. A block key with nothing printed
//   on that layer sends nothing (&none).
// - Everything that is not a block key (thumb keys, CTRL, ALT, the 5-way switch, the knob, the "simple"
//   top row and the combos) is copied from layout/hu.json.
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { pretty } from './extract-layout.mjs';

const ROOT = path.resolve(import.meta.dirname, '..');
const SITE = process.argv[2] ?? path.resolve(ROOT, '../honlap/monotypist-site/src/data/keyboard.ts');
const site = await import(pathToFileURL(SITE).href);
const keyboard = JSON.parse(fs.readFileSync(path.join(ROOT, 'layout/keyboard.json'), 'utf8'));
const hu = JSON.parse(fs.readFileSync(path.join(ROOT, 'layout/hu.json'), 'utf8'));

// A character -> its ZMK key code on a computer set to US English (dt-bindings/zmk/keys.h names).
const CODE = {
  ' ': 'SPACE', '"': 'DQT', '*': 'STAR', '>': 'GT', '=': 'EQUAL', '+': 'PLUS', '<': 'LT', '%': 'PRCNT',
  '\\': 'BSLH', '|': 'PIPE', '/': 'FSLH', '!': 'EXCL', '&': 'AMPS', '{': 'LBRC', '[': 'LBKT', '(': 'LPAR',
  ')': 'RPAR', ']': 'RBKT', '}': 'RBRC', '_': 'UNDER', ':': 'COLON', '?': 'QMARK', '#': 'HASH', '@': 'AT',
  ';': 'SEMI', "'": 'SQT', '.': 'DOT', ',': 'COMMA', '-': 'MINUS', '`': 'GRAVE', '~': 'TILDE', '^': 'CARET', '$': 'DLLR',
  ...Object.fromEntries('0123456789'.split('').map((d) => [d, `N${d}`])),
};

const layers = structuredClone(hu.layers);
const cols = keyboard.cols;
const legends = { base: {}, blue: {}, red: {}, orange: {} };
for (const { site: id, position } of keyboard.block) {
  const k = Number(id.slice(1));
  for (const layer of ['base', 'blue', 'red', 'orange']) {
    const ch = site.legends.us[layer][k] ?? '';
    if (ch) legends[layer][position] = ch;
    if (layer === 'red' || layer === 'orange') {
      let binding = '&none';
      if (ch) {
        if (!CODE[ch]) throw new Error(`no key code for "${ch}" (${layer} k${k})`);
        binding = `&kp ${CODE[ch]}`;
      }
      layers[layer][Math.floor(position / cols)][position % cols] = binding;
    }
  }
}

const data = {
  language: 'us',
  source: 'made by tools/make-us-layout.mjs on 2026-11-14: red and orange from the English keycaps, the rest from layout/hu.json',
  sensor: hu.sensor,
  layers,
  simple: hu.simple,
  combos: hu.combos,
  legends,
};
fs.writeFileSync(path.join(ROOT, 'layout/us.json'), pretty(data));
console.log('wrote layout/us.json');
