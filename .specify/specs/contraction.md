# 陣痛タイマー仕様書 (Contraction Timer)

## 機能概要
- 陣痛の開始と終了を記録し、持続時間と間隔を自動計算する。
- 直近 1 時間の統計を表示し、病院へ連絡する目安とする。

## ロジック (`ContractionService`)
- **持続時間 (Duration)**: `end_time - start_time`
- **間隔 (Interval)**: `現在の start_time - 前回の end_time`
- **統計 (Statistics)**: 直近 1 時間の平均持続時間と平均間隔。

## 操作
- **開始**: `POST /contractions/start`
- **終了**: `POST /contractions/{id}/end`
- **削除**: `DELETE /contractions/{id}`
