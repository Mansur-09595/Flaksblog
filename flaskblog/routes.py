import datetime
import requests

from flask import render_template, url_for, redirect, flash, request
from flaskblog import app, brycpt, db
from flaskblog.forms import RegistrationForm, LoginForm
from flaskblog.models import Flight, User


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


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = brycpt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Аккаунт  создан {form.username.data}! Вы можете войти в свой аккаунт!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)



@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', form=form)