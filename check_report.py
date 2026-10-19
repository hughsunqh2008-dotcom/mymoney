"""check_report.py —— 看模块 6 当前输出长什么样

用法（在项目根目录）：

    python check_report.py

它按顺序做六件事，任何一步失败都不会挡住后面的：

    1. src/reporter.py 能不能编译、能不能 import
    2. 跑 data/2026-01.csv 的完整链路（模块 1-5），打印喂给 to_text 的参数
    3. to_text 的输出，带行号和行宽，方便核对列对齐
    4. 边界：不传月份、空数据、top_txs 不足 5 笔、金额全为 0.00
    5. to_csv / to_json 写出后回读，检查 BOM、行尾、空字段、中文转义
    6. category 为 None 的交易怎么处理
"""

from __future__ import annotations

import sys
import traceback
import unicodedata
from pathlib import Path

try:                                    # 控制台是 GBK 时也能打印中文
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def display_width(text: str) -> int:
    """等宽终端里的显示宽度：汉字/全角符号算 2 格。"""
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text)


def hr(title: str) -> None:
    print()
    print("=" * 64)
    print(title)
    print("=" * 64)


def show(text: str, ruler: bool = True) -> None:
    """带行号、字符数 len、显示宽度 dw 打印。

    对齐只能看 dw：汉字占 2 格，len 相同的两行 dw 可能差好几格。
    """
    if ruler:
        print("          1         2         3         4")
        print("0123456789" * 4)
    widths: dict[int, list[int]] = {}
    for i, line in enumerate(text.splitlines(), 1):
        dw = display_width(line)
        widths.setdefault(dw, []).append(i)
        print(f"{i:>3} |{line}|  len={len(line):>3} dw={dw:>3}")
    # 只比较数据行：缩进行（分类 / 最大账单）和含 CNY 的三行总计。
    # "按分类：" 这类短标签和分隔线本来就不等宽，不算问题。
    rows = {}
    for i, line in enumerate(text.splitlines(), 1):
        if line.startswith("  ") or "CNY" in line:
            rows.setdefault(display_width(line), []).append(i)
    if len(rows) > 1:
        detail = "、".join(f"dw={dw}(行 {','.join(map(str, ls))})" for dw, ls in rows.items())
        print(f"    !! 数据行宽度不一致：{detail}")
    elif rows:
        print(f"    数据行宽度一致：dw={next(iter(rows))}")
    print(f"    共 {len(text.splitlines())} 行，以 \\n 结尾: {text.endswith(chr(10))}")


def section(title: str, fn) -> None:
    hr(title)
    try:
        fn()
    except Exception:
        traceback.print_exc(limit=2)


# ---------------------------------------------------------------- 0. 环境
hr("0. 环境")
print("解释器:", sys.executable)
print("版本:  ", sys.version.split()[0])
print("项目根:", ROOT)

# ------------------------------------------------- 1. 编译 + import
hr("1. src/reporter.py 能否编译 / import")
reporter = None
source = (ROOT / "src" / "reporter.py").read_text(encoding="utf-8")
compile_ok = True
try:
    compile(source, "src/reporter.py", "exec")
    print(f"编译 OK（{len(source.splitlines())} 行）")
except SyntaxError as e:
    compile_ok = False
    print(f"编译失败：SyntaxError: {e.msg}    （第 {e.lineno} 行）")

if compile_ok:
    try:
        import importlib
        reporter = importlib.import_module("src.reporter")
        print("import OK")
        print("已有函数:", [n for n in ("to_text", "to_csv", "to_json") if hasattr(reporter, n)])
        print("缺失函数:", [n for n in ("to_text", "to_csv", "to_json") if not hasattr(reporter, n)])
    except Exception as e:
        reporter = None
        print(f"import 失败：{type(e).__name__}: {e}")

# --------------------------------------------------- 2. 模块 1-5 的链路
hr("2. 数据链路（模块 1-5）")
from src import analyzer
from src.categorizer import categorize_all, load_rules
from src.parser import parse_file

txs, report = parse_file(str(ROOT / "data" / "2026-01.csv"))
print("解析报告:", report)

rules = load_rules(str(ROOT / "config" / "categories.json"))
print("分类计数:", categorize_all(txs, rules))    # categorize 只返回分类，赋值得用 categorize_all

stats = analyzer.summary(txs)
cat_stats = analyzer.by_category(txs)
month_stats = analyzer.by_month(txs)
top_txs = analyzer.top_expenses(txs, n=5)

print()
print("stats      =", stats)
print("cat_stats  =", cat_stats)
print("month_stats=", month_stats)
print("top_txs    =")
for tx in top_txs:
    print(f"   {tx.date}  {tx.raw_desc:<10} {tx.amount:>10.2f}  分类={tx.category}")

