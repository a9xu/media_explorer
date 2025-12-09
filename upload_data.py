import mysql.connector
import pandas as pd
import ast
import re

# -----------------------------
# DB CONNECTION CONFIG
# -----------------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "workbench",
    "password": "StrongPW!123",
    "database": "team_project",  # change if needed
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


# -----------------------------
# HELPER: GET OR CREATE ROWS
# -----------------------------
def get_or_create_genre(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT id FROM genres WHERE name = %s", (name,))
    row = cur.fetchone()
    if row:
        cur.close()
        return row[0]

    cur.execute("INSERT INTO genres (name) VALUES (%s)", (name,))
    conn.commit()
    gid = cur.lastrowid
    cur.close()
    return gid


def get_or_create_artist(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT id FROM artists WHERE name = %s", (name,))
    row = cur.fetchone()
    if row:
        cur.close()
        return row[0]

    cur.execute("INSERT INTO artists (name) VALUES (%s)", (name,))
    conn.commit()
    aid = cur.lastrowid
    cur.close()
    return aid


def get_or_create_album(conn, title, year=None):
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM albums WHERE title = %s AND (year = %s OR (%s IS NULL AND year IS NULL))",
        (title, year, year),
    )
    row = cur.fetchone()
    if row:
        cur.close()
        return row[0]

    cur.execute("INSERT INTO albums (title, year) VALUES (%s, %s)", (title, year))
    conn.commit()
    alb_id = cur.lastrowid
    cur.close()
    return alb_id


def get_or_create_author(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT id FROM authors WHERE name = %s", (name,))
    row = cur.fetchone()
    if row:
        cur.close()
        return row[0]

    cur.execute("INSERT INTO authors (name) VALUES (%s)", (name,))
    conn.commit()
    auth_id = cur.lastrowid
    cur.close()
    return auth_id


def get_or_create_creator(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT id FROM creators WHERE name = %s", (name,))
    row = cur.fetchone()
    if row:
        cur.close()
        return row[0]

    cur.execute("INSERT INTO creators (name) VALUES (%s)", (name,))
    conn.commit()
    creator_id = cur.lastrowid
    cur.close()
    return creator_id


def get_or_create_book(conn, title, author_id, year=None):
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM books WHERE title = %s AND author_id = %s AND (year = %s OR (%s IS NULL AND year IS NULL))",
        (title, author_id, year, year),
    )
    row = cur.fetchone()
    if row:
        cur.close()
        return row[0]

    cur.execute(
        "INSERT INTO books (title, author_id, year, avg_rating) VALUES (%s, %s, %s, %s)",
        (title, author_id, year, None),
    )
    conn.commit()
    book_id = cur.lastrowid
    cur.close()
    return book_id


def get_or_create_movie(conn, title, year=None, imdb_rating=None, director_id=None):
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM movies WHERE title = %s AND (year = %s OR (%s IS NULL AND year IS NULL))",
        (title, year, year),
    )
    row = cur.fetchone()
    if row:
        cur.close()
        return row[0]

    cur.execute(
        "INSERT INTO movies (title, year, imdb_rating, director_id) VALUES (%s, %s, %s, %s)",
        (title, year, imdb_rating, director_id),
    )
    conn.commit()
    movie_id = cur.lastrowid
    cur.close()
    return movie_id


def get_or_create_song(conn, title, artist_id, album_id, popularity, year=None):
    cur = conn.cursor()
    cur.execute(
        """SELECT id FROM songs
           WHERE title = %s AND artist_id = %s AND album_id = %s""",
        (title, artist_id, album_id),
    )
    row = cur.fetchone()
    if row:
        cur.close()
        return row[0]

    cur.execute(
        """INSERT INTO songs (title, artist_id, album_id, spotify_popularity, year)
           VALUES (%s, %s, %s, %s, %s)""",
        (title, artist_id, album_id, popularity, year),
    )
    conn.commit()
    song_id = cur.lastrowid
    cur.close()
    return song_id


def get_or_create_item(conn, item_type, ref_id):
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM items WHERE item_type = %s AND ref_id = %s",
        (item_type, ref_id),
    )
    row = cur.fetchone()
    if row:
        cur.close()
        return row[0]

    cur.execute(
        "INSERT INTO items (item_type, ref_id) VALUES (%s, %s)",
        (item_type, ref_id),
    )
    conn.commit()
    item_id = cur.lastrowid
    cur.close()
    return item_id


