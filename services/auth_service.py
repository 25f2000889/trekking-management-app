from models import User
from db import db
from enums import UserRole, UserStatus
from werkzeug.security import check_password_hash, generate_password_hash

def login(email: str, password: str) -> User | None:
    user = db.session.query(User).filter_by(email=email.lower()).first()
    if user and check_password_hash(user.password_hash, password):
        return user
    return None

def register(first_name: str, last_name: str, email: str, password: str, role: UserRole, status: UserStatus = UserStatus.ACTIVE) -> User | Exception:
    if db.session.query(User).filter_by(email=email.lower()).first():
        return Exception("Email already exists")

    new_user = User(
        first_name=first_name,
        last_name=last_name,
        email=email.lower(),
        password_hash=generate_password_hash(password),
        role=role,
        status=status
    )

    db.session.add(new_user)
    
    try:
        db.session.commit()
        return new_user
    except Exception as e:
        db.session.rollback()
        return e