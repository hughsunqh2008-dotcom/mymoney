"""test_analyzer.py —— analyzer 模块的测试

对齐当前的 src/analyzer.py，测这 7 个函数：
    summary / by_category / by_month / top_expenses
    / group_by_category / group_by_month / find_anomials

期望值全部是手工按 data/2026-01.csv 那 14 行算出来的，不是跑程序抄回来的。
金额一律用 pytest.approx 比较——浮点累加会有 0.000000001 级的误差，
钱的口径是两位小数，不该被这个误差卡住。
"""

from datetime import date

import pytest

from src.models import Transaction
from src import analyzer


# ============================================================
# 测试数据：data/2026-01.csv 的全部 14 行
# ============================================================
def make_tx(day: int, desc: str, amount: float, category: str | None,
            month: int = 1) -> Transaction:
    """造一笔交易。desc 同时当 raw_desc 和 norm_desc。"""
    return Transaction(
        tx_date=date(2026, month, day),
        raw_desc=desc,
        norm_desc=desc,
        amount=amount,
        currency="CNY",
        category=category,
        uid=None,
    )


def build_txs() -> list[Transaction]:
    return [
        make_tx(3,  "星巴克(国贸店)", -38.00,   "餐饮"),
        make_tx(3,  "地铁出行",       -6.00,    "交通"),
        make_tx(5,  "工资",           18500.00, "收入"),
        make_tx(7,  "美团外卖",       -52.50,   "餐饮"),
        make_tx(8,  "京东商城",       -299.00,  "购物"),
        make_tx(10, "滴滴出行",       -45.80,   "交通"),
        make_tx(12, "房租",           -3000.00, "居住"),
        make_tx(15, "瑞幸咖啡",       -19.90,   "餐饮"),
        make_tx(18, "超市购物",       -183.40,  "购物"),
        make_tx(20, "话费充值",       -99.00,   "通讯"),
        make_tx(22, "美团外卖",       -68.00,   "餐饮"),
        make_tx(25, "高铁票",         -553.00,  "交通"),
        make_tx(28, "星巴克(国贸店)", -42.00,   "餐饮"),
        make_tx(30, "电费",           -126.50,  "居住"),
    ]


# 手算过程（13 笔支出，正数口径）：
#   38.00 + 6.00 + 52.50 + 299.00 + 45.80 + 3000.00 + 19.90
# + 183.40 + 99.00 + 68.00 + 553.00 + 42.00 + 126.50 = 4533.10
EXPECTED_INCOME = 18500.00
EXPECTED_EXPENSE = 4533.10
EXPECTED_BALANCE = 13966.90

# 按金额降序；每个分类的构成写在后面
EXPECTED_BY_CATEGORY = {
    "居住": 3126.50,   # 房租 3000.00 + 电费 126.50
    "交通": 604.80,    # 地铁 6.00 + 滴滴 45.80 + 高铁 553.00
    "购物": 482.40,    # 京东 299.00 + 超市 183.40
    "餐饮": 220.40,    # 星巴克 38.00 + 美团 52.50 + 瑞幸 19.90 + 美团 68.00 + 星巴克 42.00
    "通讯": 99.00,     # 话费充值
}


# ============================================================
# summary
# ============================================================
def test_summary_empty():
    """空列表：返回合理的零值，不能崩。"""
    s = analyzer.summary([])
    assert s["笔数"] == 0
    assert s["总收入"] == 0
    assert s["总支出"] == 0
    assert s["结余"] == 0


def test_summary_single():
    """只有一条数据也不能崩。"""
    s = analyzer.summary([make_tx(3, "x", -10.0, None)])
    assert s["笔数"] == 1


def test_summary_count():
    assert analyzer.summary(build_txs())["笔数"] == 14


def test_summary_totals():
    """总收入和总支出必须和手算一致。"""
    s = analyzer.summary(build_txs())
    assert s["总收入"] == pytest.approx(EXPECTED_INCOME)
    assert s["总支出"] == pytest.approx(EXPECTED_EXPENSE)


def test_summary_balance():
    """结余 = 收入 - 支出。"""
    assert analyzer.summary(build_txs())["结余"] == pytest.approx(EXPECTED_BALANCE)


def test_summary_date_range():
    """起止日期是最早和最晚那两笔的日期。"""
    s = analyzer.summary(build_txs())
    # 用 str() 比较，返回 date 对象或字符串都能过
    assert str(s["起始日期"]) == "2026-01-03"
    assert str(s["结束日期"]) == "2026-01-30"


def test_summary_date_range_with_unsorted_input():
    """输入顺序被打乱时，起止日期仍然正确（不能靠首尾元素碰巧对）。"""
    shuffled = list(reversed(build_txs()))
    s = analyzer.summary(shuffled)
    assert str(s["起始日期"]) == "2026-01-03"
    assert str(s["结束日期"]) == "2026-01-30"


