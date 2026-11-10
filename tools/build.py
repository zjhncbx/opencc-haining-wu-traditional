# -*- coding: utf-8 -*-
"""
Build the whole "OpenCC大陆标准繁体海宁吴语修订" tree from the upstream tables.

Usage:
    python tools/build.py --upstream <path-to-upstream/t2gov> [--dry-run]
    python tools/build.py --upstream ../upstream/t2gov

The generator is deterministic and idempotent: it never edits the upstream
files, and re-running it reproduces byte-identical output.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rules as R

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHAR_TABLES = [
    'STCharacters.txt', 'TSCharacters.txt', 'TGCharacters.txt',
    'TGCharacters_keep_simp.txt', 'GovVariants.txt',
    'GovVariants_keep_simp.txt', 'VSCharacters.txt',
]
PHRASE_TABLES = [
    'STPhrases.txt', 'TSPhrases.txt', 'TGPhrases.txt', 'VSPhrases.txt',
]


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def read_lines(path):
    with io.open(path, 'r', encoding='utf-8-sig') as f:
        return f.read().splitlines()


def write_lines(path, lines, dry):
    if dry:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')


def write_text(path, text, dry):
    if dry:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def is_data(ln):
    return bool(ln.strip()) and not ln.lstrip().startswith('#')


def split_kv(ln):
    p = ln.split('\t')
    return p[0], (p[1] if len(p) > 1 else '')


def load_pairs(path):
    d = OrderedDict()
    for ln in read_lines(path):
        if is_data(ln) and '\t' in ln:
            k, v = split_kv(ln)
            d[k] = v
    return d


# ---------------------------------------------------------------------------
# character tables
# ---------------------------------------------------------------------------
def patch_char_table(name, upstream, out_dir, dry, report):
    cfg = R.CHAR_PATCH.get(name, {'delete': [], 'set': {}})
    dels, sets = set(cfg['delete']), dict(cfg['set'])
    out, seen = [], set()
    for ln in read_lines(os.path.join(upstream, name)):
        if not is_data(ln) or '\t' not in ln:
            out.append(ln)
            continue
        k, v = split_kv(ln)
        if k in dels:
            report['char_deleted'].append('%s: %s -> %s' % (name, k, v))
            continue
        nv = sets.get(k, v)
        if nv != v:
            report['char_changed'].append('%s: %s : %s -> %s' % (name, k, v, nv))
        out.append(k + '\t' + nv)
        seen.add(k)
    added = [(k, v) for k, v in sets.items() if k not in seen]
    if added:
        out.append('# Haining Wu revision: added by tools/build.py (see tools/rules.py)')
        for k, v in sorted(added):
            out.append(k + '\t' + v)
            report['char_added'].append('%s: %s -> %s' % (name, k, v))
    write_lines(os.path.join(out_dir, name), out, dry)
    report['tables'][name] = sum(1 for x in out if is_data(x))


# ---------------------------------------------------------------------------
# phrase tables
# ---------------------------------------------------------------------------
def tg_value(k, v):
    """Reason 1: keep split orthodox characters. Reason 2: fold 纔/嚮 back."""
    if len(k) != len(v):
        return v
    a = list(v)
    for i, (kc, vc) in enumerate(zip(k, v)):
        if kc in R.ORTHODOX_SPLIT and vc in R.MERGE_TARGET:
            a[i] = kc
        elif vc in ('纔', '嚮', '曏', '幷', '倂', '竝', '閧'):
            a[i] = R.VARIANT_NORMALIZE.get(vc, vc)
    return ''.join(a)


def st_value(k, v, ref):
    """Reason 1: restore split characters using the OpenCC original s2t reference.
    Reason 2: 纔/嚮 are variants -> 才/向. Reason 3: 个/個/箇 trichotomy."""
    a = list(v)
    for i, c in enumerate(a):
        if c == '纔':
            a[i] = '才'
        elif c == '嚮':
            a[i] = '向'
    r = ref.get(k)
    if r and len(r) == len(a):
        for i, (rc, ac) in enumerate(zip(r, a)):
            if ac in ('并', '吃', '哄', '個') and rc in (
                    '並', '併', '喫', '鬨', '箇', '幷', '倂', '竝', '閧'):
                a[i] = R.VARIANT_NORMALIZE.get(rc, rc)
    # 「合」不再对应「閤」；「閤」的简体规范字是「𬮤」
    for i, c in enumerate(a):
        if c == '閤' and i < len(k) and k[i] == '合':
            a[i] = '合'
    # 未被词表命中的默认正字：进食义用「喫」、喧闹义用「鬨」。
    # 「口吃」（居乞切）与「哄笑/哄骗」（呼公切）由 HNPhrases.txt 保护。
    for i, c in enumerate(a):
        if c == '吃' and '口吃' not in k:
            a[i] = '喫'
        elif c == '哄' and not any(x in k for x in (
                '哄笑', '哄骗', '哄弄', '哄小孩', '哄逗', '哄劝', '哄慰')):
            a[i] = '鬨'
    return ''.join(a)


def rewrite_phrase_table(name, upstream, out_dir, ref, dry, report):
    out = []
    changed = 0
    for ln in read_lines(os.path.join(upstream, name)):
        if not is_data(ln) or '\t' not in ln:
            out.append(ln)
            continue
        k, v = split_kv(ln)
        if name == 'TGPhrases.txt':
            nv = tg_value(k, v)
        elif name == 'STPhrases.txt':
            nv = st_value(k, v, ref)
        elif name == 'VSPhrases.txt':
            # 「閤」已升格为繁体正字，不再是 v2s 的处理对象
            if '閤' in k:
                report['phrase_deleted'].append('%s: %s -> %s' % (name, k, v))
                continue
            nv = v
        else:
            nv = v
        if nv != v:
            changed += 1
        out.append(k + '\t' + nv)
    write_lines(os.path.join(out_dir, name), out, dry)
    report['phrase_rewritten'][name] = changed
    report['tables'][name] = sum(1 for x in out if is_data(x))


# ---------------------------------------------------------------------------
# OpenCC json configs
# ---------------------------------------------------------------------------
def insert_text_dict_before(node, target, new_file):
    """Insert {"type":"text","file":new_file} before every dicts[] entry whose
    file == target. Works for plain, jieba and keep_simp configs alike."""
    if isinstance(node, dict):
        for key, val in list(node.items()):
            if key == 'dicts' and isinstance(val, list):
                for i, item in enumerate(val):
                    if isinstance(item, dict) and item.get('file') == target:
                        if not any(isinstance(x, dict) and x.get('file') == new_file
                                   for x in val):
                            val.insert(i, {'type': 'text', 'file': new_file})
                        return True
            if insert_text_dict_before(val, target, new_file):
                return True
    elif isinstance(node, list):
        for x in node:
            if insert_text_dict_before(x, target, new_file):
                return True
    return False


def build_configs(upstream, out_dir, dry, report):
    built = {}
    for fn in sorted(f for f in os.listdir(upstream) if f.endswith('.json')):
        with io.open(os.path.join(upstream, fn), 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        data['name'] = data.get('name', '') + ' — Haining Wu Revision'
        if fn.startswith('s2t'):
            insert_text_dict_before(data, 'STPhrases.txt', 'HNPhrases.txt')
        if fn.startswith('t2gov'):
            insert_text_dict_before(data, 'TGPhrases.txt', 'HNGuard.txt')
        built[fn] = data
        write_text(os.path.join(out_dir, fn),
                   json.dumps(data, ensure_ascii=False, indent=2) + '\n', dry)
        report['configs'].append(fn)

    for alias, source in R.SCHEME_ALIASES.items():
        data = json.loads(json.dumps(built[source], ensure_ascii=False))
        data['name'] = {
            's2hn': 'Simplified Chinese to Haining Wu Mainland Standard Traditional Chinese',
            'hn2s': 'Haining Wu Mainland Standard Traditional Chinese to Simplified Chinese',
            't2hn': 'Traditional Chinese to Haining Wu Mainland Standard Traditional Chinese',
            't2hn_keep_simp': 'Traditional Chinese to Haining Wu Mainland Standard Traditional Chinese (keep simplified)',
        }[alias]
        write_text(os.path.join(out_dir, alias + '.json'),
                   json.dumps(data, ensure_ascii=False, indent=2) + '\n', dry)
        report['configs'].append(alias + '.json')


# ---------------------------------------------------------------------------
# Rime files
# ---------------------------------------------------------------------------
RIME_T2HN_OCD2 = {
    "name": "Haining Wu Mainland Standard Traditional Chinese (Rime / ocd2)",
    "segmentation": {"type": "mmseg",
                     "dict": {"type": "ocd2", "file": "TGPhrases.ocd2"}},
    "conversion_chain": [{"dict": {"type": "group", "dicts": [
        {"type": "ocd2", "file": "HNGuard.ocd2"},
        {"type": "ocd2", "file": "TGPhrases.ocd2"},
        {"type": "ocd2", "file": "TGCharacters_keep_simp.ocd2"},
    ]}}],
}

RIME_T2HN_TEXT = {
    "name": "Haining Wu Mainland Standard Traditional Chinese (Rime / plain text dictionaries)",
    "conversion_chain": [{"dict": {"type": "group",
                                   "match_policy": "short_circuit",
                                   "dicts": [
                                       {"type": "text", "file": "HNGuard.txt"},
                                       {"type": "text", "file": "TGPhrases.txt"},
                                       {"type": "text", "file": "TGCharacters_keep_simp.txt"},
                                   ]}}],
}

RIME_S2HN_TEXT = {
    "name": "Simplified Chinese to Haining Wu Mainland Standard Traditional Chinese (Rime)",
    "conversion_chain": [{"dict": {"type": "group",
                                   "match_policy": "short_circuit",
                                   "dicts": [
                                       {"type": "text", "file": "HNPhrases.txt"},
                                       {"type": "text", "file": "STPhrases.txt"},
                                       {"type": "text", "file": "STCharacters.txt"},
                                   ]}}],
}

LUNA_CUSTOM = """# luna_pinyin.custom.yaml
# 将朙月拼音的输出切换为《大陆标准繁体汉字海宁吴语修订方案》字形。
# 放到 Rime 用户文件夹后「重新部署」即可。
patch:
  switches:
    - name: simplification
      reset: 1
  simplifier:
    opencc_config: t2hn_keep_simp.json
    option_name: simplification
  "translator/dictionary": haining_wu_extended
