# 成長記録仕様書 (Growth Records)

## データモデル
- `baby_id`: 対象の赤ちゃん ID (必須)
- `user_id`: 記録したユーザー ID (必須)
- `measurement_date`: 測定日
- `weight_kg`: 体重 (kg)
- `height_cm`: 身長 (cm)
- `head_circumference_cm`: 頭囲 (cm)
- `notes`: メモ

## 機能
- 指定された赤ちゃんの成長記録を共有管理。
- 記録の修正および削除。
- 最新値のダッシュボード表示。
