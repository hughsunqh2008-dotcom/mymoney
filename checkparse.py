from src.parser import parse_file

for f in ["data/2026-01.csv", "data/2026-02.csv", "data/2026-03.csv"]:
    txs, report = parse_file(f)
    print(f"\n=== {f} ===")
    print(report)
    for tx in txs[:3]:
        print(f"  {tx.date} | {tx.raw_desc!r} -> {tx.norm_desc!r} | {tx.amount}")