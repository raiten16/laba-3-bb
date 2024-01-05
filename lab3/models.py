from lab3 import db
from datetime import datetime

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=False)

    records = db.relationship("Record", back_populates="user", lazy="dynamic")

    default_currency_id = db.Column(db.Integer, db.ForeignKey("currency.id"))
    default_currency = db.relationship("Currency", foreign_keys=[default_currency_id])
    def __repr__(self):
        return f'User {self.username}'

class Currency(db.Model):
    __tablename__ = "currency"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False, unique=False)
    symbol = db.Column(db.String(length=5), nullable=False, unique=False)

    def __repr__(self):
        return f'Currency {self.name}'

class Category(db.Model):
    __tablename__ = "category"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False, unique=False)

    record = db.relationship("Record", back_populates="category", lazy="dynamic")
class Record(db.Model):
    __tablename__ = "record"

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=False, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.Float(precision=2), unique=False, nullable=False)
    currency_id = db.Column(db.Integer, db.ForeignKey("currency.id"), unique=False, nullable=False)
    user = db.relationship("User", back_populates="records")
    category = db.relationship("Category", back_populates="record")