## Project name:

    Ultimate Media Explorer

## Short app description

The app lets users search movies, songs, and books, compare them side-by-side, and discover similar content using static datasets stored in a relational database. The app also stores detailed information about each piece of media, such as ratings, genres, release year, and creators. Users can view summaries of items, explore related titles, and identify similarities across different media types. By unifying movies, songs, and books under one system, the app provides a centralized hub for media exploration, making it easy to analyze trends, compare metadata, and discover new content based on personal preferences.

## ER-Diagram

![Er_diagram](CS3620%20Team%20Project.png)

## Recording


![Recording](final_recording.mp4)

## Authentication & Permissions Setup

### Initial Setup

1. **Initialize Roles and Permissions:**

   ```bash
   python init_roles_permissions.py
   ```

   This creates:

   - 4 permissions: `read`, `create`, `update`, `delete`
   - 2 roles:
     - `user`: Can only read (view media)
     - `admin`: Can do all operations (read, create, update, delete)

2. **Assign Roles to Users:**

   ```bash
   # Assign 'user' role to a user
   python assign_user_role.py <username> user add

   # Assign 'admin' role to a user
   python assign_user_role.py <username> admin add

   # Remove a role from a user
   python assign_user_role.py <username> user remove
   ```

### Permission System

All CRUD operations for movies, songs, and books are protected by permissions:

- **Read**: Required to view lists and details (all users have this)
- **Create**: Required to add new items (admin only)
- **Update**: Required to edit existing items (admin only)
- **Delete**: Required to delete items (admin only)

Users with the `user` role can only view media. Users with the `admin` role can perform all operations.

The UI automatically hides create/edit/delete buttons for users who don't have the required permissions.
