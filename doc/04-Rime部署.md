# 四、Rime（小狼毫）部署

与上游仓库 README「规范繁体转换方案如何应用于小狼毫」完全同一套做法：
**朙月拼音原词库一字不动**，只把 `simplifier` 用的 OpenCC 字典换成修订版。
不新建词库、不改 `translator/dictionary`、不动候选排序。

## 一、放 4 个字典文件

复制到小狼毫**共享数据目录**的 `opencc` 文件夹，例如：

```
D:\Program Files\Rime\weasel-0.17.4\data\opencc\
```

| 文件 | 说明 |
| --- | --- |
| `t2hn_keep_simp.json` | 修订版转换配置（对应上游 `t2gov_keep_simp.json`） |
| `HNGuard.ocd2` | 修订新增：保护「真个 / 个中→箇中 / 內閤 / 胴疘」等特例 |
| `TGPhrases.ocd2` | 修订后的词表 |
| `TGCharacters_keep_simp.ocd2` | 修订后的字表（保留简体字，含「黃→黄」） |

上游是 1 个 json + 2 个 ocd2；本修订多 1 个 `HNGuard.ocd2`，
用来保证分立正字不被词表规则归并。ocd2 已随仓库提供，无需自行编译。

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
- 「並 / 併 / 喫 / 衹 / 隻 / 鬨 / 疘 / 閤 / 箇」保持分立，不再被归并

## 三、重新部署

右键小狼毫「中」字图标 → **重新部署**。

## 四、验证

| 输入 | 期望 |
| --- | --- |
| `huang` | 出「黄」，不是旧字形「黃」 |
| `ge ren` | 首选「個人」 |
| `wo` | 首选「我」，不会先冒出「㠛㦱㧴」 |
| `he bing` / `bing fei` / `chi fan` | 合併 / 並非 / 喫飯 |
| `ge` | 候选可翻到「個 / 箇 / 閤」 |

分立正字和整词都来自朙月拼音原词库 + `essay.txt` 词频，本仓库不另建词库：
`luna_pinyin.dict.yaml` 已收录 並 / 併 / 喫 / 衹 / 隻 / 鬨 / 疘 / 閤 / 箇 / 個 等单字，
`essay.txt` 已有「個人 102677」「合併 9371」「並非 20707」「喫飯 31690」等词频。

## 五、改动字表后重新编译

改完 `opencc/*.txt` 并跑 `tools/build.py` 之后：

```
python tools/build_ocd2.py
```

把 `rime/` 下新生成的 3 个 `.ocd2` 复制到 `data\opencc`，再重新部署。
`opencc_dict.exe` 打不开含中文的路径，脚本会自动用纯 ASCII 临时目录中转。

## 六、不要做的事

| 不要 | 原因 |
| --- | --- |
| 不要 `patch: "translator/dictionary": ...` 挂自建扩展词库 | `import_tables` 不继承 `use_preset_vocabulary`，会丢掉 `essay.txt` 全部词频，候选按码点排序，出现 `wo → 㠛㦱㧴` |
| 不要删 `simplifier` 段 | 候选不再经过规范繁体转换，`huang` 就只剩旧字形「黃」 |
| 不要改 `opencc_config` 为 `s2hn.json` | 那是整篇「简 → 修订繁」转换，不是输入法候选过滤 |

> **复盘**：早期版本曾自建 `haining_wu_extended` 词库并去掉 `simplifier`，
> 导致「𬮤㠴」伪词抢占首选、`wo` 冒出扩展区生僻字、`huang` 不出「黄」。
> 现已全部回退到上游方案，仓库不再包含任何自建 Rime 词库。
