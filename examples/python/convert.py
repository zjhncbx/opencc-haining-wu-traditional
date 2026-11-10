#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""辞典协作编辑系统的接入示例（服务端 Python）。

    pip install opencc
    python examples/python/convert.py

演示三件事：
  1. 把本仓库的 opencc/*.json 直接交给 OpenCC 加载（不需要安装到系统目录）；
  2. 封装成 HainingWuConverter，供词目 / 义项 / 例句字段调用；
  3. 对旧资料做一次「规范化 -> 校验」的批量导入。
"""
from __future__ import annotations
import os
import sys

try:
    import opencc
except ImportError:
    sys.exit('缺少依赖：pip install opencc')

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_DIR = os.path.join(ROOT, 'opencc')


class HainingWuConverter:
    """面向辞典条目的繁简转换封装。

    s2hn   简体 -> 修订版大陆标准繁体：录入时把编辑者的简体输入规范化
    hn2s   修订版大陆标准繁体 -> 简体：检索、对外展示、导出简版
    t2hn   任意繁体 -> 修订版大陆标准繁体：导入港台/旧字形/异体混杂的旧资料
    """

    def __init__(self, config_dir=CONFIG_DIR):
        self._c = {
            name: opencc.OpenCC(os.path.join(config_dir, name + '.json'))
            for name in ('s2hn', 'hn2s', 't2hn', 't2hn_keep_simp')
        }

    def to_traditional(self, text: str) -> str:
        return self._c['s2hn'].convert(text)

    def to_simplified(self, text: str) -> str:
        return self._c['hn2s'].convert(text)

    def normalize(self, text: str) -> str:
        return self._c['t2hn'].convert(text)

    def normalize_keep_simplified(self, text: str) -> str:
        return self._c['t2hn_keep_simp'].convert(text)

    def convert_entry(self, entry: dict, fields=('headword', 'senses', 'examples')) -> dict:
        """按字段转换一条辞典词条；原对象不被修改。"""
        out = dict(entry)
        for field in fields:
            value = entry.get(field)
            if isinstance(value, str):
                out[field] = self.to_traditional(value)
            elif isinstance(value, list):
                out[field] = [
                    self.to_traditional(v) if isinstance(v, str) else
                    self.convert_entry(v, fields) if isinstance(v, dict) else v
                    for v in value
                ]
        return out

    def is_consistent(self, simplified: str, traditional: str) -> bool:
        """校验「简体原文」与「繁体词条」是否互为转换结果。"""
        return self.to_traditional(simplified) == traditional and \
               self.to_simplified(traditional) == simplified


def main():
    c = HainingWuConverter()

    print('=== 单句转换 ===')
    sample = '并州 合并 并非 吃饭 个中 真个 面向 刚才 内哄 阁楼 内𬮤'
    trad = c.to_traditional(sample)
    print('s2hn :', trad)
    print('hn2s :', c.to_simplified(trad))
    print('t2hn :', c.normalize('一併 並不 喫飯 纔來 面嚮 箇中 內閤 疘'))

    print('\n=== 辞典词条字段转换 ===')
    entry = {
        'id': 'HN-0001',
        'headword': '吃饭',
        'senses': ['进食', '承受、吃亏'],
        'examples': ['一个人吃饭，只是随便吃点。', '这只鸟真个好看。'],
    }
    converted = c.convert_entry(entry)
    for k, v in converted.items():
        print('  %-10s %s' % (k, v))

    print('\n=== 导入旧资料 + 一致性校验 ===')
    legacy = '一併處理，並非箇中緣由；剛纔面嚮講臺'
    normalized = c.normalize(legacy)
    print('  normalized:', normalized)
    print('  round-trip:', c.to_simplified(normalized))
    print('  consistent:', c.is_consistent(
        '合并 并非 吃饭 个中 真个',
        '合併 並非 喫飯 箇中 真个'))


if __name__ == '__main__':
    main()
