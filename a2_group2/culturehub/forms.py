from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, StringField, PasswordField, TextAreaField, SelectField, IntegerField, FloatField, DateTimeLocalField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import InputRequired, Length, Email, EqualTo, NumberRange, ValidationError
from datetime import datetime
import re

# ── Custom password validator ──
def strong_password(form, field):
    password = field.data
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter.')
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain at least one lowercase letter.')
    if not re.search(r'[0-9]', password):
        raise ValidationError('Password must contain at least one number.')
    if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
        raise ValidationError('Password must contain at least one special character (!@#$%^&* etc).')

class LoginForm(FlaskForm):
    username = StringField("Username or Email", validators=[
        InputRequired('Enter your username or email')
    ])
    password = PasswordField("Password", validators=[InputRequired('Enter your password')])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    first_name = StringField("First Name", validators=[
        InputRequired('Enter your first name'),
        Length(min=2, max=50, message='First name must be between 2 and 50 characters')
    ])
    last_name = StringField("Surname", validators=[
        InputRequired('Enter your surname'),
        Length(min=2, max=50, message='Surname must be between 2 and 50 characters')
    ])
    username = StringField("Username", validators=[
        InputRequired('Choose a username'),
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
    address = StringField("Street Address", validators=[
        InputRequired('Enter your address')
    ])
    password = PasswordField("Password", validators=[
        InputRequired('Enter a password'),
        Length(min=8, message='Password must be at least 8 characters'),
        strong_password,
        EqualTo('confirm', message="Passwords must match")
    ])
    confirm = PasswordField("Confirm Password", validators=[
        InputRequired('Please confirm your password')
    ])
    submit = SubmitField("Create Account")

# Event creation form
class EventForm(FlaskForm):
    name = StringField("Event Title", validators=[InputRequired()])
    category = SelectField("Event Category", choices=[
        ('food', 'Food'),
        ('dance', 'Dance'),
        ('language', 'Language'),
        ('ceremony', 'Ceremony'),
        ('art', 'Art'),
        ('music', 'Music'),
        ('festival', 'Festival')
    ])
    date = DateTimeLocalField("Event Date and Time", format='%Y-%m-%dT%H:%M', validators=[InputRequired()])
    location = StringField("Event Location", validators=[InputRequired()])
    description = TextAreaField("Event Description", validators=[InputRequired()])
    image = FileField("Event Image", validators=[FileAllowed(['jpg', 'png'])])
    tickets_available = IntegerField("Total Tickets Available", validators=[InputRequired(), NumberRange(min=1)])
    price = FloatField("Ticket Price ($)", validators=[InputRequired(), NumberRange(min=0)])
    acknowledgement = SelectField("acknowledgement of Country", choices=[
        ("none", "No acknowledgement "),
        ("generic", "Generic acknowledgement "),
        ("enhanced", "Enhanced acknowledgement ")
    ])
    acknowledgement_text = TextAreaField("Custom Acknowledgement Statement")

    def validate_acknowledgement_text(self, field):
        if self.acknowledgement.data == 'enhanced' and not field.data:
            raise ValidationError('Please provide a custom acknowledgement statement for the Enhanced option.')
    submit = SubmitField("Create Event")

# Separate form for event editing (without image requirement)
class CreateEventForm(EventForm):
    image = FileField("Event Image", validators=[
        FileRequired(message='Please upload an image for your event.'),
        FileAllowed(['jpg', 'png'], message='Images only — JPG or PNG.')
    ])

    def validate_date(self, field):
        if field.data and field.data < datetime.now():
            raise ValidationError('Event date must be in the future.')

# Edit profile form
class EditProfileForm(FlaskForm):
    first_name = StringField("First Name", validators=[InputRequired(), Length(min=2, max=50)])
    last_name = StringField("Surname", validators=[InputRequired(), Length(min=2, max=50)])
    name = StringField("Username", validators=[InputRequired(), Length(min=3, max=50)])
    email = StringField("Email Address", validators=[InputRequired(), Email()])
    phone = StringField("Phone Number", validators=[InputRequired()])
    address = StringField("Address", validators=[InputRequired()])
    bio = TextAreaField("Bio", validators=[Length(max=500)])
    languages = StringField("Language(s) Spoken")
    cultural_interests = StringField("Cultural Interests")
    profile_image = FileField(
        "Profile Image",
        validators=[
            FileAllowed(["jpg", "jpeg", "png", "webp"], "Images only!")
        ]
    )
    submit = SubmitField("Update Profile")

# Booking form
class BookingForm(FlaskForm):
    quantity = IntegerField("Number of Tickets", validators=[InputRequired(), NumberRange(min=1)])
    submit = SubmitField("Confirm Booking")
