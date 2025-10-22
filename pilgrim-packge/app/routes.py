from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Package, Event, Contact, db
from .forms import ContactForm
from . import cache

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def home():
    cards = Package.query.limit(3).all()
    events = Event.query.all()
    form = ContactForm()
    if form.validate_on_submit():
        contact = Contact(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            message=form.message.data
        )
        db.session.add(contact)
        db.session.commit()
        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('main.home'))
    return render_template('home.html', cards=cards, events=events, form=form)

@main.route('/packages')
@cache.cached(timeout=300)
def packages():
    destination = request.args.get('destination')
    price_range = request.args.get('price')
    duration = request.args.get('duration')
    sort_by = request.args.get('sort', 'title')  # Default sort by title
    page = int(request.args.get('page', 1))
    per_page = 10  # Items per page

    query = Package.query

    if destination:
        query = query.filter(Package.destination.ilike(f'%{destination}%'))
    if price_range:
        if price_range == 'below_10000':
            query = query.filter(Package.price < '₹10,000')
        elif price_range == '10000_25000':
            query = query.filter(Package.price.between('₹10,000', '₹25,000'))
        elif price_range == 'above_50000':
            query = query.filter(Package.price > '₹50,000')
    if duration:
        if duration == '1-3':
            query = query.filter(Package.duration.ilike('%1-3%'))
        elif duration == '4-7':
            query = query.filter(Package.duration.ilike('%4-7%'))
        elif duration == '8-14':
            query = query.filter(Package.duration.ilike('%8-14%'))
        elif duration == '15+':
            query = query.filter(Package.duration.ilike('%15+%'))

    # Sorting
    if sort_by == 'price':
        query = query.order_by(Package.price)
    elif sort_by == 'duration':
        query = query.order_by(Package.duration)
    elif sort_by == 'rating':
        query = query.order_by(Package.rating.desc())
    else:
        query = query.order_by(Package.title)

    # Pagination
    packages = query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('packages.html', packages=packages)

@main.route('/package/<int:id>')
@cache.cached(timeout=600)
def package_detail(id):
    package = Package.query.get_or_404(id)
    return render_template('package_detail.html', package=package)

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        contact = Contact(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            message=form.message.data
        )
        db.session.add(contact)
        db.session.commit()
        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('main.contact'))
    return render_template('contact.html', form=form)
