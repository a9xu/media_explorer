"""Main routes."""

from flask import Blueprint, render_template
from auth_helpers import get_current_user

# Create a Blueprint for main routes
main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Home page."""
    user = get_current_user()
    return render_template("index.html", user=user)
