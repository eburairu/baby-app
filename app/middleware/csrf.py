from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import secrets

class CSRFCookieMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        csrf_token = request.cookies.get("csrf_token")
        new_token = False
        if not csrf_token:
            csrf_token = secrets.token_urlsafe(32)
            new_token = True

        request.state.csrf_token = csrf_token

        response = await call_next(request)

        if new_token:
            response.set_cookie(
                key="csrf_token",
                value=csrf_token,
                httponly=True,
                samesite="lax",
                secure=False  # Modify this based on environment if needed
            )

        return response
