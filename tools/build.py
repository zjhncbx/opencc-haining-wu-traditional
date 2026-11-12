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
    # 第 4 类修订（补充附注）：寔 / 蹔 非纯粹异体字，相关字表一律恒等，不归并到 實 / 暫。
    if name in R.VARIANT_KEEP_TABLES:
        sets.update(R.VARIANT_KEEP)
    out, seen = [], set()
    fixes = R.UPSTREAM_COMMENT_FIX.get(name, {})
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
    out = [fixes.get(x.strip(), x) for x in out]
    write_lines(os.path.join(out_dir, name), out, dry)
    report['tables'][name] = sum(1 for x in out if is_data(x))


# ---------------------------------------------------------------------------
# phrase tables
# ---------------------------------------------------------------------------
def tg_value(k, v):
    """Reason 1: keep split orthodox characters. Reason 2: fold 纔/嚮 back.
    「衹」在海宁吴语书写中统一作「只」（「隻」仍为量词正字）；
    港台「於」除 R.YU_KEEP_PHRASES 外统一作「于」；
    「霉」是「黴」的简化字，规范繁体统一作「黴」。"""
    if len(k) != len(v):
        return v
    a = list(v)
    for i, (kc, vc) in enumerate(zip(k, v)):
        if vc == '衹':
            a[i] = '只'
        elif vc == '霉':
            a[i] = '黴'
        elif kc in R.ORTHODOX_SPLIT and vc in R.MERGE_TARGET:
            a[i] = kc
        elif vc in ('纔', '嚮', '曏', '幷', '倂', '竝', '閧'):
            a[i] = R.VARIANT_NORMALIZE.get(vc, vc)
    # 用字约定：姓氏人名、地名与感叹词（YU_KEEP_PHRASES）保留「於」，其余一律→「于」
    if k not in R.YU_KEEP_PHRASES:
        for i, c in enumerate(a):
            if c == '於':
                a[i] = '于'
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
        elif c == '衹':
            a[i] = '只'
        elif c == '霉':
            a[i] = '黴'
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
    if name == 'TSPhrases.txt' and R.HN2S_EXTRA_PHRASES:
        out.append('# Haining Wu revision: added by tools/build.py (see tools/rules.py)')
        for k, v in sorted(R.HN2S_EXTRA_PHRASES.items()):
            out.append(k + '\t' + v)
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

# 上游 Rime 方案：朙月拼音原词库一字不动，只把 simplifier 的 OpenCC 配置
# 换成修订版字典。写法与上游 README「规范繁体转换方案如何应用于小狼毫」一致。
# 不要自建 import_tables 扩展词库：那会丢掉 essay.txt 词频、破坏候选排序。
LUNA_CUSTOM = """# luna_pinyin.custom.yaml
# 放到 Rime 用户文件夹；与上游仓库 README 的写法一致。
# 词库保持朙月拼音原版，仅替换 OpenCC 转换为本修订方案。
patch:
  switches:
    - name: simplification
      reset: 1

  simplifier:
    opencc_config: t2hn_keep_simp.json
    option_name: simplification
"""

# 可选：用上游自带的 custom_phrase 机制把吴语助词「个」的单字候选提前。
# 不改词库、不改 schema，只新增一个纯文本短语文件；用户目录若已有同名文件，
# 应把最后一行追加进去而不是覆盖。
CUSTOM_PHRASE = """# custom_phrase.txt — 朙月拼音自定义短语（海宁吴语修订方案）
# 放到 Rime 用户文件夹（Windows：%APPDATA%\\Rime）。
# 上游 luna_pinyin.schema.yaml 默认已启用 table_translator@custom_phrase，
# 因此不需要改 luna_pinyin.custom.yaml，也不需要新建任何词库。
#
# 格式：文字<TAB>拼音码<TAB>权重
# 「个」在海宁吴语中作结构助词（约相当于普通话「的」），多单字出现、使用极频繁。
# 这里只把单字候选往前排，不造词组、不改词库、不影响其他音节与整词候选。
# 想更靠前就把 1000 调大；想恢复默认就删掉下面这一行。
# 若本文件夹已有 custom_phrase.txt，把最后一行追加进去即可，不要覆盖。
个\tge\t1000
"""


