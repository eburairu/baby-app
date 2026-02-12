# おむつ交換記録仕様書 (Diaper Records)

## データモデル
- `baby_id`: 対象の赤ちゃん ID (必須)
- `user_id`: 記録したユーザー ID (必須)
- `change_time`: 交換時刻
- `diaper_type`: おしっこ (wet), うんち (dirty), 両方 (both)
- `notes`: メモ

## 機能
- 指定された赤ちゃんの交換記録をワンタップで作成。
- 家族メンバーでの一覧共有。
- 記録の修正および削除。
