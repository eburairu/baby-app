from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.types import ASGIApp
import secrets
from app.config import settings

class CSRFMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # 1. Get or generate token
        csrf_token = request.cookies.get("csrf_token")
        new_token = False
        if not csrf_token:
            csrf_token = secrets.token_urlsafe(32)
            new_token = True

        # Store in state for templates
        request.state.csrf_token = csrf_token

        # 2. Validate for unsafe methods
        if request.method in ("POST", "PUT", "DELETE", "PATCH"):
            # Check header first
            header_token = request.headers.get("X-CSRF-Token")

            # Check form data if header is missing
            form_token = None
            content_type = request.headers.get("content-type", "")
            if not header_token and (
                content_type.startswith("multipart/form-data") or
                content_type.startswith("application/x-www-form-urlencoded")
            ):
                try:
                    form = await request.form()
                    form_token = form.get("csrf_token")
                except Exception:
                    pass

            submitted_token = header_token or form_token

            if not submitted_token or not secrets.compare_digest(submitted_token, csrf_token):
                return JSONResponse(
                    {"detail": "CSRF token missing or incorrect"},
                    status_code=403
                )

        # 3. Process request
        response = await call_next(request)

        # 4. Set cookie if new token generated
        if new_token:
            response.set_cookie(
                key="csrf_token",
                value=csrf_token,
                httponly=True,
                samesite="lax",
                secure=False  # Modify this based on environment if needed
            )

        return response
