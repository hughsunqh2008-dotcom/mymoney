"""
models.py —— 数据模型

【这个文件负责什么】
    定义项目里的"数据长什么样"。
    这是所有模块的地基：parser 产出它、categorizer 改它、
    storage 存它、analyzer 统计它、reporter 输出它。

【你的任务】
    按《项目说明书》模块 1 的要求，实现 Transaction 类。

【三个必须做的设计决策】（做完写进 README）
    ① 支出用负数表示，还是用正数 + 一个"类型"字段？
       两种都行。想清楚：做统计时哪种写法更省事？
    ② "唯一标识"怎么生成？
       想清楚：什么情况下，同一笔交易会生成两个不同的标识？
    ③ 日期存字符串还是 datetime 对象？
       想清楚：后面要"按月份筛选"，哪种更方便？

【卡住去哪查】
    - 类的定义 / __init__ / self  →  Think Python chap14
    - 方法、__str__               →  Think Python chap15
    - datetime 基本用法            →  Automate Ch15
    - 类型注解（可选）             →  Python 官方文档 "typing"
"""

from __future__ import annotations

from datetime import date




class Transaction:
    """一笔交易。

    字段说明（类型由你决定，这里只是建议）：
        date         日期
        raw_desc     银行给的原始描述，一个字都不改（用于追溯）
        norm_desc    规范化后的描述（用于匹配分类规则）
        amount       金额
        currency     币种，如 "CNY"
        category     分类，初始为空，由 categorizer 填
        uid          唯一标识，用于去重
    """

    def __init__(self, tx_date: date, raw_desc, norm_desc, amount: float, currency, category, uid):
        self.date = tx_date
        self.raw_desc = raw_desc
        if norm_desc is not None: self.norm_desc = norm_desc
        else: self.norm_desc = raw_desc
        self.amount = amount
        if currency is not None: self.currency = currency
        else: self.currency = "CNY"
        self.category = category
        if uid is not None: self.uid = uid
        else: self.uid = self._make_uid()

    def __str__(self):
        return f"Transaction: {self.date} {self.raw_desc} {self.amount}{self.currency}"
        

    def __repr__(self):
        return f"Transaction(date={self.date}, raw_desc={self.raw_desc}, norm_desc={self.norm_desc}, amount={self.amount}, currency={self.currency}, category={self.category}, uid={self.uid})"

    def to_dict(self):
        return  {
                'date': self.date.isoformat(), 
                'raw_desc': self.raw_desc,
                'norm_desc': self.norm_desc,
                'amount': self.amount,
                'currency': self.currency,
                'category': self.category,
                'uid': self.uid
                }
    
    def _make_uid(self):
        return f'{self.date}_{self.raw_desc}_{self.amount:.2f}_{self.currency}'

            
    @classmethod
    def from_dict(cls, d: dict):
        for key in ("date", "raw_desc", "amount"):
            if key not in d:
                raise ValueError(f"缺少必需的字段 {key!r}:{d}")

        return cls(
            tx_date=date.fromisoformat(d["date"]),
            raw_desc=d["raw_desc"],
            norm_desc=d.get("norm_desc"),
            amount=d["amount"],
            currency=d.get("currency"),
            category=d.get("category"),
            uid=d.get("uid"),
            )