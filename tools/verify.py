#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验「OpenCC大陆标准繁体海宁吴语修订」的转换结果。

    python tools/verify.py
    python tools/verify.py --config-dir /path/to/opencc

需要 Python 版 OpenCC（pip install opencc）。退出码 0 表示全部通过。
"""
from __future__ import annotations
import argparse
import io
import json
import os
import sys

try:
    import opencc
except ImportError:
    sys.exit('缺少依赖：请先执行 pip install opencc')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ROUNDTRIP = [
    '并州 合并 并非 吃饭 口吃 个中 真个 一个人',
    '面向 刚才 内哄 阁楼 肛门 胴疘',
    '只要 只是 一只鸟 三江并流 相提并论',
    '海宁吴语用字规范 词目 义项 例句',
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config-dir', default=os.path.join(ROOT, 'opencc'))
    ap.add_argument('--cases', default=os.path.join(ROOT, 'tests', 'cases.json'))
    args = ap.parse_args()

    with io.open(args.cases, 'r', encoding='utf-8') as f:
        cases = json.load(f)

    cache = {}

    def conv(scheme):
        if scheme not in cache:
            path = os.path.join(args.config_dir, scheme + '.json')
            cache[scheme] = opencc.OpenCC(path)
        return cache[scheme]

    passed = failed = 0
    print('%-18s %-6s %s' % ('scheme', 'result', 'input -> output'))
    print('-' * 100)
    for c in cases:
        got = conv(c['scheme']).convert(c['input'])
        ok = got == c['expected']
        passed += ok
        failed += (not ok)
        print('%-18s %-6s %s' % (c['scheme'], 'PASS' if ok else 'FAIL', got))
        if not ok:
            print('    expected: %s' % c['expected'])

    print('\n--- round-trip (s2hn -> hn2s) ---')
    for text in ROUNDTRIP:
        back = conv('hn2s').convert(conv('s2hn').convert(text))
        ok = back == text
        passed += ok
        failed += (not ok)
        print('%-6s %s' % ('PASS' if ok else 'FAIL', back))
        if not ok:
            print('    original: %s' % text)

    print('\n%d passed, %d failed' % (passed, failed))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
