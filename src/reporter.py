from __future__ import annotations

from pathlib import Path

from .models import Transaction

import csv
import json
import unicodedata

LINE = '-' * 40
COLUMNS = {"日期": "date", "描述": "raw_desc", "金额": "amount",
           "币种": "currency", "分类": "category"}


def _width(text: str) -> int:
    """这段文字在等宽终端里占几格：汉字、全角符号算 2 格，其它算 1 格。

    len() 数的是字符数，中英文混排时不能拿它对窗口宽度。
    """
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text)


def _pad(text: str, width: int, align: str = "<") -> str:
    """按**显示宽度**补空格，而不是按字符数。align='>' 右对齐。"""
    gap = max(0, width - _width(text))
    return " " * gap + text if align == ">" else text + " " * gap


def _title_eq(label: str, width: int = 40) -> str:
    """用 = 把标题居中到 width 格（按显示宽度，不是字符数）。"""
    body = f' {label} '
    left = (width - _width(body)) // 2
    return '=' * left + body + '=' * (width - _width(body) - left)


def to_text(
    stats: dict,
    cat_stats: dict[str, float],
    month_stats: dict[str, dict[str, float]],
    top_txs: list[Transaction],
    month: str | None = None,
) -> str:
    label = f'{month} 账目报告' if month else '全部 账目报告'
    lines = [_title_eq(label), LINE]

    # 三个标签的显示宽度都是 8 格，金额右对齐到同一列
    for title, key in (('总收入：', '总收入'), ('总支出：', '总支出'), ('结  余：', '结余')):
        lines.append(_pad(title, 8) + _pad(f'{stats[key]:,.2f} CNY', 30, '>'))
    lines.append(LINE)

    lines.append('按分类：')
    for cat, amount in cat_stats.items():
        # 分母是 stats["总支出"]；cat_stats 非空时它一定 > 0（README 决策 11）
        pct = amount * 100 / stats["总支出"]
        lines.append(_pad(f'  {cat}', 13)
                     + _pad(f'{amount:,.2f}', 15, '>')
                     + f'  ( {pct:4.1f}%)')
    lines.append(LINE)

    if top_txs:
        lines.append(f'最大{len(top_txs)}笔账单：')
        for tx in top_txs:
            lines.append(_pad(f'  {tx.date.isoformat()}  {tx.norm_desc}', 26)
                         + _pad(f'{tx.amount:,.2f}', 12, '>'))

    return '\n'.join(lines) + '\n'


def _row(tx: Transaction) -> dict[str, str]:
    if not tx.date:
        raise ValueError(f'日期数据损坏 {tx.norm_desc!r}')
    d = tx.to_dict()
    return {
        "日期": d["date"],
        "描述": d["raw_desc"],
        # CSV 不加千分位：加了会被引号包住，Excel 当文本，自己再导入还会解析失败
        "金额": f"{d['amount']:.2f}",
        "币种": d["currency"] or "",
        "分类": d["category"] or "未分类",
    }


def to_csv(txs: list[Transaction], out_path: str | Path) -> None:
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        for tx in txs:
            w.writerow(_row(tx))


def to_json(report: list | dict, out_path: str | Path | None) -> None:
    if not out_path:
        raise ValueError('out_path 不能为空；默认路径由调用方（mymoney.py）决定')
    with open(Path(out_path), 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
