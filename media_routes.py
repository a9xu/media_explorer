"""Media CRUD routes (movies, songs, books)."""

from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_connection
from auth_decorators import permission_required
from auth_helpers import get_user_permissions
from audit_helpers import log_action_from_session

# Create a Blueprint for media routes
media_bp = Blueprint("media", __name__)


def get_user_permissions_dict():
    """Get current user's permissions as a dictionary for template use."""
    if "user_id" not in session:
        return {}
    permissions = get_user_permissions(session["user_id"])
    return {perm["name"]: True for perm in permissions}


# ============================================
# MOVIES CRUD
# ============================================


@media_bp.route("/movies")
@permission_required("read")
def list_movies():
    """
    READ + FILTER
    - Shows first N movies
    - Optional ?title= filter (LIKE search)
    - Optional ?min_rating=
    """
    title_filter = request.args.get("title", default="", type=str)
    min_rating = request.args.get("min_rating", default=None, type=float)

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    query = "SELECT id, title, year, imdb_rating FROM movies WHERE 1=1"
    params = []

    if title_filter:
        query += " AND title LIKE %s"
        params.append(f"%{title_filter}%")

    if min_rating is not None:
        query += " AND imdb_rating >= %s"
        params.append(min_rating)

    query += " ORDER BY year DESC LIMIT 50"

    cur.execute(query, params)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "movies_list.html",
        movies=rows,
        title_filter=title_filter,
        min_rating=min_rating if min_rating is not None else "",
        permissions=get_user_permissions_dict(),
    )


@media_bp.route("/movies/new", methods=["GET", "POST"])
@permission_required("create")
def create_movie():
    if request.method == "POST":
        title = request.form.get("title")
        year = request.form.get("year") or None
        imdb_rating = request.form.get("imdb_rating") or None

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO movies (title, year, imdb_rating, director_id) VALUES (%s, %s, %s, %s)",
            (title, year, imdb_rating, None),  # no director yet
        )

        conn.commit()
        movie_id = cur.lastrowid
        cur.close()
        conn.close()

        log_action_from_session(f"Created movie: {title} (ID: {movie_id})")

        return redirect(url_for("media.list_movies"))

    return render_template("movie_form.html", movie=None)


@media_bp.route("/movies/<int:movie_id>/edit", methods=["GET", "POST"])
@permission_required("update")
def edit_movie(movie_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        title = request.form.get("title")
        year = request.form.get("year") or None
        imdb_rating = request.form.get("imdb_rating") or None

        cur.execute(
            "UPDATE movies SET title = %s, year = %s, imdb_rating = %s WHERE id = %s",
            (title, year, imdb_rating, movie_id),
        )
        conn.commit()
        cur.close()
        conn.close()

        log_action_from_session(f"Updated movie: {title} (ID: {movie_id})")

        return redirect(url_for("media.list_movies"))

    cur.execute(
        "SELECT id, title, year, imdb_rating FROM movies WHERE id = %s", (movie_id,)
    )
    movie = cur.fetchone()
    cur.close()
    conn.close()

    if not movie:
        return "Movie not found", 404

    return render_template("movie_form.html", movie=movie)


@media_bp.route("/movies/<int:movie_id>/delete", methods=["POST"])
@permission_required("delete")
def delete_movie(movie_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # Get movie title before deleting for audit log
    cur.execute("SELECT title FROM movies WHERE id = %s", (movie_id,))
    movie = cur.fetchone()
    movie_title = movie["title"] if movie else f"ID {movie_id}"

    cur.execute("DELETE FROM movies WHERE id = %s", (movie_id,))
    conn.commit()
    cur.close()
    conn.close()

    log_action_from_session(f"Deleted movie: {movie_title} (ID: {movie_id})")

    return redirect(url_for("media.list_movies"))


# ============================================
# SONGS CRUD
# ============================================


@media_bp.route("/songs")
@permission_required("read")
def list_songs():
    """
    READ + FILTER
    - Shows first N songs
    - Optional ?title= filter (LIKE search)
    - Optional ?min_popularity=
    """
    title_filter = request.args.get("title", default="", type=str)
    min_popularity = request.args.get("min_popularity", default=None, type=int)

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    query = "SELECT id, title, year, spotify_popularity FROM songs WHERE 1=1"
    params = []

    if title_filter:
        query += " AND title LIKE %s"
        params.append(f"%{title_filter}%")

    if min_popularity is not None:
        query += " AND spotify_popularity >= %s"
        params.append(min_popularity)

    query += " ORDER BY year DESC LIMIT 50"

    cur.execute(query, params)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "songs_list.html",
        songs=rows,
        title_filter=title_filter,
        min_popularity=min_popularity if min_popularity is not None else "",
        permissions=get_user_permissions_dict(),
    )


@media_bp.route("/songs/new", methods=["GET", "POST"])
@permission_required("create")
def create_song():
    if request.method == "POST":
        title = request.form.get("title")
        year = request.form.get("year") or None
        spotify_popularity = request.form.get("spotify_popularity") or None

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO songs (title, artist_id, album_id, spotify_popularity, year) VALUES (%s, %s, %s, %s, %s)",
            (title, None, None, spotify_popularity, year),  # no artist/album yet
        )

        conn.commit()
        song_id = cur.lastrowid
        cur.close()
        conn.close()

        log_action_from_session(f"Created song: {title} (ID: {song_id})")

        return redirect(url_for("media.list_songs"))

    return render_template("song_form.html", song=None)