def get_or_create_item_genre(conn, item_id, genre_id):
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM item_genres WHERE item_id = %s AND genre_id = %s",
        (item_id, genre_id),
    )
    row = cur.fetchone()
    if row:
        cur.close()
        return row[0]

    cur.execute(
        "INSERT INTO item_genres (item_id, genre_id) VALUES (%s, %s)",
        (item_id, genre_id),
    )
    conn.commit()
    ig_id = cur.lastrowid
    cur.close()
    return ig_id


def add_rating(conn, item_id, source, rating_value):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO ratings (item_id, source, rating) VALUES (%s, %s, %s)",
        (item_id, source, rating_value),
    )
    conn.commit()
    cur.close()


# -----------------------------
# LOAD BOOKS (Books.csv)
# -----------------------------
def load_books(books_csv, limit=20):
    df = pd.read_csv(books_csv, nrows=limit)
    conn = get_connection()

    for _, row in df.iterrows():
        title = str(row["Book-Title"])
        author_name = str(row["Book-Author"])

        # Year may be missing or non-int
        year = None
        try:
            year = int(row["Year-Of-Publication"])
        except Exception:
            year = None

        author_id = get_or_create_author(conn, author_name)
        book_id = get_or_create_book(conn, title, author_id, year)
        get_or_create_item(conn, "book", book_id)

    conn.close()
    print(f"Inserted up to {limit} books (with authors + items).")


# -----------------------------
# LOAD SONGS (song.csv)
# -----------------------------
def load_songs(song_csv, limit=20):
    df = pd.read_csv(song_csv, nrows=limit)
    conn = get_connection()

    for _, row in df.iterrows():
        title = str(row["track_name"])
        artists_field = str(row["artists"])
        main_artist_name = artists_field.split(";")[0].strip()

        album_name = str(row["album_name"])
        popularity = int(row["popularity"]) if not pd.isna(row["popularity"]) else 0

        # No year column in your sample → keep None
        year = None

        artist_id = get_or_create_artist(conn, main_artist_name)
        album_id = get_or_create_album(conn, album_name, year)
        song_id = get_or_create_song(conn, title, artist_id, album_id, popularity, year)
        item_id = get_or_create_item(conn, "song", song_id)

        # Genre from track_genre column (simple 1-genre case)
        if "track_genre" in df.columns:
            genre_name = str(row["track_genre"])
            if genre_name and genre_name != "nan":
                gid = get_or_create_genre(conn, genre_name)
                get_or_create_item_genre(conn, item_id, gid)

    conn.close()
    print(f"Inserted up to {limit} songs (with artists, albums, items, genres).")


