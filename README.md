# OpenCC 大陆标准繁体 · 海宁吴语修订

> ## 在线转换工具 · 开箱即用 → <https://www.hncbx.org.cn/opencc-haining-wu-traditional/>
>
> **[直接打开使用](https://www.hncbx.org.cn/opencc-haining-wu-traditional/)** —— 不用装 OpenCC、不用配 Rime、不用注册，浏览器打开就能转。
> 8 个转换方向、实时转换与改动高亮、命中规则逐条溯源、36 条用例一键自检；
> 纯前端页面，文本不上传。需要离线时，下载 [`web/`](web/index.html) 双击 `index.html` 同样可用。

---

> 基于 [TerryTian-tech/OpenCC-...Chinese-government-standards](https://github.com/TerryTian-tech/OpenCC-Traditional-Chinese-characters-according-to-Chinese-government-standards)，
> 按海宁吴语繁体用字约定修订字表、词表后的 OpenCC 转换方案集合。
> 具备完整的**简⇄繁互转**与 **Rime 定制**能力，面向
> [海宁方言辞典](https://github.com/zjhncbx/haining-dialect-dictionary) 协作编纂系统的自动繁简转换，
> 并让编辑者在录入时可直接输入修订后的大陆标准繁体字。
> 本方案用于「潮人语」语保品牌（海宁市潮百相公益发展协会）的海宁吴语书写实践，品牌介绍见文末。

---

## 一、这是什么

2013 年国务院公布的[《通用规范汉字表》](https://www.gov.cn/zhengce/content/2013-08/19/content_1289.htm)在界定简体汉字规范性的同时，
其附件《规范字与繁体字、异体字对照表》确定了繁体汉字的正、异之别；
《新华字典》《现代汉语词典》也通过标注繁简关系间接解释了繁体汉字的字义，
基本确立了中国大陆地区的繁体汉字体系。
上游项目据此提供了 OpenCC 转换方案，本方案在其基础上作**极少量、可追溯**的修订，
作为使用繁体汉字书写海宁吴语时的规范。四类修订：

| 类型 | 内容 |
| --- | --- |
| **① 分立** | 原表部分繁体正字与其异体字中古音韵不同、海宁吴语今音亦不同，且较常用，不宜视为异体：并/併/並、只/衹/隻、吃/喫、哄/鬨、肛/疘、阁(閣)/𬮤(閤) |
| **② 合并** | 原表视为两个繁体正字、简体规范字均为甲字，实则音义等同；出于实际书写的择字需要取甲为正、乙为异体：才/纔、向/嚮曏 |
| **③ 三分** | 现代南方方言「个」字义多且有读音分化，传统方言文献已有以异体字区分音义的用例；借鉴《南昌方言词典》，定「个」助词、「個」量词名词、「箇」指示代词，**简体规范字仍作「个」** |
| **④ 补充附注** | 原表附注未注明、而海宁吴语常用者，在特定义项上也是繁体正字，故补充：序号 1285「寔」自身即为繁体正字（此、这）、不作「實」的异体；2599「蹔」（疾进）同理，其简体规范字作「𫏐」 |

分立字的简体规范字按三种情形确定：国家通用语常用且有同形繁体正字 → 参照该同形字；
常用但无同形繁体正字 → 参照原表简体规范字（并/併/並 即属此类）；罕用 → 参照类推简化字。
合并一类的典型例为「才」「纔」在「方、僅」义项上音义皆同，取「才」为正。
第 ③ 类落到简体文本时，单字「个」及未被词表收录的「个」按助词正字保留「个」；
「個」（量词、名词）、「箇」（指示代词）由词表分派。
第 ④ 类补充附注的两字不是纯粹的异体字；因「蹔」兼有「暫」的异体字身份，转换时无法按义项自动判别，故各方向保留原形、不补词组，也不把「蹔」改写为「𫏐」，输入法可直接打单字。

用字约定：海宁吴语一般说「只」，故「只」「衹」相关词在各方向一律用「只」，
不按中古反切分派「衹」；量词「隻」仍是独立正字（「一只鸟 → 一隻鳥」不受影响）。

港台习用的「於」只保留于**姓氏、人名、地名**与**感叹词**（於乎、於戲、於菟／於莵等），
其余词一律作「于」：於是→于是、等於→等于、於此→于此（繁→修订繁保持其余字形，
繁→简再按常规简化）。单字「於」不设字表映射，保留姓氏用法；
`v2s`、`t2new` 是字形方案，不参与本条约定。

《规范字与繁体字、异体字对照表》以「霉—黴」为规范字与繁体正字的对应，故「霉」是
「黴」的简化字，规范繁体一律作「黴」：发霉／發霉→發黴、倒霉→倒黴、霉乾菜→黴乾菜。
上游采用的港台按义项分化（保留「霉」及 `黴 霉` 一对多候选）本修订不采用；
Rime 里 `famei` 的两个同频候选经 `simplifier` 规范后由 `uniquifier` 并为「發黴」一个。

完整对照表见 [`doc/01-修订方案.md`](doc/01-修订方案.md)，逐条差异见
[`doc/02-与上游差异.md`](doc/02-与上游差异.md)。

### 效果示例

| 简体输入 `s2hn` | 修订版繁体 | 上游 `s2t` |
| --- | --- | --- |
| 合并 / 并非 / 并州 | **合併 / 並非 / 并州** | 合并 / 并非 / 并州 |
| 吃饭 / 口吃 | **喫飯 / 口吃** | 吃饭 / 口吃 |
| 个中 / 真个 / 一个人 | **箇中 / 真个 / 一個人** | 個中 / 真個 / 一個人 |
| 个（单字） | **个** | 個 |
| 刚才 / 面向 | **剛才 / 面向** | 剛纔 / 面嚮 |
| 内哄 / 哄笑 | **内鬨 / 哄笑** | 内哄 / 哄笑 |
| 内𬮤 / 阁楼 | **内閤 / 閣樓** | 内合 / 閣樓 |
| 发霉 / 倒霉 / 霉菌 | **發黴 / 倒黴 / 黴菌** | 發黴 / 倒霉 / 黴菌 |

港台／繁简混杂稿件走 `t2hn` 时：

| 繁体输入 `t2hn` | 修订版繁体 | 上游 `t2gov` |
| --- | --- | --- |
| 關於 / 於是 / 等於 / 於此 | **關于 / 于是 / 等于 / 于此** | 關於 / 於是 / 等於 / 於此 |
| 青出於藍 / 幾近於 | **青出于藍 / 幾近于** | 青出於藍 / 幾近於 |
| 於乎 / 於戲 / 於菟（於莵） | **原样保留「於」** | 同左 |
| 於梨華 / 樊於期 / 於潛 | **原样保留「於」** | 同左 |
| 發霉 / 發黴 / 倒霉 | **發黴 / 發黴 / 倒黴** | 發霉 / 發黴 / 倒霉 |

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

> 另有一个**开箱即用的在线转换页面**（见下），两者用途不同：
> `dist/hn-dicts.json` 供辞典系统集成，`web/dicts.js` 供页面离线直接使用。

### Rime（小狼毫）

见 [`doc/04-Rime部署.md`](doc/04-Rime部署.md)。与上游完全同一套做法：
把 `rime/` 的 1 个 json + 3 个 ocd2 放进小狼毫 `data\opencc`，
把 `luna_pinyin.custom.yaml` 放进用户文件夹，重新部署即可。
**朙月拼音原词库不动**，只替换 `simplifier` 的 OpenCC 字典。

可选：再把 `rime/custom_phrase.txt` 放进用户文件夹，把吴语助词「个」的单字候选提前
（`ge` 打出来更靠前）。用的仍是上游 schema 自带的 `custom_phrase` 机制，
不新建词库、不改 `luna_pinyin.custom.yaml`；不需要就别放。

### 在线转换页面（浏览器里直接验证）

线上入口：**<https://www.hncbx.org.cn/opencc-haining-wu-traditional/>**（见文首）。
[`web/index.html`](web/index.html) 是同一个纯前端单页工具，**双击即可离线使用**，
不需要服务器、文本不上传。用来快速核对某个字／词到底会转成什么、命中了哪条规则。

| 功能 | 说明 |
| --- | --- |
| 8 个转换方向 | `s2hn` / `t2hn` / `hn2s` / `t2s` / `t2hn_keep_simp` / `v2s` / `t2new` / `t2new_keep_simp` |
| 实时转换 + 改动高亮 | 悬停高亮处显示命中的字典与原文片段 |
| 命中规则表 | 逐条列出「原文 → 结果 → 规则来源」，含 `HNGuard` 的恒等保护词条 |
| 36 条用例自检 | 页面内一键运行，确认字典没过期、转换语义没跑偏 |
| 复制 / 粘贴 / 下载 / 字号 / 字体 | 便于把结果贴回辞典稿件、核对字形 |

字典由 `python tools/build_web.py` 从 `opencc/` 生成到 `web/dicts.js`（约 2.5 MB，
随仓库提交，页面不联网）；`tools/build.py` 已自动调用它。改字表词表后：

```bash
python tools/build.py            # 重建字典 + 刷新网页字典
python tools/make_web_corpus.py   # 用原生 OpenCC 刷新语料基准（需 pip install opencc）
node tools/verify_web.mjs         # 36 条用例 + 10 万级词表语料 md5 比对
```

线上页面已发布：**<https://www.hncbx.org.cn/opencc-haining-wu-traditional/>**
（备用地址 <https://zjhncbx.github.io/opencc-haining-wu-traditional/>）。
仓库 **Settings → Pages → Source 选 GitHub Actions** 后，
[`pages.yml`](.github/workflows/pages.yml) 会在 `web/**` 变动时自动重新部署；
也可以把 `web/` 整个目录丢到任意静态服务器，或本地双击 `index.html`。

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

数据文件：`HNPhrases.txt`（94 条方案优先词条）、`HNGuard.txt`（46 条保护词条）、
`STCharacters/STPhrases`、`TSCharacters/TSPhrases`、`TGCharacters/TGPhrases`、
`GovVariants`、`VSCharacters/VSPhrases`、`CJK_Compatibility_Ideographs.txt`。

---

## 四、目录结构

```
├── README.md  LICENSE  NOTICE  CONTRIBUTING.md  .gitignore
├── assets/
│   └── chaorenyu-brand.jpg   # 「潮人语」品牌图（仅用于 README 展示）
├── doc/
│   ├── 01-修订方案.md        # 修订说明与对照表
│   ├── 02-与上游差异.md      # 字表/词表逐条差异、已知取舍
│   ├── 03-集成指南.md        # 辞典协作系统接入、CI 校验
│   └── 04-Rime部署.md        # 小狼毫部署与分立正字输入
├── opencc/                   # 25 个 json + 修订后的完整 txt 字表词表
├── rime/                     # 1 json + 3 ocd2 + luna_pinyin.custom.yaml + 可选 custom_phrase.txt
├── web/                      # 在线转换页面：index.html / style.css / engine.js / app.js / dicts.js
├── rules/
│   ├── overrides.tsv         # ★ 协作编辑入口：简 -> 修订繁 特例词表
│   └── split_reference.txt   # OpenCC 原版 595 条分立字参考词条
├── tools/
│   ├── rules.py              # 修订规则单一数据源
│   ├── build.py              # 生成器（支持 --dry-run）
│   ├── build_ocd2.py         # 编译 Rime ocd2
│   ├── build_web.py          # 生成 web/dicts.js（由 build.py 自动调用）
│   ├── export_web_dict.py    # 导出集成用 dist/hn-dicts.json
│   ├── make_web_corpus.py    # 刷新网页引擎的语料基准
│   ├── verify_web.mjs        # Node 网页引擎回归（用例 + 语料 md5）
│   └── verify.py             # 35 项转换回归测试（31 组用例 + 4 组往返）
├── examples/python/convert.py
├── examples/js/convert.mjs
└── tests/
    ├── cases.json            # 31 组转换用例
    └── web_corpus.json       # 网页引擎 vs 原生 OpenCC 的语料 md5 基准
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
词组级规则集中在 `rules/overrides.tsv` 与 `tools/rules.py`（`TG_GUARD`）。
Rime 不另建词库，输入方案沿用朙月拼音原词库。

回归测试：`python tools/verify.py`（转换用例）与 `node tools/verify_web.mjs`（网页引擎语料比对）。

---

## 六、许可与边界

- 代码、文档、修订规则：**Apache License 2.0**（`LICENSE` 为上游全文副本）。
- 字典数据为上游字典的派生作品，同样适用 Apache-2.0，
  上游版权声明与贡献者信息保留在各 `.txt` 文件头与 `NOTICE` 中。
- `assets/chaorenyu-brand.jpg` 为「潮人语」品牌图片，版权归海宁市潮百相公益发展协会所有，
  仅用于本 README 的品牌展示，**不适用** Apache-2.0 授权。
- 上游字典数据、以及本修订方案，均**不能替代**国家现行汉字规范的法定效力；
  出版、教材等场景请以[《通用规范汉字表》](https://www.gov.cn/zhengce/content/2013-08/19/content_1289.htm)等官方文件为准。
- 本方案是面向海宁吴语书写的地方性用字约定，不是对《通用规范汉字表》的官方修订。

---

## 七、相关链接

- **在线转换工具（开箱即用）：<https://www.hncbx.org.cn/opencc-haining-wu-traditional/>**
- 《通用规范汉字表》（2013）：<https://www.gov.cn/zhengce/content/2013-08/19/content_1289.htm>
- 上游方案：<https://github.com/TerryTian-tech/OpenCC-Traditional-Chinese-characters-according-to-Chinese-government-standards>
- OpenCC：<https://github.com/BYVoid/OpenCC>
- 集成目标：<https://github.com/zjhncbx/haining-dialect-dictionary>
- 协会组织：<https://github.com/zjhncbx> · <https://www.hncbx.org.cn>

---

## 八、关于「潮人语」

「潮人语」是海宁市潮百相公益发展协会的语保品牌与音乐组合，以海宁方言的记录、书写与传播为工作方向。
本方案服务于「潮人语」的海宁吴语书写与[海宁方言辞典](https://github.com/zjhncbx/haining-dialect-dictionary)编纂实践，
为繁体用字提供一套可复现、可校验的转换依据。

<img src="assets/chaorenyu-brand.jpg" alt="潮人语 · 海宁市潮百相公益发展协会 · 语保品牌与音乐组合" width="720">

> 图片含「潮人语」品牌二维码。版权归海宁市潮百相公益发展协会所有，授权说明见「六、许可与边界」。