"""

EXTENDED_DICT = """# Rime dictionary
# 朙月拼音原词库 + 海宁吴语修订方案分立正字词库
---
name: haining_wu_extended
version: "1.0.0"
sort: by_weight
import_tables:
  - luna_pinyin
  - haining_wu
...
"""


def build_rime(rime_dir, dry, report):
    for fn, data in [('t2hn_keep_simp.json', RIME_T2HN_OCD2),
                     ('t2hn_keep_simp_text.json', RIME_T2HN_TEXT),
                     ('s2hn.json', RIME_S2HN_TEXT)]:
        write_text(os.path.join(rime_dir, fn),
                   json.dumps(data, ensure_ascii=False, indent=2) + '\n', dry)
        report['rime'].append(fn)
    write_text(os.path.join(rime_dir, 'luna_pinyin.custom.yaml'), LUNA_CUSTOM, dry)
    write_text(os.path.join(rime_dir, 'haining_wu_extended.dict.yaml'),
               EXTENDED_DICT, dry)
    lines = [
        '# Rime dictionary',
        '# 《大陆标准繁体汉字海宁吴语修订方案》分立正字与例词',
        '# 由 tools/build.py 依据 tools/rules.py 生成，请勿手工改动本文件。',
        '---',
        'name: haining_wu',
        'version: "1.0.0"',
        'sort: by_weight',
        '...',
    ]
    for word, pinyin, weight in R.RIME_ENTRIES:
        lines.append('%s\t%s\t%d' % (word, pinyin, weight))
    write_lines(os.path.join(rime_dir, 'haining_wu.dict.yaml'), lines, dry)
    report['rime'].extend(['luna_pinyin.custom.yaml',
                           'haining_wu_extended.dict.yaml',
                           'haining_wu.dict.yaml'])


# ---------------------------------------------------------------------------
# docs / tests / rules
# ---------------------------------------------------------------------------
def build_overrides(tsv_path, dry, report):
    if os.path.exists(tsv_path):
        ov = load_pairs(tsv_path)
    else:
        ov = OrderedDict(sorted(R.PHRASE_OVERRIDES.items()))
        lines = ['# 简体词<TAB>修订版大陆标准繁体词',
                 '# 本文件是「个/個/箇」「并/併/並」等分立字的协作编辑入口。',
                 '# 修改后重新运行 python tools/build.py 即可重建全部字表词表。']
        lines.extend('%s\t%s' % (k, v) for k, v in ov.items())
        write_lines(tsv_path, lines, dry)
    report['overrides'] = len(ov)
    return ov


def build_phrase_files(out_dir, overrides, dry, report):
    hn = ['# OpenCC Dictionary — Haining Wu revision priority phrases (s -> HN traditional)',
          '# Generated by tools/build.py from rules/overrides.tsv. Do not edit here.',
          '# Format: key<TAB>value']
    hn.extend('%s\t%s' % (k, v) for k, v in overrides.items())
    write_lines(os.path.join(out_dir, 'HNPhrases.txt'), hn, dry)

    guard = ['# OpenCC Dictionary — Haining Wu revision guard phrases (T -> HN traditional)',
             '# Generated by tools/build.py from tools/rules.py (TG_GUARD).',
             '# Format: key<TAB>value']
    guard.extend('%s\t%s' % (k, v) for k, v in R.TG_GUARD.items())
    write_lines(os.path.join(out_dir, 'HNGuard.txt'), guard, dry)
    report['tables']['HNPhrases.txt'] = len(overrides)
    report['tables']['HNGuard.txt'] = len(R.TG_GUARD)


def build_revision_doc(doc_dir, dry):
    lines = [
        '# 大陆标准繁体汉字海宁吴语修订方案',
        '',
        '> 本文件由《大陸標準繁體漢字海寧吴語修訂方案.docx》表格转录，',
        '> 并纳入 2026-11-10 更正：1639 组「閤」的简体规范字由「閤」更正为「𬮤」。',
        '',
        '繁体汉字为简体规范字之源，使用汉字书写、记录海宁吴语时以繁体为佳。',
        '本方案基于《通用规范汉字表》附件 1《规范字与繁体字、异体字对照表》作极少量修订，',
        '作为使用繁体汉字书写海宁吴语时的规范。',
        '',
        '## 三类修订',
        '',
        '1. **分立**：原表部分繁体正字与其异体字在现代吴语中读音、字义、用法并不构成异体关系，',
        '   则分立为多个繁体正字。国家通用语常用的字，简体规范字形同原表；罕用的字若有同形字，',
        '   参照该同形字的简体规范字，否则同繁体正字。',
        '2. **合并**：原表视为两个繁体正字、简体规范字均为甲字，而两字传统上音义等同者，',
        '   取甲字为正、乙字为异体（才/纔、向/嚮）。',
        '3. **个/個/箇 三分**：借鉴《南昌方言词典》，规定「个」用于助词、「個」用于量词和名词、',
        '   「箇」用于指示代词。',
        '',
        '## 修订对照表',
        '',
        '| 序号 | 简体规范字 | 繁体正字 | 异体字 | 原因 | 备注 |',
        '| --- | --- | --- | --- | --- | --- |',
    ]
    for no, simp, trads, variants, reason, note in R.REVISION_TABLE:
        lines.append('| %s | %s | %s | %s | %s | %s |' % (
            no, simp, ' / '.join(trads), variants or '—', reason, note))
    lines += [
        '',
        '## 对转换方案的落地方式',
        '',
        '| 修订 | 繁→修订繁 `t2hn` | 简→修订繁 `s2hn` | 修订繁→简 `hn2s` |',
        '| --- | --- | --- | --- |',
        '| 分立 | 不再把 並/併/喫/衹/隻/鬨/疘/閤/箇 归并 | 按义项分派正字（词表优先） | 各自对应简体规范字 |',
        '| 合并 | 纔→才、嚮→向 | 不再输出 纔/嚮 | 纔→才、嚮→向 |',
        '| 三分 | 个/個/箇 一律原样保留 | 个（助词）/個（量词名词）/箇（指示代词） | 三者→个 |',
        '| 𬮤 更正 | 閤 为独立正字 | 𬮤→閤 | 閤→𬮤 |',
        '',
        '> 说明：`t2hn` 主方案对「个/個/箇」三者一律原样保留，不再做上游的 `个→個` 归并；',
        '> 如需把繁简混杂稿件中的简体按义项转为修订繁体，请用 `s2hn`。',
        '',
    ]
    write_text(os.path.join(doc_dir, '01-修订方案.md'), '\n'.join(lines), dry)


def build_tests(tests_dir, report, dry):
    data = []
    for scheme, src, expected in R.TEST_CASES:
        data.append({'scheme': scheme, 'input': src, 'expected': expected})
    write_text(os.path.join(tests_dir, 'cases.json'),
               json.dumps(data, ensure_ascii=False, indent=2) + '\n', dry)
    report['test_cases'] = len(data)


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--upstream', default=os.path.join(ROOT, '..', 'upstream', 't2gov'))
    ap.add_argument('--out', default=os.path.join(ROOT, 'opencc'))
    ap.add_argument('--rime-out', default=os.path.join(ROOT, 'rime'))
    ap.add_argument('--rules-dir', default=os.path.join(ROOT, 'rules'))
    ap.add_argument('--doc-dir', default=os.path.join(ROOT, 'doc'))
    ap.add_argument('--tests-dir', default=os.path.join(ROOT, 'tests'))
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    upstream = os.path.abspath(args.upstream)
    if not os.path.isdir(upstream):
        sys.exit('upstream t2gov directory not found: %s' % upstream)
    dry = args.dry_run
    report = dict(tables={}, configs=[], rime=[], char_deleted=[], char_changed=[],
                  char_added=[], phrase_rewritten={}, phrase_deleted=[],
                  overrides=0, test_cases=0)

    overrides = build_overrides(os.path.join(args.rules_dir, 'overrides.tsv'), dry, report)
    ref = load_pairs(os.path.join(args.rules_dir, 'split_reference.txt'))

    for name in CHAR_TABLES:
        patch_char_table(name, upstream, args.out, dry, report)
    for name in PHRASE_TABLES:
        rewrite_phrase_table(name, upstream, args.out, ref, dry, report)
    # CJK compatibility normalisation table is unchanged
    src = os.path.join(upstream, 'CJK_Compatibility_Ideographs.txt')
    if not dry:
        os.makedirs(args.out, exist_ok=True)
        import shutil
        shutil.copyfile(src, os.path.join(args.out, 'CJK_Compatibility_Ideographs.txt'))
    report['tables']['CJK_Compatibility_Ideographs.txt'] = len(read_lines(src))

    build_phrase_files(args.out, overrides, dry, report)
    build_configs(upstream, args.out, dry, report)
    build_rime(args.rime_out, dry, report)
    build_revision_doc(args.doc_dir, dry)
    build_tests(args.tests_dir, report, dry)

    print('=== BUILD REPORT%s ===' % (' (dry-run, no files written)' if dry else ''))
    print('upstream        : %s' % upstream)
    print('output          : %s' % os.path.abspath(args.out))
    print('char deleted    : %d' % len(report['char_deleted']))
    for x in report['char_deleted']:
        print('    - %s' % x)
    print('char changed    : %d' % len(report['char_changed']))
    for x in report['char_changed']:
        print('    * %s' % x)
    print('char added      : %d' % len(report['char_added']))
    for x in report['char_added']:
        print('    + %s' % x)
    print('phrase rewritten: %s' % report['phrase_rewritten'])
    print('phrase deleted  : %d' % len(report['phrase_deleted']))
    print('override phrases: %d' % report['overrides'])
    print('configs         : %d' % len(report['configs']))
    print('rime files      : %d' % len(report['rime']))
    print('test cases      : %d' % report['test_cases'])
    print('table sizes     :')
    for k, v in report['tables'].items():
        print('    %-38s %7d' % (k, v))


if __name__ == '__main__':
    main()
