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
import matplotlib
matplotlib.use("Agg")                       # 不弹窗，纯后台出图
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]   # 中文
plt.rcParams["axes.unicode_minus"] = False             # 负号别变方块


def _month_range(start:str,end:str) -> list[str]:
    months = []
    start_ = start.split('-')
    end_ = end.split('-')
    year = int(start_[0])
    month = int(start_[1])
    while (year,month) <= (int(end_[0]),int(end_[1])):
        month_str = f'{month:02d}'
        months.append('-'.join((str(year),month_str)))
        if month == 12:
            year += 1
            month = 1
        else: month +=1
    
    return months
        
            


def trend_chart(month_stats: dict[str, dict[str, float]], out_path: str | Path) -> None:
    months = _month_range(min(month_stats),max(month_stats))
    income = []
    expense = []
    for month in months:
        income.append(month_stats.get(month,{}).get('收入'))
        expense.append(month_stats.get(month,{}).get('支出'))
    fig, ax = plt.subplots(figsize=(8,4.5),dpi=200)
    ax.plot(months, income,  marker="o", linewidth=2, label="收入")
    ax.plot(months, expense, marker="s", linewidth=2, label="支出")
    ax.set_title("月度收支趋势")
    ax.set_xlabel("月份")
    ax.set_ylabel("金额（CNY）")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left")
    ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
        
