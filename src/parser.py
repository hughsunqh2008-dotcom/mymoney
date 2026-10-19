"""
parser.py —— 读 CSV、清洗、解析成 Transaction

【这个文件负责什么】
    把"脏的银行 CSV"变成"干净的 Transaction 列表"。
    这是整个项目最硬的一块，也是最能练到东西的一块。

【你的任务】
    实现下面三个函数。具体要求见《项目说明书》模块 2。

【必须处理的情况清单】（一个都不能漏）
    [ ] 空行
    [ ] 金额是文字（如 "abc"）→ 跳过并计数，不要崩溃
    [ ] 金额带空格、带全角符号（如 "－38.00"）
    [ ] 列名不同（"交易日期" vs "日期" vs "交易时间"）
    [ ] 文件编码是 GBK（不是 UTF-8）
    [ ] 描述里有多余空格、全角括号

【关键设计点】
    normalize_description() 是这个项目的灵魂之一。
    想一想："星巴克(国贸店)" 和 " STARBUCKS " 应该算同一个商户吗？
    如果要，你需要做什么处理？

【卡住去哪查】
    - 正则：字符类、量词、分组、re.sub  →  Automate Ch7
    - 读文件、with open、encoding 参数   →  Automate Ch8
    - csv 模块、DictReader                →  Automate Ch14
    - try/except 捕获异常                 →  Automate Ch3
    - 字符串 strip/lower/replace          →  Automate Ch6
    - 列表推导式、None 判断               →  Think Python chap09
"""

from __future__ import annotations

from pathlib import Path

from src.models import Transaction

import re

import csv

from datetime import date

LOCATION_KEYWORDS = ("店", "路", "街", "号", "城", "区", "广场", "中心", "支", "分店")
DATE_CANDIDATES = ['交易日期','日期','交易时间','date','Date']
DESC_CANDIDATES = ['交易描述','描述','摘要','备注','Description','description']
CURRENCY_CANDIDATES = ['币种','货币','货币种类','Currency','currency']
AMOUNT_CANDIDATE = ['金额','总额','Amount','amount']


_BRACKET_RE = re.compile(r'[（(][^（）()]+?([路店街号城区]|广场|中心|分店|支)[）)]')


def normalize_description(raw: str) -> str:
    normalizing = " ".join(raw.split())
    return _BRACKET_RE.sub('', normalizing)

def parse_row(row: dict) -> Transaction | None:
    # ① DictReader 读出的每个 row，它的 keys 就是表头
    fieldnames = list(row.keys())

    # ② 找列（用你的 _find_column）
    date_col     = _find_column(fieldnames, DATE_CANDIDATES)
    desc_col     = _find_column(fieldnames, DESC_CANDIDATES)
    amount_col   = _find_column(fieldnames, AMOUNT_CANDIDATE)
    currency_col = _find_column(fieldnames, CURRENCY_CANDIDATES)   # ← 可以找不到

    # ③ 关键列缺失 → 这行作废
    if date_col is None or desc_col is None or amount_col is None:
        return None

    # ④ 取值 + 转类型
    tx_date = _parse_date(row[date_col])
    tx_desc = row[desc_col]
    tx_amount = _parse_amount(row[amount_col])
    tx_currency = row[currency_col] if currency_col else None
    if tx_date is None or tx_amount is None:
        return None
    # 提示：用 _parse_date(row[date_col]) 和 _parse_amount(row[amount_col])
    #       任何一个返回 None → return None

    # ⑤ 构造对象（注意：字段名必须是 Transaction 的字段名，
    #    不是 CSV 的列名！这是你之前转发失败的根本原因）
    return Transaction(
        tx_date=tx_date,
        raw_desc=tx_desc,
        norm_desc=normalize_description(tx_desc),
        amount=tx_amount,
        currency=tx_currency,
        category=None,
        uid=None,
    )
    
    
def parse_file(path: str | Path) -> tuple[list[Transaction], dict]:
    error_info = []
    try:
        parsing_info = {"文件":path}
        transaction_list = []
        error_num = 0
        amount = 0
        with open(path,'r',encoding='utf-8-sig') as fin:
            reader = csv.DictReader(fin)
            for line_no,row in enumerate(reader,start=2):
                parsed_row = parse_row(row)
                if parsed_row: transaction_list.append(parsed_row)
                else: 
                    error_info.append((line_no,row))
                    error_num+=1
                amount+=1
        decode_type = 'utf-8-sig'
    except UnicodeDecodeError:
        parsing_info = {"文件":path}
        transaction_list = []
        error_num = 0
        amount = 0
        with open(path,'r',encoding='gb18030') as fin:
            reader = csv.DictReader(fin)
            for line_no,row in enumerate(reader,start=2):
                parsed_row = parse_row(row)
                if parsed_row: transaction_list.append(parsed_row)
                else:
                    error_info.append((line_no,row)) 
                    error_num+=1
                amount+=1
        decode_type = 'gb18030'
    
    parsing_info = {
        '文件':path,
        '编码':decode_type,
        '总数':amount,
        '成功':amount - error_num,
        '失败':error_num,
        '失败信息':error_info
    }
                
    return (transaction_list,parsing_info)
            
        
    
        

def _find_column(fieldnames: list[str], candidates: list[str]) -> str | None:
    for candidate in candidates:
        if candidate in fieldnames:
            return candidate
    return
def _parse_amount(text: str) -> float|None:
    try:
        value = float(text.strip())
    except (ValueError,TypeError):
        return
    if value == 0:          # 0.00 的"余额查询"类行：没有金额信息，视为无效行
        return
    return value
    
def _parse_date(text: str) -> date|None:
    try:
        return date.fromisoformat(text.strip())
    except (ValueError,TypeError):
        return