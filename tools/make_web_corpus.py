#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用原生 Python OpenCC 生成 tests/web_corpus.json（网页引擎的语料基准）。

    python tools/make_web_corpus.py
    node tools/verify_web.mjs

仅在改动字表词表后需要重跑。需要 `pip install opencc`（>=1.3.2）。
语料：逐方案按 tools/build_web.py 的 chain 顺序，每个字典每隔 7 条取 1 条，
另加全部单字键，用空格拼接；转换结果取 UTF-8 的 md5。
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys

import opencc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import build_web  # noqa: E402

STEP = 7


def keys_of(fn):
    with io.open(os.path.join(ROOT, 'opencc', fn), encoding='utf-8') as f:
        for ln in f:
            ln = ln.rstrip('\r\n')
            if not ln.strip() or ln.lstrip().startswith('#') or '\t' not in ln:
                continue
            yield ln.split('\t', 1)[0]


def main():
    out = {
        'note': '由 tools/make_web_corpus.py 用原生 Python OpenCC 生成；改动字表词表后重跑。',
        'step': STEP,
        'schemes': {},
    }
    for item in build_web.SCHEMES:
        sid = item['id']
        _norm, chain = build_web.chain_of(sid)
        parts = []
        for fn in chain:
            for i, k in enumerate(keys_of(fn)):
                if i % STEP == 0 or len(k) == 1:
                    parts.append(k)
        corpus = ' '.join(parts)
        converted = opencc.OpenCC(os.path.join(ROOT, 'opencc', sid + '.json')).convert(corpus)
        md5 = hashlib.md5(converted.encode('utf-8')).hexdigest()
        out['schemes'][sid] = {'chars': len(corpus), 'md5': md5}
        print('%-18s %7d 字  md5 %s' % (sid, len(corpus), md5[:12]))

    dst = os.path.join(ROOT, 'tests', 'web_corpus.json')
    with io.open(dst, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print('written:', dst)


if __name__ == '__main__':
    main()