# ============================================================
# by_category —— 只统计支出，按金额降序
# ============================================================
def test_by_category_empty():
    assert analyzer.by_category([]) == {}


def test_by_category_values():
    """每个分类的支出金额必须和手算一致（正数口径）。"""
    result = analyzer.by_category(build_txs())
    assert {k: round(v, 2) for k, v in result.items()} == EXPECTED_BY_CATEGORY


def test_by_category_sorted_desc():
    """返回值按金额降序——模块 6 的报告会直接依赖这个顺序。"""
    amounts = list(analyzer.by_category(build_txs()).values())
    assert amounts == sorted(amounts, reverse=True)


def test_by_category_excludes_income():
    """工资不能进支出汇总。"""
    assert "收入" not in analyzer.by_category(build_txs())


def test_by_category_single_item():
    result = analyzer.by_category([make_tx(3, "地铁", -6.0, "交通")])
    assert {k: round(v, 2) for k, v in result.items()} == {"交通": 6.00}


# ============================================================
# by_month —— {YYYY-MM: {收入, 支出, 结余}}
# ============================================================
def test_by_month_empty():
    assert analyzer.by_month([]) == {}


def test_by_month_single_month():
    """14 笔全在 1 月，只该有一个键。"""
    result = analyzer.by_month(build_txs())
    assert list(result.keys()) == ["2026-01"]


def test_by_month_values():
    jan = analyzer.by_month(build_txs())["2026-01"]
    assert jan["收入"] == pytest.approx(EXPECTED_INCOME)
    assert jan["支出"] == pytest.approx(EXPECTED_EXPENSE)
    assert jan["结余"] == pytest.approx(EXPECTED_BALANCE)


def test_by_month_key_format():
    """键必须是 YYYY-MM，月份补零——否则按字符串排 10 月会跑到 1 月前面。"""
    txs = [make_tx(3, "a", -10.0, None, month=1),
           make_tx(3, "b", -10.0, None, month=10)]
    assert sorted(analyzer.by_month(txs).keys()) == ["2026-01", "2026-10"]


def test_by_month_only_expense():
    """只有支出的月份：收入是 0，结余是负的。"""
    result = analyzer.by_month([make_tx(3, "x", -50.0, "交通", month=2)])
    feb = result["2026-02"]
    assert feb["收入"] == 0
    assert feb["支出"] == pytest.approx(50.0)
    assert feb["结余"] == pytest.approx(-50.0)


def test_by_month_single_item():
    assert list(analyzer.by_month([make_tx(3, "x", -10.0, None)]).keys()) == ["2026-01"]


# ============================================================
# top_expenses —— 金额最大的 n 笔支出
# ============================================================
def test_top_expenses_empty():
    assert analyzer.top_expenses([], n=5) == []


def test_top_expenses_default_n():
    """不传 n 时按默认值 5 取。"""
    assert len(analyzer.top_expenses(build_txs())) == 5


def test_top_expenses_returns_largest_first():
    result = analyzer.top_expenses(build_txs(), n=3)
    assert [t.amount for t in result] == [
        pytest.approx(-3000.00),   # 房租
        pytest.approx(-553.00),    # 高铁票
        pytest.approx(-299.00),    # 京东
    ]


def test_top_expenses_excludes_income():
    """工资是正数，永远不该出现在支出排行里。"""
    result = analyzer.top_expenses(build_txs(), n=999)
    assert all(t.amount < 0 for t in result)


def test_top_expenses_fewer_than_n():
    """数据不足 n 条时返回全部支出，不能报错。"""
    result = analyzer.top_expenses(build_txs(), n=999)
    assert len(result) == 13


def test_top_expenses_filter_by_category():
    result = analyzer.top_expenses(build_txs(), n=3, category="餐饮")
    assert all(t.category == "餐饮" for t in result)
    assert [t.amount for t in result] == [
        pytest.approx(-68.00),     # 美团外卖
        pytest.approx(-52.50),     # 美团外卖
        pytest.approx(-42.00),     # 星巴克
    ]


def test_top_expenses_single_item():
    assert len(analyzer.top_expenses([make_tx(3, "x", -10.0, None)], n=5)) == 1


# ============================================================
# group_by_month
# ============================================================
def test_group_by_month_empty():
    assert analyzer.group_by_month([]) == {}


def test_group_by_month_keys_are_months():
    grouped = analyzer.group_by_month(build_txs())
    assert list(grouped.keys()) == ["2026-01"]
    assert len(grouped["2026-01"]) == 14


