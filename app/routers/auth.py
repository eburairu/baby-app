"""認証ルーター"""
import secrets
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.session import UserSession, SESSION_MAX_AGE_DAYS
from app.services.auth_service import AuthService
from app.dependencies import get_current_user_optional
from app.config import settings

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="app/templates")

# Cookie設定
COOKIE_MAX_AGE = 86400 * SESSION_MAX_AGE_DAYS


def _set_session_cookie(response: RedirectResponse, token: str) -> None:
    """セッションCookieを設定"""
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        max_age=COOKIE_MAX_AGE,
        samesite="lax",
        secure=settings.ENVIRONMENT == "production",
    )


def _create_session(db: Session, user_id: int) -> str:
    """DBにセッションレコードを作成し、トークンを返す"""
    token = secrets.token_urlsafe(32)
    user_session = UserSession(
        token=token,
        user_id=user_id,
        expires_at=UserSession.default_expires_at(),
    )
    db.add(user_session)
    db.commit()
    return token


@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    user: User | None = Depends(get_current_user_optional),
):
    """ログインページ表示（ログイン済みならダッシュボードへ）"""
    if user:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": None},
    )


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """ログイン処理"""
    user = db.query(User).filter(User.username == username).first()

    if not user or not AuthService.verify_password(password, user.hashed_password):
        # エラーをフォームに表示（JSONではなく）
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "ユーザー名またはパスワードが正しくありません",
            },
            status_code=401,
        )

    # セッション作成
    token = _create_session(db, user.id)

    response = RedirectResponse(url="/dashboard", status_code=303)
    _set_session_cookie(response, token)
    return response


@router.get("/register", response_class=HTMLResponse)
async def register_page(
    request: Request,
    user: User | None = Depends(get_current_user_optional),
):
    """ユーザー登録ページ表示（ログイン済みならダッシュボードへ）"""
    if user:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "error": None},
    )


@router.post("/register")
async def register(
    request: Request,
    username: str = Form(..., min_length=3, max_length=50),
    password: str = Form(..., min_length=6, max_length=72),
    db: Session = Depends(get_db),
):
    """ユーザー登録処理"""
    # ユーザー名の重複チェック
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "このユーザー名は既に使用されています",
            },
            status_code=400,
        )

    # ユーザー作成
    hashed_password = AuthService.get_password_hash(password)
    new_user = User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 自動ログイン
    token = _create_session(db, new_user.id)

    response = RedirectResponse(url="/dashboard", status_code=303)
    _set_session_cookie(response, token)
    return response


@router.get("/logout")
async def logout(
    request: Request,
    session_token: str | None = None,
    db: Session = Depends(get_db),
):
    """ログアウト処理"""
    from fastapi import Cookie

    # Cookieからトークンを取得
    session_token = request.cookies.get("session_token")

    # DBからセッション削除
    if session_token:
        user_session = db.query(UserSession).filter(
            UserSession.token == session_token
        ).first()
        if user_session:
            db.delete(user_session)
            db.commit()

    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="session_token")
    return response
