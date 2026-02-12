# Baby-App デプロイガイド

このドキュメントは、Baby-AppをRenderにデプロイする手順を詳しく説明します。

## 前提条件チェックリスト

デプロイ前に、以下を確認してください：

- [ ] GitHubリポジトリにコードがプッシュされている
- [ ] `main` ブランチが最新の状態
- [ ] ローカルでDocker Composeビルドが成功する
- [ ] ローカルでアプリケーションが正常に動作する
- [ ] Renderアカウントを作成済み（無料プランでOK）
- [ ] データベース接続情報を準備済み（Neon または Render PostgreSQL）

## Step 1: データベースの準備

### Option A: Neon Serverless Postgres（推奨）

**メリット:**
- 無料枠が大きい（500MB + 192時間のコンピュート）
- 自動スケーリング
- バックアップ・リストア機能
- 高速

**セットアップ手順:**

1. [Neon](https://neon.tech) にアクセスしてサインアップ

2. 新しいプロジェクトを作成:
   - Project name: `baby-app-production`
   - Region: 最寄りのリージョン（例: Oregon (US West)）
   - Postgres version: 16

3. 接続文字列をコピー:
   ```
   postgresql://[user]:[password]@[host]/[database]?sslmode=require
   ```
   - **重要**: `?sslmode=require` が付いていることを確認

4. データベース名を確認（デフォルトは `neondb`）

### Option B: Render Managed PostgreSQL

**セットアップ手順:**

1. Renderダッシュボードで「New PostgreSQL」をクリック

2. 設定:
   - Name: `baby-app-db`
   - Region: Oregon (Free tier)
   - Database: `baby_app_prod`
   - User: `baby_app_user`

3. 「Create Database」をクリック

4. 作成後、「Internal Database URL」をコピー:
   ```
   postgresql://baby_app_user:[password]@[host]/baby_app_prod
   ```

## Step 2: Webサービスのデプロイ

### 2.1 Blueprintでデプロイ（推奨）

1. **Renderダッシュボードで「New」 → 「Blueprint」を選択**

2. **GitHubリポジトリを接続**:
   - 「Connect GitHub」をクリック
   - リポジトリを検索: `baby-app`
   - リポジトリを選択
   - ブランチ: `main`

3. **Blueprint検出**:
   - `render.yaml` が自動検出される
   - サービス名: `baby-app` が表示される

4. **環境変数を設定**:
   以下の環境変数を手動で設定（Sync: Noになっているもの）:

   | Key | Value | 例 |
   |-----|-------|-----|
   | `DATABASE_URL` | データベース接続文字列 | `postgresql://user:pass@host/db?sslmode=require` |
   | `SYSTEM_INVITE_CODE` | 任意の招待コード | `my-secure-invite-code-2024` |

   自動生成される環境変数:
   - `SECRET_KEY`: 自動生成される（変更不要）
   - `ENVIRONMENT`: `production` が設定される
   - `PORT`: `8000` が設定される

5. **「Create Blueprint」をクリック**

6. **ビルド＆デプロイを待つ**:
   - ビルド時間: 約5-10分
   - ログをリアルタイムで確認できる
   - 完了すると、URLが発行される: `https://baby-app-xxxx.onrender.com`

### 2.2 手動デプロイ（Blueprintを使わない場合）

1. **「New」 → 「Web Service」を選択**

2. **リポジトリを接続**:
   - GitHubリポジトリを選択
   - ブランチ: `main`

3. **設定**:
   - Name: `baby-app`
   - Region: Oregon (Free tier)
   - Branch: `main`
   - Runtime: Docker
   - Plan: Free

4. **ビルド設定**:
   - Dockerfile Path: `./Dockerfile`
   - Docker Command: `sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT"`

5. **環境変数を設定**（上記の表を参照）

6. **「Create Web Service」をクリック**

## Step 3: デプロイ確認

### 3.1 ヘルスチェック

```bash
curl https://baby-app-xxxx.onrender.com/api/health
# 期待される出力: {"status":"healthy"}
```

### 3.2 フロントエンドアクセス

1. ブラウザで `https://baby-app-xxxx.onrender.com` にアクセス
2. Baby-Appのランディングページが表示される
3. 「新規登録」をクリック

### 3.3 初回ユーザー登録

1. **ユーザー登録**:
   - ユーザー名: 任意（英数字）
   - パスワード: 8文字以上
   - 招待コード: `SYSTEM_INVITE_CODE` で設定した値

2. **ログイン**:
   - 登録したユーザー名とパスワードでログイン

3. **家族を作成**:
   - 家族名を入力
   - 家族の招待コードが自動生成される（他のユーザーを招待する際に使用）

4. **赤ちゃんを登録**:
   - 赤ちゃんの名前と誕生日を入力
   - プレママの場合は、出産予定日を入力

5. **ダッシュボードへアクセス**:
   - 記録を追加して動作確認

## Step 4: デプロイ後の設定

### 4.1 カスタムドメインの設定（オプション）

1. Renderダッシュボードで「Settings」タブ
2. 「Custom Domains」セクション
3. 「Add Custom Domain」をクリック
4. ドメイン名を入力（例: `baby-app.yourdomain.com`）
5. DNSレコードを設定:
   - Type: CNAME
   - Name: `baby-app`
   - Value: Renderが提供するホスト名

### 4.2 自動デプロイの設定

デフォルトで、`main` ブランチへのプッシュで自動デプロイが有効です。

**無効にする場合:**
1. Renderダッシュボードで「Settings」タブ
2. 「Build & Deploy」セクション
3. 「Auto-Deploy」をオフ

**手動デプロイ:**
1. Renderダッシュボードで「Manual Deploy」をクリック
2. デプロイするブランチを選択
3. 「Deploy」をクリック

### 4.3 環境変数の更新

1. Renderダッシュボードで「Environment」タブ
2. 変数を追加・編集
3. 「Save Changes」をクリック
4. サービスが自動的に再起動される

## Step 5: モニタリング

### 5.1 ログの確認

1. Renderダッシュボードで「Logs」タブ
2. リアルタイムログを確認
3. エラーやワーニングを確認

**よく見るログ:**
```
INFO:     Application startup complete.
INFO:     [alembic.runtime.migration] Running upgrade ... -> ...
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 5.2 メトリクスの確認

1. Renderダッシュボードで「Metrics」タブ
2. CPU使用率、メモリ使用率を確認
3. リクエスト数、レスポンスタイムを確認

**無料プランの制限:**
- メモリ: 512MB
- CPU: 0.1 vCPU
- 15分間アクセスがないとスリープ（初回アクセス時に起動に時間がかかる）

### 5.3 アラートの設定（有料プラン）

1. Renderダッシュボードで「Notifications」
2. Slack/Email 通知を設定
3. エラー発生時に通知を受け取る

## トラブルシューティング

### ビルドエラー

**症状**: ビルドが失敗する

**確認事項**:
1. ローカルで `docker build .` が成功するか
2. Renderのビルドログで具体的なエラーを確認
3. `requirements.txt` に不足している依存関係がないか

**よくあるエラー**:
```
ERROR: Could not find a version that satisfies the requirement ...
→ requirements.txt を確認
```

### データベース接続エラー

**症状**: アプリケーションが起動するが、データベースに接続できない

**確認事項**:
1. `DATABASE_URL` が正しく設定されているか
2. PostgreSQLのホスト名・ポート・認証情報を確認
3. Neonの場合: `?sslmode=require` が付いているか
4. ファイアウォールやセキュリティグループの設定

**デバッグ方法**:
```bash
# ログで接続エラーを確認
# Renderダッシュボード → Logs タブ

# よくあるエラー:
"connection to server at ... failed"
→ DATABASE_URLのホスト名を確認

"SSL connection required"
→ ?sslmode=require を追加
```

### マイグレーションエラー

**症状**: `alembic upgrade head` が失敗する

**確認事項**:
1. Renderのログで詳細なエラーメッセージを確認
2. ローカルでマイグレーションが成功するか
3. データベースに接続できているか

**手動マイグレーション**:
1. Renderダッシュボードで「Shell」タブ
2. コマンドを実行:
   ```bash
   alembic upgrade head
   ```

### フロントエンドが表示されない

**症状**: ブラウザでアクセスしても白い画面

**確認事項**:
1. `/api/health` エンドポイントが正常に応答するか
2. `frontend/out` ディレクトリがビルド時に生成されているか
3. Dockerビルドログで `npm run build` が成功しているか

**デバッグ方法**:
```bash
# ヘルスチェック
curl https://baby-app-xxxx.onrender.com/api/health

# ルートアクセス
curl https://baby-app-xxxx.onrender.com/
# → HTMLが返されるべき
```

### スリープからの起動が遅い

**症状**: 無料プランで15分間アクセスがないとスリープし、初回アクセスに時間がかかる

**対策**:
1. 有料プラン（Starter $7/月）にアップグレード
2. 外部モニタリングサービスでpingを送る（例: UptimeRobot）
   - 5分ごとに `/api/health` にアクセス
   - スリープを防げる

## デプロイチェックリスト

デプロイ完了後、以下を確認してください：

- [ ] ヘルスチェックが成功する（`/api/health`）
- [ ] フロントエンドが表示される
- [ ] ユーザー登録ができる
- [ ] ログインができる
- [ ] 家族と赤ちゃんを登録できる
- [ ] ダッシュボードが表示される
- [ ] 各記録機能（授乳、睡眠、おむつ、成長）が動作する
- [ ] 陣痛タイマーが動作する
- [ ] スケジュールが作成できる
- [ ] ダークモードが切り替わる
- [ ] ログアウトができる

## 更新とメンテナンス

### コードの更新

```bash
# 1. 変更をコミット
git add .
git commit -m "feat: new feature"

# 2. mainブランチにプッシュ
git push origin main

# 3. Renderで自動デプロイが開始される
# 　 ダッシュボードでデプロイ状況を確認
```

### データベースのバックアップ

**Neonの場合:**
- 自動バックアップが有効（無料プラン: 7日間保持）
- ダッシュボードで「Restore」から復元可能

**Render PostgreSQLの場合:**
- 手動バックアップ（有料プラン）
- または `pg_dump` でエクスポート

### スケールアップ

無料プランから有料プランへのアップグレード:

1. Renderダッシュボードで「Settings」タブ
2. 「Plan」セクション
3. プランを選択:
   - **Starter ($7/月)**: スリープなし、512MB RAM
   - **Standard ($25/月)**: 2GB RAM、より高速
   - **Pro ($85/月)**: 4GB RAM、優先サポート

## 参考リンク

- [Render公式ドキュメント](https://render.com/docs)
- [Neon公式ドキュメント](https://neon.tech/docs)
- [FastAPI公式ドキュメント](https://fastapi.tiangolo.com/)
- [Next.js公式ドキュメント](https://nextjs.org/docs)

---

**最終更新**: 2026-02-13
