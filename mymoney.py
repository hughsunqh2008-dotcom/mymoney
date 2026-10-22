#!/usr/bin/env python3
"""
mymoney —— 个人账目分析系统

命令行入口。

【本文件的设计原则】
    这个文件只做两件事：
        ① 解析命令行参数（argparse）
        ② 把任务分派给 src/ 下的各个模块
    它不写任何业务逻辑。业务逻辑全在 src/ 里。

    为什么要这样分？
        因为入口文件是"调度层"，业务模块是"实现层"。
        混在一起的话，你的代码很快就变成一个几百行的 main()，
        改一个功能要在一堆缩进里找人。

【当前状态】
    骨架已搭好，参数解析可用。各功能函数还是空的（会抛 NotImplementedError）。
    你的任务是按《项目说明书》的模块顺序，逐个填上实现。

【自己测试】
    python mymoney.py --help          看帮助
    python mymoney.py --version       看版本
    python mymoney.py --import data/2026-01.csv     （会提示未实现，这是正常的）
"""

import argparse
import sys
from pathlib import Path

# 让 `python mymoney.py` 从项目根目录运行时能找到 src 包
sys.path.insert(0, str(Path(__file__).parent))

from src import analyzer, reporter, storage, plotter,parser,categorizer

# 项目里的固定目录（用 pathlib，不用字符串拼路径）
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "out"
CONFIG_DIR = ROOT / "config"

VERSION = "0.1.0"


def build_parser() -> argparse.ArgumentParser:
    """构造命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="mymoney",
        description="个人账目分析系统：导入账单、自动分类、统计、出报告。",
        epilog="示例：python mymoney.py --import data/2026-01.csv",
    )
    parser.add_argument("--version", action="version", version=f"mymoney {VERSION}")

    # ---- 功能开关 ----
    parser.add_argument(
        "--import-file",
        dest="import_path",
        metavar="PATH",
        help="导入一个账单 CSV 文件",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="输出账目报告",
    )
    parser.add_argument(
        "--top",
        type=int,
        metavar="N",
        help="列出金额最大的 N 笔支出",
    )
    parser.add_argument(
        "--export",
        metavar="PATH",
        help="导出结果（按扩展名判断 csv 还是 json）",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="生成消费趋势图（保存到 out/trend.png）",
    )

    # ---- 过滤条件 ----
    parser.add_argument("--month", metavar="YYYY-MM", help="只统计某个月")
    parser.add_argument("--category", metavar="NAME", help="只统计某个分类")

    # ---- 行为开关 ----
    parser.add_argument("--verbose", action="store_true", help="打印详细过程")

    return parser


# ============================================================
# 各功能的实现骨架
# 你要做的就是按《项目说明书》把下面每个函数填起来
# ============================================================

def cmd_import(path: str, verbose: bool) -> int:
    txs, parse_info = parser.parse_file(Path(path))
    if parse_info['成功'] == 0:
        print(f"没有一行能解析：{path}", file=sys.stderr)
        return 1
    
    rules = categorizer.load_rules(str(CONFIG_DIR / "categories.json"))
    categorizer.categorize_all(txs, rules)
    added = storage.append_new(txs)
    
    print(f"总数 {parse_info['总数']}  成功 {parse_info['成功']}  失败 {parse_info['失败']}  新增 {added}")
    
    if parse_info["失败"]:
        print(f"警告：{parse_info['失败']} 行无法解析（--verbose 看明细）", file=sys.stderr)
        if verbose:
            for row_no, row in parse_info["失败信息"]:
                print(f"  第 {row_no} 个数据行：{row}", file=sys.stderr)

    return 0


def cmd_report(month: str | None, verbose: bool) -> int:
    txs = storage.load_all()
    if month:
        txs = [t for t in txs if t.date.strftime("%Y-%m") == month]
    if not txs:
        print(f"没有数据{('（' + month + '）') if month else ''}，先 --import-file 导入账单", file=sys.stderr)
        return 1
    stats      = analyzer.summary(txs)
    cat_stats  = analyzer.by_category(txs)
    month_stats= analyzer.by_month(txs)
    top_txs    = analyzer.top_expenses(txs, n=5)

    if month:
        text = reporter.to_text(stats=stats,cat_stats=cat_stats,month_stats=month_stats,top_txs=top_txs,month=month)
    else:
        text = reporter.to_text(stats=stats,cat_stats=cat_stats,month_stats=month_stats,top_txs=top_txs)
    print(text,end='')
    return 0


def cmd_top(n: int, category: str | None) -> int:
    txs = storage.load_all()
    top_txs = analyzer.top_expenses(txs,category=category,n=n)
    
    if not top_txs:
        return 2
    
    for tx in top_txs:
        print(f'{tx.date}  {tx.norm_desc}  金额：{tx.amount} 类别：{tx.category} 货币{tx.currency}')
    return 0

def cmd_export(path: str, month: str | None) -> int:
    target = Path(path)
    suffix = target.suffix.lower()
    if suffix not in {".csv", ".json"}:
        print(f"--export 只支持 .csv 或 .json，收到 {target.suffix!r}", file=sys.stderr)
        return 2

    txs = storage.load_all()
    if month:
        txs = [t for t in txs if t.date.strftime("%Y-%m") == month]

    target.parent.mkdir(parents=True, exist_ok=True)

    if suffix == ".csv":
        reporter.to_csv(txs=txs, out_path=target)
    else:
        payload = {
            "summary": analyzer.summary(txs),
            "by_category": analyzer.by_category(txs),
            "by_month": analyzer.by_month(txs),
            "top_expenses": [t.to_dict() for t in analyzer.top_expenses(txs, n=5)],
        }
        reporter.to_json(report=payload, out_path=target)
    return 0


def cmd_plot(month: str | None) -> int:
    txs = storage.load_all()
    month_stats = analyzer.by_month(txs)
    plotter.trend_chart(month_stats=month_stats,out_path=OUT_DIR/'trend.png')
    return 0

def ensure_dirs() -> None:
    """确保输出目录存在。

    为什么需要它：写文件时如果目录不存在，会抛 FileNotFoundError。
    与其在每个写文件的地方判断，不如启动时统一建一次。
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def main(argv: list[str] | None = None) -> int:
    """主调度函数：解析参数 → 分派任务。

    返回值就是进程退出码：0 表示成功，非 0 表示出错。
    这个约定在第 8 章（模块 8）要用来做测试。
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    ensure_dirs()

    try:
        # 判据统一用 is not None：值的真假 ≠ "用户有没有给这个参数"
        # （args.top == 0 是合法输入，用真值判断会把它当成"没给"）
        if args.import_path is not None:
            return cmd_import(args.import_path, args.verbose)
        if args.report:
            return cmd_report(args.month, args.verbose)
        if args.top is not None:
            return cmd_top(args.top, args.category)
        if args.export is not None:
            return cmd_export(args.export, args.month)
        if args.plot:
            return cmd_plot(args.month)
    except NotImplementedError as exc:
        print(f"[未实现] {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"[文件不存在] {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # 兜底：保证不会甩一堆堆栈给人看
        print(f"[出错] {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    # 走到这里 = 没有任何命令被命中（空参数，或只给了 --month / --verbose 这类修饰）
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
