from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class PackageForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    price = StringField('Price', validators=[DataRequired(), Length(max=20)])
    rating = StringField('Rating', validators=[Length(max=10)])
    image = StringField('Image URL', validators=[Length(max=255)])
    duration = StringField('Duration', validators=[Length(max=50)])
    destination = StringField('Destination', validators=[Length(max=100)])
    best_time = StringField('Best Time', validators=[Length(max=100)])
    group_size = StringField('Group Size', validators=[Length(max=50)])
    overview = TextAreaField('Overview')
    itinerary = TextAreaField('Itinerary')
    inclusions = TextAreaField('Inclusions')
    exclusions = TextAreaField('Exclusions')
    submit = SubmitField('Save Package')

class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    date = StringField('Date', validators=[Length(max=50)])
    destination = StringField('Destination', validators=[Length(max=100)])
    image = StringField('Image URL', validators=[Length(max=255)])
    link = StringField('Link', validators=[Length(max=255)])
    submit = SubmitField('Save Event')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    phone = StringField('Phone', validators=[Length(max=20)])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')
