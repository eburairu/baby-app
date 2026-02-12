# AI開発者向けガイド

このファイルは、Claude、Gemini、その他のAI開発アシスタント向けの重要な情報をまとめたものです。

## プロジェクト概要

**Baby-App** - FastAPI + PostgreSQL + htmxによる総合育児管理アプリケーション

- **言語**: Python 3.10+
- **フレームワーク**: FastAPI 0.109.0
- **データベース**: PostgreSQL 16 (Docker)
- **ORM**: SQLAlchemy 2.0.25
- **テンプレート**: Jinja2 3.1.3
- **フロントエンド**: htmx + Tailwind CSS

## 重要な制約事項

### データベース

**PostgreSQL専用プロジェクトです。SQLiteは使用しません。**

- ✅ 開発環境: PostgreSQL (Docker, ポート5434)
- ✅ テスト環境: PostgreSQL (Docker, ポート5433)
- ✅ 本番環境: PostgreSQL (Render)
- ❌ SQLite: 完全に削除済み

### 必須環境変数

`.env`ファイルには以下の4つの変数が**必須**です:

```env
DATABASE_URL=postgresql://dev_user:dev_password@localhost:5434/baby_app_dev
SECRET_KEY=dev-secret-key
SYSTEM_INVITE_CODE=dev-invite-code  # ← これがないとPydanticエラーになる
ENVIRONMENT=development
```

### Python実行環境

**必ず仮想環境のPythonを使用してください:**

```bash
# ✅ 正しい
./venv/bin/python -m alembic upgrade head
./venv/bin/pytest -v
./venv/bin/uvicorn app.main:app --reload

# ❌ 間違い (システムPythonを使うとモジュールが見つからない)
python -m alembic upgrade head
pytest -v
uvicorn app.main:app --reload
```

## 開発ワークフロー

### 新機能開発の典型的な流れ

1. **現状確認**: `Read`ツールで関連ファイルを読む
2. **データベース起動**: `docker compose ps` で確認、必要なら `docker compose up -d`
3. **コード変更**: モデル → スキーマ → ルーター → テンプレートの順
4. **マイグレーション**: モデル変更時は `./venv/bin/python -m alembic revision --autogenerate -m "description"`
5. **テスト**: `docker compose -f docker-compose.test.yml up -d` → `./venv/bin/pytest -v`
6. **動作確認**: `./venv/bin/uvicorn app.main:app --reload`

### ファイル編集のベストプラクティス

#### Editツールの制限事項

日本語コメントで全角括弧「()」と半角括弧「()」が混在する場合、Editツールでの文字列マッチングが失敗することがあります。

**解決策**: Pythonスクリプトで直接編集

```bash
./venv/bin/python << 'EOF'
with open('path/to/file.py', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('old_string', 'new_string')
with open('path/to/file.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated successfully")
EOF
```

#### 編集前の確認事項

1. **必ずReadツールで事前確認**: 現在の状態を把握してから編集
2. **文字コードに注意**: `repr()` や `od -c` で正確な文字列を確認
3. **インデントを保持**: Pythonはインデントが重要

## よくある問題と解決策

### 問題1: `alembic: command not found`

**原因**: 仮想環境が有効化されていないか、システムPythonを使用している

**解決策**:
```bash
./venv/bin/python -m alembic upgrade head
```

### 問題2: `Field required [type=missing] - SYSTEM_INVITE_CODE`

**原因**: `.env`ファイルに`SYSTEM_INVITE_CODE`が設定されていない

**解決策**:
```bash
echo "SYSTEM_INVITE_CODE=dev-invite-code" >> .env
```

### 問題3: `No module named 'uvicorn'` / `No module named 'pytest'`

**原因**: 仮想環境に依存関係がインストールされていない

**解決策**:
```bash
./venv/bin/pip install -r requirements.txt
```

### 問題4: PostgreSQL接続エラー

**原因**: Dockerコンテナが起動していない

**解決策**:
```bash
docker compose ps                    # 状態確認
docker compose up -d                 # 起動
docker compose logs db               # ログ確認
```

### 問題5: ポート5432が既に使用されている

**原因**: ローカルでPostgreSQLが動作している

**解決策**: 既に対応済み。開発DBは5434ポートを使用しています。

## テスト実行

### 基本的なテスト実行

```bash
# 1. テスト用DB起動
docker compose -f docker-compose.test.yml up -d

# 2. テスト実行
./venv/bin/pytest -v

# 3. 特定のテストファイルのみ
./venv/bin/pytest tests/test_feeding_vulnerability.py -v

# 4. テスト用DB停止
docker compose -f docker-compose.test.yml down
```

### テストの注意点

- `tests/conftest.py` が自動的にPostgreSQL (localhost:5433) を使用
- 各テスト関数ごとにスキーマがリセットされる (`DROP SCHEMA public CASCADE`)
- SQLiteフォールバックは削除済み

## プロジェクト構造

```
baby-app/
├── app/
│   ├── main.py              # FastAPIアプリケーション
│   ├── config.py            # 環境変数管理 (Pydantic Settings)
│   ├── database.py          # SQLAlchemy設定 (PostgreSQL接続プール)
│   ├── dependencies.py      # 認証・権限チェック
│   ├── models/              # SQLAlchemyモデル
│   ├── schemas/             # Pydanticスキーマ
│   ├── routers/             # APIエンドポイント
│   ├── services/            # ビジネスロジック
│   ├── templates/           # Jinja2テンプレート
│   └── static/              # 静的ファイル (CSS, JS, 画像)
├── alembic/                 # データベースマイグレーション
│   ├── env.py              # Alembic設定 (PostgreSQL最適化済み)
│   └── versions/           # マイグレーションファイル
├── tests/                   # pytest テスト
│   └── conftest.py         # テスト設定 (PostgreSQL専用)
├── venv/                    # Python仮想環境
├── docker-compose.yml       # 開発用PostgreSQL (ポート5434)
├── docker-compose.test.yml  # テスト用PostgreSQL (ポート5433)
├── .env                     # 環境変数 (gitignore対象)
├── .env.example             # 環境変数テンプレート
├── requirements.txt         # Python依存関係
├── alembic.ini             # Alembic設定
├── README.md               # ユーザー向けドキュメント
└── CLAUDE.md               # このファイル (AI開発者向け)
```

## コミット前のチェックリスト

新機能追加やバグ修正後、以下を確認してください:

- [ ] PostgreSQLコンテナが起動している (`docker compose ps`)
- [ ] マイグレーションが適用されている (`./venv/bin/python -m alembic current`)
- [ ] テストがパスする (`./venv/bin/pytest -v`)
- [ ] 開発サーバーが正常に起動する (`./venv/bin/uvicorn app.main:app`)
- [ ] 新しいモデルを追加した場合、マイグレーションを作成
- [ ] 新しいルーターを追加した場合、`app/main.py`に登録

## デプロイ情報

- **プラットフォーム**: Render
- **Web Service**: FastAPIアプリケーション
- **Database**: Render Managed PostgreSQL
- **設定ファイル**: `render.yaml`
- **ブランチ**: `main` (自動デプロイ)

## 参考リンク

- [FastAPI公式ドキュメント](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0ドキュメント](https://docs.sqlalchemy.org/en/20/)
- [Alembic チュートリアル](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [htmx ドキュメント](https://htmx.org/docs/)

---

**最終更新**: 2026-02-12
**移行履歴**: SQLiteからPostgreSQL専用に移行完了
