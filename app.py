from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "workbench",
    "password": "StrongPW!123",
    "database": "media_explorer",
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

    cur.execute("SELECT id, title, year, imdb_rating FROM movies WHERE id = %s", (movie_id,))
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


if __name__ == "__main__":
    app.run(debug=True)
