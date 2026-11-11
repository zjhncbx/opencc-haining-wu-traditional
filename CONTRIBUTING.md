# 贡献指南

本项目的字表词表是「海宁方言辞典」协作编纂系统的一部分，改动会直接影响历史词条。
请按下面的流程提交，避免双写漂移与静默改写。

## 一、最常做的改动：补一条词组

发现「某简体词」转出来的繁体不对（或某个修订繁体字被误归并）时：

1. 在 `rules/overrides.tsv` 加一行，用 **TAB** 分隔：

   ```
   简体词	修订版大陆标准繁体词
   ```

   例：`吃酒	喫酒`。这一层优先于全部上游词表命中。

2. 重新生成并回归：

   ```bash
   python tools/build.py --upstream /path/to/upstream/t2gov --dry-run
   python tools/build.py --upstream /path/to/upstream/t2gov
   python tools/verify.py
   python tools/export_web_dict.py
   ```

3. 在 `tools/rules.py` 的 `TEST_CASES` 里补一组用例（输入 + 期望输出），
   让 `tools/verify.py` 能长期守住这条规则。

4. Rime 无需单独维护词库：字表、词表改完后跑 `tools/build_ocd2.py`
   重新编译 3 个 ocd2 即可。输入方案沿用朙月拼音原词库与 `essay.txt` 词频。

## 二、改动字表级规则

只有「修订方案本身」变化时才动 `tools/rules.py` 的 `CHAR_PATCH` /
`REVISION_TABLE` / `ORTHODOX_SPLIT` 等。这类改动影响面大，请：

- 同步更新 `doc/01-修订方案.md`、`doc/02-与上游差异.md`；
- 在 PR 描述里写清依据（方案条款、字书出处、讨论结论）；
- 全量跑 `verify.py`，并抽查 `t2hn` 处理繁体稿件的结果。

## 三、不要做的事

- **不要直接编辑 `opencc/*.txt`**：它们由 `tools/build.py` 生成，下次 build 会被覆盖。
- **不要改动上游仓库**：本仓库只读上游，所有差异必须落在 `rules/` 与 `tools/`。
- **不要把 `dist/`、`rime/*.ocd2` 提交进 Git**：它们是构建产物（已 `.gitignore`）。
- **不要为了「看起来更顺」擅自合并分立正字**：`併 / 並 / 喫 / 衹 / 隻 / 鬨 / 疘 / 閤 / 箇 / 个`
  的分立是本方案的核心，改动需要方案层面的讨论结论。

## 四、判断标准速查

| 字 | 用于 | 例 |
| --- | --- | --- |
| 并 / 併 / 並 | 地名 / 合并 / 副词 | 并州 / 合併 / 並非 |
| 只 / 衹 / 隻 | 「只要」/ 仅仅 / 量词 | 只要 / 衹是 / 一隻鳥 |
| 吃 / 喫 | 口吃 / 进食 | 口吃 / 喫飯 |
| 个 / 個 / 箇 | 助词 / 量词名词 / 指示代词 | 真个 / 一個人 / 箇中 |
| 向 / 才 | 正字（嚮、纔 为异体） | 面向 / 剛才 |
| 哄 / 鬨 | 哄笑 / 喧闹 | 哄笑 / 內鬨 |
| 肛 / 疘 | 肛门 / 胴疘 | 肛門 / 胴疘 |
| 阁(閣) / 𬮤(閤) | 楼阁 / 内閤 | 閣樓 / 內閤 |

## 五、PR 检查清单

- [ ] `python tools/verify.py` 全部通过
- [ ] 新增用例已写入 `TEST_CASES`
- [ ] `doc/02-与上游差异.md` 的统计数字已更新（若改动规则）
- [ ] 如涉及前端，`python tools/export_web_dict.py` 可正常生成
- [ ] 如涉及 Rime，`python tools/build_ocd2.py` 可正常生成
- [ ] 未提交任何二进制构建产物
