"""test_reporter.py —— 模块 6（报告输出）的测试

契约来源：《项目说明书》模块 6 + `模块6任务卡-报告输出.md` + README 设计决策 9/11。

数据仍然是 data/2026-01.csv 那 14 行，手算口径：
    收入 18500.00 / 支出 4533.10 / 结余 13966.90
    居住 3126.50(69.0%) 交通 604.80(13.3%) 购物 482.40(10.6%) 餐饮 220.40(4.9%) 通讯 99.00(2.2%)

对齐一律按**显示宽度**判断（汉字占 2 格），不按字符数——`ljust` 数的是字符，
这正是之前对不齐的原因，所以测试也要按显示宽度写，否则测不出问题。
"""

from __future__ import annotations

import json
import unicodedata
from datetime import date

import pytest

from src import analyzer, parser, reporter
from src.models import Transaction


# ============================================================
# 测试数据
# ============================================================
def make_tx(day: int, desc: str, amount: float, category: str | None,
            month: int = 1) -> Transaction:
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
    """data/2026-01.csv 的 14 行，分类按 categories.json 的结果写好。"""
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


EXPECTED_INCOME = 18500.00
EXPECTED_EXPENSE = 4533.10
EXPECTED_BALANCE = 13966.90

EMPTY_STATS = {
    "笔数": 0, "总收入": 0, "总支出": 0, "结余": 0,
    "起始日期": "无有效信息", "结束日期": "无有效信息",
}


def display_width(text: str) -> int:
    """字符串在等宽终端里的显示宽度：全角/宽字符算 2 格。"""
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text)


def report_of(txs: list[Transaction], month: str | None = "2026-01") -> str:
    """按真实链路的参数组装一次 to_text。"""
    return reporter.to_text(
        stats=analyzer.summary(txs),
        cat_stats=analyzer.by_category(txs),
        month_stats=analyzer.by_month(txs),
        top_txs=analyzer.top_expenses(txs, n=5),
        month=month,
    )


def lines_containing(text: str, needle: str) -> list[str]:
    return [line for line in text.splitlines() if needle in line]


# ============================================================
# to_text —— 结构与数字
# ============================================================
def test_to_text_returns_string_and_prints_nothing(capsys):
    """返回 str，调用时屏幕上不能有任何输出（print 的函数没法测）。"""
    out = report_of(build_txs())
    assert isinstance(out, str)
    assert out.endswith("\n")
    assert capsys.readouterr().out == ""


def test_to_text_title_shows_month():
    assert "2026-01" in report_of(build_txs()).splitlines()[0]


def test_to_text_totals():
    """三行金额必须和手算一致，且带千分位。"""
    text = report_of(build_txs())
    assert "18,500.00" in text
    assert "4,533.10" in text
    assert "13,966.90" in text


def test_to_text_has_three_total_lines():
    assert len(lines_containing(report_of(build_txs()), "CNY")) == 3


def test_to_text_categories_listed_in_order():
    """分类要全部出现，顺序跟 cat_stats 一致（降序）。"""
    text = report_of(build_txs())
    names = ["居住", "交通", "购物", "餐饮", "通讯"]
    positions = [text.index(name) for name in names]
    assert positions == sorted(positions)


def test_to_text_percentage():
    """百分比按总支出算，保留一位小数。"""
    text = report_of(build_txs())
    assert "69.0%" in text        # 3126.50 / 4533.10
    assert "2.2%" in text         # 99.00 / 4533.10


def test_to_text_top_expenses_appear():
    text = report_of(build_txs())
    for desc in ("房租", "高铁票", "京东商城", "超市购物", "电费"):
        assert desc in text


def test_to_text_no_nan():
    """任何情况下都不能出现 nan / inf。"""
    text = report_of(build_txs())
    assert "nan" not in text.lower()
    assert "inf" not in text.lower()


