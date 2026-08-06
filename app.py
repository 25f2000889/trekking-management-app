from flask import Flask, session
from flask_jwt_extended import JWTManager
from enums import UserRole, UserStatus, TrekDifficulty, TrekStatus, TrekBookingStatus
from config import Config
from db import db

from models.user import User
from routes.web.auth import auth_bp
from routes.web.admin import admin_bp
from routes.web.staff import staff_bp
from routes.web.shared import shared_bp
from routes.web.trekker import trekker_bp

from routes.api.auth import api_auth_bp
from routes.api.bookings import api_bookings_bp
from routes.api.treks import api_treks_bp
from routes.api.users import api_users_bp


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    jwt = JWTManager(app)

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
    app.register_blueprint(trekker_bp)
    app.register_blueprint(shared_bp)

    app.register_blueprint(api_auth_bp)
    app.register_blueprint(api_treks_bp)
    app.register_blueprint(api_users_bp)
    app.register_blueprint(api_bookings_bp)

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)