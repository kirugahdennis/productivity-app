import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secret key used to sign the session cookie. In production this
    # MUST be set via an environment variable.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    # Session cookie settings for a frontend running on a different
    # origin/port (e.g. React dev server on :4000/:5173 talking to
    # this API on :5555). SameSite=None + Secure is required for
    # cross-site cookies in modern browsers; for local http-only dev
    # you may need to relax SESSION_COOKIE_SECURE to False.
    SESSION_COOKIE_SAMESITE = os.environ.get("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"

    JSON_SORT_KEYS = False