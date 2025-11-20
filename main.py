import mysql.connector
import pandas as pd

DB_CONFIG = {
    "host": "localhost",
    "user": "workbench",
    "password": "StrongPW!123",
    "database": "media_explorer",
}

TABLES = [
    "genres",
    "creators",
    "artists",
    "authors",
    "albums",
    "movies",
    "tv_shows",
    "songs",
    "books",
    "items",
    "item_genres",
    "ratings"
]


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def print_first_ten_rows():
    conn = get_connection()

    print("\n============================")
    print("  FIRST TEN ROWS OF TABLES")
    print("============================\n")

    for table in TABLES:
        print(f"--- {table.upper()} ---")

        try:
            df = pd.read_sql(f"SELECT * FROM {table} LIMIT 10;", conn)
            print(df if not df.empty else "(No rows)")
        except Exception as e:
            print(f"Error reading {table}: {e}")

        print("\n")

    conn.close()


if __name__ == "__main__":
    print_first_ten_rows()
