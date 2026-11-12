# 四、Rime（小狼毫）部署

与上游仓库 README「规范繁体转换方案如何应用于小狼毫」完全同一套做法：
**朙月拼音原词库一字不动**，只把 `simplifier` 用的 OpenCC 字典换成修订版。
不新建词库、不改 `translator/dictionary`，候选排序继续由原词库 + `essay.txt` 决定。

唯一与上游不同的可选步骤：多放一个纯文本 `custom_phrase.txt`，
把吴语助词「个」的**单字**候选往前排。这一步用的是上游 schema 自带的
`table_translator@custom_phrase`，仍不涉及任何自建词库。

## 一、放 4 个字典文件

复制到小狼毫**共享数据目录**的 `opencc` 文件夹，例如：

```
D:\Program Files\Rime\weasel-0.17.4\data\opencc\
```

| 文件 | 说明 |
| --- | --- |
| `t2hn_keep_simp.json` | 修订版转换配置（对应上游 `t2gov_keep_simp.json`） |
| `HNGuard.ocd2` | 修订新增：保护「真个 / 个中→箇中 / 内閤 / 胴疘」等特例 |
| `TGPhrases.ocd2` | 修订后的词表 |
| `TGCharacters_keep_simp.ocd2` | 修订后的字表（保留简体字，含「黃→黄」） |

上游是 1 个 json + 2 个 ocd2；本修订多 1 个 `HNGuard.ocd2`，
用来保证分立正字不被词表规则归并。ocd2 已随仓库提供，无需自行编译。

另：`TGCharacters_keep_simp.txt` 已把文档附注的「寔」「蹔」改为恒等映射，
重新编译后的 `TGCharacters_keep_simp.ocd2` 会保留这两个单字候选，不会转成
「實 / 暫」；词表不补任何含这两字的词组。

## 二、放 1 个方案补丁

把 `rime/luna_pinyin.custom.yaml` 复制到 Rime **用户文件夹**
（Windows：`%APPDATA%\Rime`）。内容就是上游 README 的 8 行：

```yaml
patch:
  switches:
    - name: simplification
      reset: 1

  simplifier:
    opencc_config: t2hn_keep_simp.json
    option_name: simplification
```

`reset: 1` 让转换默认开启，所有候选都过一遍修订版规范繁体：

- 「黃」→「黄」（大陆标准字形）、「纔」→「才」、「嚮 / 曏」→「向」
- 「並 / 併 / 喫 / 隻 / 鬨 / 疘 / 閤 / 箇」保持分立，不再被归并
- 「衹」→「只」（吴语用字约定；「神祇」不受影响）

## 三、可选：把助词「个」提前

海宁吴语里「个」作结构助词（约相当于普通话「的」），通常**单字出现**、使用极频繁；
朙月拼音原词库按普通话词频排序，打 `ge` 时它未必在前几位。
把 `rime/custom_phrase.txt` 复制到 Rime **用户文件夹**（`%APPDATA%\Rime`）即可：

```
个	ge	1000
```

原理是上游 `luna_pinyin.schema.yaml` 本来就带
`table_translator@custom_phrase` 和 `custom_phrase` 段，用户文件夹里放同名 txt
就会自动生效，**不需要改 `luna_pinyin.custom.yaml`，也不需要 `import_tables`**。

| 想怎样 | 怎么改 |
| --- | --- |
| 更靠前 / 稳居首选 | 把 `1000` 调大，如 `10000` |
| 只想往前挪几位 | 把 `1000` 调小，如 `100` |
| 恢复上游默认 | 删掉这一行或整个文件，重新部署 |

注意：

- 只加**单字**，不造「个XX」之类的词，不影响 `ge ren`、`yi ge`、`ge ge` 等整词候选，
  也不影响其他音节。
- 「个」不是 `TGCharacters_keep_simp.txt` 的转换键，`simplifier` 不会改写它，
  上屏仍是「个」；「個 / 箇」分立正字照旧从原词库出。
