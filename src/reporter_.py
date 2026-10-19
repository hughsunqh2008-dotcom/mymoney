"""
reporter.py —— 生成报告

【这个文件负责什么】
    把 analyzer 算出来的统计结果，输出成人能看的、或程序能读的格式。

【你的任务】
    实现下面三个函数。要求见《项目说明书》模块 6。

【文本报告的目标长相】
    ========== 2026-01 账目报告 ==========
    总收入:      18,500.00 CNY
    总支出:       4,533.10 CNY
    结  余:      13,966.90 CNY
    --------------------------------------
    按分类:
      居住         3,126.50  ( 69.0%)
      交通           604.80  ( 13.3%)
      购物           482.40  ( 10.6%)
      餐饮           220.40  (  4.9%)
      通讯            99.00  (  2.2%)
    --------------------------------------
    最大 5 笔支出:
      2026-01-12  房租            -3,000.00
      ...

【卡住去哪查】
    - rjust / ljust / center 对齐      →  Automate Ch6
    - f-string 格式化（:.2f、千分位）   →  Automate Ch6
    - 写 CSV、DictWriter               →  Automate Ch14
    - JSON 中文处理（ensure_ascii）  6   →  Automate Ch14
    - pathlib 写文件、mkdir            →  Automate Ch9
"""

from __future__ import annotations

from pathlib import Path

from .models import Transaction

LINE = '-'*18 + '\n'

def to_text(
    stats: dict,
    cat_stats: dict[str, float],
    month_stats: dict[str, dict[str, float]],
    top_txs: list[Transaction],
    month: str | None = None,
) -> str:
    
    if not month: return ''
    title = f'{month} 账目报告'.center(36,'=')+'\n'
    total_in = '总收入'.ljust(18) + f'{stats['总收入']:.2f} CNY'.rjust(18) + '\n'
    total_out = '总支出：'.ljust(18) + f'{stats['总支出']:.2f} CNY'.rjust(18) + '\n'
    total = '结余：'.ljust(18) + f'{stats['结余']:.2f} CNY'.rjust(18) + '\n'
    categories = []
    top_str = []
    for category in cat_stats:
        categories.append(f'  {category}'.ljust(18) + f'{cat_stats[category]:.2f}('.rjust(11) +f'{cat_stats[category]*100/stats["总支出"]:.2f}%)'.rjust(7) + '\n')
    if top_txs:
        for tx in top_txs:
            top_str.append(f'  {tx.date.isoformat()}'.ljust(12) + f'{tx.category}'.center(6) + f'{tx.amount:.2f}'.rjust(18) + '\n')
            
    text = title + total_in + total_out + total + LINE
    text += '按类别：\n'
        
    for cat in categories:
        text += cat
    
    text += LINE
    text += f'最大{len(top_txs)}笔支出：\n'
    
    for tx_str in top_str:
        text += tx_str
        
    return text
    
    
    
    
    


def to_csv(txs: list[Transaction], out_path: str | Path) -> None:
    


def to_json(payload: dict | list, out_path: str | Path) -> None:
    """把任意数据导出成 JSON。

    提示：json.dump(..., ensure_ascii=False, indent=2)
         ensure_ascii=False 保证中文是中文而不是 \\uXXXX
    """
    # TODO(模块6)
    raise NotImplementedError
