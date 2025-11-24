from datetime import datetime, timedelta
import uuid

from sqlalchemy import event
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Integer, index=True)
    rating = db.Column(db.String(10))
    image = db.Column(db.String(255))
    gallery_images = db.Column(db.Text)  # Comma-separated image URLs
    duration = db.Column(db.String(50), index=True)
    destination = db.Column(db.String(100), index=True)
    best_time = db.Column(db.String(100))
    group_size = db.Column(db.String(50))
    overview = db.Column(db.Text)
    itinerary = db.Column(db.Text)
    itinerary_days = db.Column(db.Text)  # Structured day-by-day data
    inclusions = db.Column(db.Text)
    exclusions = db.Column(db.Text)
    highlights = db.Column(db.Text)  # Key package highlights
    accommodation_details = db.Column(db.Text)
    transportation_details = db.Column(db.Text)
    cancellation_policy = db.Column(db.Text)
    terms_conditions = db.Column(db.Text)
    video_url = db.Column(db.String(255))  # For video tours
    map_location = db.Column(db.String(255))  # For embedded maps
    version = db.Column(db.String(20))  # Package version

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(50))
    destination = db.Column(db.String(100))
    image = db.Column(db.String(255))
    link = db.Column(db.String(255))

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    meta_title = db.Column(db.String(200))
    meta_description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    image = db.Column(db.String(255))
    link = db.Column(db.String(255))
    position = db.Column(db.String(50), default='home')  # home, packages, etc.
    is_active = db.Column(db.Boolean, default=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class FAQ(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), default='general')
    is_active = db.Column(db.Boolean, default=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    rating = db.Column(db.Integer, default=5)
    message = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class SEOConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(255))

class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)  # e.g., 'en', 'hi'
    name = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_default = db.Column(db.Boolean, default=False)

class Query(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20))
    query_type = db.Column(db.String(100))  # e.g., booking, payment, etc.
    status = db.Column(db.String(50), default='Open')  # Open, In Progress, Resolved, Closed, Responded
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    priority = db.Column(db.String(50), default='Normal')  # Normal, Urgent, Escalated
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    sla_deadline = db.Column(db.DateTime, nullable=True)
    response_due_at = db.Column(db.DateTime, nullable=True)
    first_response_at = db.Column(db.DateTime, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    escalated_at = db.Column(db.DateTime, nullable=True)
    escalation_reason = db.Column(db.String(255), nullable=True)
    last_contact_channel = db.Column(db.String(50), nullable=True)
    last_response_summary = db.Column(db.Text, nullable=True)
    ticket_number = db.Column(db.String(20), unique=True, index=True)
    tags = db.Column(db.String(255), nullable=True)  # comma separated labels
    source = db.Column(db.String(50), nullable=True)  # web, whatsapp, phone, etc.
    assigned_staff = db.relationship('User', backref='assigned_queries', lazy=True)
    responses = db.relationship('QueryResponse', backref='query', lazy=True, cascade='all, delete-orphan', order_by='QueryResponse.created_at')

    def is_overdue(self):
        if not self.sla_deadline:
            return False
        if self.status in {'Closed', 'Resolved'}:
            return False
        return datetime.utcnow() > self.sla_deadline

    def minutes_to_sla(self):
        if not self.sla_deadline:
            return None
        delta = self.sla_deadline - datetime.utcnow()
        return int(delta.total_seconds() / 60)

    def sla_badge_context(self):
        remaining = self.minutes_to_sla()
        if remaining is None:
            return ('secondary', 'No SLA')
        if remaining < 0:
            return ('danger', 'Overdue')
        if remaining < 60:
            return ('warning', f'{remaining}m')
        hours = remaining // 60
        return ('success', f'{hours}h')


class QueryResponseTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100), nullable=True)
    subject = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    responses = db.relationship('QueryResponse', backref='template', lazy=True)


class QueryResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query_id = db.Column(db.Integer, db.ForeignKey('query.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    subject = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    channel = db.Column(db.String(50), default='email')  # email, phone, chat
    attachment_urls = db.Column(db.Text, nullable=True)
    used_template_id = db.Column(db.Integer, db.ForeignKey('query_response_template.id'), nullable=True)
    status_after = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    staff = db.relationship('User', backref=db.backref('query_responses', lazy=True))


@event.listens_for(Query, 'before_insert')
def _assign_ticket_and_sla(mapper, connection, target):
    if not target.ticket_number:
        target.ticket_number = f"Q-{uuid.uuid4().hex[:8].upper()}"
    if not target.sla_deadline:
        target.sla_deadline = datetime.utcnow() + timedelta(hours=12)
    if not target.response_due_at:
        target.response_due_at = target.sla_deadline
