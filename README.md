# recurring-corrections · 纠偏台账

Boris 法「计数触发固化」的最小实现：**同一类纠偏出现 ≥3 次，就必须固化成规则或检查脚本，不再靠记性。**

灵感来自 Boris Cherny（Claude Code 创造者）的 code review 自动化法：每次留下同类型 review 意见就记一笔，某模式累计 3-4 次，就写成 lint 规则自动消灭它。本工具把这个机制泛化到 AI agent 的日常运维：被用户纠正、验收被打回、复踩同一个坑，都记一笔；攒够次数就强制固化。

## 用法

```bash
# 记一笔纠偏（被纠正 / 验收打回 / 复踩同坑时）
python3 recurring.py add --tag <短slug> --note <一句话>

# 查看台账：同一 tag 固化后仍累计 ≥3 次 → ⚠️ 该固化
python3 recurring.py report

# 固化后标记（落成 skill 条目或检查脚本），计数从该点重新累计
python3 recurring.py fix --tag <slug> --where <skill名或脚本路径>
```

- 数据：`$RC_DB` 或 `~/.hermes/recurring-corrections.jsonl`（append-only JSONL，不手改）
- `fix` 只重置计数——固化后再犯继续累计；固化后仍 ⚠️ = 文字约定没起作用，该升级成检查脚本/看门 cron 等机械手段
- 按行序而非时间戳定位 last fix，同一秒内的 add/fix 不会误判

## 零依赖

纯 Python 标准库，单文件，无需安装。