# ------------------------------------------------------ 3. to_text 输出
if reporter is None or not hasattr(reporter, "to_text"):
    hr("3. to_text 输出（跳过：没准备好）")
else:
    section("3. to_text 输出（month='2026-01'）",
            lambda: show(reporter.to_text(stats, cat_stats, month_stats, top_txs,
                                          month="2026-01")))

# ------------------------------------------------------------ 4. 边界
if reporter is not None and hasattr(reporter, "to_text"):
    section("4a. 边界：不传 month", lambda: show(
        reporter.to_text(stats, cat_stats, month_stats, top_txs), ruler=False))

    def _empty():
        empty_stats = {"笔数": 0, "总收入": 0, "总支出": 0, "结余": 0,
                       "起始日期": "无有效信息", "结束日期": "无有效信息"}
        show(reporter.to_text(empty_stats, {}, {}, [], month="2026-01"), ruler=False)

    section("4b. 边界：空数据", _empty)
    section("4c. 边界：top_txs 只有 2 笔", lambda: show(
        reporter.to_text(stats, cat_stats, month_stats, top_txs[:2], month="2026-01"),
        ruler=False))

    def _zero_row_in_csv():
        """含 0.00 行的 CSV 走完整解析链路：确认它在数据层就被拦掉（决策 11）。"""
        sample = ROOT / "out" / "zero_sample.csv"
        sample.parent.mkdir(parents=True, exist_ok=True)
        sample.write_text(
            "交易日期,交易描述,金额,币种\n"
            "2026-01-03,余额查询,0.00,CNY\n"
            "2026-01-04,话费充值,-99.00,CNY\n",
            encoding="utf-8")
        ztxs, zrep = parse_file(str(sample))
        print("解析报告:", zrep)
        print("通过的行:", [(t.raw_desc, t.amount) for t in ztxs])
        print("金额都不为 0:", all(t.amount != 0 for t in ztxs))
        categorize_all(ztxs, rules)
        show(reporter.to_text(analyzer.summary(ztxs), analyzer.by_category(ztxs),
                              analyzer.by_month(ztxs), analyzer.top_expenses(ztxs),
                              month="2026-01"), ruler=False)

    section("4d. 含 0.00 行的 CSV（数据层拦截）", _zero_row_in_csv)

# ------------------------------------------------------------ 5. 导出
def _export():
    out_dir = ROOT / "out"
    out_dir.mkdir(parents=True, exist_ok=True)      # 父目录由调用方建
    print("输出目录:", out_dir)

    if not hasattr(reporter, "to_csv"):
        print("\n[CSV] to_csv 还没写")
    else:
        try:
            path = out_dir / "transactions.csv"
            reporter.to_csv(txs, path)
            raw = path.read_bytes()
            text = raw.decode("utf-8-sig")
            has_bom = raw.startswith(b"\xef\xbb\xbf")
            has_crlf = b"\r\n" in raw
            print(f"\n[CSV] {path.name}  {len(raw)} 字节  BOM={has_bom}  CRLF={has_crlf}")
            print("内容：")
            for line in text.splitlines():
                print("   ", line)
            if ",,,," in text:
                print("    !! 出现整行空字段：键和 fieldnames 对不上")
        except Exception:
            traceback.print_exc(limit=3)

    if not hasattr(reporter, "to_json"):
        print("\n[JSON] to_json 还没写")
    else:
        try:
            path = out_dir / "report.json"
            reporter.to_json({"summary": stats, "by_category": cat_stats}, path)
            text = path.read_text(encoding="utf-8")
            has_bom = path.read_bytes().startswith(b"\xef\xbb\xbf")
            has_escape = "\\u" in text
            print(f"\n[JSON] {path.name}  {len(text)} 字节  BOM={has_bom}  含 \\u 转义={has_escape}")
            print("前 160 字符：")
            print("   ", text[:160].replace("\n", " "))
        except Exception:
            traceback.print_exc(limit=3)


if reporter is not None:
    section("5. 导出 CSV / JSON", _export)

# --------------------------------------------------- 6. category 为 None
def _none_category():
    from datetime import date
    from src.models import Transaction
    rows = [
        Transaction(tx_date=date(2026, 2, 1), raw_desc="超市购物", norm_desc="超市购物",
                    amount=-183.40, currency="CNY", category=None, uid=None),
        Transaction(tx_date=date(2026, 2, 2), raw_desc="话费", norm_desc="话费",
                    amount=-99.00, currency=None, category="通讯", uid=None),
    ]
    print("输入：category=None / currency=None 各一笔")
    for tx in rows:
        print("   ", tx.to_dict())
    if reporter is not None and hasattr(reporter, "to_csv"):
        path = ROOT / "out" / "none_check.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        reporter.to_csv(rows, path)
        print("\n写出来的 CSV：")
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            print("   ", line)


if reporter is not None:
    section("6. category / currency 为 None", _none_category)

hr("结束")
