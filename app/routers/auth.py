"""認証ルーター"""
import secrets
from fastapi import APIRouter, Depends, Request, Form, Response, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from typing import Optional
from app.models.user import User
from app.models.family import Family
from app.models.family_user import FamilyUser
from app.models.session import UserSession, SESSION_MAX_AGE_DAYS
from app.services.auth_service import AuthService
from app.dependencies import get_current_user_optional
from app.config import settings
from app.schemas.user import UserLogin, UserRegisterRequest, UserResponse

router = APIRouter(tags=["auth"])

# Cookie設定
COOKIE_MAX_AGE = 86400 * SESSION_MAX_AGE_DAYS


def _set_session_cookie(response: Response, token: str) -> None:
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




@router.post("/login", response_model=dict)
def login(
    request: Request,
    login_data: UserLogin,
    response: Response,
    db: Session = Depends(get_db),
):
    """ログイン処理"""
    user = db.query(User).filter(User.username == login_data.username).first()

    if not user or not AuthService.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザー名またはパスワードが正しくありません",
        )

    # セッション作成
    token = _create_session(db, user.id)

    _set_session_cookie(response, token)
    return {"message": "Login successful", "user": UserResponse.model_validate(user)}




@router.post("/register", response_model=dict)
def register(
    request: Request,
    register_data: UserRegisterRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    """ユーザー登録処理"""
    # 1. ハニーポットチェック
    if register_data.email_confirm_hidden:
        raise HTTPException(status_code=400, detail="Bot detected")

    # 2. 招待コード検証
    invite_code = register_data.invite_code
    is_valid_system_code = (invite_code == settings.SYSTEM_INVITE_CODE)
    family = db.query(Family).filter(Family.invite_code == invite_code.upper()).first()

    if not is_valid_system_code and not family:
        raise HTTPException(
            status_code=400,
            detail="無効な招待コードです。管理者からコードを取得してください。",
        )

    # 3. ユーザー名の重複チェック
    existing_user = db.query(User).filter(User.username == register_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="このユーザー名は既に使用されています",
        )

    # 4. ユーザー作成
    hashed_password = AuthService.get_password_hash(register_data.password)
    new_user = User(username=register_data.username, hashed_password=hashed_password)
    db.add(new_user)
    db.flush()

    # 5. 家族招待コードの場合は自動参加
    if family:
        family_user = FamilyUser(
            family_id=family.id,
            user_id=new_user.id,
            role="member"
        )
        db.add(family_user)

    db.commit()
    db.refresh(new_user)

    # 6. 自動ログイン
    token = _create_session(db, new_user.id)

    _set_session_cookie(response, token)
    return {"message": "Registration successful", "user": UserResponse.model_validate(new_user)}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    user: User = Depends(get_current_user_optional),
):
    """現在のユーザー情報を取得"""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return user


@router.get("/logout")
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """ログアウト処理"""
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

    response.delete_cookie(key="session_token")
    return {"message": "Logout successful"}
