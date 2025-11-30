USE team_project;

-- Enable foreign keys
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================
-- MASTER TABLES
-- ============================================

CREATE TABLE genres (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE creators (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE artists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE authors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE albums (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    year INT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- MEDIA ENTITY TABLES
-- ============================================

CREATE TABLE movies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    year INT,
    imdb_rating DECIMAL(3,1),
    director_id INT,
    FOREIGN KEY (director_id) REFERENCES creators(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE tv_shows (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    start_year INT,
    avg_rating DECIMAL(3,1),
    creator_id INT,
    FOREIGN KEY (creator_id) REFERENCES creators(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE songs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    artist_id INT,
    album_id INT,
    spotify_popularity INT,
    year INT,
    FOREIGN KEY (artist_id) REFERENCES artists(id),
    FOREIGN KEY (album_id) REFERENCES albums(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author_id INT,
    year INT,
    avg_rating DECIMAL(3,2),
    FOREIGN KEY (author_id) REFERENCES authors(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- UNIFIED ITEMS TABLE
-- ============================================

CREATE TABLE items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_type ENUM('movie','tv','song','book') NOT NULL,
    ref_id INT NOT NULL   -- ID from movies, tv_shows, songs, or books
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- RELATIONSHIP TABLES
-- ============================================

CREATE TABLE item_genres (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    genre_id INT NOT NULL,
    FOREIGN KEY (item_id) REFERENCES items(id),
    FOREIGN KEY (genre_id) REFERENCES genres(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE ratings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    source VARCHAR(100) NOT NULL,
    rating DECIMAL(3,2),
    FOREIGN KEY (item_id) REFERENCES items(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;