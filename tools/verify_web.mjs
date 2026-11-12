/**
 * 网页转换引擎的 Node 回归测试。
 *
 *   node tools/verify_web.mjs
 *
 * 两道校验：
 *   1. 跑完 web/dicts.js 内置的 41 条用例（tests/cases.json + 补齐方向的用例）；
 *   2. 用各方案字典的键拼出约 10 万字语料，转换后与 tests/web_corpus.json
 *      里由「原生 Python OpenCC」算出的 md5 对比，确保短路语义没有跑偏。
 *
 * 纯前端页面本身不需要 Node；此脚本只用于开发者本地/CI 自检。
 */
import { createRequire } from 'node:module';
import { createHash } from 'node:crypto';
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const require = createRequire(import.meta.url);
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

require(path.join(ROOT, 'web', 'dicts.js'));
require(path.join(ROOT, 'web', 'engine.js'));
const DATA = globalThis.HN_DATA;
const engine = globalThis.HN_ENGINE.createEngine(DATA);

let failed = 0;

// ---- 1. 用例 ---------------------------------------------------------------
const results = engine.runCases();
const passed = results.filter(r => r.pass).length;
console.log('用例: %d/%d 通过', passed, results.length);
results.filter(r => !r.pass).forEach(r => {
  failed++;
  console.log('  FAIL [%s] %s', r.scheme, r.input.slice(0, 60));
  console.log('    expected: %s', r.expected);
  console.log('    actual  : %s', r.actual);
});

// ---- 2. 全量语料与原生 OpenCC 对照 -----------------------------------------
const goldenPath = path.join(ROOT, 'tests', 'web_corpus.json');
if (!existsSync(goldenPath)) {
  console.log('语料基准缺失（tests/web_corpus.json），跳过；可跑 tools/make_web_corpus.py 生成。');
} else {
  const golden = JSON.parse(readFileSync(goldenPath, 'utf8'));
  const step = golden.step;
  const schemeMap = new Map(DATA.schemes.map(s => [s.id, s]));
  Object.keys(golden.schemes).forEach(id => {
    const scheme = schemeMap.get(id);
    if (!scheme) {
      console.log('  FAIL [%s] 页面缺少该方案', id);
      failed++;
      return;
    }
    const parts = [];
    scheme.chain.forEach(fn => {
      let i = 0;
      globalThis.HN_ENGINE.parseTSV(DATA.dicts[fn]).forEach((_v, k) => {
        if (i % step === 0 || Array.from(k).length === 1) parts.push(k);
        i++;
      });
    });
    const corpus = parts.join(' ');
    const out = engine.convert(corpus, id).text;
    const md5 = createHash('md5').update(out, 'utf8').digest('hex');
    const ok = md5 === golden.schemes[id].md5;
    if (!ok) failed++;
    console.log('语料 %s %s 字  md5 %s  %s',
      id.padEnd(18), String(Array.from(corpus).length).padStart(7),
      md5.slice(0, 12), ok ? 'OK' : 'DIFF');
  });
}

const info = engine.info();
console.log('字典 %d 个 / 方案 %d 个 / 用例 %d 条 / 字典 %d 字节',
  info.dicts, info.schemes, info.cases, info.bytes);
console.log(failed === 0 ? 'ALL OK' : 'FAILED: ' + failed);
process.exit(failed === 0 ? 0 : 1);
