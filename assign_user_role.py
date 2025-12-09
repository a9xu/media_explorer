"""Helper script to assign roles to users."""
from db import get_connection
from auth_helpers import get_user_by_username


def assign_role_to_user(username, role_name):
    """Assign a role to a user."""
    # Get user
    user = get_user_by_username(username)
    if not user:
        print(f"Error: User '{username}' not found.")
        return False

    # Get role
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id FROM roles WHERE name = %s", (role_name,))
    role = cur.fetchone()

    if not role:
        print(f"Error: Role '{role_name}' not found.")
        cur.close()
        conn.close()
        return False

    role_id = role["id"]

    # Check if user already has this role
    cur.execute(
        "SELECT user_id FROM user_roles WHERE user_id = %s AND role_id = %s",
        (user["id"], role_id),
    )
    existing = cur.fetchone()

    if existing:
        print(f"User '{username}' already has role '{role_name}'.")
        cur.close()
        conn.close()
        return False

    # Assign role
    cur.execute(
        "INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)",
        (user["id"], role_id),
    )
    conn.commit()
    cur.close()
    conn.close()

    print(f"✅ Successfully assigned role '{role_name}' to user '{username}'.")
    return True


def remove_role_from_user(username, role_name):
    """Remove a role from a user."""
    # Get user
    user = get_user_by_username(username)
    if not user:
        print(f"Error: User '{username}' not found.")
        return False

    # Get role
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id FROM roles WHERE name = %s", (role_name,))
    role = cur.fetchone()

    if not role:
        print(f"Error: Role '{role_name}' not found.")
        cur.close()
        conn.close()
        return False

    role_id = role["id"]

    # Remove role
    cur.execute(
        "DELETE FROM user_roles WHERE user_id = %s AND role_id = %s",
        (user["id"], role_id),
    )
    conn.commit()
    affected = cur.rowcount
    cur.close()
    conn.close()

    if affected > 0:
        print(f"✅ Successfully removed role '{role_name}' from user '{username}'.")
        return True
    else:
        print(f"User '{username}' does not have role '{role_name}'.")
        return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print("Usage:")
        print("  python assign_user_role.py <username> <role_name> <action>")
        print("  Actions: 'add' or 'remove'")
        print("\nExample:")
        print("  python assign_user_role.py john_doe user add")
        print("  python assign_user_role.py john_doe admin add")
        sys.exit(1)

    username = sys.argv[1]
    role_name = sys.argv[2]
    action = sys.argv[3].lower()

    if action == "add":
        assign_role_to_user(username, role_name)
    elif action == "remove":
        remove_role_from_user(username, role_name)
    else:
        print(f"Error: Invalid action '{action}'. Use 'add' or 'remove'.")
        sys.exit(1)

