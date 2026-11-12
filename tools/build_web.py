#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成在线转换页面所需的浏览器字典（web/dicts.js）。

    python tools/build_web.py
    # 或：python tools/build.py 会在重建字典时自动调用

数据来源全部是本仓库 opencc/ 下的 txt 字表词表与 json 配置，
以及 tests/cases.json。页面不联网、不依赖原生 OpenCC，双击 web/index.html 即可用。

字典以「紧凑 TSV 字符串」写入 JS，而不是 JSON 对象：
    STPhrases.txt + TGPhrases.txt 约 2 MB，TSV 比对象字面量省 1/3 体积。
引擎（web/engine.js）按 OpenCC 的 group / short_circuit 语义装载：
    字典按配置顺序短路，字典内部最长匹配；与原生 OpenCC 已逐字比对一致。
"""
from __future__ import annotations

import datetime
import hashlib
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OPENCC = os.path.join(ROOT, 'opencc')
TESTS = os.path.join(ROOT, 'tests', 'cases.json')
WEB = os.path.join(ROOT, 'web')

# 页面上提供的转换方向。chain 直接从 opencc/<id>.json 解析，避免与配置脱节。
SCHEMES = [
    {
        'id': 's2hn',
        'label': '简体 → 修订繁',
        'desc': '主入口。按义项分派正字：合併 / 並非 / 喫飯 / 箇中 / 真个 / 内鬨 / 内閤 / 發黴',
        'sample': '并州 合并 并非 吃饭 口吃 个中 真个 一个人 面向 刚才 内哄 阁楼 内𬮤 肛門 胴疘\n'
                  '合併之後並非一回事，喫飯時只在此山中。\n'
                  '发霉 倒霉 霉菌 霉干菜 青霉素',
    },
    {
        'id': 't2hn',
        'label': '任意繁 → 修订繁',
        'desc': '导入港台／旧字形／异体字资料时规范化：纔→才、嚮曏→向、內→内、關於→關于、發霉→發黴，分立正字一律保留',
        'sample': '一併 並不 喫飯 纔來 面嚮講臺 內閤 曏 寔 蹔 黃 神祇 內鬨 合併 內閣\n'
                  '關於 對於 於是 等於 青出於藍 於此 於乎 於戲 於菟 於莵 於梨華 樊於期 於潛\n'
                  '發霉 發黴 倒霉 霉 黴 黴菌 霉乾菜',
    },
    {
        'id': 'hn2s',
        'label': '修订繁 → 简体',
        'desc': '检索／简版展示／导出。並併→并、喫→吃、箇個个→个、閤→𬮤',
        'sample': '合併 並非 喫飯 箇中 真个 一個人 内鬨 內閣 内閤 肛門 胴疘 寔 蹔',
    },
    {
        'id': 't2s',
        'label': '繁体 → 简体',
        'desc': '上游命名兼容入口，与 hn2s 同配置',
        'sample': '合併 並非 喫飯 箇中 真个 一個人 内鬨 內閣 内閤 肛門 胴疘',
    },
    {
        'id': 't2hn_keep_simp',
        'label': '繁 → 修订繁（留简体）',
        'desc': '繁简混杂稿件；也是 Rime simplifier 用的同一套转换',
        'sample': '一併 並不 喫飯 纔來 真个 一个人 合并 內閤 黃 曏 關於 於是 於乎 於\n'
                  '發霉 發黴 倒霉 霉 黴',
    },
    {
        'id': 'v2s',
        'label': '异体字 → 简体',
        'desc': '校对辅助。倂竝閧幷等归并；分立正字与寔／蹔不处理',
        'sample': '倂 竝 閧 幷 祇 秖 喫 纔 嚮 曏 寔 蹔',
    },
    {
        'id': 't2new',
        'label': '旧字形 → 新字形',
        'desc': '只按《古籍印刷通用字规范字形表》规范字形，不做繁简转换',
        'sample': '黃 內 眞 敎 爲 幷 竝 閤 說 溫 个 個',
    },
    {
        'id': 't2new_keep_simp',
        'label': '旧字形 → 新字形（留简体）',
        'desc': '同上，但保留文中的简体字',
        'sample': '黃 內 眞 敎 爲 幷 竝 閤 說 溫 个 個 合并',
    },
]

# 补齐 tests/cases.json 未覆盖的方向（expected 由原生 OpenCC 生成并核对）。
EXTRA_CASES = [
    {'scheme': 't2s',
     'input': '合併 並非 喫飯 箇中 真个 一個人 内鬨 內閣 内閤',
     'expected': '合并 并非 吃饭 个中 真个 一个人 内哄 内阁 内𬮤'},
    {'scheme': 't2new',
     'input': '黃 內 眞 敎 爲 幷 竝 閤 說 溫',
     'expected': '黄 内 真 敎 爲 并 竝 閤 説 温'},
    {'scheme': 't2new_keep_simp',
     'input': '黃 內 眞 敎 爲 幷 竝 閤 說 溫 个 合并',
     'expected': '黄 内 真 敎 爲 并 竝 閤 説 温 个 合并'},
    {'scheme': 'v2s',
     'input': '倂 竝 閧 幷 祇 秖 喫 纔 嚮 曏 寔 蹔',
     'expected': '并 并 哄 并 只 只 喫 纔 嚮 向 寔 蹔'},
    {'scheme': 't2hn_keep_simp',
     'input': '一併 並不 喫飯 纔來 真个 一个人 合并 內閤 關於 於是 於乎',
     'expected': '一併 並不 喫飯 才來 真个 一个人 合并 内閤 關于 于是 於乎'},
]


def read_pairs(fn):
    """读取 OpenCC text 字典；多候选取首选（与 OpenCC 默认 convert 一致）。"""
    pairs = []
    with io.open(os.path.join(OPENCC, fn), encoding='utf-8') as f:
        for ln in f:
            ln = ln.rstrip('\r\n')
            if not ln.strip() or ln.lstrip().startswith('#') or '\t' not in ln:
                continue
            k, v = ln.split('\t', 1)
            pairs.append((k, v.split(' ')[0]))
    return pairs


def chain_of(config_name):
    """从 opencc/<name>.json 解析 normalization 与 conversion_chain 的字典顺序。"""
    with io.open(os.path.join(OPENCC, config_name + '.json'), encoding='utf-8') as f:
        cfg = json.load(f)
    norm = cfg.get('normalization', [{}])[0].get('dict', {}).get('file')
    stage = cfg['conversion_chain'][0]['dict']
    if stage.get('type') == 'group':
        chain = [d['file'] for d in stage['dicts']]
        policy = stage.get('match_policy', 'short_circuit')
    else:
        chain = [stage['file']]
        policy = 'short_circuit'
    assert policy == 'short_circuit', '%s: unsupported match_policy %s' % (config_name, policy)
    return norm, chain


def main(dry=False):
    schemes = []
    needed = set()
    for item in SCHEMES:
        norm, chain = chain_of(item['id'])
        s = dict(item)
        s['norm'] = norm
        s['chain'] = chain
        schemes.append(s)
        needed.update(chain)
        if norm:
            needed.add(norm)

    dicts = {}
    stats = {}
    for fn in sorted(needed):
        pairs = read_pairs(fn)
        tsv = ''.join('%s\t%s\n' % (k, v) for k, v in pairs)
        dicts[fn] = tsv
        stats[fn] = {'entries': len(pairs), 'bytes': len(tsv.encode('utf-8')),
                     'md5': hashlib.md5(tsv.encode('utf-8')).hexdigest()[:12]}

    cases = []
    with io.open(TESTS, encoding='utf-8') as f:
        for c in json.load(f):
            cases.append({'scheme': c['scheme'], 'input': c['input'],
                          'expected': c['expected'], 'source': 'tests/cases.json'})
    for c in EXTRA_CASES:
        cases.append(dict(c, source='web'))

    data = {
        'meta': {
            'project': 'OpenCC 大陆标准繁体 · 海宁吴语修订',
            'generated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
            'generator': 'tools/build_web.py',
            'matching': 'OpenCC group / short_circuit（字典顺序短路 + 字典内最长匹配）',
            'dicts': stats,
            'total_bytes': sum(v['bytes'] for v in stats.values()),
            'case_count': len(cases),
            'aliases': {
                's2t': 's2hn', 't2gov': 't2hn',
                't2gov_keep_simp': 't2hn_keep_simp',
            },
            'note': '多候选取首选；不含 jieba 分词与候选字功能，完整能力请用原生 OpenCC 配置。',
        },
        'dicts': dicts,
        'schemes': schemes,
        'cases': cases,
    }

    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    # JS 字符串字面量里 U+2028/U+2029 在旧引擎中会截断，统一转义
    payload = payload.replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    js = ('/* Generated by tools/build_web.py — DO NOT EDIT BY HAND. */\n'
          ';(function (root) {\n'
          '  root.HN_DATA = ' + payload + ';\n'
          '})(typeof window !== \'undefined\' ? window : globalThis);\n')

    out = os.path.join(WEB, 'dicts.js')
    if dry:
        print('[dry-run] would write %s (%d bytes, %d dicts, %d cases)' %
              (out, len(js.encode('utf-8')), len(dicts), len(cases)))
        return
    os.makedirs(WEB, exist_ok=True)
    with io.open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write(js)
    print('=== WEB DICT REPORT ===')
    for fn in sorted(dicts):
        print('  %-38s %7d entries  %8d B  md5:%s' %
              (fn, stats[fn]['entries'], stats[fn]['bytes'], stats[fn]['md5']))
    print('  total %d B, %d schemes, %d cases' %
          (data['meta']['total_bytes'], len(schemes), len(cases)))
    print('written: %s (%d bytes)' % (out, os.path.getsize(out)))


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dry-run', action='store_true')
    main(ap.parse_args().dry)
