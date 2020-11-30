from flaskblog import db, login_manager
from flask_login import UserMixin


class Flight(db.Model):
    __tablename__ = "blog"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    mail = db.Column(db.String, nullable=False)
    commen = db.Column(db.String, nullable=False)

class Passenger(db.Model):
    __tablename__ = "blogs"
    id = db.Column(db.Integer, primary_key=True)
    names = db.Column(db.String, nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey("blog.id"), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    avatar = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(20), nullable=False)


    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"