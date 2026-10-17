"""test_store.py —— storage 模块的测试

【这个文件测什么】
    src/storage.py 的四个函数：load_all / save_all / append_new / count_by_category

【为什么每个测试都要 tmp_path】
    因为存储函数会写文件。如果直接写 data/transactions.json，
    测试就会污染你的真实数据。
    tmp_path 是 pytest 内置的 fixture：在函数参数里写上它，
    pytest 自动给你一个临时目录，测试结束后自动清理。

    用法：
        def test_xxx(tmp_path):
            p = tmp_path / "store.json"      # ← 临时目录里的文件
            ...

【怎么跑】
    在项目根目录执行：
        python -m pytest tests/test_store.py -v
"""

from datetime import date

from src.models import Transaction
from src import storage


# ============================================================
# 辅助：造一笔交易
# 注意 amount 默认是负数（支出）；测收入时要显式传正数
# ============================================================
def tx(desc: str, amount: float = -10.0, category: str | None = None) -> Transaction:
    return Transaction(
        tx_date=date(2026, 1, 3),
        raw_desc=desc,
        norm_desc=desc,
        amount=amount,
        currency="CNY",
        category=category,
        uid=None,
    )


# ============================================================
# 1. save_all —— 能写出文件
# ============================================================
def test_save_all_creates_file(tmp_path):
    """save_all 应该真的创建了文件。"""
    p = tmp_path / "store.json"
    assert not p.exists()

    storage.save_all([tx("星巴克")], p)

    assert p.exists(), "save_all 跑完了但文件不存在"


def test_save_all_writes_readable_chinese(tmp_path):
    """⚠️ 中文必须原样写入，不能变成 \\u661f\\u5df4\\u514b。

    这条测试针对 save_all 里的 json.dump 参数——
    如果写成 ensure_ascii=True（或拼错参数名），文件内容会不可读。
    """
    p = tmp_path / "store.json"
    storage.save_all([tx("星巴克")], p)

    raw_text = p.read_text(encoding="utf-8")

    assert "星巴克" in raw_text, (
        "文件里看不到中文，说明 ensure_ascii 没设成 False。\n"
        f"文件实际内容（前 200 字符）：{raw_text[:200]}"
    )


def test_save_all_creates_parent_directory(tmp_path):
    """父目录不存在时也要能写成功（靠 mkdir(parents=True)）。"""
    p = tmp_path / "nested" / "deep" / "store.json"
    storage.save_all([tx("星巴克")], p)

    assert p.exists()
    assert p.parent.is_dir()


# ============================================================
# 2. load_all —— 读回来
# ============================================================
def test_load_all_missing_file_returns_empty(tmp_path):
    """文件不存在 → 返回空列表，不要抛异常。

    因为"第一次运行"本来就没有文件，这不是错误。
    """
    result = storage.load_all(tmp_path / "根本不存在.json")
    assert result == []


def test_load_save_roundtrip(tmp_path):
    """存进去再读出来，内容必须一致。"""
    p = tmp_path / "store.json"
    original = [tx("星巴克", -38.0), tx("地铁", -6.0)]

    storage.save_all(original, p)
    loaded = storage.load_all(p)

    assert len(loaded) == 2
    assert loaded[0].raw_desc == "星巴克"
    assert loaded[0].amount == -38.0
    assert loaded[1].raw_desc == "地铁"


def test_roundtrip_preserves_date_type(tmp_path):
    """⚠️ 日期读回来必须还是 date 对象，不能变成字符串。

    这条针对 to_dict / from_dict 的 isoformat 转换。
    """
    p = tmp_path / "store.json"
    storage.save_all([tx("星巴克")], p)
    loaded = storage.load_all(p)

    assert isinstance(loaded[0].date, date), (
        f"date 应该是 date 对象，实际是 {type(loaded[0].date).__name__}"
    )
    assert loaded[0].date == date(2026, 1, 3)


def test_roundtrip_preserves_category(tmp_path):
    """分类也要能存下来、读回来。"""
    p = tmp_path / "store.json"
    storage.save_all([tx("星巴克", category="餐饮")], p)
    loaded = storage.load_all(p)

    assert loaded[0].category == "餐饮"


# ============================================================
# 3. append_new —— 本模块的核心
# ============================================================
def test_append_new_returns_count(tmp_path):
    """第一次追加，返回实际新增数。"""
    p = tmp_path / "store.json"
    added = storage.append_new([tx("星巴克"), tx("地铁")], p)

    assert added == 2
    assert len(storage.load_all(p)) == 2


