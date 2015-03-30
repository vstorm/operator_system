from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, BooleanField
from wtforms.validators import Required, EqualTo, Length, Email


class LoginForm(Form):
    username = TextField('username', validators=[Required()])
    password = PasswordField('password', validators=[Required()])
    remember_me = BooleanField('remember_me', default=False)


class PasswordForm(Form):
    password = PasswordField('New Password', validators=[Required()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[Required(), Length(min=6, max=20),
                                                 EqualTo('password', message='Passwords must match')])


class ProfileForm(Form):
    username = TextField('Username', validators=[Required(),
                                                 Length(min=5, max=10)])
    email = TextField('Email', validators=[Required(), Email()])
    alarm_email = TextField('Alarm Email', validators=[Email()])


# Define login and registration forms (for flask-login)
class AdminLoginForm(Form):
    user = TextField(validators=[Required()])
    password = PasswordField(validators=[Required()])