- 若用户文件夹已有自己的 `custom_phrase.txt`，**追加最后一行**，不要覆盖。

## 四、重新部署

右键小狼毫「中」字图标 → **重新部署**。
新增或改动 `custom_phrase.txt` 后若没立刻生效，做一次全量重新部署（不要用增量）。

## 五、验证

| 输入 | 期望 |
| --- | --- |
| `huang` | 出「黄」，不是旧字形「黃」 |
| `ge ren` | 首选「個人」 |
| `wo` | 首选「我」，不会先冒出「㠛㦱㧴」 |
| `he bing` / `bing fei` / `chi fan` | 合併 / 並非 / 喫飯 |
| `ge` | 加了第三节的文件后「个」明显靠前；「個 / 箇 / 閤」仍可翻到 |
| `shi` / `zhan` | 「寔」「蹔」单字可打出，不会被转成「實 / 暫」（附注两字） |
| `zhi` | 「衹」候选统一显示为「只」，「隻」仍可打出 |
| `nei` | 「内」为大陆标准字形，不是旧字形「內」 |
| `yu` | 「于」为大陆标准字形；「於是 / 關於」等词显示为「于是 / 關于」，单字「於」保留供姓氏使用 |
| `famei` / `mei` | 只出一个「發黴」／「黴」，不再与「發霉」／「霉」并存 |

分立正字和整词都来自朙月拼音原词库 + `essay.txt` 词频，本仓库不另建词库：
`luna_pinyin.dict.yaml` 已收录 並 / 併 / 喫 / 隻 / 鬨 / 疘 / 閤 / 箇 / 個 等单字；
「衹」虽在原词库中，但会由 `simplifier` 规范为「只」，
`essay.txt` 已有「個人 102677」「合併 9371」「並非 20707」「喫飯 31690」等词频。
「於」的例外词（於乎、於戲、於菟／於莵、於梨華、樊於期、於潛 等）由 `HNGuard.ocd2`
恒等保护，不会被 simplifier 改写；其余含「於」的词由 `TGPhrases.ocd2` 规范为「于」。
「霉」由 `TGCharacters_keep_simp.ocd2` 规范为「黴」（《对照表》繁简对应），
`essay.txt` 里同为 1135 词频的「發霉」「發黴」经 `uniquifier` 去重后只显示一个「發黴」；
单字 `mei` 同理。第三节的 `custom_phrase.txt` 是唯一一处词频调整，且只作用于 `ge` 的单字候选。

## 六、改动字表后重新编译

改完 `opencc/*.txt` 并跑 `tools/build.py` 之后：

```
python tools/build_ocd2.py
```

把 `rime/` 下新生成的 3 个 `.ocd2` 复制到 `data\opencc`，再重新部署。
`opencc_dict.exe` 打不开含中文的路径，脚本会自动用纯 ASCII 临时目录中转。

## 七、不要做的事

| 不要 | 原因 |
| --- | --- |
| 不要 `patch: "translator/dictionary": ...` 挂自建扩展词库 | `import_tables` 不继承 `use_preset_vocabulary`，会丢掉 `essay.txt` 全部词频，候选按码点排序，出现 `wo → 㠛㦱㧴` |
| 不要为了调「个」的词频去改 `luna_pinyin.dict.yaml` 或新建 dict | 上游自带的 `custom_phrase.txt` 就够，改动面最小、随时可撤 |
| 不要删 `simplifier` 段 | 候选不再经过规范繁体转换，`huang` 就只剩旧字形「黃」 |
| 不要改 `opencc_config` 为 `s2hn.json` | 那是整篇「简 → 修订繁」转换，不是输入法候选过滤 |

> **复盘**：早期版本曾自建 `haining_wu_extended` 词库并去掉 `simplifier`，
> 导致「𬮤㠴」伪词抢占首选、`wo` 冒出扩展区生僻字、`huang` 不出「黄」。
> 现已全部回退到上游方案，仓库不再包含任何自建 Rime 词库。
