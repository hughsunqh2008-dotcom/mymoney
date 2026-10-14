"""
tests 包 —— 存放 pytest 测试文件。

【这个空文件（__init__.py）的作用】
    它只是告诉 Python："tests 是一个包"。

    为什么需要它？
        不写的话，pytest 会用"把测试文件当独立脚本"的方式导入，
        那样 sys.path 里就只有 tests/ 这一层，
        于是 `from src.models import Transaction` 会报
        ModuleNotFoundError: No module named 'src'。

    加了它之后，pytest 按包的方式导入，
    项目根目录会在 sys.path 里，src 就能被找到了。

【怎么跑测试】
    在项目根目录（不是 tests 目录里）执行：
        python -m pytest -v

    注意是 `python -m pytest`，不是直接 `pytest`。
    加 `python -m` 会让 Python 把"当前目录"加进 sys.path，
    这也是更稳的跑法。
"""
