"""認証ルーター"""
import secrets
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.services.auth_service import AuthService
from app.dependencies import sessions, get_current_user_optional

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """ログインページ表示"""
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )


@router.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """ログイン処理"""
    # ユーザー検索
    user = db.query(User).filter(User.username == username).first()

    if not user or not AuthService.verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="ユーザー名またはパスワードが正しくありません"
        )

    # セッショントークン生成
    session_token = secrets.token_urlsafe(32)
    sessions[session_token] = user.id

    # Cookieにセッショントークンを設定
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        max_age=86400 * 7,  # 7日間
        samesite="lax"
    )

    return response


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """ユーザー登録ページ表示"""
    return templates.TemplateResponse(
        "register.html",
        {"request": request}
    )


@router.post("/register")
async def register(
    username: str = Form(..., min_length=3, max_length=50),
    password: str = Form(..., min_length=6, max_length=72),
    db: Session = Depends(get_db)
):
    """ユーザー登録処理"""
    # ユーザー名の重複チェック
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="このユーザー名は既に使用されています"
        )

    # ユーザー作成
    hashed_password = AuthService.get_password_hash(password)
    new_user = User(
        username=username,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 自動ログイン
    session_token = secrets.token_urlsafe(32)
    sessions[session_token] = new_user.id

    # Cookieにセッショントークンを設定
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        max_age=86400 * 7,  # 7日間
        samesite="lax"
    )

    return response


@router.get("/logout")
async def logout(
    response: Response,
    user = Depends(get_current_user_optional)
):
    """ログアウト処理"""
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="session_token")

    return response
