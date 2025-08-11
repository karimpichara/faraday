from flask_login import UserMixin
from sqlalchemy import UniqueConstraint
from werkzeug.security import check_password_hash, generate_password_hash

from src.models import BaseModel, db


class User(UserMixin, BaseModel):
    __tablename__ = "users"
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    roles = db.relationship(
        "Role", secondary="user_roles", backref=db.backref("users"), lazy="subquery"
    )
    empresas = db.relationship(
        "EmpresasExternasToa",
        secondary="user_empresas",
        backref=db.backref("users"),
        lazy="subquery",
    )

    def __init__(
        self,
        username,
        password,
    ):
        self.username = username
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def get_id(self):
        return str(self.id)

    @classmethod
    def get_by_username(cls, username):
        return cls.active_records().filter_by(username=username).first()

    @classmethod
    def authenticate(cls, username, password) -> bool:
        user = cls.get_by_username(username)
        return bool(user and user.verify_password(password))

    def __repr__(self):
        return f"<User {self.username}>"

    def has_roles(self, role_list: list) -> bool:
        return any(role in [x.name for x in self.roles] for role in role_list)


class Role(BaseModel):
    __tablename__ = "roles"
    name = db.Column(db.String(50), unique=True)


class UserRole(BaseModel):
    __tablename__ = "user_roles"
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id", ondelete="CASCADE"))
    role_id = db.Column(db.Integer(), db.ForeignKey("roles.id", ondelete="CASCADE"))

    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_role"),)


class UserEmpresa(BaseModel):
    __tablename__ = "user_empresas"
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id", ondelete="CASCADE"))
    empresa_id = db.Column(
        db.Integer(), db.ForeignKey("empresas_externas_toa.id", ondelete="CASCADE")
    )

    __table_args__ = (
        UniqueConstraint("user_id", "empresa_id", name="uq_user_empresa"),
    )
