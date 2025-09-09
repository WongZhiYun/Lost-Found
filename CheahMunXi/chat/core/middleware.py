from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from models import User
from services.database import SessionLocal
from nicegui import app


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        db = SessionLocal()
        
        # Define unprotected paths
        unprotected_path_prefixes = {'/login', '/_nicegui', '/static'}

        # Check if the current request path starts with any of the "unprotected" prefixes
        is_unprotected = any(request.url.path.startswith(prefix) for prefix in unprotected_path_prefixes)

        # If it is an unprotected path, process the next request
        if is_unprotected:
            response = await call_next(request)
            return response

        # Check if user ID is in session storage
        user_id = app.storage.user.get("user_id")
        if not user_id:
            return RedirectResponse("/login")

        # Check if user exists in the database
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            # If user does not exist, clear the session and redirect to login
            app.storage.user.clear()
            return RedirectResponse("/login")

        # If all checks pass, proceed with the request
        response = await call_next(request)
        db.close()
        
        return response
