"""Database connection and configuration."""

import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Mysql@2005",
    "database": "team_project",
}


def get_connection():
    """Get a database connection."""
    return mysql.connector.connect(**DB_CONFIG)
