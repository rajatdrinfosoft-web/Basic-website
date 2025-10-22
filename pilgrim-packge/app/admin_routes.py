import pandas as pd
import matplotlib.pyplot as plt
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, Response
from flask_login import login_required
from .models import Package, Event, Contact, db
from .forms import PackageForm, EventForm
from io import BytesIO
from sqlalchemy import func

admin = Blueprint('admin', __name__)

@admin.route('/')
@login_required
def dashboard():
    packages = Package.query.all()
    events = Event.query.all()
    contacts = Contact.query.order_by(Contact.created_at.desc()).all()

    # Analytics data
    total_packages = len(packages)
    total_events = len(events)
    total_contacts = len(contacts)

    # Recent contacts (last 7 days)
    from datetime import datetime, timedelta
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_contacts = Contact.query.filter(Contact.created_at >= seven_days_ago).count()

    # Package destinations count
    destination_counts = db.session.query(Package.destination, func.count(Package.id)).group_by(Package.destination).all()
    destinations = [d[0] for d in destination_counts]
    dest_counts = [d[1] for d in destination_counts]

    # Contact messages over time (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    contact_dates = db.session.query(func.date(Contact.created_at), func.count(Contact.id)).filter(Contact.created_at >= thirty_days_ago).group_by(func.date(Contact.created_at)).all()
    contact_dates = sorted(contact_dates, key=lambda x: x[0])
    dates = [str(d[0]) for d in contact_dates]
    contact_counts = [d[1] for d in contact_dates]

    return render_template('admin/dashboard.html', packages=packages, events=events, contacts=contacts,
                         total_packages=total_packages, total_events=total_events, total_contacts=total_contacts,
                         recent_contacts=recent_contacts, destinations=destinations, dest_counts=dest_counts,
                         dates=dates, contact_counts=contact_counts)

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

# Bulk Import/Export
@admin.route('/export/packages')
@login_required
def export_packages():
    packages = Package.query.all()
    data = [{
        'id': p.id,
        'title': p.title,
        'description': p.description,
        'price': p.price,
        'rating': p.rating,
        'image': p.image,
        'duration': p.duration,
        'destination': p.destination,
        'best_time': p.best_time,
        'group_size': p.group_size,
        'overview': p.overview,
        'itinerary': p.itinerary,
        'inclusions': p.inclusions,
        'exclusions': p.exclusions
    } for p in packages]
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Packages')
    output.seek(0)
    return send_file(output, download_name='packages.xlsx', as_attachment=True)

@admin.route('/export/events')
@login_required
def export_events():
    events = Event.query.all()
    data = [{
        'id': e.id,
        'title': e.title,
        'date': e.date,
        'destination': e.destination,
        'image': e.image,
        'link': e.link
    } for e in events]
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Events')
    output.seek(0)
    return send_file(output, download_name='events.xlsx', as_attachment=True)

@admin.route('/export/contacts')
@login_required
def export_contacts():
    contacts = Contact.query.all()
    data = [{
        'id': c.id,
        'name': c.name,
        'email': c.email,
        'phone': c.phone,
        'message': c.message,
        'created_at': c.created_at
    } for c in contacts]
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Contacts')
    output.seek(0)
    return send_file(output, download_name='contacts.xlsx', as_attachment=True)

# Package duplication
@admin.route('/package/<int:id>/duplicate')
@login_required
def duplicate_package(id):
    package = Package.query.get_or_404(id)
    new_package = Package(
        title=f"{package.title} (Copy)",
        description=package.description,
        price=package.price,
        rating=package.rating,
        image=package.image,
        duration=package.duration,
        destination=package.destination,
        best_time=package.best_time,
        group_size=package.group_size,
        overview=package.overview,
        itinerary=package.itinerary,
        inclusions=package.inclusions,
        exclusions=package.exclusions
    )
    db.session.add(new_package)
    db.session.commit()
    flash('Package duplicated successfully!')
    return redirect(url_for('admin.dashboard'))