# -----------------------------
# LOAD MOVIES (tmdb_5000_movies.csv + tmdb_5000_credits.csv)
# -----------------------------
def load_movies(movies_csv, credits_csv, limit=1000):
    movies_df = pd.read_csv(movies_csv, nrows=limit)
    # Handle BOM and encoding issues in credits CSV
    credits_df = pd.read_csv(credits_csv, encoding="utf-8-sig")

    # Create a lookup dictionary for credits by movie_id
    credits_lookup = {}
    for _, cred_row in credits_df.iterrows():
        movie_id = cred_row.get("movie_id")
        if pd.notna(movie_id):
            try:
                # Try to convert to int, skip if it fails
                movie_id_int = int(
                    float(movie_id)
                )  # Use float first to handle numeric strings
                credits_lookup[movie_id_int] = cred_row
            except (ValueError, TypeError):
                # Skip rows where movie_id can't be converted to int
                continue

    conn = get_connection()

    for _, row in movies_df.iterrows():
        title = str(row["title"])
        movie_id_tmdb = row.get("id")

        # Extract year from release_date (format: MM/DD/YYYY or YYYY-MM-DD)
        release_date = row.get("release_date", None)
        year = None
        if (
            pd.notna(release_date)
            and isinstance(release_date, str)
            and release_date.strip()
        ):
            try:
                # Try to parse different date formats
                if "/" in release_date:
                    # Format: MM/DD/YYYY
                    parts = release_date.split("/")
                    if len(parts) >= 3:
                        year = int(parts[2])
                elif "-" in release_date:
                    # Format: YYYY-MM-DD
                    year = int(release_date.split("-")[0])
                else:
                    # Try to extract first 4 digits if it's a different format
                    match = re.search(r"\d{4}", release_date)
                    if match:
                        year = int(match.group())
            except (ValueError, IndexError, AttributeError):
                year = None

        vote_avg = None
        if not pd.isna(row["vote_average"]):
            try:
                vote_avg = float(row["vote_average"])
            except Exception:
                vote_avg = None

        # Extract director from credits CSV
        director_id = None
        if pd.notna(movie_id_tmdb) and int(movie_id_tmdb) in credits_lookup:
            cred_row = credits_lookup[int(movie_id_tmdb)]
            crew_raw = cred_row.get("crew", "")

            if isinstance(crew_raw, str) and crew_raw.strip():
                try:
                    # crew is string like: "[{"job": "Director", "name": "James Cameron"}, ...]"
                    crew_list = ast.literal_eval(crew_raw)
                    for crew_member in crew_list:
                        if crew_member.get("job") == "Director":
                            director_name = crew_member.get("name")
                            if director_name:
                                director_id = get_or_create_creator(conn, director_name)
                                break  # Take the first director found
                except Exception:
                    # if parse fails, just skip director for this movie
                    pass

        movie_id = get_or_create_movie(conn, title, year, vote_avg, director_id)
        item_id = get_or_create_item(conn, "movie", movie_id)

        # Parse genres JSON-like field
        genres_raw = row.get("genres", "")
        if isinstance(genres_raw, str) and genres_raw.strip():
            try:
                # genres is string like: "[{"id": 28, "name": "Action"}, ...]"
                genres_list = ast.literal_eval(genres_raw)
                for g in genres_list:
                    gname = g.get("name")
                    if gname:
                        gid = get_or_create_genre(conn, gname)
                        get_or_create_item_genre(conn, item_id, gid)
            except Exception:
                # if parse fails, just skip genres for this movie
                pass

        # Store movie rating from vote_average into ratings table
        if vote_avg is not None:
            add_rating(conn, item_id, "tmdb_vote_average", vote_avg)

    conn.close()
    print(f"Inserted up to {limit} movies (with directors, items, genres, ratings).")


# -----------------------------
# LOAD BOOK RATINGS (Ratings.csv → ratings for book items)
# -----------------------------
def load_book_ratings(ratings_csv, books_csv, limit=20):
    """
    Use Ratings.csv (User-ID, ISBN, Book-Rating) + Books.csv to
    find the book info, ensure the book + item exist, then insert into ratings table.
    """
    ratings_df = pd.read_csv(ratings_csv, nrows=limit)
    books_df = pd.read_csv(books_csv)  # full, to find ISBN matches

    conn = get_connection()

    for _, row in ratings_df.iterrows():
        isbn = str(row["ISBN"])
        rating_val = None
        try:
            rating_val = float(row["Book-Rating"])
        except Exception:
            continue

        # Find matching book row in Books.csv by ISBN
        match = books_df[books_df["ISBN"] == isbn]
        if match.empty:
            # no book info for that ISBN in Books.csv → skip
            continue

        b = match.iloc[0]
        title = str(b["Book-Title"])
        author_name = str(b["Book-Author"])

        year = None
        try:
            year = int(b["Year-Of-Publication"])
        except Exception:
            year = None

        author_id = get_or_create_author(conn, author_name)
        book_id = get_or_create_book(conn, title, author_id, year)
        item_id = get_or_create_item(conn, "book", book_id)

        # Source label so you know where it came from
        add_rating(conn, item_id, "book_ratings_csv", rating_val)

    conn.close()
    print(f"Inserted up to {limit} book ratings (into ratings table).")


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    # Update these paths to where your CSVs actually are:
    BOOKS_CSV = "csvs/Books.csv"
    SONG_CSV = "csvs/song.csv"
    MOVIES_CSV = "csvs/tmdb_5000_movies.csv"
    CREDITS_CSV = "csvs/tmdb_5000_credits.csv"
    RATINGS_CSV = "csvs/Ratings.csv"

    # How many rows of each to insert
    N = 30

    load_books(BOOKS_CSV, limit=N)
    load_songs(SONG_CSV, limit=N)
    load_movies(MOVIES_CSV, CREDITS_CSV, limit=N)
    load_book_ratings(RATINGS_CSV, BOOKS_CSV, limit=N)

    print("✅ Done inserting sample data into your schema.")
