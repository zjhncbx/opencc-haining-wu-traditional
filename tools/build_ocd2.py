#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把修订后的 txt 字典编译为 Rime / librime 使用的 ocd2 二进制字典。

    python tools/build_ocd2.py
    python tools/build_ocd2.py --opencc-dict "C:/path/to/opencc_dict.exe"

工具来源：OpenCC 1.3.2+ 自带 opencc_dict（Windows 的 Python OpenCC 包位于
  <python>/Lib/site-packages/opencc/clib/bin/opencc_dict.exe）。
本脚本会自动探测；找不到时用 --opencc-dict 指定。

生成的 3 个 ocd2 随仓库发布（与上游 rime/ 目录一致），
改动字表后重跑本脚本并重新部署即可。

Windows 注意：原生 opencc_dict.exe 无法打开含非 ASCII 字符的路径。
若项目解压到中文目录（例如「上传用-仓库文件」），本脚本会自动把字典
复制到纯 ASCII 的临时目录编译，再把 .ocd2 拷回 rime/，无需手工改路径。
"""
from __future__ import annotations
import argparse
import glob
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _has_non_ascii(path):
    return any(ord(c) > 127 for c in os.path.abspath(path))


def _decode(data):
    """opencc_dict.exe 在 Windows 上按系统 ANSI (GBK) 输出错误信息。"""
    if not data:
        return ''
    for enc in ('utf-8', 'gbk', 'mbcs'):
        try:
            return data.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return data.decode('utf-8', 'replace')


def _ascii_workdir():
    """原生 opencc_dict.exe 无法打开含非 ASCII 字符的路径，准备纯 ASCII 暂存目录。"""
    d = tempfile.mkdtemp(prefix='hn_ocd2_')
    if not _has_non_ascii(d):
        return d
    shutil.rmtree(d, ignore_errors=True)
    root = os.environ.get('SystemRoot') or 'C:\\Windows'
    d = os.path.join(root, 'Temp', 'hn_ocd2_' + str(os.getpid()))
    os.makedirs(d, exist_ok=True)
    return d

JOBS = [
    ('HNGuard.txt', 'HNGuard.ocd2'),
    ('TGPhrases.txt', 'TGPhrases.ocd2'),
    ('TGCharacters_keep_simp.txt', 'TGCharacters_keep_simp.ocd2'),
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

    # opencc_dict.exe 读不了中文路径：必要时在纯 ASCII 暂存目录里编译，再拷回 rime/。
    paths = [os.path.join(args.opencc_dir, s) for s, _ in JOBS]
    paths += [os.path.join(args.rime_dir, d) for _, d in JOBS]
    scratch = None
    if not args.dry_run and any(_has_non_ascii(p) for p in paths):
        scratch = _ascii_workdir()
    if scratch:
        print('ascii scratch: %s' % scratch)

    failed = 0
    try:
        for src, dst in JOBS:
            inp = os.path.join(args.opencc_dir, src)
            out = os.path.join(args.rime_dir, dst)
            if not os.path.isfile(inp):
                print('SKIP (missing) : %s' % src)
                failed += 1
                continue
            if args.dry_run:
                print('DRY-RUN       : %s -> %s' % (src, dst))
                continue
            if scratch:
                work_in = os.path.join(scratch, src)
                work_out = os.path.join(scratch, dst)
                shutil.copyfile(inp, work_in)
            else:
                work_in, work_out = inp, out
            cmd = [tool, '-i', work_in, '-o', work_out, '-f', 'text', '-t', 'ocd2']
            r = subprocess.run(cmd, capture_output=True)  # bytes，避免 GBK 解码异常
            if r.returncode != 0:
                msg = (_decode(r.stderr) or _decode(r.stdout)).strip()[:200]
                print('FAIL          : %s (%s)' % (src, msg))
                failed += 1
            else:
                if scratch:
                    shutil.copyfile(work_out, out)
                print('OK            : %-32s %8d bytes' % (dst, os.path.getsize(out)))
    finally:
        if scratch:
            shutil.rmtree(scratch, ignore_errors=True)
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
