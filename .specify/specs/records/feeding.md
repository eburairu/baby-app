# 授乳記録仕様書 (Feeding Records)

## データモデル
- `baby_id`: 対象の赤ちゃん ID (必須)
- `user_id`: 記録したユーザー ID (必須)
- `feeding_time`: 授乳時刻
- `feeding_type`: 母乳 (breast), ミルク (bottle), 混合 (mixed)
- `amount_ml`: 量 (ml)
- `duration_minutes`: 授乳時間（分）
- `notes`: メモ

## 機能
- 指定された赤ちゃんの授乳記録を作成、一覧表示、削除。
- 家族メンバーであれば誰でも閲覧・追加可能。
