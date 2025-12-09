"""Initialize roles and permissions in the database."""
from db import get_connection

# Define permissions
PERMISSIONS = [
    {"name": "read"},
    {"name": "create"},
    {"name": "update"},
    {"name": "delete"},
]

# Define roles and their permissions
ROLES = {
    "user": ["read"],  # User can only read
    "admin": ["read", "create", "update", "delete"],  # Admin can do everything
}


def init_permissions():
    """Create permissions in the database."""
    conn = get_connection()
    cur = conn.cursor()

    permission_ids = {}
    for perm in PERMISSIONS:
        # Check if permission already exists
        cur.execute("SELECT id FROM permissions WHERE name = %s", (perm["name"],))
        existing = cur.fetchone()

        if existing:
            permission_ids[perm["name"]] = existing[0]
            print(f"Permission '{perm['name']}' already exists (ID: {existing[0]})")
        else:
            cur.execute("INSERT INTO permissions (name) VALUES (%s)", (perm["name"],))
            permission_ids[perm["name"]] = cur.lastrowid
            print(f"Created permission '{perm['name']}' (ID: {cur.lastrowid})")

    conn.commit()
    cur.close()
    conn.close()
    return permission_ids


def init_roles(permission_ids):
    """Create roles and assign permissions."""
    conn = get_connection()
    cur = conn.cursor()

    role_ids = {}
    for role_name, permission_names in ROLES.items():
        # Check if role already exists
        cur.execute("SELECT id FROM roles WHERE name = %s", (role_name,))
        existing = cur.fetchone()

        if existing:
            role_id = existing[0]
            role_ids[role_name] = role_id
            print(f"Role '{role_name}' already exists (ID: {role_id})")
        else:
            cur.execute("INSERT INTO roles (name) VALUES (%s)", (role_name,))
            role_id = cur.lastrowid
            role_ids[role_name] = role_id
            print(f"Created role '{role_name}' (ID: {role_id})")

        # Assign permissions to role
        for perm_name in permission_names:
            perm_id = permission_ids[perm_name]

            # Check if relationship already exists
            cur.execute(
                "SELECT role_id FROM role_permissions WHERE role_id = %s AND permission_id = %s",
                (role_id, perm_id),
            )
            existing_rel = cur.fetchone()

            if not existing_rel:
                cur.execute(
                    "INSERT INTO role_permissions (role_id, permission_id) VALUES (%s, %s)",
                    (role_id, perm_id),
                )
                print(f"  Assigned permission '{perm_name}' to role '{role_name}'")
            else:
                print(
                    f"  Permission '{perm_name}' already assigned to role '{role_name}'"
                )

    conn.commit()
    cur.close()
    conn.close()
    return role_ids


def main():
    """Main function to initialize roles and permissions."""
    print("Initializing permissions...")
    permission_ids = init_permissions()

    print("\nInitializing roles...")
    role_ids = init_roles(permission_ids)

    print("\n✅ Roles and permissions initialized successfully!")
    print(f"\nRole IDs: {role_ids}")
    print(f"Permission IDs: {permission_ids}")


if __name__ == "__main__":
    main()

