from app import create_app
from db import db
from enums import UserRole
from models import *
from werkzeug.security import generate_password_hash

app = create_app()

def create_admin():
    admin = User.query.filter_by(role=UserRole.ADMIN).first()

    if admin:
        print("Admin user already exists.")
        return
    
    admin = User(
        first_name='Admin',
        last_name='User',
        email='admin@trekflow.com',
        password_hash=generate_password_hash('Admin@123'),
        role=UserRole.ADMIN,
    )

    db.session.add(admin)
    db.session.commit()

    print("Admin user created successfully.")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin()