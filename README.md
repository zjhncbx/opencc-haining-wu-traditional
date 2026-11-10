# OpenCC 大陆标准繁体 · 海宁吴语修订

> 基于 [TerryTian-tech/OpenCC-...Chinese-government-standards](https://github.com/TerryTian-tech/OpenCC-Traditional-Chinese-characters-according-to-Chinese-government-standards)，
> 按《大陸標準繁體漢字海寧吴語修訂方案》修订字表、词表后的 OpenCC 转换方案集合。
> 具备完整的**简⇄繁互转**与 **Rime 定制**能力，面向
> [海宁方言辞典](https://github.com/zjhncbx/haining-dialect-dictionary) 协作编纂系统的自动繁简转换，
> 并让编辑者在录入时可直接输入修订后的大陆标准繁体字。

---

## 一、这是什么

2013 年《通用规范汉字表》附件 1 确定了大陆地区的规范繁体字形，上游项目据此提供了
OpenCC 转换方案。本方案在其基础上作**极少量、可追溯**的修订，作为使用繁体汉字书写
海宁吴语时的规范。三类修订：

| 类型 | 内容 |
| --- | --- |
| **① 分立** | 原表视为异体/合并、但在现代吴语中读音字义并不等同的字，分立为多个繁体正字：并/併/並、只/衹/隻、吃/喫、哄/鬨、肛/疘、阁(閣)/𬮤(閤) |
| **② 合并** | 原本两个繁体正字而音义等同者，取一为正、另一为异体：才（正）/纔（异）、向（正）/嚮（异） |
| **③ 三分** | 借鉴《南昌方言词典》：「个」助词、「個」量词与名词、「箇」指示代词 |

> **2026-11-10 更正**：1639 组「閤」的简体规范字由「閤」更正为「**𬮤**」
> （原文档因该类推简化字当时无法输入而暂写作「閤」）。繁体正字仍为「閤」。

完整对照表见 [`doc/01-修订方案.md`](doc/01-修订方案.md)，逐条差异见
[`doc/02-与上游差异.md`](doc/02-与上游差异.md)。

### 效果示例

| 简体输入 `s2hn` | 修订版繁体 | 上游 `s2t` |
| --- | --- | --- |
| 合并 / 并非 / 并州 | **合併 / 並非 / 并州** | 合并 / 并非 / 并州 |
| 吃饭 / 口吃 | **喫飯 / 口吃** | 吃饭 / 口吃 |
| 个中 / 真个 / 一个人 | **箇中 / 真个 / 一個人** | 個中 / 真個 / 一個人 |
| 刚才 / 面向 | **剛才 / 面向** | 剛纔 / 面嚮 |
| 内哄 / 哄笑 | **內鬨 / 哄笑** | 内哄 / 哄笑 |
| 内𬮤 / 阁楼 | **內閤 / 閣樓** | 内合 / 閣樓 |

---

## 二、快速开始

### 直接用 OpenCC（Python）

```bash
pip install opencc            # 需 >= 1.3.2，实测 1.4.2
```

```python
import opencc
CFG = './opencc'
s2hn = opencc.OpenCC(f'{CFG}/s2hn.json')   # 简 -> 修订繁
hn2s = opencc.OpenCC(f'{CFG}/hn2s.json')   # 修订繁 -> 简
t2hn = opencc.OpenCC(f'{CFG}/t2hn.json')   # 任意繁（港台/异体/旧字形）-> 修订繁

s2hn.convert('合并 并非 吃饭 个中 真个')
# '合併 並非 喫飯 箇中 真个'
```

json 支持绝对路径，字典按 json 所在目录解析，**无需安装到系统目录**。
完整封装见 [`examples/python/convert.py`](examples/python/convert.py)。

### 浏览器 / Node（无需原生 OpenCC）

```bash
python tools/export_web_dict.py     # 生成 dist/hn-dicts.json
node examples/js/convert.mjs
```

见 [`examples/js/convert.mjs`](examples/js/convert.mjs) 与
[`doc/03-集成指南.md`](doc/03-集成指南.md)。

### Rime（小狼毫）

见 [`doc/04-Rime部署.md`](doc/04-Rime部署.md)。一句话流程：
`python tools/build_ocd2.py` → 复制 `rime/` 文件 → 放
`luna_pinyin.custom.yaml` + 两个 `.dict.yaml` → 重新部署。
之后 `he bing` 直接出「合併」、`ge` 可打出「箇 / 閤 / 𬮤」。

---

## 三、转换方案清单

`opencc/` 下共 25 个配置，保留上游全部五种基础方案及其 jieba / keep_simp 变体，
另增四个语义清晰的集成入口（加粗）：

| 方案 | 方向 | 用途 |
| --- | --- | --- |
| **`s2hn.json`** | 简体 → 修订版大陆标准繁体 | **辞典录入时自动繁化（主入口）** |
| **`hn2s.json`** | 修订版繁体 → 简体 | **检索 / 简版展示 / 导出（主入口）** |
| **`t2hn.json`** | 任意繁体 → 修订版繁体 | **导入旧资料规范化（主入口）** |
| **`t2hn_keep_simp.json`** | 同上但保留文中简体 | 繁简混杂稿件 |
| `s2t.json` | 同 `s2hn` | 上游命名兼容 |
| `t2s.json` | 同 `hn2s` | 上游命名兼容 |
| `t2gov.json` | 同 `t2hn` | 上游命名兼容 |
| `t2gov_keep_simp.json` | 同 `t2hn_keep_simp` | 上游命名兼容 |
| `t2new.json` / `t2new_keep_simp.json` | 只转旧字形→新字形，保留异体 | 古诗文整理 |
| `v2s.json` | 只把异体字转简体 | 校对辅助 |
| `*_jieba.json` / `*_jieba_traditional.json` | 上述方案的分词/候选字变体 | 需 jieba 词典 |

数据文件：`HNPhrases.txt`（93 条方案优先词条）、`HNGuard.txt`（15 条保护词条）、
`STCharacters/STPhrases`、`TSCharacters/TSPhrases`、`TGCharacters/TGPhrases`、
`GovVariants`、`VSCharacters/VSPhrases`、`CJK_Compatibility_Ideographs.txt`。

---

## 四、目录结构

```
├── README.md  LICENSE  NOTICE  CONTRIBUTING.md  .gitignore
├── doc/
│   ├── 01-修订方案.md        # docx 对照表转录（含 𬮤 更正）
│   ├── 02-与上游差异.md      # 字表/词表逐条差异、已知取舍
│   ├── 03-集成指南.md        # 辞典协作系统接入、CI 校验
│   └── 04-Rime部署.md        # 小狼毫部署与分立正字输入
├── opencc/                   # 25 个 json + 修订后的完整 txt 字表词表
├── rime/                     # Rime 配置、词库、部署用 yaml
├── rules/
│   ├── overrides.tsv         # ★ 协作编辑入口：简 -> 修订繁 特例词表
│   └── split_reference.txt   # OpenCC 原版 595 条分立字参考词条
├── tools/
│   ├── rules.py              # 修订规则单一数据源
│   ├── build.py              # 生成器（支持 --dry-run）
│   ├── build_ocd2.py         # 编译 Rime ocd2
│   ├── export_web_dict.py    # 导出前端 JSON 字典
│   └── verify.py             # 18 项转换回归测试
├── examples/python/convert.py
├── examples/js/convert.mjs
└── tests/cases.json          # 14 组转换用例
```

---

## 五、协作与复现

字典会随辞典编纂持续修订。发现漏转 / 误转时，**只需改一处**：

```bash
# 1) 在 rules/overrides.tsv 补一行：「简体词<TAB>修订繁体词」
# 2) 重新生成 + 回归
git clone --depth 1 https://github.com/TerryTian-tech/OpenCC-Traditional-Chinese-characters-according-to-Chinese-government-standards.git /path/to/upstream
python tools/build.py --upstream /path/to/upstream/t2gov --dry-run   # 先看改动
python tools/build.py --upstream /path/to/upstream/t2gov
python tools/verify.py
python tools/export_web_dict.py
```

生成器确定且幂等：不修改上游文件，重复运行得到相同结果。
字表级规则集中在 `tools/rules.py`（`CHAR_PATCH`、`REVISION_TABLE`），
词组级规则集中在 `rules/overrides.tsv` 与 `tools/rules.py`（`TG_GUARD`、`RIME_ENTRIES`）。

当前回归结果：**18 项全部通过**（14 组转换用例 + 4 组简繁往返一致性）。

---

## 六、许可与边界

- 代码、文档、修订规则：**Apache License 2.0**（`LICENSE` 为上游全文副本）。
- 字典数据为上游字典的派生作品，同样适用 Apache-2.0，
  上游版权声明与贡献者信息保留在各 `.txt` 文件头与 `NOTICE` 中。
- 上游字典数据、以及本修订方案，均**不能替代**国家现行汉字规范的法定效力；
  出版、教材等场景请以《通用规范汉字表》等官方文件为准。
- 本方案是面向海宁吴语书写的地方性用字约定，不是对《通用规范汉字表》的官方修订。

---

## 七、相关链接

- 上游方案：<https://github.com/TerryTian-tech/OpenCC-Traditional-Chinese-characters-according-to-Chinese-government-standards>
- OpenCC：<https://github.com/BYVoid/OpenCC>
- 集成目标：<https://github.com/zjhncbx/haining-dialect-dictionary>
- 协会组织：<https://github.com/zjhncbx> · <https://www.hncbx.org.cn>
