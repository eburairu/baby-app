# 修正タスクリスト (Fix Tasks)

## フェーズ 1: 重大なロジックの修正 (High Priority)

- [ ] **TASK-001: 統計計算サービスのバグ修正**
    - `StatisticsService.get_sleep_stats` で継続中の睡眠を考慮するよう修正。
    - `ContractionService.get_statistics` で現在進行中の陣痛を考慮するよう修正。
- [ ] **TASK-002: ユニットテストの拡充**
    - `StatisticsService` および `ContractionService` のテストコードを作成し、計算ロジックの正確性を担保する。

## フェーズ 2: バリデーションと堅牢性の向上 (Medium Priority)

- [ ] **TASK-003: Pydantic スキーマによる Form バリデーションの統一**
    - 各ルーターの `POST` / `PATCH` エンドポイントを、Pydantic モデルを使用したバリデーションに移行する。
- [ ] **TASK-004: 削除確認機能の実装**
    - 全ての削除ボタンに `hx-confirm` を追加し、誤削除を防止する。

## フェーズ 3: UX/UI の改善 (Low Priority)

- [ ] **TASK-005: htmx エラーハンドリングとトースト通知の導入**
    - エラー発生時に適切なメッセージをトーストで表示する仕組みをフロントエンドとバックエンドに導入する。
- [ ] **TASK-006: ローディングインジケーターの追加**
    - ダッシュボードの更新等に `hx-indicator` を追加する。
