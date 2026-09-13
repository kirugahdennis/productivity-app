from functools import wraps

from flask import session
from flask_restful import abort

from server.extensions import db
from server.models.user import User


def login_required(f):
    """Protect a Resource method: rejects the request with 401 unless
    a valid, logged-in user_id is present in the session cookie.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            abort(401, message="Unauthorized: please log in")
        if not db.session.get(User, user_id):
            # Session references a user that no longer exists
            session.pop("user_id", None)
            abort(401, message="Unauthorized: please log in")
        return f(*args, **kwargs)

    return wrapper


def current_user():
    """Fetch the User for the currently active session. Only call this
    inside a route already wrapped with @login_required.
    """
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.session.get(User, user_id)