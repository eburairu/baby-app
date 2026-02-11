# 認証仕様書 (Authentication)

ユーザー認証とセッション管理の仕様を定義します。

## 機能概要
- ユーザー登録 (Signup)
- ログイン (Login) / ログアウト (Logout)
- セッション管理 (Cookie ベース)

## 技術詳細
- **パスワードハッシュ化**: `passlib` (bcrypt)
- **セッション管理**: カスタム Cookie (`session_id`)。
- **認証保護**: `AuthenticationRequired` 依存関係により、未認証ユーザーを `/login` へリダイレクト（htmx リクエストの場合は `HX-Redirect` ヘッダーを使用）。

## エンドポイント
- `GET /register`: 登録フォーム
- `POST /register`: ユーザー登録処理
- `GET /login`: ログインフォーム
- `POST /login`: ログイン処理
- `GET /logout`: ログアウト処理

## 制約
- ユーザー名は 3-50 文字。
- パスワードは 6-72 文字。
- ユーザー名はユニークである必要がある。
