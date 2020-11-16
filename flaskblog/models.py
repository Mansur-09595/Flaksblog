from flaskblog import db


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

class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    #avatar = db.Column(db.String(20), nullable=False, default='dafault.jpg')
    password = db.Column(db.String(20), nullable=False)