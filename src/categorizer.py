"""
categorizer.py —— 分类引擎

【这个文件负责什么】
    按 config/categories.json 里的规则，给每笔交易打上分类标签。

【你的任务】
    实现下面两个函数。要求见《项目说明书》模块 3。

【两个必须做的设计决策】
    ① 规则冲突怎么办？
       如果描述里同时出现"美团"（餐饮）和"淘宝"（购物），归哪类？
       常见策略：
         - 按 JSON 里的顺序，先匹配到的赢
         - 按关键词长度，长的优先（更具体）
         - 自己定义优先级
       选一个，然后写进 README 说明理由。
    ② 匹配"原始描述"还是"规范化描述"？
       两种都试一次，看结果差异，再决定。

【验收标准】
    改 categories.json 就能改变分类结果，一行代码都不用动。

【卡住去哪查】
    - 读 JSON（json.load）           →  Automate Ch14
    - 字典遍历、in 判断、get 默认值   →  Automate Ch5
    - 把函数拆到多个文件、import      →  Python 官方文档 "Modules"
"""

from __future__ import annotations

from pathlib import Path

from .models import Transaction

import json

UNCATEGORIZED = "未分类"


def load_rules(path: str | Path) -> dict[str, list[str]]:
    with open(path,'r',encoding='utf-8-sig') as fin:
        rules = json.load(fin)
        rules = {k: v for k, v in rules.items() if not k.startswith('_')}
    return rules


def categorize(tx: Transaction, rules: dict[str, list[str]]) -> str:
    if tx.amount > 0: return '收入'
    for rule in rules:
        for desc in rules[rule]:
            if desc.lower() in tx.norm_desc.lower(): return rule
    return UNCATEGORIZED



def categorize_all(txs: list[Transaction], rules: dict[str, list[str]]) -> dict[str, int]:
    category = {}
    for transaction in txs:
        transaction.category = categorize(transaction,rules)
        if transaction.category in category: category[transaction.category]+=1
        else: category[transaction.category] =1
    
    return category