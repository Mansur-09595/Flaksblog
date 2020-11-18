from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User
import email_validator

class RegistrationForm(FlaskForm):
    username = StringField("Логин", validators=[DataRequired(message="Это поле не может быть пустым!"), Length(min=2, max=20, message="Длина")])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    confirm_password = PasswordField("Потверждение пароля", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Регистрация")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Этот логин занят. Пожалуйста, выберите другое.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Этот email существует в базе. Пожалуйста, выберите другое.')

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember = BooleanField("Запомнить")
    submit = SubmitField("Войти")