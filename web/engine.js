/* 海宁吴语修订版转换引擎（浏览器 / Node 通用）。
 * 语义与原生 OpenCC 的 group / match_policy=short_circuit 一致：
 *   1. 先用 CJK_Compatibility_Ideographs.txt 做兼容区规范化；
 *   2. 按配置里的字典顺序逐个尝试，第一个命中的字典胜出（字典内取最长匹配）；
 *   3. 未命中的码点原样输出。
 * 关键：跨字典「不」取全局最长——原生 OpenCC 是逐字典短路，实测 10 万级词表逐字一致。
 * 用 Array.from 按 Unicode 码点切分，「𬮤」这类扩展区汉字不会被拆成代理对。
 */
;(function (root) {
  'use strict';

  function parseTSV(tsv) {
    const map = new Map();
    const lines = tsv.split('\n');
    for (let n = 0; n < lines.length; n++) {
      const line = lines[n];
      if (!line) continue;
      const tab = line.indexOf('\t');
      if (tab < 0) continue;
      map.set(line.slice(0, tab), line.slice(tab + 1));
    }
    return map;
  }

  function buildTrie(map) {
    const rootNode = { c: new Map(), v: undefined };
    map.forEach(function (value, key) {
      let node = rootNode;
      const cps = Array.from(key);
      for (let i = 0; i < cps.length; i++) {
        const ch = cps[i];
        let next = node.c.get(ch);
        if (!next) {
          next = { c: new Map(), v: undefined };
          node.c.set(ch, next);
        }
        node = next;
      }
      node.v = value;
    });
    return rootNode;
  }

  function createEngine(DATA) {
    const tries = new Map();
    const normMap = new Map();
    const schemes = new Map();

    DATA.schemes.forEach(function (s) {
      schemes.set(s.id, s);
      if (s.norm && !normMap.size) {
        parseTSV(DATA.dicts[s.norm]).forEach(function (v, k) { normMap.set(k, v); });
      }
      s.chain.forEach(function (fn) {
        if (!tries.has(fn)) {
          if (!DATA.dicts[fn]) throw new Error('missing dictionary: ' + fn);
          tries.set(fn, buildTrie(parseTSV(DATA.dicts[fn])));
        }
      });
    });

    function convert(text, schemeId) {
      const scheme = schemes.get(schemeId);
      if (!scheme) throw new Error('unknown scheme: ' + schemeId);
      const input = Array.from(String(text == null ? '' : text));
      const src = input.map(function (ch) {
        return normMap.has(ch) ? normMap.get(ch) : ch;
      });
      const normChanged = input.map(function (ch, i) { return src[i] !== ch; });

      const segments = [];
      const hits = [];
      let i = 0;
      while (i < src.length) {
        let matched = false;
        for (let d = 0; d < scheme.chain.length; d++) {
          const fn = scheme.chain[d];
          const trie = tries.get(fn);
          let node = trie;
          let j = i;
          let bestVal;
          let bestEnd = -1;
          while (j < src.length) {
            const next = node.c.get(src[j]);
            if (!next) break;
            node = next;
            j++;
            if (node.v !== undefined) {
              bestVal = node.v;
              bestEnd = j;
            }
          }
          if (bestEnd > i) {
            const key = src.slice(i, bestEnd).join('');
            const changed = bestVal !== key;
            const seg = { text: bestVal, changed: changed, dict: fn, src: key, pos: i };
            segments.push(seg);
            hits.push(seg);
            i = bestEnd;
            matched = true;
            break;
          }
        }
        if (!matched) {
          const changed = normChanged[i];
          const seg = {
            text: src[i], changed: changed,
            dict: changed ? scheme.norm : null,
            src: input[i], pos: i
          };
          segments.push(seg);
          if (changed) hits.push(seg);
          i++;
        }
      }
      return {
        text: segments.map(function (s) { return s.text; }).join(''),
        segments: segments,
        hits: hits,
        scheme: scheme
      };
    }

    function runCases() {
      return DATA.cases.map(function (c) {
        const actual = convert(c.input, c.scheme).text;
        return {
          scheme: c.scheme, input: c.input, expected: c.expected,
          actual: actual, pass: actual === c.expected, source: c.source
        };
      });
    }

    return {
      convert: convert,
      runCases: runCases,
      schemes: DATA.schemes,
      meta: DATA.meta,
      cases: DATA.cases,
      info: function () {
        return {
          dicts: Object.keys(DATA.dicts).length,
          schemes: DATA.schemes.length,
          cases: DATA.cases.length,
          bytes: DATA.meta.total_bytes
        };
      }
    };
  }

  root.HN_ENGINE = { createEngine: createEngine, parseTSV: parseTSV, buildTrie: buildTrie };
})(typeof window !== 'undefined' ? window : globalThis);
