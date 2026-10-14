"""
analyzer.py —— 统计与分析

【这个文件负责什么】
    从一堆 Transaction 里算出各种统计口径。

【你的任务】
    实现下面这些函数。要求见《项目说明书》模块 5。

【★ 硬性要求：所有函数都必须能处理空列表和单条数据】
    这是最容易被忽略、也最容易被真实数据打脸的地方。
    你自己造的数据永远"看着正常"，但真实账单里可能某个月只有 1 笔。

【卡住去哪查】
    - 字典聚合（往字典里累加）        →  Automate Ch5 的 setdefault()
    - sorted(key=...) 排序            →  Automate Ch4；Think Python chap09
    - 从 datetime 取年月              →  Automate Ch15
    - sum/max/min/len                 →  内置函数
    - 边界值思维                      →  Automate Ch10（调试那章）
    - statistics.mean / median        →  Python 标准库（可选）
"""

from __future__ import annotations

from .models import Transaction


def summary(txs: list[Transaction]) -> dict:
    """总体摘要。

    返回，例如：
        {
            "笔数": 14,
            "总收入": 18500.00,
            "总支出": 4593.10,
            "结余": 13906.90,
            "起始日期": "2026-01-03",
            "结束日期": "2026-01-30",
        }

    注意"收入/支出"怎么区分——这取决于你在模块 1 做的设计决策（金额正负？）。
    """
    # TODO(模块5)
    raise NotImplementedError


def by_category(txs: list[Transaction]) -> dict[str, float]:
    """按分类汇总支出金额，**按金额降序**返回。

    返回，例如：{"餐饮": 642.5, "居住": 3000.0, "未分类": 406.0}

    提示：
        - dict 在 Python 3.7+ 是有序的，但你想按"金额"排序的话，
          需要 sorted(d.items(), key=...) 再转回 dict
    """
    # TODO(模块5)
    raise NotImplementedError


def by_month(txs: list[Transaction]) -> dict[str, dict[str, float]]:
    """按月份汇总。

    返回，例如：
        {
            "2026-01": {"收入": 18500.0, "支出": 4593.1, "结余": 13906.9},
            "2026-02": {...},
        }

    提示：从每个 tx 的日期里取出 "YYYY-MM" 字符串作为键。
    """
    # TODO(模块5)
    raise NotImplementedError


def top_expenses(
    txs: list[Transaction],
    n: int = 5,
    category: str | None = None,
) -> list[Transaction]:
    """金额最大的 n 笔支出。

    参数：
        n:        取几笔
        category: 只在这个分类里找；None 表示不限制
    返回：
        排好序的 Transaction 列表（金额最大的在前，或绝对值最大——你定）

    提示：
        - 先过滤（只看支出、只看指定分类）
        - 再排序
        - 再切片取前 n 个
        - 数据不足 n 条时返回全部（不要报错）
    """
    # TODO(模块5)
    raise NotImplementedError


def find_anomalies(txs: list[Transaction]) -> list[Transaction]:
    """★ 找出"异常"交易。异常的定义由你自己定，并写进 README。

    你可能想到的定义（选一个或自己发明）：
        - 单笔金额超过该分类平均值的 3 倍
        - 同一商户在 7 天内出现多次
        - 某月支出比上月暴涨超过 50%

    做这个题的目的不是"答对"，而是练习
    **把模糊需求变成明确规则** —— 这是真实工作里最常见的事。
    """
    # TODO(模块5)
    raise NotImplementedError
