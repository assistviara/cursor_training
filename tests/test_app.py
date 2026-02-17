# -*- coding: utf-8 -*-
"""app.py のテスト（CSV永続化・日付キー・定数）"""
import csv
from pathlib import Path

import pytest

# テスト用に CSV_PATH を上書きするため app を import 前に準備
import app as app_module


@pytest.fixture(autouse=True)
def use_tmp_csv(tmp_path, monkeypatch):
    """全テストで本物の hyakunin_isshu.csv の代わりに一時ファイルを使う"""
    csv_path = tmp_path / "hyakunin_isshu.csv"
    monkeypatch.setattr(app_module, "CSV_PATH", csv_path)
    yield csv_path


def test_ensure_csv_creates_file_with_headers(use_tmp_csv):
    """ensure_csv は CSV が無いときにヘッダー付きで作成する"""
    assert not use_tmp_csv.exists()
    app_module.ensure_csv()
    assert use_tmp_csv.exists()
    with open(use_tmp_csv, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == ["date", "read"]


def test_load_records_empty_returns_empty_dict():
    """空の CSV なら load_records は空の辞書を返す"""
    app_module.ensure_csv()
    assert app_module.load_records() == {}


def test_load_records_parses_valid_rows(use_tmp_csv):
    """有効な行だけ読み込み、date -> 0|1 の辞書を返す"""
    with open(use_tmp_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "read"])
        w.writeheader()
        w.writerow({"date": "2025-02-17", "read": "1"})
        w.writerow({"date": "2025-02-18", "read": "0"})
    got = app_module.load_records()
    assert got == {"2025-02-17": 1, "2025-02-18": 0}


def test_load_records_skips_invalid_read_value(use_tmp_csv):
    """read が 0/1 以外の行は無視する"""
    with open(use_tmp_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "read"])
        w.writeheader()
        w.writerow({"date": "2025-02-17", "read": "1"})
        w.writerow({"date": "2025-02-18", "read": "2"})
        w.writerow({"date": "2025-02-19", "read": ""})
    got = app_module.load_records()
    assert got == {"2025-02-17": 1}


def test_load_records_skips_empty_date(use_tmp_csv):
    """date が空の行は無視する"""
    with open(use_tmp_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "read"])
        w.writeheader()
        w.writerow({"date": "", "read": "1"})
        w.writerow({"date": "2025-02-17", "read": "1"})
    got = app_module.load_records()
    assert got == {"2025-02-17": 1}


def test_save_records_roundtrip():
    """save_records した内容を load_records で再読み込みできる"""
    records = {"2025-03-01": 1, "2025-02-15": 0, "2025-02-20": 1}
    app_module.save_records(records)
    assert app_module.load_records() == records


def test_save_records_writes_sorted_by_date(use_tmp_csv):
    """save_records は日付でソートして書き込む"""
    app_module.save_records({"2025-03-01": 1, "2025-02-15": 0})
    with open(use_tmp_csv, "r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    dates = [r["date"] for r in rows]
    assert dates == ["2025-02-15", "2025-03-01"]


def test_rewards_has_ten_items():
    """ご褒美リストは10件ある"""
    assert len(app_module.REWARDS) == 10
    assert all(isinstance(r, str) and len(r) > 0 for r in app_module.REWARDS)
