import hashlib
from dataclasses import dataclass

from flask_login import login_user

from app.models import User


@dataclass
class LoginStatus:
    SUCCESS = 0
    USER_NOT_FOUND = 1
    EMPTY_FIELDS = 2


def check_password_hash(user_password: str, password: str):
    return hashlib.sha512(password.encode()).hexdigest() == user_password


def auth_user(login: str, password: str):
    if login and password:
        user = User.query.filter_by(login=login).first()
        if not user or not check_password_hash(user.password, password):
            return LoginStatus.USER_NOT_FOUND
        else:
            login_user(user)
            return LoginStatus.SUCCESS
    return LoginStatus.EMPTY_FIELDS


