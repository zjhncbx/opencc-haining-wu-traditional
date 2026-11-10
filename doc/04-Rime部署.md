# Rime（小狼毫）部署与「直接输入修订繁体字」

本仓库提供与上游等价的 Rime 定制能力，并额外提供一个**分立正字词库**，
让编辑辞典时能直接打出 `併 / 並 / 喫 / 衹 / 隻 / 鬨 / 疘 / 閤 / 箇 / 𬮤`
等修订后的大陆标准繁体字。

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

## 二、配置输出方案

把 `rime/luna_pinyin.custom.yaml` 复制到 Rime 用户文件夹
（Windows：`%APPDATA%\Rime`）：

```yaml
patch:
  switches:
    - name: simplification
      reset: 1
  simplifier:
    opencc_config: t2hn_keep_simp.json
    option_name: simplification
  "translator/dictionary": haining_wu_extended
```

再把这两个文件放到同一目录：

```
rime/haining_wu.dict.yaml            # 分立正字 + 例词
rime/haining_wu_extended.dict.yaml   # 朙月拼音原词库 + 上面的补充词库
```

在小狼毫「中」字图标右键 → **重新部署**。

---

## 三、直接输入修订后的繁体正字

`haining_wu.dict.yaml` 已为每个分立正字标注拼音并给出较高权重：

| 拼音 | 候选（部分） |
| --- | --- |
| `bing` | 并、併、並、幷、倂、竝、并州、合併、並非、並且 |
| `chi` / `ji` | 喫、吃；口吃（`kou ji`） |
| `zhi` | 只、衹、隻、祇、秖；衹是、只要、一隻鳥 |
| `ge` | 个、個、箇、閤、𬮤、阁、閣；箇中、真个、內閤、閣樓 |
| `hong` | 哄、鬨、閧；哄笑、內鬨、一鬨而散 |
| `gang` / `gong` | 肛（gang）、疘（gong）、肛門、胴疘 |
| `xiang` / `cai` | 向、嚮、才、纔（后二者为异体，权重较低） |

例词也被收录，因此词组输入即可直接出规范字形：
`he bing → 合併`、`bing fei → 並非`、`chi fan → 喫飯`、
`ge zhong → 箇中`、`nei ge → 內閤`、`nei hong → 內鬨`。

### 验证

部署后依次输入，确认候选栏出现的是修订字形：

```
he bing   → 合併（不是「合并」）
bing fei  → 並非
chi fan   → 喫飯
ge zhong  → 箇中
zhen ge   → 真个（不是「真個」）
nei ge    → 內閤
gang cai  → 剛才（不是「剛纔」）
```

---

## 四、改成其它输入方案

本仓库的 `t2hn_keep_simp.json` / `s2hn.json` 是通用 OpenCC 配置，
可按同样思路挂到任何 Rime 方案的 `simplifier`：

```yaml
# <方案名>.custom.yaml
patch:
  simplifier:
    opencc_config: s2hn.json      # 简体输入 -> 修订繁体输出
    option_name: simplification
```

`s2hn.json` 使用 `HNPhrases.txt`、`STPhrases.txt`、`STCharacters.txt`
（纯文本，方案 B 的目录内已包含前两个，另需复制 `STCharacters.txt`）。

> 注意：`s2hn` 是「简 → 修订繁」，用于**本来输出简体**的输入方案；
> 若方案本身已输出繁体，应使用 `t2hn_keep_simp`（繁 → 修订繁），
> 否则会出现二次转换。

---

## 五、字体提示

`𬮤`（U+2CB64）属 CJK 扩展区，旧版字体可能显示成方框。
请使用思源黑体 / Noto Sans CJK、霞鹜文楷等较新字体，
并在 Rime 的 `style/font_face` 中指定。