# ============================================================
# to_text —— 对齐（按显示宽度，不是字符数）
# ============================================================
def test_to_text_total_lines_aligned():
    """三行总计的显示宽度必须相同，否则金额列对不齐。"""
    lines = lines_containing(report_of(build_txs()), "CNY")
    widths = {display_width(line) for line in lines}
    assert len(widths) == 1, "\n" + "\n".join(f"{display_width(l):>3} |{l}|" for l in lines)


def test_to_text_category_lines_aligned():
    """所有分类行显示宽度相同，且都以 ) 结尾。"""
    lines = lines_containing(report_of(build_txs()), "%")
    assert all(line.endswith(")") for line in lines)
    widths = {display_width(line) for line in lines}
    assert len(widths) == 1, "\n" + "\n".join(f"{display_width(l):>3} |{l}|" for l in lines)


def test_to_text_top_lines_aligned():
    """最大账单那几行显示宽度相同（描述长短不一也要对齐）。"""
    lines = [line for line in report_of(build_txs()).splitlines()
             if line.strip().startswith("2026-")]
    assert len(lines) == 5
    widths = {display_width(line) for line in lines}
    assert len(widths) == 1, "\n" + "\n".join(f"{display_width(l):>3} |{l}|" for l in lines)


def test_to_text_no_blank_lines():
    """不能有多余空行（行末多拼一个 \\n 就会出现）。"""
    assert "" not in report_of(build_txs()).splitlines()


# ============================================================
# to_text —— 边界
# ============================================================
def test_to_text_empty_data():
    """空数据也要出一份完整报告，不能崩、不能 nan。"""
    text = reporter.to_text(EMPTY_STATS, {}, {}, [], month="2026-01")
    assert isinstance(text, str)
    assert "0.00" in text
    assert "nan" not in text.lower()


def test_to_text_without_month():
    """不传月份要退回"全部"，不能返回空串。"""
    text = reporter.to_text(
        analyzer.summary(build_txs()),
        analyzer.by_category(build_txs()),
        analyzer.by_month(build_txs()),
        analyzer.top_expenses(build_txs(), n=5),
        month=None,
    )
    assert text.strip()
    assert "账目报告" in text


def test_to_text_fewer_top_expenses():
    """top_txs 不足 5 笔时标题按实际条数写，不能写死 5。"""
    txs = build_txs()
    text = reporter.to_text(analyzer.summary(txs), analyzer.by_category(txs),
                            analyzer.by_month(txs),
                            analyzer.top_expenses(txs, n=2), month="2026-01")
    assert "最大2笔" in text
    assert "最大5笔" not in text


# ============================================================
# to_csv
# ============================================================
def test_to_csv_header(tmp_path):
    path = tmp_path / "r.csv"
    reporter.to_csv(build_txs(), path)
    assert path.read_text(encoding="utf-8-sig").splitlines()[0] == "日期,描述,金额,币种,分类"


def test_to_csv_line_count(tmp_path):
    path = tmp_path / "r.csv"
    reporter.to_csv(build_txs(), path)
    assert len(path.read_text(encoding="utf-8-sig").splitlines()) == 1 + 14


def test_to_csv_has_bom_for_excel(tmp_path):
    """Excel 靠 BOM 认 UTF-8，没有就是乱码。"""
    path = tmp_path / "r.csv"
    reporter.to_csv(build_txs(), path)
    assert path.read_bytes().startswith(b"\xef\xbb\xbf")


def test_to_csv_uses_lf(tmp_path):
    """统一用 \\n，不要 \\r\\n，否则和 data/*.csv 混着 git diff 会全变。"""
    path = tmp_path / "r.csv"
    reporter.to_csv(build_txs(), path)
    assert b"\r\n" not in path.read_bytes()


def test_to_csv_amount_has_no_thousands_separator(tmp_path):
    """CSV 是机读的：千分位会让金额变成带引号的文本，Excel 当文本，自己再导入还失败。"""
    path = tmp_path / "r.csv"
    reporter.to_csv(build_txs(), path)
    text = path.read_text(encoding="utf-8-sig")
    assert "18,500.00" not in text
    assert "18500.00" in text
    assert "-3000.00" in text


