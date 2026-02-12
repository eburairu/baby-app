# スケジュール管理仕様書 (Schedule Management)

## 機能概要
- 育児に関する予定の作成と管理。
- 家族メンバー間での予定共有。

## データモデル
- `baby_id`: 対象の赤ちゃん ID (必須)
- `user_id`: 作成ユーザー ID (必須)
- `title`: 予定タイトル
- `description`: 詳細
- `scheduled_time`: 予定日時
- `is_completed`: 完了フラグ

## 操作
- 一覧表示、新規作成、修正、ステータス切り替え、削除。
