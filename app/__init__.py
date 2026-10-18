from pathlib import Path

from dotenv import load_dotenv
from flask import Flask


def create_app(config: dict | None = None) -> Flask:
    load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=False)
    app = Flask(__name__, instance_path=str(Path(__file__).resolve().parent.parent / "instance"))
    app.json.sort_keys = False
    app.config.update(config or {})

    from . import db
    from .account import bp as account_bp
    from .admin import bp as admin_bp
    from .routes import bp

    db.init_app(app)
    app.register_blueprint(bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(admin_bp)
    return app
