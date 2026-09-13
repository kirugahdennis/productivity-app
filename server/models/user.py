from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property

from server.extensions import db, bcrypt


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False, index=True)
    _password_hash = db.Column("password_hash", db.String, nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    journal_entries = db.relationship(
        "JournalEntry",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="(JournalEntry.created_at.desc(), JournalEntry.id.desc())",
    )

    @hybrid_property
    def password_hash(self):
        raise AttributeError("password_hash is not a readable attribute")

    @password_hash.setter
    def password_hash(self, password):
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        self._password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)

    @validates("username")
    def validate_username(self, key, username):
        if not username or not username.strip():
            raise ValueError("Username cannot be empty")
        return username.strip()

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
        }

    def __repr__(self):
        return f"<User {self.id}: {self.username}>"