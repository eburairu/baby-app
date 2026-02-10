"""FastAPI アプリケーションエントリポイント"""
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.routers import auth, dashboard, feeding, sleep, diaper, growth, contraction, schedule
from app.dependencies import get_current_user_optional

# FastAPIアプリケーション作成
app = FastAPI(
    title="Baby-App",
    description="総合育児管理アプリケーション",
    version="1.0.0"
)

# セッションミドルウェア追加
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="session",
    max_age=86400 * 7  # 7日間
)

# 静的ファイル
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ルーター登録
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(feeding.router)
app.include_router(sleep.router)
app.include_router(diaper.router)
app.include_router(growth.router)
app.include_router(contraction.router)
app.include_router(schedule.router)


@app.get("/")
async def root():
    """ルートパス - ダッシュボードへリダイレクト"""
    return RedirectResponse(url="/dashboard")


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy"}
