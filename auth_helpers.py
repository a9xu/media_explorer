"""Authentication helper functions."""

from datetime import datetime
from flask import session
from db import get_connection


def get_user_by_username(username):
    """Get user by username from database."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM app_users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user


def get_user_by_email(email):
    """Get user by email from database."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM app_users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user


def get_user_by_id(user_id):
    """Get user by ID from database."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM app_users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user


def get_user_roles(user_id):
    """Get all roles for a user."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT r.id, r.name 
        FROM roles r
        INNER JOIN user_roles ur ON r.id = ur.role_id
        WHERE ur.user_id = %s
        """,
        (user_id,),
    )
    roles = cur.fetchall()
    cur.close()
    conn.close()
    return roles


def get_user_permissions(user_id):
    """Get all permissions for a user (through their roles)."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT DISTINCT p.id, p.name
        FROM permissions p
        INNER JOIN role_permissions rp ON p.id = rp.permission_id
        INNER JOIN user_roles ur ON rp.role_id = ur.role_id
        WHERE ur.user_id = %s
        """,
        (user_id,),
    )
    permissions = cur.fetchall()
    cur.close()
    conn.close()
    return permissions


def user_has_role(user_id, role_name):
    """Check if user has a specific role."""
    roles = get_user_roles(user_id)
    return any(role["name"] == role_name for role in roles)


def user_has_permission(user_id, permission_name):
    """Check if user has a specific permission."""
    permissions = get_user_permissions(user_id)
    return any(perm["name"] == permission_name for perm in permissions)


def create_session(user_id):
    """Create a new session for a user."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO sessions (user_id, started_at) VALUES (%s, %s)",
        (user_id, datetime.now()),
    )
    conn.commit()
    session_id = cur.lastrowid
    cur.close()
    conn.close()
    return session_id


def get_current_user():
    """Get the current logged-in user from session."""
    if "user_id" in session:
        return get_user_by_id(session["user_id"])
    return None
