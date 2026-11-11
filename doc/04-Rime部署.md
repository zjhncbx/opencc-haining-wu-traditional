# Rime（小狼毫）部署与「直接输入修订繁体字」

本仓库提供与上游等价的 Rime 定制能力，并额外提供一个**分立正字词库**，
让编辑辞典时能直接打出 `併 / 並 / 喫 / 衹 / 隻 / 鬨 / 疘 / 閤 / 箇 / 𬮤`
等修订后的大陆标准繁体字。

> **最省事的部署只需 3 个 yaml 文件**（见第二节），不需要编译 `.ocd2`、
> 也不需要 `opencc` 目录。下面第一节的 ocd2 / 纯文本方案，只在需要
> 「繁体稿件规范化」或「全局简 → 修订繁」时才用。
>
> 上游 Rime 目录直接给出预编译 `.ocd2`；本仓库改为**脚本生成**，
> 因为修订字表会随协作编辑持续更新，预编译二进制容易过时。
> 若不想生成二进制，可直接使用 `t2hn_keep_simp_text.json`（纯文本配置）。

---

## 一、准备文件

```bash
# 1) 生成 ocd2（需要 OpenCC 自带的 opencc_dict，Python 版 opencc 包已包含）
python tools/build_ocd2.py
# 产物：rime/*.ocd2 共 6 个

# 2) 若找不到 opencc_dict，显式指定
python tools/build_ocd2.py --opencc-dict "D:/ProgramData/anaconda3/Lib/site-packages/opencc/clib/bin/opencc_dict.exe"
```

> **Windows 中文路径**：原生 `opencc_dict.exe` 无法读取含非 ASCII 字符的路径，
> 在「上传用-仓库文件」这类中文目录下会误报 `not found or not accessible`。
> 本脚本会自动把字典复制到纯 ASCII 临时目录编译，再把 `.ocd2` 拷回 `rime/`，
> 无需手工改名或搬目录。若自行指定 `--opencc-dict`，请确保该 exe 自身路径为纯 ASCII。

### 方案 A：ocd2（与上游一致，推荐）

把以下文件复制到小狼毫的 opencc 数据目录
（Windows 示例：`C:\Program Files\Rime\weasel-0.17.4\data\opencc`，
版本号按实际安装版本替换）：

```
rime/t2hn_keep_simp.json
rime/HNGuard.ocd2
rime/TGPhrases.ocd2
rime/TGCharacters_keep_simp.ocd2
```

### 方案 B：纯文本（免编译）

把以下文件复制到 Rime 用户文件夹下的 `opencc/` 子目录
（Windows：`%APPDATA%\Rime\opencc\`）：

```
rime/t2hn_keep_simp_text.json   → 重命名为 t2hn_keep_simp.json
opencc/HNGuard.txt
opencc/TGPhrases.txt
opencc/TGCharacters_keep_simp.txt
opencc/CJK_Compatibility_Ideographs.txt
```

> `t2hn_keep_simp_text.json` 省略了 `segmentation`（mmseg 需要 ocd2），
> 使用 `short_circuit` 的 group 做最长匹配，功能等价、速度略慢。

---

## 二、基础部署：直接打出修订繁体（推荐）

把这三个文件放进 Rime 用户文件夹（Windows：`%APPDATA%\Rime`）：

```
rime/luna_pinyin.custom.yaml
rime/haining_wu.dict.yaml            # 分立正字 + 常用整词
rime/haining_wu_extended.dict.yaml   # 朙月拼音原词库 + 上面的补充词库
```

`luna_pinyin.custom.yaml` 里只做一件事：

```yaml
patch:
  "translator/dictionary": haining_wu_extended
