import datetime
import requests
import bcrypt

from flask import render_template, url_for, redirect, flash, request
from flaskblog import app, db, brycpt
from flaskblog.forms import RegistrationForm, LoginForm
from flaskblog.models import Flight, User
from flask_login import login_user, current_user, logout_user, login_required

WEATHER_TOKEN = '1e35d2f152ba4f4f8e0175010202109'


@app.route('/')
def about():
    return render_template('about.html')


def weather_by_city():
    weather_url = 'http://api.worldweatheronline.com/premium/v1/weather.ashx'
    params = {
        'key': WEATHER_TOKEN,
        'q': 'Grozny, Russia',
        'format': 'json',
        'num_of_days': 1,
        'lang': 'ru'
    }
    result = requests.get(weather_url, params=params)
    return result.json()


@app.route("/weather", methods=["GET","POST"])
def weather():
    weather = weather_by_city()
    degrees = {
        9: weather['data']['weather'][0]['hourly'][3]['tempC'],
        12: weather['data']['weather'][0]['hourly'][4]['tempC'],
        15: weather['data']['weather'][0]['hourly'][5]['tempC'],
        18: weather['data']['weather'][0]['hourly'][6]['tempC'],
        21: weather['data']['weather'][0]['hourly'][7]['tempC']
    }
    day = weather[ 'data']['weather'][0]['date']
    msg = f'Сегодня {day} погода ожидается следующая: в 9:00 {degrees[9]}°C,\
        в 12:00 {degrees[12]}°C в 15:00 {degrees[15]}°C, в 18:00 {degrees[18]}°C, в 21:00 {degrees[21]}°C'
    time = time=datetime.datetime.strptime('09:12AM', '%I:%M%p').time()
    return render_template( "weather.html", text=msg, time=time)


@app.route("/index", methods=["GET","POST"])
def index():
    if request.method == "POST":
        name = request.form.get('name')
        mail = request.form.get('mail')
        commen = request.form.get('commen')
        comm = Flight(name=name, mail=mail, commen=commen)
        db.session.add(comm)
    flights = Flight.query.all()
    db.session.commit()
    return render_template("index.html", flights=flights)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('about'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = brycpt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Аккаунт  создан {form.username.data}! Вы можете войти в свой аккаунт!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('about'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and brycpt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('account'))
        else:
            flash(f'Войти не удалось. Пожалуйста, проверьте почту и пароль', 'danger')
    return render_template('login.html', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('about'))


@app.route("/account")
@login_required
def account():
    return render_template('account.html')