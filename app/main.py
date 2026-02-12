"""FastAPI アプリケーションエントリポイント"""
import secrets
from typing import Optional
from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fastapi.exceptions import RequestValidationError
from app.config import settings
from app.routers import auth, dashboard, feeding, sleep, diaper, growth, contraction, schedule, family, baby
from app.dependencies import get_current_user_optional, AuthenticationRequired, PermissionDenied
from app.models.user import User

# FastAPIアプリケーション作成
app = FastAPI(
    title="Baby-App",
    description="総合育児管理アプリケーション",
    version="1.0.0",
    default_response_class=JSONResponse,
)

templates = Jinja2Templates(directory="app/templates")


# ===== CSRF Middleware =====

@app.middleware("http")
async def csrf_middleware(request: Request, call_next):
    """CSRF保護ミドルウェア (Double Submit Cookie パターン)"""
    # 1. トークンの取得または生成
    token = request.cookies.get("csrf_token")
    is_new_token = False
    if not token:
        token = secrets.token_urlsafe(32)
        is_new_token = True

    # 2. テンプレートで使用するために request.state に保存
    request.state.csrf_token = token

    # 3. 安全でないメソッドに対する検証
    if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
        sent_token = None

        # フォームデータからトークンを取得
        content_type = request.headers.get("Content-Type", "")
        if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
            try:
                form = await request.form()
                sent_token = form.get("csrf_token")
            except Exception:
                pass

        # ヘッダーからトークンを取得 (htmx等用)
        if not sent_token:
            sent_token = request.headers.get("X-CSRF-Token")

        # 検証 (クッキーのトークンと一致するか)
        # 注意: is_new_token が True の場合は、クッキーがなかったので検証失敗とする
        if is_new_token or not sent_token or sent_token != token:
            return JSONResponse(
                status_code=403,
                content={"detail": "CSRF token missing or invalid"}
            )

    response = await call_next(request)

    # 4. クッキーの設定
    if is_new_token:
        response.set_cookie(
            "csrf_token",
            token,
            httponly=True,
            samesite="lax",
            secure=settings.ENVIRONMENT == "production",
        )

    return response


# ===== エラーハンドラー =====

@app.exception_handler(PermissionDenied)
async def permission_denied_handler(request: Request, exc: PermissionDenied):
    """権限不足時のハンドラー"""
    msg = str(exc)
    if request.headers.get("HX-Request"):
        response = HTMLResponse(content="", status_code=200)
        if "家族に所属していません" in msg:
            response.headers["HX-Redirect"] = "/families/setup"
        elif "赤ちゃんが登録されていません" in msg:
            response.headers["HX-Redirect"] = "/babies/new"
        else:
            response.headers["HX-Redirect"] = "/dashboard"
        return response

    if "家族に所属していません" in msg:
        return RedirectResponse(url="/families/setup", status_code=303)
    if "赤ちゃんが登録されていません" in msg:
        return RedirectResponse(url="/babies/new", status_code=303)
    return RedirectResponse(url="/dashboard", status_code=303)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """バリデーションエラーのハンドラー"""
    # エラーメッセージを一つにまとめる
    errors = exc.errors()
    if errors:
        msg = errors[0].get("msg", "入力内容に誤りがあります")
        # "Value error, " などのプレフィックスを削除（Pydantic v2 用）
        msg = msg.replace("Value error, ", "").replace("Assertion failed, ", "")
    else:
        msg = "入力内容に誤りがあります"

    return JSONResponse(
        status_code=400,
        content={"detail": msg},
    )


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
app.include_router(family.router)
app.include_router(baby.router)
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
