"""Authentication routes."""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection
from auth_helpers import (
    get_user_by_username,
    get_user_by_email,
    get_user_roles,
    get_user_permissions,
    get_current_user,
    create_session,
)
from auth_decorators import login_required, permission_required
from audit_helpers import get_audit_logs

# Create a Blueprint for auth routes
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """User registration route."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Validation
        errors = []
        if not username:
            errors.append("Username is required.")
        if not email:
            errors.append("Email is required.")
        if not password:
            errors.append("Password is required.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters long.")

        # Check if username or email already exists
        if get_user_by_username(username):
            errors.append("Username already exists.")
        if get_user_by_email(email):
            errors.append("Email already exists.")

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("register.html")

        # Create new user
        password_hash = generate_password_hash(password)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO app_users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, password_hash),
        )
        conn.commit()
        user_id = cur.lastrowid
        cur.close()
        conn.close()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """User login route."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please provide both username and password.", "error")
            return render_template("login.html")

        user = get_user_by_username(username)
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid username or password.", "error")
            return render_template("login.html")

        # Create session
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        create_session(user["id"])

        flash(f"Welcome back, {user['username']}!", "success")
        next_page = request.args.get("next")
        return redirect(next_page) if next_page else redirect(url_for("main.index"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    """User logout route."""
    if "user_id" in session:
        username = session.get("username", "User")
        session.clear()
        flash(f"Goodbye, {username}! You have been logged out.", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/profile")
@login_required
def profile():
    """User profile page."""
    user = get_current_user()
    if not user:
        return redirect(url_for("auth.login"))

    # Get user roles and permissions
    roles = get_user_roles(user["id"])
    permissions = get_user_permissions(user["id"])
    
    # Check if user is admin (has all 4 permissions: read, create, update, delete)
    permission_names = {perm["name"] for perm in permissions}
    has_all_permissions = permission_names >= {"read", "create", "update", "delete"}

    # Get user preferences (genres)
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT g.id, g.name
        FROM genres g
        INNER JOIN user_preferences up ON g.id = up.genre_id
        WHERE up.user_id = %s
        """,
        (user["id"],),
    )
    preferences = cur.fetchall()
    cur.close()
    conn.close()

    return render_template(
        "profile.html",
        user=user,
        roles=roles,
        permissions=permissions,
        preferences=preferences,
        is_admin=has_all_permissions,
    )


@auth_bp.route("/preferences", methods=["GET", "POST"])
@login_required
def manage_preferences():
    """Manage user genre preferences."""
    user = get_current_user()
    if not user:
        return redirect(url_for("auth.login"))

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        # Get selected genre IDs from form
        selected_genres = request.form.getlist("genres")
        genre_ids = [int(gid) for gid in selected_genres if gid.isdigit()]

        # Delete existing preferences
        cur.execute("DELETE FROM user_preferences WHERE user_id = %s", (user["id"],))

        # Insert new preferences
        for genre_id in genre_ids:
            cur.execute(
                "INSERT INTO user_preferences (user_id, genre_id) VALUES (%s, %s)",
                (user["id"], genre_id),
            )

        conn.commit()
        flash("Preferences updated successfully!", "success")
        cur.close()
        conn.close()
        return redirect(url_for("auth.profile"))

    # GET: Show form with all genres and user's current preferences
    cur.execute("SELECT id, name FROM genres ORDER BY name")
    all_genres = cur.fetchall()

    cur.execute(
        "SELECT genre_id FROM user_preferences WHERE user_id = %s", (user["id"],)
    )
    user_pref_ids = {row["genre_id"] for row in cur.fetchall()}

    cur.close()
    conn.close()

    return render_template(
        "preferences.html", genres=all_genres, selected_genres=user_pref_ids
    )


@auth_bp.route("/audit-logs")
@login_required
@permission_required("read")
def audit_logs():
    """View audit logs (admin only)."""
    user = get_current_user()
    if not user:
        return redirect(url_for("auth.login"))

    # Get audit logs (limit to 200 most recent)
    logs = get_audit_logs(limit=200)

    return render_template("audit_logs.html", logs=logs)
