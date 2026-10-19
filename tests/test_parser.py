"""
test_parser.py —— parser 模块的测试

【这个文件负责什么】
    用自动化测试验证 parser 的行为正确。

【为什么必须写测试】
    因为你会在模块 2 之后不断改 parser（加新格式支持、修 bug）。
    每次改完，你都要回答"我有没有把原来能用的搞坏？"
    手动重新跑一遍三个文件很累，测试一秒钟给你答案。

【你的任务】（模块 8）
    写至少 8 条测试，必须覆盖：
        [ ] 正常的一行 → 能解析出正确的日期/金额/描述
        [ ] 空行 → 被跳过
        [ ] 金额是文字（"abc"）→ 返回 None，不抛异常
        [ ] 金额带空格 → 能正确解析
        [ ] GBK 编码的文件 → 能读进来
        [ ] normalize_description 的行为
        [ ] 表头列名不同 → 能找到正确的列
        [ ] 一条完整的"文件 → 报告"流程

【怎么运行】
    在项目根目录、激活虚拟环境后：
        python -m pytest -v
    或者：
        pytest -v

【卡住去哪查】
    - assert 断言                →  Automate Ch10（调试那章讲断言）
    - try/except 测异常          →  Automate Ch3
    - pytest 的用法（assert 即可，不需要特殊语法）
      →  pytest 官方文档 "Get Started"
"""

from __future__ import annotations

import pytest

from src.models import Transaction
from src import parser


# ------------------------------------------------------------
# 示例：一条已经写好的测试，让你看清格式
# 你可以照着这个样式往下写
# ------------------------------------------------------------
def test_normalize_description_strips_whitespace():
    """规范化应该去掉首尾空格。"""
    result = parser.normalize_description("  STARBUCKS  ")
    assert result == result.strip()
    assert result != "  STARBUCKS  "

def test_collapse_inner_spaces():
    assert parser.normalize_description(" STARBUCKS     COFFEE  ") == "STARBUCKS COFFEE"

def test_remove_location_info():
    assert parser.normalize_description("STARBUCKS(GUOMAO店)") == "STARBUCKS"
    assert parser.normalize_description("STARBUCKS(HEPING路)") == "STARBUCKS"
    
def test_keep_meaningful_info():
    assert parser.normalize_description("(已退款)STARBUCKS") == "(已退款)STARBUCKS"
    assert parser.normalize_description("STARBUCKS(退款)") == "STARBUCKS(退款)"
    
def test_space():
    assert parser.normalize_description("    ") == ""

def test_no_bracket_unchanged():
    assert parser.normalize_description("STARBUCKS") == "STARBUCKS"
    
def test_idempotent():
    for s in ["星巴克(国贸店)", " STARBUCKS ", "星巴克(已退款)", "", "  "]  :
        assert parser.normalize_description(parser.normalize_description(s)) == parser.normalize_description(s), f"不幂等: {s!r}"
     
def test_fullwidth_bracket():
    assert parser.normalize_description("星巴克（国贸店）") == "星巴克"

def test_bracket_not_over_eaten():
    """防止贪婪匹配跨过括号——这条是给上面那个 bug 上的保险。"""
    assert parser.normalize_description("(退款)星巴克(国贸店)") == "(退款)星巴克"

def test_find_column_prefers_order():
    """candidates 的顺序 = 优先级"""
    assert parser._find_column(["日期", "交易日期"], ["交易日期", "日期"]) == "交易日期"

def test_find_column_not_found():
    assert parser._find_column(["a", "b"], ["日期"]) is None

def test_parse_amount_ok():
    assert parser._parse_amount(" -18.5 ") == -18.5
    assert parser._parse_amount("18500") == 18500.0

def test_parse_amount_bad_returns_none():
    assert parser._parse_amount("abc") is None          # ← 不抛异常

def test_parse_amount_zero_returns_none():
    """金额为 0 视为无效行：统计口径都假设"有金额才算交易"。"""
    assert parser._parse_amount("0.00") is None
    assert parser._parse_amount("-0.00") is None
    assert parser._parse_amount("0") is None

def test_parse_row_rejects_zero_amount():
    row = {"交易日期": "2026-01-03", "交易描述": "余额查询", "金额": "0.00", "币种": "CNY"}
    assert parser.parse_row(row) is None

def test_parsed_amounts_are_never_zero():
    """不变式：解析成功的交易，金额一定不为 0。

    reporter.to_text 用 stats["总支出"] 当百分比的分母，靠的就是这条：
        cat_stats 非空 ⇒ 至少有一笔支出 ⇒ 总支出 > 0 ⇒ 不会除零
    如果这条挂了，说明不变式被破坏，reporter 里那道除法就不再安全。
    """
    for name in ("2026-01.csv", "2026-02.csv", "2026-03.csv"):
        txs, _ = parser.parse_file(f"data/{name}")
        assert all(tx.amount != 0 for tx in txs), name

def test_parse_row_ok():
    tx = parser.parse_row({"交易日期": "2026-01-03", "交易描述": "星巴克(国贸店)",
                           "金额": "-38.00", "币种": "CNY"})
    assert tx is not None
    assert tx.amount == -38.0
    assert tx.raw_desc == "星巴克(国贸店)"       # 原文保留
    assert tx.norm_desc == "星巴克"              # 清洗生效

def test_parse_row_missing_currency():
    """没有币种列 → 用默认 CNY（这是你之前 NameError 的那个场景）"""
    tx = parser.parse_row({"日期": "2026-02-01", "摘要": "STARBUCKS", "金额": "-45.0"})
    assert tx is not None
    assert tx.currency == "CNY"

def test_parse_file_reports_counts():
    txs, report = parser.parse_file("data/2026-02.csv")
    assert report["成功"] == 13
    assert report["失败"] == 1
    assert len(report["失败信息"]) == 1