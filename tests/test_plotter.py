"""test_plotter.py —— 模块 7（图表）的测试

图的内容没法断言，能测的是两件事：
    1. `_month_range` 的纯逻辑（补零、跨年、单月）——这是最容易错的地方
    2. `trend_chart` 是否真的写出一个合法 PNG

⚠️ 跑这组测试前确认 `_month_range` 里有 `month` 的递增分支，
   否则 `while` 条件永远成立，测试会**卡死**（不是报错）。
"""

from __future__ import annotations

import pytest

from src import analyzer, plotter


PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


# ============================================================
# _month_range
# ============================================================
def test_month_range_single_month():
    assert plotter._month_range("2026-01", "2026-01") == ["2026-01"]


def test_month_range_three_months():
    assert plotter._month_range("2026-01", "2026-03") == [
        "2026-01", "2026-02", "2026-03"]


def test_month_range_pads_zero():
    """月份必须补零：否则 '2026-9' 和 by_month 的键 '2026-09' 对不上。"""
    assert plotter._month_range("2026-09", "2026-10") == ["2026-09", "2026-10"]


def test_month_range_crosses_year():
    """跨年是这类循环最容易翻车的地方。"""
    assert plotter._month_range("2025-11", "2026-02") == [
        "2025-11", "2025-12", "2026-01", "2026-02"]


def test_month_range_december():
    assert plotter._month_range("2026-12", "2027-01") == ["2026-12", "2027-01"]


# ============================================================
# trend_chart
# ============================================================
def test_trend_chart_creates_png(tmp_path):
    month_stats = {
        "2026-01": {"收入": 18500.0, "支出": 4533.1, "结余": 13966.9},
        "2026-02": {"收入": 15200.0, "支出": 6120.5, "结余": 9079.5},
        "2026-03": {"收入": 21000.0, "支出": 3980.0, "结余": 17020.0},
    }
    out = tmp_path / "trend.png"
    plotter.trend_chart(month_stats, out)

    assert out.exists()
    raw = out.read_bytes()
    assert raw.startswith(PNG_MAGIC)
    assert len(raw) > 1000          # 不是空图


def test_trend_chart_single_month(tmp_path):
    """只有一个月不能崩（折线会退化成点）。"""
    out = tmp_path / "trend.png"
    plotter.trend_chart({"2026-01": {"收入": 1.0, "支出": 0.5, "结余": 0.5}}, out)
    assert out.read_bytes().startswith(PNG_MAGIC)


def test_trend_chart_with_missing_month(tmp_path):
    """中间缺一个月：补轴不补数据，不能崩。"""
    month_stats = {
        "2026-01": {"收入": 18500.0, "支出": 4533.1, "结余": 13966.9},
        "2026-03": {"收入": 21000.0, "支出": 3980.0, "结余": 17020.0},
    }
    out = tmp_path / "trend.png"
    plotter.trend_chart(month_stats, out)
    assert out.read_bytes().startswith(PNG_MAGIC)


def test_trend_chart_does_not_create_parent_dir(tmp_path):
    """父目录由调用方建，没建就该报 FileNotFoundError。"""
    with pytest.raises(FileNotFoundError):
        plotter.trend_chart({"2026-01": {"收入": 1.0, "支出": 0.5, "结余": 0.5}},
                            tmp_path / "no_such_dir" / "trend.png")


# ============================================================
# 和真实数据接一下
# ============================================================
def test_trend_chart_from_real_csv(tmp_path):
    """用 data/2026-01.csv 走一遍 by_month，图要能出。"""
    from src.categorizer import categorize_all, load_rules
    from src.parser import parse_file

    txs, _ = parse_file("data/2026-01.csv")
    categorize_all(txs, load_rules("config/categories.json"))
    out = tmp_path / "trend.png"
    plotter.trend_chart(analyzer.by_month(txs), out)
    assert out.read_bytes().startswith(PNG_MAGIC)
