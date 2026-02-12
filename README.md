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
- 30秒ごとの自動更新

### 3. 記録機能
- **授乳記録**: 時間、種類（母乳/ミルク/混合）、量、持続時間
- **睡眠記録**: 開始/終了時刻、リアルタイムタイマー機能
- **おむつ交換**: ワンタップ記録、種類（おしっこ/うんち/両方）
- **成長記録**: 体重、身長、頭囲、時系列グラフ表示（Recharts）

### 4. 陣痛タイマー（重要機能）
- 大きな開始/終了ボタン
- リアルタイムタイマー表示（1秒更新）
- 間隔・持続時間の自動計算
- 直近1時間の統計サマリー
- 5秒ごとの記録一覧自動更新

### 5. スケジュール管理
- 予定の追加・管理
- ワンクリック完了マーク
- 期限切れアラート表示

### 6. ダークモード
- ライト/ダークテーマの切り替え
- next-themesで設定保存

## 技術スタック

### バックエンド
- **FastAPI** 0.109.0 - REST API
- **SQLAlchemy** 2.0.25 - ORM
- **Alembic** 1.13.1 - データベースマイグレーション
- **Pydantic** 2.5.3 - データバリデーション
- **PostgreSQL** 16 - データベース
- **bcrypt** - パスワードハッシュ化

### フロントエンド
- **Next.js** 16.1.6 (App Router) - React フレームワーク
- **React** 19 - UIライブラリ
- **TypeScript** 5 - 型安全性
- **Tailwind CSS** 4 - スタイリング
- **SWR** 2.4.0 - データフェッチ・キャッシュ・自動更新
- **Zustand** 5.0.2 - 状態管理
- **React Hook Form** 7.54.2 - フォーム管理
- **Zod** 3.24.1 - バリデーション
- **Recharts** 2.15.0 - グラフ表示
- **Radix UI** - アクセシブルなUIコンポーネント

### デプロイ
- **Render** - Web Service + PostgreSQL
- **Docker** - マルチステージビルド

## セットアップ

### 推奨: Docker Composeで起動（最も簡単）

```bash
# 1. リポジトリクローン
git clone <repo-url>
cd baby-app

# 2. すべてのサービス（DB + Backend + Frontend）を起動
docker compose up --build

# 3. ブラウザで http://localhost:3000 にアクセス
```

### 従来の方法: 手動セットアップ

#### 1. バックエンドのセットアップ

```bash
# 仮想環境作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt

# PostgreSQL起動 (Docker Compose)
docker compose up -d db

# 環境変数設定
cp .env.example .env
# .envファイルを編集
# DATABASE_URL=postgresql://dev_user:dev_password@localhost:5434/baby_app_dev
# SECRET_KEY=dev-secret-key
# SYSTEM_INVITE_CODE=dev-invite-code (必須)
# ENVIRONMENT=development

# データベースマイグレーション
./venv/bin/python -m alembic upgrade head

# バックエンドサーバー起動
./venv/bin/uvicorn app.main:app --reload
# → http://localhost:8000 で起動
```

#### 2. フロントエンドのセットアップ

```bash
cd frontend

# 依存関係インストール
npm install

# 環境変数設定
# .env.local を作成（オプション）
# NEXT_PUBLIC_API_URL=http://localhost:8000

# 開発サーバー起動
npm run dev
# → http://localhost:3000 で起動
```

### テスト実行

```bash
# 1. テスト用DB起動
docker compose -f docker-compose.test.yml up -d

# 2. バックエンドテスト実行
./venv/bin/pytest tests/ -v

# 3. 終了後、停止
docker compose -f docker-compose.test.yml down
```

## 本番デプロイ（Render）

### 前提条件
- GitHubリポジトリにコードがプッシュされている
- Render アカウント（無料プランでOK）
- PostgreSQL データベース（Render Managed PostgreSQL または Neon）

### デプロイ手順

#### 1. データベースの準備

**Option A: Render Managed PostgreSQL**
1. Renderダッシュボードで「New PostgreSQL」を作成
2. 接続文字列（Internal Database URL）をコピー

