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

# 匹配不到任何规则时用的分类名
UNCATEGORIZED = "未分类"


def load_rules(path: str | Path) -> dict[str, list[str]]:
    """从 JSON 文件读取分类规则。

    参数：
        path: categories.json 的路径
    返回：
        形如 {"餐饮": ["星巴克", "美团"], "交通": ["地铁"]}

    提示：
        - JSON 里我加了几行以 "_" 开头的说明性键（"_说明"、"_格式"、""
          _重要"），它们的值是字符串而不是列表。
          读进来时要跳过它们，否则后面遍历会出错。
    """
    # TODO(模块3)
    raise NotImplementedError


def categorize(tx: Transaction, rules: dict[str, list[str]]) -> str:
    """给一笔交易判断分类，并写回 tx.category。

    参数：
        tx:    交易对象
        rules: load_rules() 读出来的规则
    返回：
        分类名；匹配不到返回 UNCATEGORIZED

    注意：这个函数有"副作用"——它会修改 tx。
         这是好设计还是坏设计？值得想一想（写进 README 可选）。
    """
    # TODO(模块3)
    raise NotImplementedError


def categorize_all(txs: list[Transaction], rules: dict[str, list[str]]) -> dict[str, int]:
    """给一批交易全部分类，返回统计：{分类名: 条数}。"""
    # TODO(模块3)
    raise NotImplementedError
