"""
plotter.py —— 图表

【这个文件负责什么】
    把统计结果画成图，保存为 PNG。

【你的任务】
    实现 trend_chart()。要求见《项目说明书》模块 7。

【前置：需要先装 matplotlib】
    在激活虚拟环境后执行：
        pip install -r requirements.txt
    （或者只装它：pip install matplotlib）

【目标图】
    - X 轴：月份（如 2026-01、2026-02）
    - Y 轴：金额
    - 两条线：收入、支出（要能区分颜色 + 有图例）
    - 有标题、X 轴标签、Y 轴标签
    - 保存到 out/trend.png

【卡住去哪查】
    - matplotlib 基础：plot / xlabel / ylabel / title / legend / savefig
      →  Automate 里与图像/绘图相关的章节，或 matplotlib 官方 "Pyplot tutorial"
    - 中文字体显示成方块？→ 这是 matplotlib 的经典问题，搜
      "matplotlib 中文乱码" 能找到解决方案（设置 rcParams 的字体）

【一个真实的坑】
    matplotlib 默认字体不含中文，你图上的中文会变成方框。
    这不是 bug，是字体配置问题——处理方式值得记进笔记。
"""

from __future__ import annotations

from pathlib import Path


def trend_chart(month_stats: dict[str, dict[str, float]], out_path: str | Path) -> None:
    """画收入/支出随月份变化的折线图，保存为 PNG。

    参数：
        month_stats: analyzer.by_month() 的返回值
                     形如 {"2026-01": {"收入": ..., "支出": ...}, ...}
        out_path:    输出文件路径，如 "out/trend.png"
    """
    # TODO(模块7)
    raise NotImplementedError