def test_to_csv_none_category_as_uncategorized(tmp_path):
    """category 为 None 表示还没分类，导出时写"未分类"，不能留空。"""
    tx = make_tx(1, "超市购物", -10.0, None, month=2)
    path = tmp_path / "r.csv"
    reporter.to_csv([tx], path)
    assert path.read_text(encoding="utf-8-sig").splitlines()[1].endswith("未分类")


def test_to_csv_empty(tmp_path):
    """没有交易时只写表头，不能崩。"""
    path = tmp_path / "r.csv"
    reporter.to_csv([], path)
    assert len(path.read_text(encoding="utf-8-sig").splitlines()) == 1


def test_to_csv_roundtrip(tmp_path):
    """导出再导入：失败数、笔数、金额总和都不能变。

    这条专门防"金额带千分位""金额被写成文本"——导出功能把数据搞坏，是最难发现的 bug。
    """
    txs = build_txs()
    path = tmp_path / "r.csv"
    reporter.to_csv(txs, path)

    back, rep = parser.parse_file(str(path))
    assert rep["失败"] == 0, rep["失败信息"]
    assert len(back) == len(txs)
    assert sum(t.amount for t in back) == pytest.approx(sum(t.amount for t in txs))


# ============================================================
# to_json
# ============================================================
def payload_of(txs: list[Transaction]) -> dict:
    """mymoney.py 里组装 payload 的样子。"""
    return {
        "summary": analyzer.summary(txs),
        "by_category": analyzer.by_category(txs),
        "by_month": analyzer.by_month(txs),
        "top_expenses": [t.to_dict() for t in analyzer.top_expenses(txs, n=5)],
    }


def test_to_json_is_readable_by_standard_json_load(tmp_path):
    """最重要的验收：别的程序用最普通的方式能读回来。"""
    path = tmp_path / "r.json"
    reporter.to_json(payload_of(build_txs()), path)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["summary"]["笔数"] == 14


def test_to_json_has_no_bom(tmp_path):
    """JSON 规范不允许 BOM；带 BOM 时 json.load 会直接 JSONDecodeError。"""
    path = tmp_path / "r.json"
    reporter.to_json(payload_of(build_txs()), path)
    assert not path.read_bytes().startswith(b"\xef\xbb\xbf")


def test_to_json_keeps_chinese(tmp_path):
    """ensure_ascii=False：中文就是中文，不是 \\uXXXX。"""
    path = tmp_path / "r.json"
    reporter.to_json(payload_of(build_txs()), path)
    text = path.read_text(encoding="utf-8")
    assert "餐饮" in text
    assert "\\u" not in text


def test_to_json_accepts_plain_dict(tmp_path):
    """契约：payload 是任意 dict / list，不是只认 Transaction 列表。"""
    path = tmp_path / "r.json"
    reporter.to_json({"summary": {"笔数": 1}}, path)
    with open(path, encoding="utf-8") as f:
        assert json.load(f) == {"summary": {"笔数": 1}}


def test_to_json_indented(tmp_path):
    """indent=2：人能读，diff 也好看。"""
    path = tmp_path / "r.json"
    reporter.to_json(payload_of(build_txs()), path)
    assert "\n  " in path.read_text(encoding="utf-8")


# ============================================================
# 路径契约：父目录由调用方（mymoney.py）创建
# ============================================================
def test_to_csv_does_not_create_parent_dir(tmp_path):
    """导出函数不建目录：目录不存在就该报 FileNotFoundError。

    否则路径拼错会静静创建一个空目录，把 bug 藏起来。
    """
    with pytest.raises(FileNotFoundError):
        reporter.to_csv(build_txs(), tmp_path / "no_such_dir" / "r.csv")


def test_to_json_does_not_create_parent_dir(tmp_path):
    with pytest.raises(FileNotFoundError):
        reporter.to_json(payload_of(build_txs()), tmp_path / "no_such_dir" / "r.json")
