# cursor_training

## 百人一首 記録アプリ

百人一首を「一首読んだ日」にチェックし、10首ごとにご褒美リストを表示するアプリです。

### 機能

- **カレンダー**: 読んだ日をクリックでチェック（✓）。もう一度クリックで解除。
- **永続化**: データは `hyakunin_isshu.csv` に保存（日付, 1=読んだ / 0=読んでいない）。アプリを閉じても消えません。
- **ご褒美**: 10首・20首・30首…の節目で、素敵なご褒美のリストを表示。

### 動かし方

Tkinter でローカルウィンドウが開きます（ブラウザは不要です）。

```powershell
.\.venv\Scripts\Activate.ps1
python app.py
```

### テストの実行

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pytest
```

### CSV 形式

`hyakunin_isshu.csv` の例:

```csv
date,read
2025-02-17,1
2025-02-18,0
```
