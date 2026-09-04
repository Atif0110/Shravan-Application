import ipaddress
import json
import secrets
import threading
import time
from functools import wraps
from urllib.parse import urlparse

from flask import jsonify, request, session


PUBLIC_ENDPOINTS = {
    ("POST", "/api/create_user"),
    ("POST", "/api/users/login"),
    ("GET", "/api/csrf-token"),
    ("GET", "/"),
    ("GET", "/api/stats"),
}

CONTENT_MANAGERS = {"ngo", "caretaker"}
PRIVILEGED_MUTATIONS = (
    "/api/asanas",
    "/api/yoga-videos",
    "/api/generate-asana-images",
    "/api/ai/generate-content",
)

_login_lock = threading.Lock()
_login_attempts = {}
LOGIN_WINDOW_SECONDS = 15 * 60
LOGIN_LIMIT = 8
IDLE_TIMEOUT_SECONDS = 30 * 60
ABSOLUTE_TIMEOUT_SECONDS = 8 * 60 * 60


def _client_ip():
    return request.remote_addr or "unknown"


def _prune_attempts(now):
    expired = [key for key, value in _login_attempts.items() if now - value[0] > LOGIN_WINDOW_SECONDS]
    for key in expired:
        _login_attempts.pop(key, None)


def login_rate_limited(identifier):
    key = f"{_client_ip()}:{identifier.lower().strip()}"
    now = time.time()
    with _login_lock:
        _prune_attempts(now)
        entry = _login_attempts.get(key)
        return bool(entry and entry[1] >= LOGIN_LIMIT)


def record_login_failure(identifier):
    key = f"{_client_ip()}:{identifier.lower().strip()}"
    now = time.time()
    with _login_lock:
        _prune_attempts(now)
        first_seen, count = _login_attempts.get(key, (now, 0))
        _login_attempts[key] = (first_seen, count + 1)


def clear_login_failures(identifier):
    key = f"{_client_ip()}:{identifier.lower().strip()}"
    with _login_lock:
        _login_attempts.pop(key, None)


def current_user_id():
    value = session.get("user_id")
    return value if isinstance(value, int) else None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_user_id() is None:
            return jsonify({"error": "Authentication required", "status": "fail"}), 401
        return view(*args, **kwargs)
    return wrapped


def role_required(*roles):
    allowed = set(roles)

    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            from models import User
            user = User.query.filter_by(user_id=current_user_id()).first()
            if not user or not user.role or user.role.name not in allowed:
                return jsonify({"error": "Insufficient permissions", "status": "fail"}), 403
            return view(*args, **kwargs)
        return wrapped
    return decorator


def issue_csrf_token():
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token


def validate_csrf():
    expected = session.get("csrf_token")
    supplied = request.headers.get("X-CSRF-Token")
    if not expected or not supplied or not secrets.compare_digest(expected, supplied):
        return jsonify({"error": "CSRF validation failed", "status": "fail"}), 403
    return None


def is_safe_external_url(value):
    try:
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            return False
        host = parsed.hostname.lower()
        if host in {"localhost", "localhost.localdomain"}:
            return False
        try:
            address = ipaddress.ip_address(host)
            if address.is_private or address.is_loopback or address.is_link_local or address.is_reserved or address.is_multicast:
                return False
        except ValueError:
            pass
        return True
    except (TypeError, ValueError):
        return False


def _requires_auth():
    if request.method == "OPTIONS" or not request.path.startswith("/api/"):
        return False
    return (request.method, request.path) not in PUBLIC_ENDPOINTS and request.path != "/api/users/logout"


def register_security(app):
    app.config.setdefault("MAX_CONTENT_LENGTH", 8 * 1024 * 1024)

    @app.before_request
    def security_before_request():
        user_id = current_user_id()
        if user_id is not None:
            now = time.time()
            created_at = session.get("session_created_at", now)
            last_seen = session.get("session_last_seen", now)
            if now - created_at > ABSOLUTE_TIMEOUT_SECONDS or now - last_seen > IDLE_TIMEOUT_SECONDS:
                session.clear()
                user_id = None
            else:
                session["session_last_seen"] = now

        if _requires_auth() and user_id is None:
            return jsonify({"error": "Authentication required", "status": "fail"}), 401

        if current_user_id() is not None and request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            if any(request.path == prefix or request.path.startswith(prefix + "/") for prefix in PRIVILEGED_MUTATIONS):
                from models import User
                user = User.query.filter_by(user_id=current_user_id()).first()
                if not user or not user.role or user.role.name not in CONTENT_MANAGERS:
                    return jsonify({"error": "Insufficient permissions", "status": "fail"}), 403

        if request.method in {"POST", "PUT", "PATCH", "DELETE"} and request.path.startswith("/api/"):
            if request.path != "/api/csrf-token":
                failure = validate_csrf()
                if failure:
                    return failure

    @app.after_request
    def security_headers(response):
        if request.path.startswith("/api/") and response.status_code >= 500:
            response.set_data(json.dumps({"error": "Internal server error", "status": "fail"}))
            response.content_type = "application/json"

        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(self), geolocation=(self)")
        response.headers.setdefault("Cache-Control", "no-store" if request.path.startswith("/api/") else "no-cache")
        if app.config.get("SESSION_COOKIE_SECURE"):
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response
