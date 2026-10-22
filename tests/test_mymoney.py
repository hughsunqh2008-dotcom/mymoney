"""test_mymoney.py —— 模块 8（命令行入口）的测试

全部通过 `mymoney.main([...])` 走完整链路，用**返回值**当退出码，不启动子进程。
真实数据目录被隔离到 tmp_path，不会碰项目里的 data/ 和 out/。

⚠️ 一个必须知道的坑：
    `src/storage.py` 里是 `def load_all(path=DEFAULT_STORE)` —— 默认参数在 **def 那一刻**
    就固化了，所以 `monkeypatch.setattr(storage, "DEFAULT_STORE", ...)` 对它**无效**。
    这里改用 `monkeypatch.chdir(tmp_path)`：DEFAULT_STORE 是**相对路径**
    `data/transactions.json`，chdir 之后自然落到 tmp_path/data/ 下面。

退出码约定：
    0 成功 / 1 数据或文件错 / 2 用法错
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import mymoney

ROOT = Path(__file__).resolve().parent.parent
CSV_JAN = str(ROOT / "data" / "2026-01.csv")       # 14 行，全部解析成功
CSV_FEB = str(ROOT / "data" / "2026-02.csv")       # 14 行，13 成功 1 失败


@pytest.fixture()
def cli(monkeypatch, tmp_path):
    """把数据目录、输出目录都挪到 tmp_path，并把 cwd 也切过去。"""
    monkeypatch.setattr(mymoney, "DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(mymoney, "OUT_DIR", tmp_path / "out")
    monkeypatch.chdir(tmp_path)          # ← 关键：storage 的相对路径靠 cwd 解析
    return tmp_path


def run(argv):
    """跑一次 main 并把 (退出码, stdout, stderr) 拿回来。"""
    return mymoney.main(argv)


# ============================================================
# 参数解析层（argparse 自己抛 SystemExit）
# ============================================================
def test_help_exits_zero(capsys):
    with pytest.raises(SystemExit) as exc:
        mymoney.main(["--help"])
    assert exc.value.code == 0
    assert "usage" in capsys.readouterr().out.lower()


def test_version_exits_zero(capsys):
    with pytest.raises(SystemExit) as exc:
        mymoney.main(["--version"])
    assert exc.value.code == 0
    assert "0.1.0" in capsys.readouterr().out


def test_no_args_prints_help(capsys):
    assert run([]) == 0
    assert "usage" in capsys.readouterr().out.lower()


def test_unknown_option_exits_two():
    with pytest.raises(SystemExit) as exc:
        mymoney.main(["--nope"])
    assert exc.value.code == 2


# ============================================================
# --import-file
# ============================================================
def test_import_creates_store(cli, capsys):
    assert run(["--import-file", CSV_JAN]) == 0
    assert (cli / "data" / "transactions.json").exists()
    assert "新增 14" in capsys.readouterr().out


def test_import_is_idempotent(cli, capsys):
    """同一个文件导两次，第二次新增 0。"""
    assert run(["--import-file", CSV_JAN]) == 0
    capsys.readouterr()
    assert run(["--import-file", CSV_JAN]) == 0
    assert "新增 0" in capsys.readouterr().out


def test_import_partial_failure_still_zero(cli):
    """2026-02.csv 是 13 成功 1 失败 —— 部分成功按成功算（有可用结果）。"""
    assert run(["--import-file", CSV_FEB]) == 0


def test_import_missing_file_returns_one(cli):
    assert run(["--import-file", "根本没有的.csv"]) == 1


def test_import_all_bad_returns_one(cli, tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("日期,摘要,金额\n2026-01-01,x,abc\n", encoding="utf-8")
    assert run(["--import-file", str(bad)]) == 1


# ============================================================
# --report
# ============================================================
def test_report_after_import(cli, capsys):
    run(["--import-file", CSV_JAN])
    capsys.readouterr()
    assert run(["--report"]) == 0
    out = capsys.readouterr().out
    assert "账目报告" in out
    assert "18,500.00" in out


def test_report_empty_store_returns_one(cli, capsys):
    """库里没数据时不是成功——没有可展示的内容。"""
    assert run(["--report"]) == 1
    assert capsys.readouterr().err.strip()      # 至少要有句话说清楚


def test_report_month_filter(cli, capsys):
    run(["--import-file", CSV_JAN])
    run(["--import-file", CSV_FEB])
    capsys.readouterr()
    assert run(["--report", "--month", "2026-01"]) == 0
    out = capsys.readouterr().out
    assert "18,500.00" in out
    assert "37,000.00" not in out               # 那是 2 月才有的合计


# ============================================================
# --top
# ============================================================
def test_top_prints_only_n_lines(cli, capsys):
    run(["--import-file", CSV_JAN])
    capsys.readouterr()
    assert run(["--top", "3"]) == 0
    lines = [line for line in capsys.readouterr().out.splitlines() if line.strip()]
    assert len(lines) == 3, f"应该只打印 3 行，实际 {len(lines)} 行"


def test_top_returns_largest_first(cli, capsys):
    run(["--import-file", CSV_JAN])
    capsys.readouterr()
    run(["--top", "2"])
    out = capsys.readouterr().out
    assert "房租" in out and "高铁票" in out


def test_top_zero_rejected(cli):
    """--top 0 是用法错误，不能静默什么都不做。"""
    assert run(["--top", "0"]) == 2


# ============================================================
# --export
# ============================================================
def test_export_bad_suffix_returns_two(cli, capsys):
    assert run(["--export", "x.txt"]) == 2
    assert capsys.readouterr().err.strip()


def test_export_json(cli):
    run(["--import-file", CSV_JAN])
    target = cli / "out" / "r.json"
    assert run(["--export", str(target)]) == 0
    data = json.loads(target.read_text(encoding="utf-8"))
    assert set(data) >= {"summary", "by_category", "by_month", "top_expenses"}
    assert data["summary"]["笔数"] == 14


def test_export_csv_has_bom(cli):
    run(["--import-file", CSV_JAN])
    target = cli / "out" / "r.csv"
    assert run(["--export", str(target)]) == 0
    assert target.read_bytes().startswith(b"\xef\xbb\xbf")


# ============================================================
# --plot
# ============================================================
def test_plot_creates_png(cli):
    run(["--import-file", CSV_JAN])
    assert run(["--plot"]) == 0
    png = cli / "out" / "trend.png"
    assert png.exists()
    assert png.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
