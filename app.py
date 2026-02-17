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
        self._apply_theme()

        self._build_ui()

    def _set_today(self):
        from datetime import date
        t = date.today()
        self.current_year = t.year
        self.current_month = t.month

    def _apply_theme(self):
        # ダーク + ネオン（ゲームっぽい雰囲気）
        self.PAL = {
            "bg": "#0B1020",  # 濃紺
            "panel": "#121A33",  # パネル背景
            "text": "#E5E7EB",
            "muted": "#93A4B8",
            "accent": "#22D3EE",  # ネオンシアン
            "good": "#34D399",  # クリア
            "danger": "#FB7185",  # 日曜/注意
            "tile": "#18224A",
            "tile_hover": "#223066",
        }

        self.configure(bg=self.PAL["bg"])

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", font=("Segoe UI", 10))

        style.configure("TFrame", background=self.PAL["bg"])
        style.configure("Panel.TFrame", background=self.PAL["panel"])

        style.configure("TLabel", background=self.PAL["panel"], foreground=self.PAL["text"])
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), foreground=self.PAL["accent"])
        style.configure("Sub.TLabel", foreground=self.PAL["muted"])
        style.configure("Stat.TLabel", font=("Consolas", 11, "bold"), foreground=self.PAL["accent"])

        # ナビ用ボタン（前月/次月）
        style.configure(
            "Nav.TButton",
            padding=(10, 6),
            background=self.PAL["panel"],
            foreground=self.PAL["text"],
            borderwidth=0,
        )
        style.map(
            "Nav.TButton",
            foreground=[("active", self.PAL["accent"])],
        )

        # ご褒美エリアの枠
        style.configure("Panel.TLabelframe", background=self.PAL["panel"], foreground=self.PAL["text"])
        style.configure(
            "Panel.TLabelframe.Label",
            background=self.PAL["bg"],
            foreground=self.PAL["accent"],
            font=("Segoe UI", 10, "bold"),
        )

    def _build_ui(self):
        # ヘッダー（ゲーム風）
        head = ttk.Frame(self, style="Panel.TFrame", padding=(14, 12))
        head.pack(fill=tk.X, padx=12, pady=(12, 6))
        ttk.Label(head, text="百人一首", style="Title.TLabel").pack(anchor=tk.W)
        ttk.Label(
            head,
            text="読んだ日にチェック → 10首クリアごとにご褒美解放",
            style="Sub.TLabel",
        ).pack(anchor=tk.W)

        # HUD（読んだ首数 / ランク / 次のご褒美ゲージ）
        hud = ttk.Frame(self, style="Panel.TFrame", padding=(14, 10))
        hud.pack(fill=tk.X, padx=12, pady=(0, 8))

        ttk.Label(hud, text="読んだ首数:", style="Sub.TLabel").pack(side=tk.LEFT)
        self.total_var = tk.StringVar(value="0")
        ttk.Label(hud, textvariable=self.total_var, style="Stat.TLabel").pack(side=tk.LEFT, padx=(6, 16))

        self.rank_var = tk.StringVar(value="ランク: E")
        ttk.Label(hud, textvariable=self.rank_var, style="Sub.TLabel").pack(side=tk.LEFT)

        self.gauge = ttk.Progressbar(hud, length=170, mode="determinate", maximum=10)
        self.gauge.pack(side=tk.RIGHT)
        self.gauge_label_var = tk.StringVar(value="次のご褒美")
        ttk.Label(hud, textvariable=self.gauge_label_var, style="Sub.TLabel").pack(side=tk.RIGHT, padx=(0, 10))

        self._update_total()

        # カレンダー見出し（年月・前後）
        cal_header = ttk.Frame(self, style="Panel.TFrame", padding=(12, 10))
        cal_header.pack(fill=tk.X, padx=12, pady=(0, 6))
        self.prev_btn = ttk.Button(cal_header, text=" ‹ 前月 ", width=8, command=self._prev_month, style="Nav.TButton")
        self.prev_btn.pack(side=tk.LEFT)
        self.month_var = tk.StringVar()
        ttk.Label(cal_header, textvariable=self.month_var, style="Stat.TLabel").pack(side=tk.LEFT, expand=True)
        self.next_btn = ttk.Button(cal_header, text=" 次月 › ", width=8, command=self._next_month, style="Nav.TButton")
        self.next_btn.pack(side=tk.RIGHT)

        # 曜日ラベル
        week_f = ttk.Frame(self, style="Panel.TFrame", padding=(12, 6))
        week_f.pack(fill=tk.X, padx=12, pady=(0, 2))
        for i, w in enumerate(("日", "月", "火", "水", "木", "金", "土")):
            fg = self.PAL["text"]
            if i == 0:
                fg = self.PAL["danger"]
            elif i == 6:
                fg = self.PAL["accent"]
            lb = ttk.Label(week_f, text=w, width=4, anchor=tk.CENTER, foreground=fg)
            lb.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 日付グリッド（Frame + 後でボタン生成）
        self.cal_frame = ttk.Frame(self, style="Panel.TFrame", padding=(12, 10))
        self.cal_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 8))

        # ご褒美エリア
        reward_f = ttk.LabelFrame(self, text="ご褒美リスト", padding=(10, 8), style="Panel.TLabelframe")
        reward_f.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        self.reward_text = tk.Text(
            reward_f,
            height=12,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Consolas", 10),
            bg=self.PAL["panel"],
            fg=self.PAL["text"],
            insertbackground=self.PAL["accent"],
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
        )
        self.reward_text.pack(fill=tk.BOTH, expand=True)
        self.next_milestone_var = tk.StringVar()
        ttk.Label(reward_f, textvariable=self.next_milestone_var, style="Sub.TLabel").pack(anchor=tk.W)

        self._refresh_calendar()
        self._refresh_rewards()

    def _update_total(self):
        total = sum(self.records.values())
        self.total_var.set(str(total))

        # 10首ごとの進捗（ゲージ）
        cur = total % 10
        if hasattr(self, "gauge"):
            self.gauge["value"] = cur
            self.gauge_label_var.set(f"次のご褒美: {((total // 10) + 1) * 10}（あと {10 - cur}）")

        # ランク（例：10首ごとに昇格）
        ranks = ["E", "D", "C", "B", "A", "S", "SS", "SSS"]
        rank = ranks[min(total // 10, len(ranks) - 1)]
        if hasattr(self, "rank_var"):
            self.rank_var.set(f"ランク: {rank}")

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
            row = ttk.Frame(self.cal_frame, style="Panel.TFrame")
            row.pack(fill=tk.X, pady=2)
            for day, _weekday in week:
                cell = ttk.Frame(row, style="Panel.TFrame")
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
                tag = "クリア" if is_read else ""
                today_tag = "今日" if is_today else ""
                sub = today_tag or tag
                text = f"{day}\n{sub}" if sub else str(day)
                btn = tk.Button(
                    cell,
                    text=text,
                    command=lambda k=date_key: self._on_day_click(k),
                    relief=tk.FLAT,
                    bd=0,
                    cursor="hand2",
                    font=("Consolas", 10, "bold" if is_today else "normal"),
                    justify="center",
                    fg=self.PAL["text"],
                    bg=self.PAL["tile"],
                    activeforeground=self.PAL["accent"],
                    activebackground=self.PAL["tile_hover"],
                    highlightthickness=0,
                )
                # 曜日色（0=日, 6=土）
                if _weekday == 0:
                    btn.configure(fg=self.PAL["danger"])
                elif _weekday == 6:
                    btn.configure(fg=self.PAL["accent"])

                # クリアは緑で強調
                if is_read:
                    btn.configure(fg=self.PAL["good"])

                btn.pack(fill=tk.BOTH, expand=True, ipady=8)

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
