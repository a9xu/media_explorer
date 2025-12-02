from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Mysql@2005",
    "database": "team_project",
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/movies")
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
    )


@app.route("/movies/new", methods=["GET", "POST"])
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
        cur.close()
        conn.close()

        return redirect(url_for("list_movies"))

    return render_template("movie_form.html", movie=None)


@app.route("/movies/<int:movie_id>/edit", methods=["GET", "POST"])
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
        return redirect(url_for("list_movies"))

    cur.execute(
        "SELECT id, title, year, imdb_rating FROM movies WHERE id = %s", (movie_id,)
    )
    movie = cur.fetchone()
    cur.close()
    conn.close()

    if not movie:
        return "Movie not found", 404

    return render_template("movie_form.html", movie=movie)


@app.route("/movies/<int:movie_id>/delete", methods=["POST"])
def delete_movie(movie_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM movies WHERE id = %s", (movie_id,))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("list_movies"))


# ============================================
# TV SHOWS CRUD
# ============================================


@app.route("/tv-shows")
def list_tv_shows():
    """
    READ + FILTER
    - Shows first N TV shows
    - Optional ?title= filter (LIKE search)
    - Optional ?min_rating=
    """
    title_filter = request.args.get("title", default="", type=str)
    min_rating = request.args.get("min_rating", default=None, type=float)

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    query = "SELECT id, title, start_year, avg_rating FROM tv_shows WHERE 1=1"
    params = []

    if title_filter:
        query += " AND title LIKE %s"
        params.append(f"%{title_filter}%")

    if min_rating is not None:
        query += " AND avg_rating >= %s"
        params.append(min_rating)

    query += " ORDER BY start_year DESC LIMIT 50"

    cur.execute(query, params)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "tv_shows_list.html",
        tv_shows=rows,
        title_filter=title_filter,
        min_rating=min_rating if min_rating is not None else "",
    )


@app.route("/tv-shows/new", methods=["GET", "POST"])
def create_tv_show():
    if request.method == "POST":
        title = request.form.get("title")
        start_year = request.form.get("start_year") or None
        avg_rating = request.form.get("avg_rating") or None

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO tv_shows (title, start_year, avg_rating, creator_id) VALUES (%s, %s, %s, %s)",
            (title, start_year, avg_rating, None),  # no creator yet
        )

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("list_tv_shows"))

    return render_template("tv_show_form.html", tv_show=None)


@app.route("/tv-shows/<int:tv_show_id>/edit", methods=["GET", "POST"])
def edit_tv_show(tv_show_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        title = request.form.get("title")
        start_year = request.form.get("start_year") or None
        avg_rating = request.form.get("avg_rating") or None

        cur.execute(
            "UPDATE tv_shows SET title = %s, start_year = %s, avg_rating = %s WHERE id = %s",
            (title, start_year, avg_rating, tv_show_id),
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("list_tv_shows"))

    cur.execute(
        "SELECT id, title, start_year, avg_rating FROM tv_shows WHERE id = %s",
        (tv_show_id,),
    )
    tv_show = cur.fetchone()
    cur.close()
    conn.close()

    if not tv_show:
        return "TV Show not found", 404

    return render_template("tv_show_form.html", tv_show=tv_show)


@app.route("/tv-shows/<int:tv_show_id>/delete", methods=["POST"])
def delete_tv_show(tv_show_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM tv_shows WHERE id = %s", (tv_show_id,))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("list_tv_shows"))


# ============================================
# SONGS CRUD
# ============================================


@app.route("/songs")
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
    )


@app.route("/songs/new", methods=["GET", "POST"])
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
        cur.close()
        conn.close()

        return redirect(url_for("list_songs"))

    return render_template("song_form.html", song=None)


@app.route("/songs/<int:song_id>/edit", methods=["GET", "POST"])
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
        return redirect(url_for("list_songs"))

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


@app.route("/songs/<int:song_id>/delete", methods=["POST"])
def delete_song(song_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM songs WHERE id = %s", (song_id,))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("list_songs"))


# ============================================
# BOOKS CRUD
# ============================================


@app.route("/books")
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
    )


@app.route("/books/new", methods=["GET", "POST"])
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
        cur.close()
        conn.close()

        return redirect(url_for("list_books"))

    return render_template("book_form.html", book=None)


@app.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
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
        return redirect(url_for("list_books"))

    cur.execute(
        "SELECT id, title, year, avg_rating FROM books WHERE id = %s", (book_id,)
    )
    book = cur.fetchone()
    cur.close()
    conn.close()

    if not book:
        return "Book not found", 404

    return render_template("book_form.html", book=book)


@app.route("/books/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM books WHERE id = %s", (book_id,))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("list_books"))


if __name__ == "__main__":
    app.run(debug=True)
