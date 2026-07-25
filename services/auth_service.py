from models import User
from werkzeug.security import check_password_hash

def login(email: str, password: str) -> User | None:
    user = User.query.filter_by(email=email.lower()).first()
    if user and check_password_hash(user.password_hash, password):
        return user
    return None