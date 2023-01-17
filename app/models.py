from app import db, manager
from flask_login import UserMixin


class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.BigInteger, nullable=False)
    api_id = db.Column(db.Integer, nullable=True)
    api_hash = db.Column(db.Integer, nullable=False)
    blocked = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    session = db.Column(db.String(512), nullable=False)


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    def __init__(self, login: str, password: str):
        self.login = login
        self.password = password


class CodeRequest(db.Model):
    __tablename__ = 'code_requests'

    id = db.Column(db.Integer, primary_key=True)
    api_id = db.Column(db.Integer, nullable=True)
    api_hash = db.Column(db.Integer, nullable=False)
    code = db.Column(db.Integer)
    code_hash = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.BigInteger, nullable=False)

    def __repr__(self):
        return f"{self.id}\n{self.code}\n{self.code_hash}\n{self.api_id}\n{self.api_id}\n{self.phone_number}"

    def json(self):
        return {
            "id": self.id,
            "api_id": self.api_id,
            "api_hash": self.api_hash,
            "code": self.code,
            "code_hash": self.code_hash
        }


@manager.user_loader
def load_user(user_id: int):
    return User.query.get(user_id)