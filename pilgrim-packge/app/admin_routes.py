from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from .models import Package, Event, Contact, db
from .forms import PackageForm, EventForm

admin = Blueprint('admin', __name__)

@admin.route('/')
@login_required
def dashboard():
    packages = Package.query.all()
    events = Event.query.all()
    contacts = Contact.query.order_by(Contact.created_at.desc()).all()
    return render_template('admin/dashboard.html', packages=packages, events=events, contacts=contacts)

# Package CRUD
@admin.route('/package/new', methods=['GET', 'POST'])
@login_required
def new_package():
    form = PackageForm()
    if form.validate_on_submit():
        package = Package(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            rating=form.rating.data,
            image=form.image.data,
            duration=form.duration.data,
            destination=form.destination.data,
            best_time=form.best_time.data,
            group_size=form.group_size.data,
            overview=form.overview.data,
            itinerary=form.itinerary.data,
            inclusions=form.inclusions.data,
            exclusions=form.exclusions.data
        )
        db.session.add(package)
        db.session.commit()
        flash('Package added successfully!')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/package_form.html', form=form, title='Add Package')

@admin.route('/package/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_package(id):
    package = Package.query.get_or_404(id)
    form = PackageForm(obj=package)
    if form.validate_on_submit():
        form.populate_obj(package)
        db.session.commit()
        flash('Package updated successfully!')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/package_form.html', form=form, title='Edit Package')

@admin.route('/package/<int:id>/delete')
@login_required
def delete_package(id):
    package = Package.query.get_or_404(id)
    db.session.delete(package)
    db.session.commit()
    flash('Package deleted successfully!')
    return redirect(url_for('admin.dashboard'))

# Event CRUD
@admin.route('/event/new', methods=['GET', 'POST'])
@login_required
def new_event():
    form = EventForm()
    if form.validate_on_submit():
        event = Event(
            title=form.title.data,
            date=form.date.data,
            destination=form.destination.data,
            image=form.image.data,
            link=form.link.data
        )
        db.session.add(event)
        db.session.commit()
        flash('Event added successfully!')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/event_form.html', form=form, title='Add Event')

@admin.route('/event/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    event = Event.query.get_or_404(id)
    form = EventForm(obj=event)
    if form.validate_on_submit():
        form.populate_obj(event)
        db.session.commit()
        flash('Event updated successfully!')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/event_form.html', form=form, title='Edit Event')

@admin.route('/event/<int:id>/delete')
@login_required
def delete_event(id):
    event = Event.query.get_or_404(id)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully!')
    return redirect(url_for('admin.dashboard'))
