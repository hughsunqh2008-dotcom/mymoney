"""
reporter.py —— 生成报告

【这个文件负责什么】
    把 analyzer 算出来的统计结果，输出成人能看的、或程序能读的格式。

【你的任务】
    实现下面三个函数。要求见《项目说明书》模块 6。

【文本报告的目标长相】
    ========== 2026-01 账目报告 ==========
    总收入:      18,500.00 CNY
    总支出:       4,593.10 CNY
    结  余:      13,906.90 CNY
    --------------------------------------
    按分类:
      居住         3,000.00  ( 65.3%)
      餐饮           642.50  ( 14.0%)
      未分类         406.00  (  8.8%)
    --------------------------------------
    最大 5 笔支出:
      2026-01-12  房租            -3,000.00
      ...

【卡住去哪查】
    - rjust / ljust / center 对齐      →  Automate Ch6
    - f-string 格式化（:.2f、千分位）   →  Automate Ch6
    - 写 CSV、DictWriter               →  Automate Ch14
    - JSON 中文处理（ensure_ascii）     →  Automate Ch14
    - pathlib 写文件、mkdir            →  Automate Ch9
"""

from __future__ import annotations

from pathlib import Path

from .models import Transaction


def to_text(
    stats: dict,
    cat_stats: dict[str, float],
    month_stats: dict[str, dict[str, float]],
    top_txs: list[Transaction],
    month: str | None = None,
) -> str:
    """生成文本报告（返回字符串，不直接打印）。

    为什么要返回字符串而不是直接 print？
        因为这样它就能被测试（比较返回值）、也能写进文件。
        直接 print 的函数没法测试。这是个重要的习惯。
    """
    # TODO(模块6)
    raise NotImplementedError


def to_csv(txs: list[Transaction], out_path: str | Path) -> None:
    """把交易导出成 CSV。

    提示：
        - 用 csv.DictWriter，fieldnames 就是你要输出的列
        - 中文要能正常打开：open(..., newline="", encoding="utf-8-sig")
          utf-8-sig 是给 Excel 看的（带 BOM），否则 Excel 打开是乱码
        - 确保父目录存在
    """
    # TODO(模块6)
    raise NotImplementedError


def to_json(payload: dict | list, out_path: str | Path) -> None:
    """把任意数据导出成 JSON。

    提示：json.dump(..., ensure_ascii=False, indent=2)
         ensure_ascii=False 保证中文是中文而不是 \\uXXXX
    """
    # TODO(模块6)
    raise NotImplementedError
