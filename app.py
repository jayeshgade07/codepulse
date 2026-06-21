import os
from flask import Flask
from models import db
from routes import main_bp


def create_app():
    app = Flask(__name__)

    # Config
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///codepulse.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Init extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(main_bp)

    # Make enumerate available in Jinja2 templates
    app.jinja_env.globals["enumerate"] = enumerate

    # Create tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