def test_group_by_month_splits_months():
    txs = [make_tx(3, "a", -10.0, None, month=1),
           make_tx(4, "b", -10.0, None, month=2)]
    grouped = analyzer.group_by_month(txs)
    assert len(grouped["2026-01"]) == 1
    assert len(grouped["2026-02"]) == 1


# ============================================================
# group_by_category
# ============================================================
def test_group_by_category_empty():
    assert analyzer.group_by_category([]) == {}


def test_group_by_category_groups_expenses():
    """支出按各自的 category 归组。"""
    grouped = analyzer.group_by_category(build_txs())
    assert len(grouped["餐饮"]) == 5
    assert len(grouped["交通"]) == 3
    assert len(grouped["居住"]) == 2


def test_group_by_category_keeps_income_apart():
    """收入不能混进任何一个支出分类里。"""
    grouped = analyzer.group_by_category(build_txs())
    for category, group in grouped.items():
        if category == "收入":
            continue
        assert all(t.amount < 0 for t in group), category


# ============================================================
# find_anomials —— 规则由你定，所以这里只测"契约级"的性质
# ============================================================
def test_find_anomials_empty():
    assert analyzer.find_anomials([]) == []


def test_find_anomials_returns_list():
    assert isinstance(analyzer.find_anomials(build_txs()), list)


def test_find_anomials_result_is_subset():
    """返回值必须是原数据的子集，不能凭空造交易。"""
    txs = build_txs()
    for t in analyzer.find_anomials(txs):
        assert t in txs


def test_find_anomials_single_item():
    """每条分类都只有 1 笔时，不能除零、不能崩。"""
    txs = [make_tx(3, "x", -10.0, "交通"), make_tx(4, "y", -20.0, "餐饮")]
    assert analyzer.find_anomials(txs) == []


# --- 以下是"必须真的挑出东西"的测试 -------------------------------------
# 规则（你自己定的）：|tx| > 3 × (同分类其他单笔的平均值)，不算自己。
# 交叉相乘后代码里可以避免除法：
#     |tx| × (n - 1) > 3 × (分类合计 - |tx|)      n = 该分类笔数
# n == 1 时没有"其他"，不参与判断。

def test_find_anomials_flags_the_outlier():
    """交通 5 笔里的 -1000 必须被挑出来，而且只挑它一笔。

    不含自己的平均 = (10+10+10+10)/4 = 10，3 倍 = 30，1000 > 30。
    反过来看那 4 笔 -10：不含自己的平均 = (30+1000)/4 = 257.5，3 倍是 772.5，都够不上。
    """
    txs = [make_tx(3, "地铁", -10.0,    "交通"),
           make_tx(4, "地铁", -10.0,    "交通"),
           make_tx(5, "地铁", -10.0,    "交通"),
           make_tx(6, "地铁", -10.0,    "交通"),
           make_tx(7, "机票", -1000.0,  "交通")]
    result = analyzer.find_anomials(txs)
    assert [t.amount for t in result] == [pytest.approx(-1000.0)]


def test_find_anomials_excludes_self_from_average():
    """两笔同分类：阈值只按"另一笔"的 3 倍算，所以大的一笔要挑得出来。

    -100 看 -10：3 倍 = 30，100 > 30  → 挑出
    -10 看 -100：3 倍 = 300，10 够不上 → 不挑
    """
    txs = [make_tx(3, "a", -10.0,  "交通"),
           make_tx(4, "b", -100.0, "交通")]
    assert [t.amount for t in analyzer.find_anomials(txs)] == [pytest.approx(-100.0)]


def test_find_anomials_no_duplicates():
    """同一笔交易不能在结果里出现两次。"""
    result = analyzer.find_anomials(build_txs())
    assert len(result) == len({id(t) for t in result})


def test_find_anomials_jan_hand_checked():
    """1 月数据的答案，手算如下（按"不含自己"的口径）：

    居住  房租 3000  看 126.5   → 3 倍 379.5，3000 > 379.5   ★
          电费 126.5 看 3000    → 3 倍 9000，够不上
    交通  高铁 553   看 (6+45.8)/2=25.9 → 3 倍 77.7，553 > 77.7  ★
          滴滴 45.8  看 (6+553)/2=279.5 → 3 倍 838.5，够不上
          地铁 6     看 (45.8+553)/2=299.4 → 够不上
    购物  京东 299   看 183.4  → 3 倍 550.2，够不上
          超市 183.4 看 299    → 3 倍 897，够不上
    餐饮  美团 68    看 152.4/4=38.1 → 3 倍 114.3，够不上（其余同理）
    通讯  话费 99    只有 1 笔，没有"其他"，不参与判断
    """
    result = analyzer.find_anomials(build_txs())
    assert sorted(t.amount for t in result) == [-3000.0, -553.0]
