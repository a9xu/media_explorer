from flask import Flask
from main_routes import main_bp
from auth_routes import auth_bp
from media_routes import media_bp

app = Flask(__name__)
app.secret_key = (
    "your-secret-key-change-this-in-production"  # Change this in production!
)

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(media_bp)

if __name__ == "__main__":
    app.run(debug=True)
