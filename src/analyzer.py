from .models import Transaction 

from datetime import date


def summary(txs:list[Transaction]) -> dict:
    info = {}
    total_in = 0.0
    total_out =0.0
    num = 0
    if not txs: return {
        "笔数": 0,
        "总收入": 0,
        "总支出": 0,
        "结余": 0,
        "起始日期": "无有效信息",
        "结束日期": "无有效信息",
    }
    txs = sorted(txs,key=lambda x:x.date)
    for tx in sorted(txs,key=lambda x:x.date):
        if tx.amount > 0: total_in += tx.amount
        else: total_out -= tx.amount
    start,end = txs[0].date.isoformat(),txs[-1].date.isoformat()
    
    return {
        "笔数": len(txs),
        "总收入": total_in,
        "总支出": total_out,
        "结余": total_in -total_out,
        "起始日期": start,
        "结束日期": end,
    }
    
def group_by_category(txs:list[Transaction]) -> dict[str,list]:
    
    category_group = {}
    if not txs: return {}
    for tx in txs:
        if tx.amount > 0:
            category_group.setdefault('收入',[]).append(tx)
            continue
        if tx.category is None: category_group.setdefault('无类别',[]).append(tx)
        category_group.setdefault(tx.category,[]).append(tx)

    return category_group
        
def group_by_month(txs:list[Transaction]) -> dict[str,list]:
    
    month_group = {}
    if not txs: return {}
    for tx in txs:
        month_group.setdefault(tx.date.strftime("%Y-%m"),[]).append(tx)
    return month_group

def by_category(txs:list[Transaction]) -> dict[str,float]:
    category_group = group_by_category(txs)
    category_info = {}
    category_sorted ={}
    for category in category_group:
        total = 0.0
        if category == '收入': continue
        for tx in category_group[category]:
            total -= tx.amount
        category_info[category] = total

    for item in sorted(category_info.items(),key=lambda x:x[1],reverse=True):
        category_sorted[item[0]] = item[1]
            
    return category_sorted

def by_month(txs:list[Transaction]) -> dict[str,dict[str,float]]:
    month_group = group_by_month(txs)
    month_info = {}
    for month in sorted(month_group.keys()):
        month_in = 0.0
        month_out = 0.0
        for tx in month_group[month]:
            if tx.amount > 0:
                month_in += tx.amount
            else:
                month_out -= tx.amount
        month_info[month] = {
            '收入': month_in,
            '支出': month_out,
            '结余': month_in - month_out
        }
    
    return month_info

def find_anomials(txs) -> list[Transaction]:
    #在同一种类中，若支出超过其他单笔支出平均值的三倍则为异常交易
    category_group = group_by_category(txs)
    category_info = by_category(txs)
    abnormals = []
    
    for category in category_info:
        if category == '收入': continue
        for tx in category_group[category]:
            if -(len(category_group[category])+2)*tx.amount > 3*category_info[category]:
                abnormals.append(tx)
                    
    return abnormals

def top_expenses(txs:list[Transaction],n=5,category=None) -> list:
    top_n = []
    if not txs: return []
    if not category:
        for tx in sorted(txs,key=lambda x:x.amount):
            if tx.amount > 0 or n <= 0: break
            top_n.append(tx)
            n -= 1
    else:
        categorized = group_by_category(txs)
        for tx in sorted(categorized[category],key=lambda x:x.amount):
                    if n <= 0: break
                    top_n.append(tx)
                    n -= 1
    return top_n
    
    
    
            
             
        

        
    