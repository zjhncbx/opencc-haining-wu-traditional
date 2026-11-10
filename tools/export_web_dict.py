#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""导出纯 JSON 字典，供浏览器 / Node 端不依赖原生 OpenCC 的辞典系统集成。

    python tools/export_web_dict.py

产物（不纳入 Git，按需生成）：
    dist/hn-dicts.json   { meta, s2hn, hn2s, t2hn }
前端可直接 import 该 JSON，用 examples/js/convert.mjs 的最长匹配转换器。
"""
from __future__ import annotations
import io
import json
import os
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OPENCC = os.path.join(ROOT, 'opencc')
DIST = os.path.join(ROOT, 'dist')

# 顺序即优先级：靠前的字典先写入，靠后的同名 key 覆盖前者。
# 使用时按「最长匹配」而非写入顺序，因此这里只做合并即可。
BUNDLES = {
    's2hn': ['STCharacters.txt', 'STPhrases.txt', 'HNPhrases.txt'],
    'hn2s': ['TSCharacters.txt', 'TSPhrases.txt'],
    't2hn': ['TGCharacters.txt', 'TGPhrases.txt', 'HNGuard.txt'],
}


def read_dict(path):
    d = OrderedDict()
    with io.open(os.path.join(OPENCC, path), 'r', encoding='utf-8') as f:
        for ln in f:
            ln = ln.rstrip('\r\n')
            if not ln.strip() or ln.lstrip().startswith('#') or '\t' not in ln:
                continue
            k, v = ln.split('\t', 1)
            # OpenCC 单字表可有多个候选值，Web 版取首选
            d[k] = v.split(' ')[0]
    return d


def main():
    os.makedirs(DIST, exist_ok=True)
    result = OrderedDict()
    result['meta'] = {
        'project': 'OpenCC大陆标准繁体海宁吴语修订',
        'generator': 'tools/export_web_dict.py',
        'matching': 'longest-match-first (phrase before character)',
        'note': '多候选值取首选；如需 jieba 分词或候选字功能，请使用原生 OpenCC 配置。',
    }
    for name, files in BUNDLES.items():
        merged = OrderedDict()
        for fn in files:
            merged.update(read_dict(fn))
        result[name] = merged
        print('%-6s %6d entries  (max key length %d)' % (
            name, len(merged), max(len(k) for k in merged)))
    out = os.path.join(DIST, 'hn-dicts.json')
    with io.open(out, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(result, f, ensure_ascii=False, separators=(',', ':'))
    print('written: %s (%d bytes)' % (out, os.path.getsize(out)))


if __name__ == '__main__':
    main()
