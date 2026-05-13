from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, StringField, PasswordField, TextAreaField, SelectField, IntegerField, FloatField, DateTimeLocalField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import InputRequired, Length, Email, EqualTo, NumberRange

# Login form
class LoginForm(FlaskForm):
    user_name = StringField("User Name", validators=[InputRequired('Enter user name')])
    password = PasswordField("Password", validators=[InputRequired('Enter user password')])
    submit = SubmitField("Login")

# Registration form
class RegisterForm(FlaskForm):
    user_name = StringField("Username", validators=[
        InputRequired('Enter a username'),
        Length(min=3, max=50, message='Username must be between 3 and 50 characters')
    ])
    email = StringField("Email Address", validators=[
        InputRequired('Enter your email'),
        Email("Please enter a valid email address")
    ])
    phone = StringField("Phone Number", validators=[
        InputRequired('Enter your phone number'),
        Length(min=8, max=15, message='Enter a valid phone number')
    ])
    address = StringField("Address", validators=[
        InputRequired('Enter your address')
    ])
    password = PasswordField("Password", validators=[
        InputRequired('Enter a password'),
        Length(min=6, message='Password must be at least 6 characters'),
        EqualTo('confirm', message="Passwords must match")
    ])
    confirm = PasswordField("Confirm Password", validators=[
        InputRequired('Please confirm your password')
    ])
    submit = SubmitField("Create Account")
