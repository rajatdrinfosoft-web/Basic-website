from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, BooleanField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, Optional, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class PackageForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    price = StringField('Price', validators=[DataRequired(), Length(max=20)])
    rating = StringField('Rating', validators=[Length(max=10)])
    image = StringField('Main Image URL', validators=[Length(max=255)])
    gallery_images = TextAreaField('Gallery Images (comma-separated URLs)')
    duration = StringField('Duration', validators=[Length(max=50)])
    destination = StringField('Destination', validators=[Length(max=100)])
    best_time = StringField('Best Time', validators=[Length(max=100)])
    group_size = StringField('Group Size', validators=[Length(max=50)])
    overview = TextAreaField('Overview')
    itinerary = TextAreaField('Itinerary (Simple)')
    itinerary_days = TextAreaField('Detailed Itinerary (Day-by-Day)')
    inclusions = TextAreaField('Inclusions')
    exclusions = TextAreaField('Exclusions')
    highlights = TextAreaField('Key Highlights')
    accommodation_details = TextAreaField('Accommodation Details')
    transportation_details = TextAreaField('Transportation Details')
    cancellation_policy = TextAreaField('Cancellation Policy')
    terms_conditions = TextAreaField('Terms & Conditions')
    video_url = StringField('Video URL', validators=[Length(max=255)])
    map_location = StringField('Map Location/Embed Code', validators=[Length(max=255)])
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

class PageForm(FlaskForm):
    slug = StringField('Slug', validators=[DataRequired(), Length(max=100)])
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    meta_title = StringField('Meta Title', validators=[Optional(), Length(max=200)])
    meta_description = TextAreaField('Meta Description', validators=[Optional()])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Page')

class BannerForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    image = StringField('Image URL', validators=[Length(max=255)])
    link = StringField('Link', validators=[Optional(), Length(max=255)])
    position = SelectField('Position', choices=[('home', 'Home'), ('packages', 'Packages'), ('about', 'About')], default='home')
    is_active = BooleanField('Active', default=True)
    order = IntegerField('Order', validators=[Optional(), NumberRange(min=0)], default=0)
    submit = SubmitField('Save Banner')

class FAQForm(FlaskForm):
    question = StringField('Question', validators=[DataRequired(), Length(max=500)])
    answer = TextAreaField('Answer', validators=[DataRequired()])
    category = StringField('Category', validators=[Optional(), Length(max=100)], default='general')
    is_active = BooleanField('Active', default=True)
    order = IntegerField('Order', validators=[Optional(), NumberRange(min=0)], default=0)
    submit = SubmitField('Save FAQ')

class TestimonialForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    rating = SelectField('Rating', choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')], coerce=int, default=5)
    message = TextAreaField('Message', validators=[DataRequired()])
    image = StringField('Image URL', validators=[Optional(), Length(max=255)])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Testimonial')

class SEOConfigForm(FlaskForm):
    key = StringField('Key', validators=[DataRequired(), Length(max=100)])
    value = TextAreaField('Value')
    description = StringField('Description', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Save SEO Config')

class LanguageForm(FlaskForm):
    code = StringField('Code', validators=[DataRequired(), Length(max=10)])
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    is_active = BooleanField('Active', default=True)
    is_default = BooleanField('Default Language', default=False)
    submit = SubmitField('Save Language')
