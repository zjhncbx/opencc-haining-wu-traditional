#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把修订后的 txt 字典编译为 Rime / librime 使用的 ocd2 二进制字典。

    python tools/build_ocd2.py
    python tools/build_ocd2.py --opencc-dict "C:/path/to/opencc_dict.exe"

工具来源：OpenCC 1.3.2+ 自带 opencc_dict（Windows 的 Python OpenCC 包位于
  <python>/Lib/site-packages/opencc/clib/bin/opencc_dict.exe）。
本脚本会自动探测；找不到时用 --opencc-dict 指定。

生成的 ocd2 不纳入 Git（体积大、二进制、随字表自动重建），
请按需在部署 Rime 时运行本脚本，产物落在 rime/ 目录。
"""
from __future__ import annotations
import argparse
import glob
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

JOBS = [
    ('HNPhrases.txt', 'HNPhrases.ocd2'),
    ('HNGuard.txt', 'HNGuard.ocd2'),
    ('TGPhrases.txt', 'TGPhrases.ocd2'),
    ('TGCharacters_keep_simp.txt', 'TGCharacters_keep_simp.ocd2'),
    ('STPhrases.txt', 'STPhrases.ocd2'),
    ('STCharacters.txt', 'STCharacters.ocd2'),
]


def find_tool(explicit=None):
    if explicit:
        return explicit
    env = os.environ.get('OPENCC_DICT')
    if env and os.path.isfile(env):
        return env
    patterns = [
        os.path.join(sys.prefix, 'Lib', 'site-packages', 'opencc', 'clib', 'bin', 'opencc_dict.exe'),
        os.path.join(sys.prefix, 'Lib', 'site-packages', 'opencc', 'clib', 'bin', 'opencc_dict'),
        os.path.join(sys.prefix, 'bin', 'opencc_dict'),
    ]
    for p in patterns:
        if os.path.isfile(p):
            return p
    for p in glob.glob('/usr/bin/opencc_dict') + glob.glob('/usr/local/bin/opencc_dict'):
        if os.path.isfile(p):
            return p
    for p in ('opencc_dict', 'opencc_dict.exe'):
        from shutil import which
        found = which(p)
        if found:
            return found
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--opencc-dict')
    ap.add_argument('--opencc-dir', default=os.path.join(ROOT, 'opencc'))
    ap.add_argument('--rime-dir', default=os.path.join(ROOT, 'rime'))
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    tool = find_tool(args.opencc_dict)
    if not tool:
        sys.exit('找不到 opencc_dict。请用 --opencc-dict 指定，或设置环境变量 OPENCC_DICT。')
    print('opencc_dict : %s' % tool)
    os.makedirs(args.rime_dir, exist_ok=True)

    failed = 0
    for src, dst in JOBS:
        inp = os.path.join(args.opencc_dir, src)
        out = os.path.join(args.rime_dir, dst)
        if not os.path.isfile(inp):
            print('SKIP (missing) : %s' % src)
            failed += 1
            continue
        cmd = [tool, '-i', inp, '-o', out, '-f', 'text', '-t', 'ocd2']
        if args.dry_run:
            print('DRY-RUN       : %s -> %s' % (src, dst))
            continue
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print('FAIL          : %s (%s)' % (src, (r.stderr or r.stdout).strip()[:200]))
            failed += 1
        else:
            print('OK            : %-32s %8d bytes' % (dst, os.path.getsize(out)))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