@media_bp.route("/songs/<int:song_id>/edit", methods=["GET", "POST"])
@permission_required("update")
def edit_song(song_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        title = request.form.get("title")
        year = request.form.get("year") or None
        spotify_popularity = request.form.get("spotify_popularity") or None

        cur.execute(
            "UPDATE songs SET title = %s, year = %s, spotify_popularity = %s WHERE id = %s",
            (title, year, spotify_popularity, song_id),
        )
        conn.commit()
        cur.close()
        conn.close()

        log_action_from_session(f"Updated song: {title} (ID: {song_id})")

        return redirect(url_for("media.list_songs"))

    cur.execute(
        "SELECT id, title, year, spotify_popularity FROM songs WHERE id = %s",
        (song_id,),
    )
    song = cur.fetchone()
    cur.close()
    conn.close()

    if not song:
        return "Song not found", 404

    return render_template("song_form.html", song=song)


@media_bp.route("/songs/<int:song_id>/delete", methods=["POST"])
@permission_required("delete")
def delete_song(song_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # Get song title before deleting for audit log
    cur.execute("SELECT title FROM songs WHERE id = %s", (song_id,))
    song = cur.fetchone()
    song_title = song["title"] if song else f"ID {song_id}"

    cur.execute("DELETE FROM songs WHERE id = %s", (song_id,))
    conn.commit()
    cur.close()
    conn.close()

    log_action_from_session(f"Deleted song: {song_title} (ID: {song_id})")

    return redirect(url_for("media.list_songs"))


# ============================================
# BOOKS CRUD
# ============================================


@media_bp.route("/books")
@permission_required("read")
def list_books():
    """
    READ + FILTER
    - Shows first N books
    - Optional ?title= filter (LIKE search)
    - Optional ?min_rating=
    """
    title_filter = request.args.get("title", default="", type=str)
    min_rating = request.args.get("min_rating", default=None, type=float)

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    query = "SELECT id, title, year, avg_rating FROM books WHERE 1=1"
    params = []

    if title_filter:
        query += " AND title LIKE %s"
        params.append(f"%{title_filter}%")

    if min_rating is not None:
        query += " AND avg_rating >= %s"
        params.append(min_rating)

    query += " ORDER BY year DESC LIMIT 50"

    cur.execute(query, params)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "books_list.html",
        books=rows,
        title_filter=title_filter,
        min_rating=min_rating if min_rating is not None else "",
        permissions=get_user_permissions_dict(),
    )


@media_bp.route("/books/new", methods=["GET", "POST"])
@permission_required("create")
def create_book():
    if request.method == "POST":
        title = request.form.get("title")
        year = request.form.get("year") or None
        avg_rating = request.form.get("avg_rating") or None

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO books (title, author_id, year, avg_rating) VALUES (%s, %s, %s, %s)",
            (title, None, year, avg_rating),  # no author yet
        )

        conn.commit()
        book_id = cur.lastrowid
        cur.close()
        conn.close()

        log_action_from_session(f"Created book: {title} (ID: {book_id})")

        return redirect(url_for("media.list_books"))

    return render_template("book_form.html", book=None)


@media_bp.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
@permission_required("update")
def edit_book(book_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        title = request.form.get("title")
        year = request.form.get("year") or None
        avg_rating = request.form.get("avg_rating") or None

        cur.execute(
            "UPDATE books SET title = %s, year = %s, avg_rating = %s WHERE id = %s",
            (title, year, avg_rating, book_id),
        )
        conn.commit()
        cur.close()
        conn.close()

        log_action_from_session(f"Updated book: {title} (ID: {book_id})")

        return redirect(url_for("media.list_books"))

    cur.execute(
        "SELECT id, title, year, avg_rating FROM books WHERE id = %s", (book_id,)
    )
    book = cur.fetchone()
    cur.close()
    conn.close()

    if not book:
        return "Book not found", 404

    return render_template("book_form.html", book=book)


@media_bp.route("/books/<int:book_id>/delete", methods=["POST"])
@permission_required("delete")
def delete_book(book_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # Get book title before deleting for audit log
    cur.execute("SELECT title FROM books WHERE id = %s", (book_id,))
    book = cur.fetchone()
    book_title = book["title"] if book else f"ID {book_id}"

    cur.execute("DELETE FROM books WHERE id = %s", (book_id,))
    conn.commit()
    cur.close()
    conn.close()

    log_action_from_session(f"Deleted book: {book_title} (ID: {book_id})")

    return redirect(url_for("media.list_books"))
