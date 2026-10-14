"""
src 包 —— mymoney 的业务逻辑都在这里。

这个文件（__init__.py）的作用只是告诉 Python："src 是一个包"。
所以你可以写 `from src import parser`。

本项目的模块划分：
    models.py       数据模型（Transaction 等）
    parser.py       读 CSV、清洗、解析成 Transaction
    categorizer.py  按规则给交易打分类标签
    storage.py      持久化（存/取/去重）
    analyzer.py     统计与分析
    reporter.py     生成报告（文本/CSV/JSON）
    plotter.py      画图
"""

__all__ = [
    "models",
    "parser",
    "categorizer",
    "storage",
    "analyzer",
    "reporter",
    "plotter",
]
