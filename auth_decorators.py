"""Authentication decorators for route protection."""

from functools import wraps
from flask import session, flash, redirect, url_for
from auth_helpers import user_has_role, user_has_permission


def login_required(f):
    """Decorator to require login for a route."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function


def role_required(role_name):
    """Decorator to require a specific role for a route."""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for("auth.login"))
            if not user_has_role(session["user_id"], role_name):
                flash("You do not have permission to access this page.", "error")
                return redirect(url_for("main.index"))
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def permission_required(permission_name):
    """Decorator to require a specific permission for a route."""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for("auth.login"))
            if not user_has_permission(session["user_id"], permission_name):
                flash("You do not have permission to access this page.", "error")
                return redirect(url_for("main.index"))
            return f(*args, **kwargs)

        return decorated_function

    return decorator
