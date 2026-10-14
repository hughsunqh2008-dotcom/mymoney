"""
storage.py —— 持久化与去重

【这个文件负责什么】
    把交易存到本地文件、下次能读回来、并且避免重复导入。

【你的任务】
    实现下面几个函数。要求见《项目说明书》模块 4。

【★ 本模块的核心难点：去重】

    你会需要 Transaction 里的 uid（模块 1 设计的）。

    但请认真想这几个场景：
      a) 同一天在同一家店买了两杯咖啡，金额一样、描述一样
         → 这是一笔还是两笔？
      b) 先导入 1 月账单，再导入"1-2 月"合并账单
         → 1 月那部分会重复吗？
      c) 你手动改了一笔交易的分类，再重新导入原文件
         → 你的修改会不会被覆盖掉？

    【结论：去重没有完美解。】
    选一个策略，并且**在 README 里写明它的局限**。
    "承认方案有局限并说清楚" —— 这个能力比写出完美代码更被看重。

【验收标准】
    导入 1 月 → N 条
    再导入同一个文件 → 新增 0 条（幂等）
    导入 2 月 → 新增 M 条，总数 N+M
    程序重启后数据还在

【卡住去哪查】
    - JSON 读写、ensure_ascii=False（中文不转义）  →  Automate Ch14
    - 文件/目录是否存在、mkdir(parents=True)      →  Automate Ch9
    - 集合 set 做去重                             →  Think Python chap10
    - 列表推导式筛数据                            →  Think Python chap09
"""

from __future__ import annotations

from pathlib import Path

from .models import Transaction

# 默认的存储文件位置（相对项目根目录）
DEFAULT_STORE = Path("data") / "transactions.json"


def load_all(path: str | Path = DEFAULT_STORE) -> list[Transaction]:
    """读出所有已保存的交易。

    文件不存在时返回空列表（不要报错！第一次运行本来就没有文件）。
    """
    # TODO(模块4)
    raise NotImplementedError


def save_all(txs: list[Transaction], path: str | Path = DEFAULT_STORE) -> None:
    """把交易全部写入文件（覆盖）。

    提示：
        - 用 json.dump(..., ensure_ascii=False, indent=2)
          ensure_ascii=False 是让中文显示成中文，而不是 \\u4e2d\\u6587
        - 写入前确保父目录存在
    """
    # TODO(模块4)
    raise NotImplementedError


def append_new(new_txs: list[Transaction], path: str | Path = DEFAULT_STORE) -> int:
    """把新交易追加进去，自动去重。

    返回：实际新增了几条。

    这是本项目最需要动脑的函数。
    提示：
        - 先 load_all() 拿到已有的
        - 用已有交易的 uid 建一个 set
        - 遍历 new_txs，uid 不在 set 里的才要
        - 别忘了把新加的 uid 也加进 set（否则文件内部自己会重复）
    """
    # TODO(模块4)
    raise NotImplementedError


def count_by_category(path: str | Path = DEFAULT_STORE) -> dict[str, int]:
    """统计已保存数据里各分类的条数——用来快速验证存储是否正常。"""
    # TODO(模块4)
    raise NotImplementedError
