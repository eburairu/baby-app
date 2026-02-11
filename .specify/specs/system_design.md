# システム設計書 (System Design)

Baby-App の全体アーキテクチャと技術スタックを定義します。

## 概要
Baby-App は、育児記録（授乳、睡眠、おむつ、成長、陣痛、スケジュール）を管理するためのフルスタック Web アプリケーションです。

## 技術スタック
- **Backend**: FastAPI (Python 3.10+)
- **ORM**: SQLAlchemy 2.0
- **Migration**: Alembic
- **Template Engine**: Jinja2
- **Frontend Interactivity**: htmx
- **CSS Framework**: Tailwind CSS
- **Database**: PostgreSQL (Neon Serverless)
- **Deployment**: Render

## ディレクトリ構造
```
baby-app/
├── app/
│   ├── main.py            # エントリポイント
│   ├── models/            # SQLAlchemy モデル
│   ├── schemas/           # Pydantic スキーマ
│   ├── routers/           # ルート定義
│   ├── services/          # ビジネスロジック
│   ├── templates/         # Jinja2 テンプレート
│   └── static/            # 静的ファイル (CSS/JS)
├── alembic/               # データベースマイグレーション
├── tests/                 # テストコード
├── .agents/               # AI エージェント用スキル・リファレンス
└── .specify/specs/        # SDD 仕様書（本ドキュメント等）
```

## データフロー
1. クライアントがブラウザからリクエストを送信。
2. FastAPI ルーターがリクエストを受信。
3. 必要に応じて `AuthenticationRequired` 依存関係により認証をチェック。
4. サービス層 (`app/services/`) を呼び出してビジネスロジックを実行。
5. SQLAlchemy モデルを介して PostgreSQL と対話。
6. Jinja2 テンプレートをレンダリングし、HTML を返却。
7. フロントエンドの動的な更新（削除、開始、停止等）は htmx を使用して部分的な HTML を交換。
