# 授乳記録仕様書 (Feeding Records)

## データモデル
- `feeding_time`: 授乳時刻
- `feeding_type`: 母乳 (breast), ミルク (bottle), 混合 (mixed)
- `amount_ml`: 量 (ml)
- `duration_minutes`: 授乳時間（分）
- `notes`: メモ

## 機能
- 記録の作成、一覧表示、削除。
- 授乳タイプに応じた入力項目のバリデーション（例：ミルクの場合は量の入力が推奨される）。
