"""Audit logging helper functions."""
from datetime import datetime
from flask import session
from db import get_connection


def log_action(user_id, action):
    """Log an action to the audit_logs table."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO audit_logs (user_id, action) VALUES (%s, %s)",
            (user_id, action),
        )
        conn.commit()
    except Exception as e:
        # Log error but don't break the main operation
        print(f"Error logging audit action: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def log_action_from_session(action):
    """Log an action using the current user from session."""
    if "user_id" in session:
        log_action(session["user_id"], action)


def get_audit_logs(limit=100, user_id=None):
    """Get audit logs, optionally filtered by user."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    if user_id:
        cur.execute(
            """
            SELECT al.id, al.user_id, al.action, al.created_at, au.username
            FROM audit_logs al
            INNER JOIN app_users au ON al.user_id = au.id
            WHERE al.user_id = %s
            ORDER BY al.created_at DESC
            LIMIT %s
            """,
            (user_id, limit),
        )
    else:
        cur.execute(
            """
            SELECT al.id, al.user_id, al.action, al.created_at, au.username
            FROM audit_logs al
            INNER JOIN app_users au ON al.user_id = au.id
            ORDER BY al.created_at DESC
            LIMIT %s
            """,
            (limit,),
        )

    logs = cur.fetchall()
    cur.close()
    conn.close()
    return logs

