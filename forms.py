from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', 
        validators=[DataRequired(message="Это поле обязательно для заполнения"), Length(min=2, max=20)])
    email = StringField('Электронная почта', 
        validators=[DataRequired(message="Это поле обязательно для заполнения"), Email()])
    password = PasswordField('Пароль', 
        validators=[DataRequired(message="Это поле обязательно для заполнения"), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль',
        validators=[DataRequired(message="Это поле обязательно для заполнения"), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Это имя пользователя уже занято.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Этот email уже зарегистрирован.')
        

class LoginForm(FlaskForm):
    email = StringField('Электронная почта', 
        validators=[DataRequired(message="Это поле обязательно для заполнения")])
    password = PasswordField('Пароль', 
        validators=[DataRequired(message="Это поле обязательно для заполнения")])
    submit = SubmitField('Войти')