```

然后在小狼毫「中」字图标右键 → **重新部署**。不需要 `opencc` 目录、
不需要编译 `.ocd2`，也不需要改任何开关。

### 两个「不要」

| 不要 | 原因 |
| --- | --- |
| 不要 patch `switches` | `switches` 是列表，整段写入会**覆盖**朙月拼音原有的 `ascii_mode` / `full_shape` / `zh_hant` / `simplification` 等开关。原来设好的繁体输出会失效，`simplification` 还会被强制默认开启 |
| 不要在这里改 `simplifier` | `t2hn_keep_simp.json` 是「繁体稿件 → 规范繁体」的**规范化**配置，不是「拼音简体候选 → 修订繁体」的输入转换；它还依赖 6 个 ocd2/txt 字典，未一并放置时转换器会加载失败 |

> **故障复盘**：曾出现「打 `geren` 首选是 `𬮤㠴`、找不到 `個人`」。
> 根因是 ① `switches` 被整段覆盖，`zh_hant` 开关丢失；
> ② 扩展词库把极生僻的「𬮤」给了 900 权重，又没有「個人」整词，
> Rime 只能用单字自动组词，拼出「𬮤」+ 同音生僻字的伪词。
> 现已把生僻正字权重压到 100~500，并补入 `個人`（权重 2000）等常用整词。

### 验证

部署后依次输入，确认候选栏出现的是修订字形：

```
ge ren    → 個人（首选，不是「𬮤㠴」）
he bing   → 合併（不是「合并」）
bing fei  → 並非
chi fan   → 喫飯
ge zhong  → 箇中
zhen ge   → 真个（不是「真個」）
nei ge    → 內閤
gang cai  → 剛才（不是「剛纔」）
```

---

## 三、直接输入修订后的繁体正字

`haining_wu.dict.yaml` 分两层权重：

| 层级 | 权重 | 内容 |
| --- | --- | --- |
| 常用整词 | 1000~2000 | `個人`、`合併`、`並非`、`喫飯`、`衹是`、`剛才`、`一個人` 等，压过自动组词 |
| 常用单字 | 800~1000 | 并、只、吃、个、個、向、才、哄、阁、閣、合 等 |
| 分立正字 | 100~500 | 併、並、喫、衹、隻、鬨、疘、閤、𬮤、箇 等，翻候选可取，不抢首选 |
| 异体字 | 100 | 幷、倂、竝、祇、秖、嚮、曏、纔、閧，仅备查 |

| 拼音 | 候选（部分） |
| --- | --- |
| `bing` | 并、並、併、幷、倂、竝、并州、合併、並非、並且 |
| `chi` / `ji` | 吃、喫；喫飯、喫茶；口吃（`kou ji`） |
| `zhi` | 只、隻、衹、祇、秖；衹是、只要、一隻鳥 |
| `ge` / `ge ren` | 个、個、阁、閣、箇、閤、𬮤；**個人**、各人、箇中、真个、內閤、閣樓 |
| `hong` | 哄、鬨、閧；哄笑、內鬨、一鬨而散 |
| `gang` / `gong` | 肛（gang）、疘（gong）、肛門、胴疘 |
| `xiang` / `cai` | 向、才；嚮、曏、纔（异体，权重最低） |

词组输入直接出规范字形：`ge ren → 個人`、`he bing → 合併`、
`bing fei → 並非`、`chi fan → 喫飯`、`ge zhong → 箇中`、
`nei ge → 內閤`、`nei hong → 內鬨`。

---

## 四、可选：全局「简 → 修订繁」（进阶）

基础部署已能打出全部修订正字。若还希望**词库里没列出的**简体候选也自动
转成修订繁体，才需要这一节。

1. 在 Rime 用户文件夹下建 `opencc/` 子目录（`%APPDATA%\Rime\opencc\`），放入：

```
rime/s2hn.json            → opencc/s2hn.json
opencc/HNPhrases.txt      → opencc/HNPhrases.txt
opencc/STPhrases.txt      → opencc/STPhrases.txt
opencc/STCharacters.txt   → opencc/STCharacters.txt
```

2. 在 `luna_pinyin.custom.yaml` 的 `patch:` 下**追加**（依旧不要动 `switches`）：

```yaml
  simplifier:
    opencc_config: s2hn.json
    option_name: simplification
```

3. 重新部署。

> `s2hn` 是「简 → 修订繁」，只适用于**本来输出简体**的方案。朙月拼音的
> `simplification` 开关原标签是「汉字／漢字」，换用 `s2hn.json` 后
> 开关开启时实际输出修订繁体，标签语义会相反，属预期行为。
> 若方案本身已输出繁体，应改用 `t2hn_keep_simp.json`（繁 → 修订繁）
> 及其 6 个字典，见第一节方案 A / B，否则会二次转换。

---

## 五、字体提示

`𬮤`（U+2CB64）属 CJK 扩展区，旧版字体可能显示成方框。
请使用思源黑体 / Noto Sans CJK、霞鹜文楷等较新字体，
并在 Rime 的 `style/font_face` 中指定。
