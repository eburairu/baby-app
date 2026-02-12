"""FastAPI アプリケーションエントリポイント"""
from typing import Optional
from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from app.utils.templates import templates

from fastapi.exceptions import RequestValidationError
from app.config import settings
from app.routers import auth, dashboard, feeding, sleep, diaper, growth, contraction, schedule, family, baby
from app.middleware.csrf import CSRFCookieMiddleware
from app.dependencies import get_current_user_optional, AuthenticationRequired, PermissionDenied, check_csrf
from app.models.user import User

# FastAPIアプリケーション作成
app = FastAPI(
    title="Baby-App",
    description="総合育児管理アプリケーション",
    version="1.0.0",
    default_response_class=JSONResponse,
    dependencies=[Depends(check_csrf)],
)

# CSRF Cookie Middleware
app.add_middleware(CSRFCookieMiddleware)


# ===== エラーハンドラー =====

@app.exception_handler(PermissionDenied)
async def permission_denied_handler(request: Request, exc: PermissionDenied):
    """権限不足時のハンドラー（改善版）"""
    msg = str(exc)

    # 特定の赤ちゃんの閲覧権限がない場合
    if "この赤ちゃんの情報を閲覧する権限がありません" in msg:
        # 閲覧可能な赤ちゃんを探してリダイレクト
        try:
            from sqlalchemy.orm import Session
            from app.database import SessionLocal
            from app.models.user_session import UserSession
            from app.models.user import User
            from app.services.permission_service import PermissionService

            # セッショントークンからユーザーを取得
            session_token = request.cookies.get("session_token")
            if session_token:
                db = SessionLocal()
                try:
                    user_session = db.query(UserSession).filter(
                        UserSession.token == session_token
                    ).first()

                    if user_session and not user_session.is_expired:
                        user = db.query(User).filter(User.id == user_session.user_id).first()
                        if user and user.families:
                            family = user.families[0].family

                            # 閲覧可能な赤ちゃんを探す
                            baby_ids = [b.id for b in family.babies]
                            perms_map = PermissionService.get_user_permissions_batch(
                                db, user.id, baby_ids, family.id, "basic_info"
                            )
                            viewable_babies = [b for b in family.babies if perms_map.get(b.id, False)]

                            if viewable_babies:
                                # 閲覧可能な最初の赤ちゃんのダッシュボードにリダイレクト
                                redirect_url = f"/dashboard?baby_id={viewable_babies[0].id}&permission_denied=1"

                                if request.headers.get("HX-Request"):
                                    response = HTMLResponse(content="", status_code=200)
                                    response.headers["HX-Redirect"] = redirect_url
                                    return response

                                return RedirectResponse(url=redirect_url, status_code=303)
                finally:
                    db.close()
        except Exception:
            pass  # エラーが発生した場合はデフォルト処理へ

    # 既存のロジック（その他のエラーケース）
    if request.headers.get("HX-Request"):
        response = HTMLResponse(content="", status_code=200)
        if "家族に所属していません" in msg:
            response.headers["HX-Redirect"] = "/families/setup"
        elif "赤ちゃんが登録されていません" in msg or "閲覧可能な赤ちゃん" in msg:
            response.headers["HX-Redirect"] = "/babies/new"
        else:
            response.headers["HX-Redirect"] = "/families/settings"
        return response

    if "家族に所属していません" in msg:
        return RedirectResponse(url="/families/setup", status_code=303)
    if "赤ちゃんが登録されていません" in msg or "閲覧可能な赤ちゃん" in msg:
        return RedirectResponse(url="/babies/new", status_code=303)
    return RedirectResponse(url="/families/settings", status_code=303)


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
