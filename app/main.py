"""FastAPI アプリケーションエントリポイント"""
from typing import Optional
from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.routers import auth, dashboard, feeding, sleep, diaper, growth, contraction, schedule
from app.dependencies import get_current_user_optional, AuthenticationRequired
from app.models.user import User

# FastAPIアプリケーション作成
app = FastAPI(
    title="Baby-App",
    description="総合育児管理アプリケーション",
    version="1.0.0",
    default_response_class=JSONResponse,
)

templates = Jinja2Templates(directory="app/templates")


# ===== エラーハンドラー =====

@app.exception_handler(AuthenticationRequired)
async def auth_required_handler(request: Request, exc: AuthenticationRequired):
    """未認証時のハンドラー: ログインページへリダイレクト"""
    # htmxリクエストの場合は HX-Redirect ヘッダーで対応
    if request.headers.get("HX-Request"):
        response = HTMLResponse(content="", status_code=200)
        response.headers["HX-Redirect"] = "/login"
        return response

    return RedirectResponse(url="/login", status_code=303)


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
async def root(user: Optional[User] = Depends(get_current_user_optional)):
    """ルートパス - 認証状態に応じてリダイレクト"""
    if user:
        return RedirectResponse(url="/dashboard")
    return RedirectResponse(url="/login")


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy"}