def test_append_new_is_idempotent(tmp_path):
    """⭐ 幂等性：同一批导入两次，第二次新增 0 条。

    这是存储操作最核心的性质：
    同一个操作跑两次，结果应该和跑一次一样。
    """
    p = tmp_path / "store.json"
    batch = [tx("星巴克", -38.0), tx("地铁", -6.0)]

    first = storage.append_new(batch, p)
    second = storage.append_new(batch, p)

    assert first == 2
    assert second == 0, f"第二次导入应该新增 0 条，实际新增 {second} 条"
    assert len(storage.load_all(p)) == 2


def test_append_new_keeps_identical_rows_in_same_batch(tmp_path):
    """⭐ 同一批里两行完全一样的，都保留。

    设计理由：同一个文件里两行完全相同，比"同一笔被导出两次"
             更可能是"真的发生了两次支付"。
             而且丢失真实交易比多记一笔更危险。

    注意：代价是无法区分"两笔真实支付"和"一笔被重复导出"。
         这个局限已记入 README。
    """
    p = tmp_path / "store.json"
    batch = [tx("星巴克", -38.0), tx("星巴克", -38.0)]

    added = storage.append_new(batch, p)

    assert added == 2, f"同一批里的相同行应都保留，实际收了 {added} 条"
    assert len(storage.load_all(p)) == 2


def test_append_new_still_idempotent_with_duplicates(tmp_path):
    """⭐ 即使有批内重复，重复导入整批也不应再新增。

    第一次全部收下，第二次全部跳过——
    幂等性靠"从库里读出来的 seen"保证。
    """
    p = tmp_path / "store.json"
    batch = [tx("星巴克", -38.0), tx("星巴克", -38.0)]

    first = storage.append_new(batch, p)
    second = storage.append_new(batch, p)

    assert first == 2
    assert second == 0, f"重复导入应新增 0，实际 {second}"
    assert len(storage.load_all(p)) == 2


def test_append_new_accumulates_across_calls(tmp_path):
    """分批追加，总数累加。"""
    p = tmp_path / "store.json"

    storage.append_new([tx("星巴克")], p)
    storage.append_new([tx("地铁")], p)
    storage.append_new([tx("房租")], p)

    assert len(storage.load_all(p)) == 3


def test_append_new_does_not_overwrite_existing(tmp_path):
    """⭐ 已存在的交易不被覆盖——手动改的分类要保住。

    场景：导入 1 月账单 → 手动把某笔分类从"餐饮"改成"娱乐"
         → 重新导入 1 月账单（比如想确认没漏数据）
         → 那笔的分类不能被冲回"餐饮"
    """
    p = tmp_path / "store.json"

    # 先存一笔
    storage.save_all([tx("星巴克", -38.0, category="餐饮")], p)

    # 模拟"手动改分类"
    loaded = storage.load_all(p)
    loaded[0].category = "娱乐"
    storage.save_all(loaded, p)

    # 再导入同一笔
    added = storage.append_new([tx("星巴克", -38.0, category="餐饮")], p)

    assert added == 0
    after = storage.load_all(p)
    assert len(after) == 1
    assert after[0].category == "娱乐", (
        f"手动改的分类被覆盖了，现在是 {after[0].category!r}"
    )


def test_append_new_different_transactions_both_kept(tmp_path):
    """反过来：真正不同的交易都要保留，不能误判为重复。"""
    p = tmp_path / "store.json"
    storage.append_new([tx("星巴克", -38.0)], p)
    added = storage.append_new([tx("地铁", -6.0)], p)

    assert added == 1
    assert len(storage.load_all(p)) == 2


# ============================================================
# 4. count_by_category
# ============================================================
def test_count_by_category(tmp_path):
    """统计各分类的条数。

    直接构造带 category 的交易存进去，避免依赖 config/categories.json
    （那样测试会因为配置变化而失效）。
    """
    p = tmp_path / "store.json"
    storage.save_all([
        tx("星巴克", category="餐饮"),
        tx("美团", category="餐饮"),
        tx("地铁", category="交通"),
        tx("未知", category="未分类"),
    ], p)

    counts = storage.count_by_category(p)

    assert isinstance(counts, dict)
    assert counts.get("餐饮") == 2
    assert counts.get("交通") == 1
    assert counts.get("未分类") == 1


def test_count_by_category_empty_store(tmp_path):
    """空库 → 空字典，不报错。"""
    assert storage.count_by_category(tmp_path / "空.json") == {}