**Option B: Neon Serverless Postgres（推奨）**
1. [Neon](https://neon.tech) でプロジェクトを作成
2. 接続文字列をコピー

#### 2. Webサービスのデプロイ

1. **Renderダッシュボードで「New Blueprint」を選択**

2. **GitHubリポジトリを接続**
   - リポジトリを選択
   - `render.yaml` が自動検出される

3. **環境変数を設定**
   - `DATABASE_URL`: データベース接続文字列（手動設定）
   - `SECRET_KEY`: 自動生成される
   - `SYSTEM_INVITE_CODE`: 任意の招待コード（手動設定）
   - `ENVIRONMENT`: `production` （自動設定）
   - `PORT`: `8000` （自動設定）

4. **デプロイ開始**
   - 「Create Blueprint」をクリック
   - ビルドとデプロイが自動実行される
   - 完了後、URLが発行される（例: `https://baby-app.onrender.com`）

#### 3. デプロイ確認

```bash
# ヘルスチェック
curl https://baby-app.onrender.com/api/health
# → {"status":"healthy"}

# フロントエンド確認
curl https://baby-app.onrender.com/
# → Next.js のHTMLが返される
```

#### 4. 初回ユーザー登録

1. デプロイされたURLにアクセス
2. 「新規登録」をクリック
3. `SYSTEM_INVITE_CODE` を使用してユーザー登録
4. ログイン後、家族と赤ちゃんを登録

### デプロイ後の更新

```bash
# mainブランチにプッシュすると自動デプロイ
git push origin main

# または特定のブランチを接続している場合
git push origin <branch-name>
```

### トラブルシューティング

#### ビルドエラー
- Renderのログを確認: Build Logs タブ
- Dockerビルドが失敗する場合: ローカルで `docker build .` を実行して確認

#### データベース接続エラー
- `DATABASE_URL` が正しく設定されているか確認
- PostgreSQL のホスト名・ポート・認証情報を確認
- Neon の場合: `?sslmode=require` が付いているか確認

#### マイグレーションエラー
- Renderのログで `alembic upgrade head` のエラーを確認
- 必要に応じて手動でマイグレーションを実行

#### フロントエンドが表示されない
- `/api/health` エンドポイントが正常に応答するか確認
- `frontend/out` ディレクトリがビルド時に生成されているか確認
- Dockerビルドログで `npm run build` が成功しているか確認

## プロジェクト構造

```
baby-app/
├── app/                          # バックエンド（FastAPI）
│   ├── main.py                   # FastAPIエントリポイント
│   ├── config.py                 # 環境変数管理
│   ├── database.py               # SQLAlchemy設定
│   ├── dependencies.py           # 認証依存性注入
│   ├── middleware/               # ミドルウェア（CSRF）
│   ├── models/                   # SQLAlchemyモデル
│   ├── schemas/                  # Pydanticスキーマ
│   ├── routers/                  # JSON APIエンドポイント
│   ├── services/                 # ビジネスロジック
│   └── static/                   # 静的ファイル
├── frontend/                     # フロントエンド（Next.js）
│   ├── src/
│   │   ├── app/                  # App Router ページ
│   │   │   ├── (dashboard)/      # 認証後のページ
│   │   │   ├── login/            # ログインページ
│   │   │   └── register/         # 登録ページ
│   │   ├── components/           # Reactコンポーネント
│   │   │   └── ui/               # 共通UIコンポーネント
│   │   └── lib/                  # ユーティリティ
│   │       ├── api/              # APIクライアント
│   │       ├── stores/           # Zustand ストア
│   │       └── hooks/            # カスタムフック
│   ├── package.json
│   └── next.config.js
├── alembic/                      # DBマイグレーション
├── tests/                        # バックエンドテスト
├── docker-compose.yml            # 開発環境
├── docker-compose.test.yml       # テスト環境
├── Dockerfile                    # 本番環境（マルチステージ）
├── render.yaml                   # Renderデプロイ設定
├── requirements.txt              # Python依存関係
└── README.md
```

## API仕様

### 認証
- `POST /api/login` - ログイン
- `POST /api/register` - ユーザー登録
- `POST /api/logout` - ログアウト
- `GET /api/me` - 現在のユーザー情報

### 記録管理
- `GET /api/feedings` - 授乳記録一覧
- `POST /api/feedings` - 授乳記録作成
- `PUT /api/feedings/{id}` - 授乳記録更新
- `DELETE /api/feedings/{id}` - 授乳記録削除

- `GET /api/sleeps` - 睡眠記録一覧
- `POST /api/sleeps/start` - 睡眠開始
- `POST /api/sleeps/{id}/end` - 睡眠終了

- `GET /api/diapers` - おむつ記録一覧
- `POST /api/diapers/quick` - ワンタップ記録

- `GET /api/growths` - 成長記録一覧
- `POST /api/growths` - 成長記録作成

- `GET /api/contractions` - 陣痛記録一覧
- `POST /api/contractions/start` - 陣痛開始
- `POST /api/contractions/{id}/end` - 陣痛終了

- `GET /api/schedules` - スケジュール一覧
- `POST /api/schedules/{id}/toggle` - 完了トグル

### その他
- `GET /api/dashboard/data` - ダッシュボードデータ
- `GET /api/health` - ヘルスチェック

## セキュリティ

- パスワードはbcryptでハッシュ化
- セッションCookieは`httponly=True`、本番では`secure=True`
- CSRF保護ミドルウェア
- 環境変数でシークレット管理
- SQLAlchemy ORMでSQLインジェクション防止
- Pydanticバリデーション
- 権限ベースのアクセス制御

## ライセンス

MIT License

## 作者

Baby-App Development Team
