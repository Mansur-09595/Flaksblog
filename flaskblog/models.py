from itsdangerous import TimedJSONWebSignatureSerializer
from flaskblog import db, login_manager, app
from flask_login import UserMixin
from datetime import datetime

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
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    avatar = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(20), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    admin = db.Column(db.Boolean(), default=False)

    def get_reset_token(self, expires_sec=600):
        token = TimedJSONWebSignatureSerializer(app.config['SECRET_KEY'], expires_sec)
        return token.dumps({'user_id': self.id}).decode('utf-8')


    @staticmethod
    def verify_token_reset(token):
        s = TimedJSONWebSignatureSerializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)


    def __repr__(self):
        return self.username

class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


    def __repr__(self):
        return self.title

#Добавление и покупка товара БД
class Item(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    titles = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer(), nullable=False)
    isActive = db.Column(db.Boolean(), default=True)

    def __repr__(self):
        return self.titles