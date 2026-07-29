from flask import Flask, session
from enums import UserRole, UserStatus, TrekDifficulty, TrekStatus, TrekBookingStatus
from config import Config
from db import db

from models.user import User
from routes.web.auth import auth_bp
from routes.web.admin import admin_bp
from routes.web.staff import staff_bp
from routes.web.shared import shared_bp


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    @app.context_processor
    def inject_current_user_and_enums():
        user_id = session.get("user_id")

        user = db.session.get(User, user_id) if user_id else None
        return {
            "current_user": user,
            "enums": {
                "UserRole": UserRole,
                "UserStatus": UserStatus,
                "TrekDifficulty": TrekDifficulty,
                "TrekStatus": TrekStatus,
                "TrekBookingStatus": TrekBookingStatus,
            }
        }

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(shared_bp)

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)