# -*- coding: utf-8 -*-
"""
百人一首 記録アプリ（Tkinter版）
ローカルだけで動作。CSVに保存し、10首ごとにご褒美を提案します。
"""
import calendar
import csv
from pathlib import Path

import tkinter as tk
from tkinter import ttk

# プロジェクトルートにCSVを保存（日付, 読んだ=1 / 読んでいない=0）
DATA_DIR = Path(__file__).resolve().parent
CSV_PATH = DATA_DIR / "hyakunin_isshu.csv"
CSV_HEADERS = ["date", "read"]

REWARDS = [
    "好きな和菓子をひとつ買う",
    "焼き鳥屋で一杯やる",
    "好きな本を一冊買える",
    "佐賀の岩盤浴に行ける",
    "好きな映画を映画館で観る",
    "好きなジャンクなお菓子を買える",
    "温かい飲み物を飲む",
    "ストレッチで体をほぐす",
    "誰かに一句送る",
    "明日の自分にメモを残す",
]


def ensure_csv():
    if not CSV_PATH.exists():
        CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            w.writeheader()


def load_records():
    ensure_csv()
    records = {}
    with open(CSV_PATH, "r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            if row.get("date") and row.get("read") in ("0", "1"):
                records[row["date"].strip()] = int(row["read"])
    return records


def save_records(records):
    ensure_csv()
    rows = [{"date": d, "read": v} for d, v in sorted(records.items())]
    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        w.writeheader()
        w.writerows(rows)


class HyakuninApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("百人一首 記録")
        self.resizable(True, True)
        self.minsize(420, 520)

        self.records = load_records()
        self.current_year = None
        self.current_month = None
        self._set_today()

        self._build_ui()

    def _set_today(self):
        from datetime import date
        t = date.today()
        self.current_year = t.year
        self.current_month = t.month

    def _build_ui(self):
        # ヘッダー
        head = ttk.Frame(self, padding=(12, 10))
        head.pack(fill=tk.X)
        ttk.Label(head, text="百人一首 記録", font=("", 14, "bold")).pack(anchor=tk.W)
        ttk.Label(head, text="読んだ日にチェック → 10首ごとにご褒美", foreground="gray").pack(anchor=tk.W)

        # 読んだ日数
        stat_f = ttk.Frame(self, padding=(12, 4))
        stat_f.pack(fill=tk.X)
        ttk.Label(stat_f, text="読んだ日（首）：").pack(side=tk.LEFT)
        self.total_var = tk.StringVar(value="0")
        self.total_label = ttk.Label(stat_f, textvariable=self.total_var, font=("", 12, "bold"))
        self.total_label.pack(side=tk.LEFT, padx=(4, 0))
        self._update_total()

        # カレンダー見出し（年月・前後）
        cal_header = ttk.Frame(self, padding=(12, 8))
        cal_header.pack(fill=tk.X)
        self.prev_btn = ttk.Button(cal_header, text=" ‹ 前月 ", width=8, command=self._prev_month)
        self.prev_btn.pack(side=tk.LEFT)
        self.month_var = tk.StringVar()
        ttk.Label(cal_header, textvariable=self.month_var, font=("", 11, "bold")).pack(side=tk.LEFT, expand=True)
        self.next_btn = ttk.Button(cal_header, text=" 次月 › ", width=8, command=self._next_month)
        self.next_btn.pack(side=tk.RIGHT)

        # 曜日ラベル
        week_f = ttk.Frame(self, padding=(12, 0))
        week_f.pack(fill=tk.X)
        for w in ("日", "月", "火", "水", "木", "金", "土"):
            lb = ttk.Label(week_f, text=w, width=4, anchor=tk.CENTER)
            lb.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 日付グリッド（Frame + 後でボタン生成）
        self.cal_frame = ttk.Frame(self, padding=(12, 4))
        self.cal_frame.pack(fill=tk.BOTH, expand=True)

        # ご褒美エリア
        reward_f = ttk.LabelFrame(self, text="ご褒美リスト", padding=(10, 8))
        reward_f.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
        self.reward_text = tk.Text(reward_f, height=12, wrap=tk.WORD, state=tk.DISABLED, font=("", 10))
        self.reward_text.pack(fill=tk.BOTH, expand=True)
        self.next_milestone_var = tk.StringVar()
        ttk.Label(reward_f, textvariable=self.next_milestone_var, foreground="gray").pack(anchor=tk.W)

        self._refresh_calendar()
        self._refresh_rewards()

    def _update_total(self):
        total = sum(self.records.values())
        self.total_var.set(str(total))

    def _date_key(self, year, month, day):
        return f"{year}-{month:02d}-{day:02d}"

    def _on_day_click(self, date_key):
        if date_key not in self.records:
            self.records[date_key] = 0
        self.records[date_key] = 1 if self.records[date_key] == 0 else 0
        save_records(self.records)
        self._update_total()
        self._refresh_calendar()
        self._refresh_rewards()

    def _prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self._refresh_calendar()

    def _next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self._refresh_calendar()

    def _refresh_calendar(self):
        self.month_var.set(f"{self.current_year}年 {self.current_month}月")

        for w in self.cal_frame.winfo_children():
            w.destroy()

        cal = calendar.Calendar(calendar.SUNDAY)
        weeks = cal.monthdays2calendar(self.current_year, self.current_month)
        from datetime import date
        today = date.today()

        for week in weeks:
            row = ttk.Frame(self.cal_frame)
            row.pack(fill=tk.X, pady=2)
            for day, _weekday in week:
                cell = ttk.Frame(row)
                cell.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=1)
                if day == 0:
                    ttk.Label(cell, text="").pack(fill=tk.BOTH, expand=True)
                    continue
                date_key = self._date_key(self.current_year, self.current_month, day)
                is_read = self.records.get(date_key, 0) == 1
                is_today = (
                    today.year == self.current_year
                    and today.month == self.current_month
                    and today.day == day
                )
                btn = tk.Button(
                    cell,
                    text=str(day),
                    command=lambda k=date_key: self._on_day_click(k),
                    relief=tk.RAISED,
                    bd=1,
                    cursor="hand2",
                    font=("", 10),
                )
                if is_read:
                    btn.configure(bg="#c8e6c9", activebackground="#a5d6a7")  # 読んだ
                else:
                    btn.configure(bg="#f5f5f5", activebackground="#eeeeee")
                if is_today:
                    btn.configure(relief=tk.SOLID, bd=2, highlightbackground="#8b4512")
                btn.pack(fill=tk.BOTH, expand=True)

    def _refresh_rewards(self):
        total = sum(self.records.values())
        next_n = ((total // 10) + 1) * 10
        remaining = next_n - total

        self.reward_text.configure(state=tk.NORMAL)
        self.reward_text.delete("1.0", tk.END)
        if total >= 10:
            self.reward_text.insert(tk.END, "\n".join(REWARDS))
            if total >= 100:
                self.next_milestone_var.set(f"おめでとうございます！{total}首達成です。")
            else:
                self.next_milestone_var.set(f"次は {next_n}首 でまたご褒美をどうぞ。（あと {remaining} 首・現在 {total} 首）")
        else:
            self.next_milestone_var.set(f"あと {remaining}首 でご褒美リストが表示されます")
        self.reward_text.configure(state=tk.DISABLED)


def main():
    ensure_csv()
    app = HyakuninApp()
    app.mainloop()


if __name__ == "__main__":
    main()
