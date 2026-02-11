# Baby-App - 総合育児管理アプリケーション

育児中の保護者が赤ちゃんの日々のケア記録を簡単に管理できる総合育児管理Webアプリケーションです。

## 主要機能

### 1. 認証システム
- ユーザー名 + パスワードのシンプルな認証
- bcryptによる安全なパスワードハッシュ化
- Cookieベースセッション管理

### 2. ダッシュボード
- 直近7日間の統計表示（授乳回数、平均睡眠時間、おむつ交換回数）
- 各カテゴリの最新記録表示
- htmxによる自動更新

### 3. 記録機能
- **授乳記録**: 時間、種類（母乳/ミルク/混合）、量、持続時間
- **睡眠記録**: 開始/終了時刻、タイマー機能
- **おむつ交換**: ワンタップ記録、種類（おしっこ/うんち/両方）
- **成長記録**: 体重、身長、頭囲、時系列グラフ表示

### 4. 陣痛タイマー（重要機能）
- 大きな開始/終了ボタン
- リアルタイムタイマー表示
- 間隔・持続時間の自動計算
- 直近1時間の統計サマリー

### 5. スケジュール管理
- 予定の追加・管理
- ワンクリック完了マーク

### 6. ダークモード
- ライト/ダークテーマの切り替え
- localStorageで設定保存

## 技術スタック

- **バックエンド**: FastAPI 0.109.0
- **テンプレートエンジン**: Jinja2 3.1.3
- **フロントエンド**: htmx 1.9.10 + Tailwind CSS (CDN)
- **ORM**: SQLAlchemy 2.0.25
- **バリデーション**: Pydantic 2.5.3
- **DB**: PostgreSQL
- **認証**: Cookieベースセッション + passlib/bcrypt
- **デプロイ**: Render (Web Service + PostgreSQL)

## セットアップ

### 開発環境

1. 仮想環境作成:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. 依存関係インストール:
```bash
pip install -r requirements.txt
```

3. PostgreSQL起動:
ローカルにPostgreSQLサーバーが必要です。Docker Composeを使う場合は以下:
```bash
docker compose -f docker-compose.test.yml up -d
```
※ ポート5433で起動しますが、`.env` の設定に合わせてください。

4. 環境変数設定:
```bash
cp .env.example .env
# .envファイルを編集してPostgreSQL接続情報を設定
```

4. データベースマイグレーション:
```bash
alembic upgrade head
```

5. 開発サーバー起動:
```bash
uvicorn app.main:app --reload
```

6. ブラウザで http://localhost:8000 にアクセス

### テスト実行

テストはDocker Composeで起動したPostgreSQLコンテナ対して実行されます。

1. テスト用DB起動:
```bash
docker compose -f docker-compose.test.yml up -d
```

2. テスト実行:
```bash
# conftest.py が自動的に localhost:5433 のDBを使用します
pytest tests/ -v
```

3. 終了後、停止:
```bash
docker compose -f docker-compose.test.yml down
```

### Renderデプロイ

1. GitHubリポジトリにプッシュ
2. Renderダッシュボードで「New Blueprint」を選択
3. リポジトリを接続
4. `render.yaml`が自動検出される
5. デプロイ開始

## プロジェクト構造

```
baby-app/
├── app/
│   ├── main.py                    # FastAPIエントリポイント
│   ├── config.py                  # 環境変数管理
│   ├── database.py                # SQLAlchemy設定
│   ├── dependencies.py            # 認証依存性注入
│   ├── models/                    # SQLAlchemyモデル
│   ├── schemas/                   # Pydanticスキーマ
│   ├── routers/                   # APIエンドポイント
│   ├── services/                  # ビジネスロジック
│   ├── templates/                 # Jinja2テンプレート
│   └── static/                    # 静的ファイル
├── alembic/                       # DBマイグレーション
├── tests/                         # テストコード
├── requirements.txt
├── alembic.ini
├── render.yaml                    # Renderデプロイ設定
└── README.md
```

## 主要なファイル

### モデル
- `app/models/user.py` - ユーザーモデル
- `app/models/feeding.py` - 授乳記録
- `app/models/sleep.py` - 睡眠記録
- `app/models/diaper.py` - おむつ交換記録
- `app/models/growth.py` - 成長記録
- `app/models/contraction.py` - 陣痛記録
- `app/models/schedule.py` - スケジュール管理

### サービス
- `app/services/auth_service.py` - 認証ロジック
- `app/services/statistics_service.py` - ダッシュボード統計
- `app/services/contraction_service.py` - 陣痛タイマー計算

### ルーター
- `app/routers/auth.py` - 認証（ログイン/登録/ログアウト）
- `app/routers/dashboard.py` - ダッシュボード
- `app/routers/feeding.py` - 授乳記録CRUD
- `app/routers/sleep.py` - 睡眠記録CRUD
- `app/routers/diaper.py` - おむつ記録CRUD
- `app/routers/growth.py` - 成長記録CRUD
- `app/routers/contraction.py` - 陣痛タイマー
- `app/routers/schedule.py` - スケジュール管理

## セキュリティ

- パスワードはbcryptでハッシュ化
- セッションCookieは`httponly=True`（本番では`secure=True`も）
- 環境変数でシークレット管理
- SQLAlchemy ORMでSQLインジェクション防止
- Pydanticバリデーション
- Jinja2自動エスケープ
- 詳細な開発ルールやワークフローについては [CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。

## 開発に参加する
## ライセンス

MIT License

## 作者

Baby-App Development Team
