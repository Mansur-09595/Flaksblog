import datetime
import requests
import bcrypt
import os
import secrets

from PIL import Image
from flask import render_template, url_for, redirect, flash, request, abort
from flaskblog import app, db, brycpt
from flaskblog.forms import RegistrationForm, LoginForm, AccountUpdateForm, PostForm
from flaskblog.models import Flight, User, Post
from flask_login import login_user, current_user, logout_user, login_required

WEATHER_TOKEN = '1e35d2f152ba4f4f8e0175010202109'


@app.route('/')
def about():
    posts = Post.query.all()
    return render_template('about.html', posts=posts)


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
    posts = Post.query.all()
    if request.method == "POST":
        name = request.form.get('name')
        mail = request.form.get('mail')
        commen = request.form.get('commen')
        comm = Flight(name=name, mail=mail, commen=commen)
        db.session.add(comm)
    flights = Flight.query.all()
    db.session.commit()
    return render_template("index.html", flights=flights, posts=posts)


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
            return redirect(next_page) if next_page else redirect(url_for('about'))
        else:
            flash(f'Войти не удалось. Пожалуйста, проверьте почту и пароль', 'danger')
    return render_template('login.html', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('about'))


def save_avatar(avatar):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(avatar.filename)
    avatar_name = random_hex + f_ext
    avatar_path = os.path.join(app.root_path, 'static/profile_images', avatar_name)
    avatar_size = (125, 125)
    i = Image.open(avatar)
    i.thumbnail(avatar_size)
    i.save(avatar_path)
    return avatar_name


@app.route('/account/<username>',  methods=['GET', 'POST'])
@login_required
def account(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = AccountUpdateForm()
    if form.validate_on_submit():
        if form.avatar.data:
            avatar_file = save_avatar(form.avatar.data)
            current_user.avatar = avatar_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Данные пользователя были обновлены!', 'success')
        return redirect(url_for('about'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    avatar = url_for('static', filename='profile_images/' + current_user.avatar)
    return render_template('account.html', form=form, avatar=avatar, user=user)


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Пост был создан!', 'success')
        redirect(url_for('index'))
    return render_template('create_post.html', form=form, legend='Создать пост')


@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)


@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Пост был обновлен!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', form=form, legend='Изменить пост')


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Пост был удален!', 'success')
    return redirect(url_for('index'))