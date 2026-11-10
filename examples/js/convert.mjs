/**
 * 纯 JS / 浏览器端的海宁吴语修订版繁简转换器。
 *
 * 前置：python tools/export_web_dict.py  生成 ../dist/hn-dicts.json
 * 用法：
 *   import { loadDictionaries, createConverter } from './convert.mjs';
 *   const d = await loadDictionaries('../../dist/hn-dicts.json');
 *   const { toTraditional, toSimplified, normalize } = createConverter(d);
 *   toTraditional('合并 并非 吃饭 个中 真个');  // 合併 並非 喫飯 箇中 真个
 *
 * 采用「最长匹配优先」，与 OpenCC 的 group / short_circuit 语义一致：
 * 词表先于字表命中，未命中的码点原样输出。使用 Array.from 按 Unicode
 * 码点切分，可正确处理「𬮤」等扩展区汉字。
 */
import { readFile } from 'node:fs/promises';

export async function loadDictionaries(path) {
  const raw = await readFile(new URL(path, import.meta.url), 'utf8');
  return JSON.parse(raw);
}

/** 最长匹配转换器。dict: { key: value }，key/value 均为字符串。 */
export function makeConverter(dict) {
  const maxLen = Object.keys(dict).reduce((m, k) => Math.max(m, Array.from(k).length), 1);
  const lookup = new Map(Object.entries(dict));

  return function convert(text) {
    const cps = Array.from(text);
    const out = [];
    let i = 0;
    while (i < cps.length) {
      let hit = false;
      const upper = Math.min(maxLen, cps.length - i);
      for (let n = upper; n > 0; n--) {
        const seg = cps.slice(i, i + n).join('');
        const val = lookup.get(seg);
        if (val !== undefined) {
          out.push(val);
          i += n;
          hit = true;
          break;
        }
      }
      if (!hit) {
        out.push(cps[i]);
        i += 1;
      }
    }
    return out.join('');
  };
}

export function createConverter(bundle) {
  return {
    /** 简体 -> 修订版大陆标准繁体（辞典词目/释义/例句录入时用） */
    toTraditional: makeConverter(bundle.s2hn),
    /** 修订版大陆标准繁体 -> 简体（对外检索、简化显示时用） */
    toSimplified: makeConverter(bundle.hn2s),
    /** 任意繁体（港台/异体/旧字形）-> 修订版大陆标准繁体（导入旧资料时用） */
    normalize: makeConverter(bundle.t2hn),
  };
}

// 直接运行时给出演示输出
if (process.argv[1] && import.meta.url.endsWith(process.argv[1].replace(/\\/g, '/'))) {
  const bundle = await loadDictionaries('../../dist/hn-dicts.json');
  const { toTraditional, toSimplified, normalize } = createConverter(bundle);
  const sample = '并州 合并 并非 吃饭 个中 真个 面向 刚才 内哄 阁楼 内𬮤';
  console.log('s2hn :', toTraditional(sample));
  console.log('hn2s :', toSimplified(toTraditional(sample)));
  console.log('t2hn :', normalize('一併 並不 喫飯 纔來 面嚮 箇中 內閤'));
}
