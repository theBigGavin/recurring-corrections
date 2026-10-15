#!/usr/bin/env python3
"""recurring.py — Boris 法「纠偏计数触发固化」台账.

用法:
  recurring.py add  --tag <slug> --note <一句话>   # 被用户纠正/验收打回/复踩同一坑时记一笔
  recurring.py fix  --tag <slug> --where <skill名或脚本路径>  # 固化后标记,计数从该点重新累计
  recurring.py report                              # 开局巡检用;同一 tag 固化后仍累计 >=3 次 → ⚠ 该固化

数据: $RC_DB 或 ~/.hermes/recurring-corrections.jsonl (append-only JSONL)
"""
import json, os, sys, collections, datetime

DB = os.environ.get("RC_DB", os.path.expanduser("~/.hermes/recurring-corrections.jsonl"))
TRIGGER = 3  # Boris: 同类型 review 意见累计 3-4 次就固化,取下限


def now():
    return datetime.datetime.now().isoformat(timespec="seconds")


def load():
    if not os.path.exists(DB):
        return []
    out = []
    with open(DB) as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                try:
                    out.append(json.loads(ln))
                except json.JSONDecodeError:
                    pass
    return out


def append(rec):
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    with open(DB, "a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def report():
    entries = load()
    if not entries:
        print("(空台账,暂无纠偏记录)")
        return 0
    tags = collections.OrderedDict()
    for e in entries:
        tags.setdefault(e["tag"], []).append(e)
    flagged = 0
    for tag, es in sorted(tags.items(), key=lambda kv: -len(kv[1])):
        # 按行序而非时间戳定位 last fix(同一秒内的 add/fix 无法靠 ts 区分)
        last_fix_idx = max((i for i, e in enumerate(es) if "fix" in e), default=None)
        fixes = [e for e in es if "fix" in e]
        open_hits = [e for i, e in enumerate(es)
                     if "note" in e and (last_fix_idx is None or i > last_fix_idx)]
        n = len(open_hits)
        mark = " ⚠️ 该固化" if n >= TRIGGER else ""
        fixinfo = f" | 已固化于 {fixes[-1]['fix']} (后又出现 {n} 次)" if fixes else ""
        print(f"[{n}] {tag}{mark}{fixinfo}")
        for e in open_hits[-3:]:
            print(f"    {e['ts'][:10]}  {e['note'][:80]}")
        if n >= TRIGGER:
            flagged += 1
    return flagged


def main():
    args = sys.argv[1:]
    if not args or args[0] not in ("add", "fix", "report"):
        print(__doc__)
        return 2
    cmd = args[0]
    if cmd == "report":
        return 0 if report() >= 0 else 0
    kv = {}
    i = 1
    while i < len(args) - 1:
        kv[args[i].lstrip("-")] = args[i + 1]
        i += 2
    if "tag" not in kv:
        print("缺 --tag")
        return 2
    if cmd == "add":
        append({"ts": now(), "tag": kv["tag"], "note": kv.get("note", "")})
        print(f"已记: {kv['tag']}")
    else:
        append({"ts": now(), "tag": kv["tag"], "fix": kv.get("where", "")})
        print(f"已标记固化: {kv['tag']} → {kv.get('where','')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
