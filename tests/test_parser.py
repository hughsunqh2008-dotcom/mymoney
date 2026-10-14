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
    assert parser.normalize_description("(已退款)STARBUCKS")
    assert parser.normalize_description("STARBUCKS(退款)")
    
def test_space():
    assert parser.normalize_description("    ") == ""

def test_no_bracket_unchanged():
    assert parser.normalize_description("STARBUCKS") == "STARBUCKS"
    
def test_idempotent():
    for s in ["星巴克(国贸店)", " STARBUCKS ", "星巴克(已退款)", "", "  "]  :
        assert parser.normalize_description(parser.normalize_description(s)) == parser.normalize_description(s), f"不幂等: {s!r}"