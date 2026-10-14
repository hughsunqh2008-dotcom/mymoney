# -*- coding: utf-8 -*-
"""
生成 GBK 编码的测试账单文件。

【为什么需要这个脚本】
    真实的银行导出文件经常是 GBK 编码（中文 Windows 的老习惯），
    而这个项目要求你的解析器能处理它。
    但用普通编辑器很难存出 GBK 文件，所以用这个小工具生成。

【怎么运行】
    在项目根目录、激活虚拟环境后：
        python make_gbk_sample.py
    它会在 data/ 下生成 2026-03.csv

【它能教会你什么】
    看第 20 行左右：同一个字符串，用不同 encoding 写出来，
    字节数完全不同。这就是"编码"的真实含义。
"""

from pathlib import Path

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"

# 故意混入全角字符和特殊符号，考察解析器的容错能力
CONTENT = """交易日期,交易描述,金额,币种
2026-03-02,星巴克(国贸店),－38.00,CNY
2026-03-03,地铁出行,-6.00,CNY
2026-03-05,工资,18500.00,CNY
2026-03-06,美团外卖,-42.30,CNY
2026-03-08,京东商城,-1299.00,CNY
2026-03-10,滴滴出行,-62.10,CNY
2026-03-12,房租,-3000.00,CNY
2026-03-15,瑞幸咖啡,-16.50,CNY
2026-03-18,超市购物,-95.20,CNY
2026-03-20,话费充值,-99.00,CNY
2026-03-22,美团外卖,-71.80,CNY
2026-03-25,电影票,-120.00,CNY
2026-03-28,星巴克(国贸店),-45.00,CNY
2026-03-30,水费,-48.60,CNY
"""


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out = DATA_DIR / "2026-03.csv"

    # ---- 关键的一行：指定 gbk 编码 ----
    out.write_text(CONTENT, encoding="gbk")

    # 顺便让你看见"编码"到底意味着什么
    utf8_bytes = CONTENT.encode("utf-8")
    gbk_bytes = CONTENT.encode("gbk")
    print(f"已生成: {out}")
    print(f"同样的文字，UTF-8 编码占 {len(utf8_bytes)} 字节")
    print(f"               GBK 编码占 {len(gbk_bytes)} 字节")
    print()
    print("下一步：试着用 utf-8 打开它，你会看到什么？")
    print("        （这就是你模块 2 要处理的问题）")


if __name__ == "__main__":
    main()
