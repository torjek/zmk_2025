// Acceptance test of M4 steps 3 and 4: the keymap as built now (its "#include"s of the generated files
// expanded) against the hand-written keymap of a git revision (default: lpos-spike, before generation).
//   node tools/verify-keymap.mjs [revision]
// Passes when every layer table (both SIMPLE_MODE variants) is the same binding for binding, and every
// combo has the same keys, timing and slow-release and sends the same key: an "&lpos" combo must point
// at the very layer and position whose binding the old macro tapped.
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { parseKeymap, comboTarget, LAYERS } from './extract-layout.mjs';

const ROOT = path.resolve(import.meta.dirname, '..');
const rev = process.argv[2] ?? 'lpos-spike';
// The keymap with its quoted includes expanded the way the preprocessor does it: a path is relative to the
// file that includes it, and "#include NAME" takes NAME from an earlier "#define NAME "path"".
function inline(file, defs = {}) {
  return fs.readFileSync(file, 'utf8').replace(/\r\n/g, '\n').split('\n').map((line) => {
    const d = line.match(/^\s*#define\s+(\w+)\s+"([^"]+)"\s*$/);
    if (d) { defs[d[1]] = d[2]; return ''; }
    const i = line.match(/^\s*#include\s+(?:"([^"]+)"|(\w+))\s*$/);
    if (!i) return line;
    const target = i[1] ?? defs[i[2]];
    if (!target) throw new Error(`${file}: #include ${i[2]} is not defined`);
    return inline(path.join(path.dirname(file), target), defs);
  }).join('\n');
}
const variants = (km) => ({ normal: km.layers, simple: Object.fromEntries(LAYERS.map((l) => [l, km.layers[l].map((b, i) => km.simple[l]?.[i] ?? b)])) });

let bad = 0;
const fail = (m) => { console.error('FAIL ' + m); bad++; };
for (const lang of ['hu', 'da']) {
  const rel = `config/boards/shields/v4_2_${lang}/v4_2_${lang}.keymap`;
  const now = parseKeymap(inline(path.join(ROOT, rel)));
  const old = parseKeymap(execFileSync('git', ['show', `${rev}:${rel}`], { cwd: ROOT, encoding: 'utf8' }));
  const [vn, vo] = [variants(now), variants(old)];
  let same = 0;
  for (const v of ['normal', 'simple']) for (const l of LAYERS) vo[v][l].forEach((b, i) => { if (vn[v][l][i] !== b) fail(`${lang} ${v} ${l}[${i}]: ${vn[v][l][i]} != ${b}`); else same++; });
  if (now.sensor !== old.sensor) fail(`${lang} sensor ${now.sensor} != ${old.sensor}`);
  if (now.combos.length !== old.combos.length) fail(`${lang}: ${now.combos.length} combos, before ${old.combos.length}`);
  for (const o of old.combos) {
    const n = now.combos.find((c) => c.name === o.name);
    if (!n) { fail(`${lang} ${o.name} missing`); continue; }
    if (n.positions.join() !== o.positions.join() || n.timeoutMs !== o.timeoutMs || n.slowRelease !== o.slowRelease || n.other.join() !== o.other.join()) fail(`${lang} ${o.name}: keys or timing changed`);
    const [tn, to] = [comboTarget(n, now), comboTarget(o, old)];
    if (tn.why || to.why || tn.layer !== to.layer || tn.position !== to.position) fail(`${lang} ${o.name}: sends something else (${tn.why ?? tn.layer + ' ' + tn.position} / ${to.why ?? to.layer + ' ' + to.position})`);
    if (!/^&lpos /.test(n.binding)) fail(`${lang} ${o.name}: not &lpos (${n.binding})`);
  }
  console.log(`${lang}: ${same} bindings the same, ${now.combos.length} combos checked against ${rev}`);
}
if (bad) { console.error(`${bad} differences`); process.exit(1); }
console.log('PASS');
