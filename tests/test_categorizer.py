import pytest
from src.models import Transaction
from src import categorizer
from datetime import date
RULES = {
    "餐饮": ["星巴克", "美团"],
    "交通": ["地铁", "滴滴"],
    "居住": ["房租"],
    "收入": ["工资"],
}

def test_right_rules():
    assert categorizer.load_rules('C:\\python_programe\\mymoney\\config\\categories.json')=={
  "餐饮": ["星巴克", "STARBUCKS", "美团", "饿了么", "肯德基", "KFC", "麦当劳", "瑞幸", "luckin", "餐", "food", "咖啡"],
  "交通": ["地铁", "滴滴", "公交", "高铁", "火车", "加油", "停车", "出租车", "taxi", "uber"],
  "购物": ["淘宝", "京东", "拼多多", "天猫", "超市", "便利店", "商场"],
  "居住": ["房租", "水费", "电费", "燃气", "物业", "宽带"],
  "收入": ["工资", "薪", "奖金", "报销", "退款", "利息"],
  "医疗": ["医院", "药店", "诊所", "体检"],
  "娱乐": ["电影", "游戏", "steam", "视频", "音乐", "会员"],
  "通讯": ["话费", "流量", "移动", "联通", "电信"]
    }
    
def test_right_categorise():
    assert categorizer.categorize(Transaction(tx_date=date(2008,1,25),raw_desc='淘宝',amount=-90,norm_desc=None,currency=None,category=None,uid=None),categorizer.load_rules('C:\\python_programe\\mymoney\\config\\categories.json'))=="购物"
    
def test_categorize_all_counts():
    """categorize_all 应返回 {分类名: 笔数}。"""
    txs = [
        Transaction(
            tx_date=date(2026, 1, 3), raw_desc="星巴克", norm_desc="星巴克",
            amount=-38.0, currency="CNY", category=None, uid=None,
        ),
        Transaction(
            tx_date=date(2026, 1, 7), raw_desc="美团", norm_desc="美团",
            amount=-52.5, currency="CNY", category=None, uid=None,
        ),
        Transaction(
            tx_date=date(2026, 1, 15), raw_desc="星巴克", norm_desc="星巴克",
            amount=-19.9, currency="CNY", category=None, uid=None,
        ),
        Transaction(
            tx_date=date(2026, 1, 3), raw_desc="地铁", norm_desc="地铁",
            amount=-6.0, currency="CNY", category=None, uid=None,
        ),
        Transaction(
            tx_date=date(2026, 1, 10), raw_desc="滴滴", norm_desc="滴滴",
            amount=-45.8, currency="CNY", category=None, uid=None,
        ),
        Transaction(
            tx_date=date(2026, 1, 12), raw_desc="房租", norm_desc="房租",
            amount=-3000.0, currency="CNY", category=None, uid=None,
        ),
        Transaction(
            tx_date=date(2026, 1, 5), raw_desc="工资", norm_desc="工资",
            amount=18500.0, currency="CNY", category=None, uid=None,   # 正数！
        ),
        Transaction(
            tx_date=date(2026, 1, 20), raw_desc="某不认识的商户",
            norm_desc="某不认识的商户",
            amount=-10.0, currency="CNY", category=None, uid=None,
        ),
        Transaction(
            tx_date=date(2026, 1, 22), raw_desc="另一个没见过的",
            norm_desc="另一个没见过的",
            amount=-10.0, currency="CNY", category=None, uid=None,
        ),
    ]

    counts = categorizer.categorize_all(txs, RULES)

    assert isinstance(counts, dict), (
        f"categorize_all 应该返回 dict，实际返回了 {type(counts).__name__}"
    )
    assert counts.get("餐饮") == 3, f"餐饮应为 3，实际 {counts.get('餐饮')}"
    assert counts.get("交通") == 2, f"交通应为 2，实际 {counts.get('交通')}"
    assert counts.get("居住") == 1, f"居住应为 1，实际 {counts.get('居住')}"
    assert counts.get("收入") == 1, f"收入应为 1，实际 {counts.get('收入')}"
    assert counts.get(categorizer.UNCATEGORIZED) == 2, (
        f"未分类应为 2，实际 {counts.get(categorizer.UNCATEGORIZED)}"
    )
    assert sum(counts.values()) == len(txs), (
        f"各类之和 {sum(counts.values())} 应等于交易总数 {len(txs)}"
    )