import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, ColumnDefault

from meta import app as application, db

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, unique=True)
    user_id = db.Column(db.Integer)
    username = db.Column(db.String(100))
    role = db.Column(db.String(30))
    is_banned = db.Column(db.Boolean)
    end_ban_date = db.Column(db.DateTime, nullable=True)
    reputation = db.Column(db.Integer)
    profile_image = db.Column(db.String(200))
    profile_link = db.Column(db.String(200))

    def __init__(self, account_id, user_id, username, reputation, profile_image, profile_link, role="user", is_banned=False):
        self.account_id = account_id
        self.user_id = user_id
        self.username = username
        self.reputation = reputation
        self.profile_image = profile_image
        self.profile_link = profile_link
        self.role = role
        self.is_banned = is_banned

    def __repr__(self):
        return '<User %r>' % str(self.id)