# システム設計書 (System Design)

Baby-App の全体アーキテクチャと技術スタックを定義します。

## 概要
Baby-App は、家族単位で赤ちゃんの育児記録（授乳、睡眠、おむつ、成長、陣痛、スケジュール）を共同管理するための Web アプリケーションです。
招待制を採用し、セキュアな家族共有環境を提供します。

## 階層構造 (Data Hierarchy)
1. **Family (家族)**: 管理の最上位単位。名前と招待コードを持つ。
2. **User (ユーザー)**: 家族に属するメンバー。'admin' (管理者) または 'member' (一般) の権限を持つ。
3. **Baby (赤ちゃん)**: 家族に紐付く記録対象。1つの家族に複数の赤ちゃんを登録可能。
4. **Records (記録)**: 各赤ちゃんに紐付く具体的なデータ（授乳、睡眠など）。作成者情報も保持する。

## 技術スタック
- **Backend**: FastAPI (Python 3.10+)
- **ORM**: SQLAlchemy 2.0
- **Migration**: Alembic
- **Template Engine**: Jinja2
- **Frontend Interactivity**: htmx
- **CSS Framework**: Tailwind CSS
- **Database**: PostgreSQL (Neon Serverless)
- **Deployment**: Render

## CI/CD & リリースプロセス
- **Version Control**: GitHub
- **Automation**: GitHub Actions
- **Versioning Strategy**: Semantic Versioning (SemVer)
- **Release Tool**: python-semantic-release
  - コミットメッセージに基づき自動でバージョンアップ (Major/Minor/Patch)
  - CHANGELOG.md の自動生成
  - GitHub Releases の作成
  - Git Tag のプッシュ

## ディレクトリ構造
```
baby-app/
├── app/
│   ├── main.py            # エントリポイント
│   ├── models/            # SQLAlchemy モデル (User, Family, Baby, etc.)
│   ├── schemas/           # Pydantic スキーマ
│   ├── routers/           # ルート定義 (auth, family, baby, records, etc.)
│   ├── services/          # ビジネスロジック
│   ├── templates/         # Jinja2 テンプレート
│   └── static/            # 静的ファイル (CSS/JS)
├── alembic/               # データベースマイグレーション
├── tests/                 # テストコード
├── .agents/               # AI エージェント用スキル・リファレンス
└── .specify/specs/        # SDD 仕様書
```

## 権限管理
- **Admin (管理者)**: 家族設定の変更、招待コードの管理、メンバーの管理、赤ちゃんの追加・編集・削除が可能。
- **Member (一般メンバー)**: 記録の閲覧、追加、自身の記録の編集・削除が可能。