def build_rime(rime_dir, dry, report):
    write_text(os.path.join(rime_dir, 't2hn_keep_simp.json'),
               json.dumps(RIME_T2HN_OCD2, ensure_ascii=False, indent=2) + '\n', dry)
    write_text(os.path.join(rime_dir, 'luna_pinyin.custom.yaml'), LUNA_CUSTOM, dry)
    write_text(os.path.join(rime_dir, 'custom_phrase.txt'), CUSTOM_PHRASE, dry)
    report['rime'].extend(['t2hn_keep_simp.json', 'luna_pinyin.custom.yaml',
                           'custom_phrase.txt'])


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
        '> 依据 [《通用规范汉字表》](https://www.gov.cn/zhengce/content/2013-08/19/content_1289.htm)',
        '> 及附件《规范字与繁体字、异体字对照表》。',
        '> 本文件是面向海宁吴语书写的地方性用字约定；转换规则见 `tools/rules.py`，',
        '> 逐条差异见 [`doc/02-与上游差异.md`](02-与上游差异.md)。',
        '',
        '## 修订说明',
        '',
        '繁體漢字爲簡體規範字之源，使用漢字書寫、記録海寧吴語時以繁體爲佳。2013年國務院公布的《通用規範漢字表》在界定簡體漢字規範性的同時，也在其附件《規範字與繁體字、异體字對照表》中確定了繁體漢字的正、异之别，同時《新華字典》《現代漢語詞典》也通過標註繁簡關係間接解釋了繁體漢字的字義，基本確立了中國大陸地區的繁體漢字體系。本方案基于《規範字與繁體字、异體字對照表》進行極少量的修訂，將其作爲使用繁體漢字書寫海寧吴語時的規範。',
        '',
        '本方案從四個方面對《規範字與繁體字、异體字對照表》進行修訂，具體修訂内容列下表。',
        '',
        '（1）原表將乙字視爲甲字的异體字，但兩者中古反切不同，海寧吴語今音亦不同，且較常用，不宜視爲异體關係，需分立。爲銜接國家通用語的簡體漢字書寫，分三類情况確定乙字的簡體規範字：其一，國家通用語常用，且有同形繁體正字，則參照該同形字的簡體規範字；其二，國家通用語常用，且無同形繁體正字，則參照原表簡體規範字；其三，國家通用語罕用，則參照類推簡化字。如：“并”“併”“並”三字在海寧吴語中讀音仍互不相同，宜分列爲三個繁體正字，因國家通用語常用，且無同形繁體正字，故簡體規範字形仍同原表作“并”。',
        '',
        '（2）原表將甲字與乙字視爲兩個繁體正字，且簡體規範字均爲甲字，實則兩字傳統上讀音、字義、用法等同，出于實際書寫的擇字需要，取甲字爲正，乙字爲异體字。如：“才”“纔”在“方、僅”義項上音義皆同，取“才”爲正。',
        '',
        '（3）現代南方方言中“个”的常用字義較多，且有讀音分化傾向，海寧吴語尤甚。傳統方言文獻已有通過异體字區分音、義的用例，《南昌方言詞典》進一步將“个”“個”“箇”三者分别使用。本方案借鑒前人，規定“个”用于助詞，“個”用于量詞和名詞，“箇”用于指示代詞。簡體規範字仍作“个”。',
        '',
        '（4）原表附注對异體字在部分義項和用法上可作規範字使用的情况做了説明，但部分异體字由于國家通用語罕用，未得到注明，故對海寧吴語常用的字做補充。如：“寔”在“此、這”義項上爲繁體正字，不作爲“實”的异體字。',
        '',
        '## 四类修订（要点）',
        '',
        '1. **分立**：原表视乙为甲的异体字，但中古反切不同、海宁吴语今音亦不同且较常用，需分立为多个繁体正字。',
        '   简体规范字按三类情形确定：常用且有同形繁体正字→参照该同形字；常用但无同形繁体正字→参照原表；罕用→参照类推简化字。',
        '   例：并/併/並 三者吴语读音互不相同，因通用语常用且无同形繁体正字，简体规范字仍同原表作「并」。',
        '2. **合并**：原表视为两个繁体正字、简体规范字均为甲字，实则音义用法等同；出于实际书写的择字需要取甲为正、乙为异体。',
        '   例：「才」「纔」在「方、僅」义项上音义皆同，取「才」为正（才/纔、向/嚮曏）。',
        '3. **个/個/箇 三分**：现代南方方言「个」字义多且有读音分化，《南昌方言词典》已分别使用三者；',
        '   本方案定「个」助词、「個」量词名词、「箇」指示代词，**简体规范字仍作「个」**。',
        '   简→修订繁时，单字「个」及未被词表收录的「个」按助词保留；「個」「箇」由词表分派。',
        '4. **补充附注**：原表附注未注明、而海宁吴语常用者，在特定义项上也是繁体正字，此处补充；',
        '   序号 1285「寔」（此、這）自身即为繁体正字、不作「實」的异体；2599「蹔」（疾進）同理，其简体规范字作「𫏐」；',
        '   两字各方向保留原形、不补词组。',
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
        '| 分立 | 不再把 並/併/喫/隻/鬨/疘/閤/箇 归并 | 按义项分派正字（词表优先） | 各自对应简体规范字 |',
        '| 合并 | 纔→才、嚮→向、曏→向 | 不再输出 纔/嚮/曏 | 纔→才、嚮→向、曏→向 |',
        '| 三分 | 个/個/箇 一律原样保留 | 单字「个」按助词保留；「個」「箇」由词表分派 | 三者→个 |',
        '| 只 / 衹 | 衹→只 | 「只」「衹」相关词一律输出「只」 | 衹→只 |',
        '| 閤 / 𬮤 | 閤 为独立正字 | 𬮤→閤 | 閤→𬮤 |',
        '| ④ 补充附注 | 寔/蹔 一律原样保留 | 𫏐 原样保留（不造「蹔」） | 寔/蹔 一律原样保留 |',
        '| 於 / 于 | 除姓氏人名、地名与感叹词外，词表「於」一律→「于」 | 简体「于」不变；感叹词由词表分派「於」 | 於→于（例外保留） |',
        '| 霉 / 黴 | 霉→黴（含「倒霉」等词） | 霉→黴 | 沿用上游 黴→霉 |',
        '',
        '> 说明：`t2hn` 主方案对「个/個/箇」三者一律原样保留，不再做上游的 `个→個` 归并；',
        '> `s2hn` 里单字「个」及未被词表收录的「个」同样按助词保留「个」。',
        '> 如需把繁简混杂稿件中的简体按义项转为修订繁体，请用 `s2hn`。',
        '',
        '## 用字约定：於 / 于',
        '',
        '大陆标准繁体一般用「于」。港台习用的「於」只保留于两类场合：',
        '',
        '1. **姓氏、人名、地名**：於梨華、樊於期、於潛 …',
        '2. **感叹词及同源古语**：於乎、於戲、於菟（於莵）、於呼哀哉、於穆、於邑 …',
        '',
        '其余词条一律作「于」：關於→關于、於是→于是、等於→等于、於此→于此、青出於藍→青出于藍。',
        '（`hn2s` 方向再按常规简化为「关于 / 于是 / 青出于蓝」。）',
        '单字「於」不设字表映射，保留姓氏用法；词组层面已覆盖常用词。',
        '港台／繁简混杂稿件请用 `t2hn` 或 `t2hn_keep_simp` 规范化；',
        '`v2s`、`t2new` 是字形方案，不参与本条用字约定。',
        '',
        '## 用字约定：霉 / 黴',
        '',
        '《规范字与繁体字、异体字对照表》把「霉—黴」列为规范字与繁体正字的对应，',
        '即「霉」是「黴」的简化字，不是可在繁体文本中独立使用的传承正字。',
        '因此本方案在 简→修订繁 与 繁→修订繁 两个方向一律作「黴」：',
        '发霉／發霉→發黴、倒霉→倒黴、霉乾菜→黴乾菜，单字「霉」→「黴」。',
        '',
        '上游 `t2gov` 采用港台按义项分化的立场，保留「倒霉」等写法，并在',
        '`STCharacters.txt` 给「霉」留了 `黴 霉` 一对多候选；本修订不采用该分化，',
        '也不保留一对多候选。修订繁→简方向沿用上游 `黴→霉`。',
        '',
        'Rime 侧：朙月拼音词库同时收「發霉」「發黴」（词频相同），',
        '`simplifier` 把「發霉」规范为「發黴」后，由 schema 自带的 `uniquifier` 去重，',
        '故 `famei` 只出一个「發黴」候选；单字 `mei` 同理。',
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
    # 在线转换页面的字典与 opencc/ 同源，随每次重建一起刷新，避免页面用到过期字表
    import build_web
    build_web.main(dry=dry)

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
