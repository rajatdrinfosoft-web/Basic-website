import pandas as pd
import matplotlib.pyplot as plt
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, Response
from flask_login import login_required
from .models import Package, Event, Contact, Page, Banner, FAQ, Testimonial, SEOConfig, Language, db
from .forms import PackageForm, EventForm, PageForm, BannerForm, FAQForm, TestimonialForm, SEOConfigForm, LanguageForm
from io import BytesIO
from sqlalchemy import func
import bleach

admin = Blueprint('admin', __name__)

@admin.route('/')
@login_required
def dashboard():
    packages = Package.query.all()
    events = Event.query.all()
    contacts = Contact.query.order_by(Contact.created_at.desc()).all()
    banners = Banner.query.all()
    testimonials = Testimonial.query.all()
    pages = Page.query.all()
    faqs = FAQ.query.all()

    # Analytics data
    total_packages = len(packages)
    total_events = len(events)
    total_contacts = len(contacts)
    total_banners = len(banners)
    total_testimonials = len(testimonials)

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
                         banners=banners, testimonials=testimonials, pages=pages, faqs=faqs,
                         total_packages=total_packages, total_events=total_events, total_contacts=total_contacts,
                         total_banners=total_banners, total_testimonials=total_testimonials,
                         recent_contacts=recent_contacts, destinations=destinations, dest_counts=dest_counts,
                         dates=dates, contact_counts=contact_counts)

# Package CRUD
@admin.route('/package/new', methods=['GET', 'POST'])
@login_required
def new_package():
    form = PackageForm()
    if form.validate_on_submit():
        # Sanitize HTML content to prevent XSS
        sanitized_overview = bleach.clean(
            form.overview.data or '',
            tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'blockquote', 'img', 'table', 'tr', 'td', 'th', 'tbody', 'thead', 'tfoot', 'span', 'div'],
            attributes={'a': ['href', 'title'], 'img': ['src', 'alt', 'title'], 'table': ['class'], 'tr': ['class'], 'td': ['class'], 'th': ['class'], 'span': ['class'], 'div': ['class']}
        )
        sanitized_itinerary = bleach.clean(
            form.itinerary.data or '',
            tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'blockquote', 'img', 'table', 'tr', 'td', 'th', 'tbody', 'thead', 'tfoot', 'span', 'div'],
            attributes={'a': ['href', 'title'], 'img': ['src', 'alt', 'title'], 'table': ['class'], 'tr': ['class'], 'td': ['class'], 'th': ['class'], 'span': ['class'], 'div': ['class']}
        )
        sanitized_itinerary_days = bleach.clean(
            form.itinerary_days.data or '',
            tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'blockquote', 'img', 'table', 'tr', 'td', 'th', 'tbody', 'thead', 'tfoot', 'span', 'div'],
            attributes={'a': ['href', 'title'], 'img': ['src', 'alt', 'title'], 'table': ['class'], 'tr': ['class'], 'td': ['class'], 'th': ['class'], 'span': ['class'], 'div': ['class']}
        )
        sanitized_inclusions = bleach.clean(
            form.inclusions.data or '',
            tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'blockquote', 'img', 'table', 'tr', 'td', 'th', 'tbody', 'thead', 'tfoot', 'span', 'div'],
            attributes={'a': ['href', 'title'], 'img': ['src', 'alt', 'title'], 'table': ['class'], 'tr': ['class'], 'td': ['class'], 'th': ['class'], 'span': ['class'], 'div': ['class']}
        )
        sanitized_exclusions = bleach.clean(
            form.exclusions.data or '',
            tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'blockquote', 'img', 'table', 'tr', 'td', 'th', 'tbody', 'thead', 'tfoot', 'span', 'div'],
            attributes={'a': ['href', 'title'], 'img': ['src', 'alt', 'title'], 'table': ['class'], 'tr': ['class'], 'td': ['class'], 'th': ['class'], 'span': ['class'], 'div': ['class']}
        )
        sanitized_highlights = bleach.clean(
            form.highlights.data or '',
            tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'blockquote', 'img', 'table', 'tr', 'td', 'th', 'tbody', 'thead', 'tfoot', 'span', 'div'],
            attributes={'a': ['href', 'title'], 'img': ['src', 'alt', 'title'], 'table': ['class'], 'tr': ['class'], 'td': ['class'], 'th': ['class'], 'span': ['class'], 'div': ['class']}
        )
        sanitized_accommodation_details = bleach.clean(
            form.accommodation_details.data or '',
            tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'blockquote', 'img', 'table', 'tr', 'td', 'th', 'tbody', 'thead', 'tfoot', 'span', 'div'],
            attributes={'a': ['href', 'title'], 'img': ['src', 'alt', 'title'], 'table': ['class'], 'tr': ['class'], 'td': ['class'], 'th': ['class'], 'span': ['class'], 'div': ['class']}
        )
        sanitized_transportation_details = bleach.clean(
            form.transportation_details.data or '',
            tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'blockquote', 'img', 'table', 'tr', 'td', 'th', 'tbody', 'thead', 'tfoot', 'span', 'div'],
            attributes={'a': ['href', 'title'], 'img': ['src', 'alt', 'title'], 'table': ['class'], 'tr': ['class'], 'td': ['class'], 'th': ['class'], 'span': ['class'], 'div': ['class']}
        )
        sanitized_cancellation_policy = bleach.clean(
            form.cancellation_policy.data or '',
            tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'blockquote', 'img', 'table', 'tr', 'td', 'th', 'tbody', 'thead', 'tfoot', 'span', 'div'],
            attributes={'a': ['href', 'title'], 'img': ['src', 'alt', 'title'], 'table': ['class'], 'tr': ['class'], 'td': ['class'], 'th': ['class'], 'span': ['class'], 'div': ['class']}
        )
        sanitized_terms_conditions = bleach.clean(
            form.terms_conditions.data or '',
            tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'blockquote', 'img', 'table', 'tr', 'td', 'th', 'tbody', 'thead', 'tfoot', 'span', 'div'],
            attributes={'a': ['href', 'title'], 'img': ['src', 'alt', 'title'], 'table': ['class'], 'tr': ['class'], 'td': ['class'], 'th': ['class'], 'span': ['class'], 'div': ['class']}
        )
        package = Package(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            rating=form.rating.data,
            image=form.image.data,
            gallery_images=form.gallery_images.data,
            duration=form.duration.data,
            destination=form.destination.data,
            best_time=form.best_time.data,
            group_size=form.group_size.data,
            overview=sanitized_overview,
            itinerary=sanitized_itinerary,
            itinerary_days=sanitized_itinerary_days,
            inclusions=sanitized_inclusions,
            exclusions=sanitized_exclusions,
            highlights=sanitized_highlights,
            accommodation_details=sanitized_accommodation_details,
            transportation_details=sanitized_transportation_details,
            cancellation_policy=sanitized_cancellation_policy,
            terms_conditions=sanitized_terms_conditions,
            video_url=form.video_url.data,
            map_location=form.map_location.data,
            version=form.version.data
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
        # Sanitize HTML content to prevent XSS
        sanitized_overview = bleach.clean(
            form.overview.data or '',
            tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'blockquote', 'img', 'table', 'tr', 'td', 'th', 'tbody', 'thead', 'tfoot', 'span', 'div'],
            attributes={'a': ['href', 'title'], 'img': ['src', 'alt', 'title'], 'table': ['class'], 'tr': ['class'], 'td': ['class'], 'th': ['class'], 'span': ['class'], 'div': ['class']}
        )
        sanitized_itinerary = bleach.clean(
            form.itinerary.data or '',
            tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'blockquote', 'img', 'table', 'tr', 'td', 'th', 'tbody', 'thead', 'tfoot', 'span', 'div'],
            attributes={'a': ['href', 'title'], 'img': ['src', 'alt', 'title'], 'table': ['class'], 'tr': ['class'], 'td': ['class'], 'th': ['class'], 'span': ['class'], 'div': ['class']}
        )
        sanitized_itinerary_days = bleach.clean(
            form.itinerary_days.data or '',
            tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'blockquote', 'img', 'table', 'tr', 'td', 'th', 'tbody', 'thead', 'tfoot', 'span', 'div'],
            attributes={'a': ['href', 'title'], 'img': ['src', 'alt', 'title'], 'table': ['class'], 'tr': ['class'], 'td': ['class'], 'th': ['class'], 'span': ['class'], 'div': ['class']}
        )
        sanitized_inclusions = bleach.clean(
            form.inclusions.data or '',
            tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'blockquote', 'img', 'table', 'tr', 'td', 'th', 'tbody', 'thead', 'tfoot', 'span', 'div'],
            attributes={'a': ['href', 'title'], 'img': ['src', 'alt', 'title'], 'table': ['class'], 'tr': ['class'], 'td': ['class'], 'th': ['class'], 'span': ['class'], 'div': ['class']}
        )
        sanitized_exclusions = bleach.clean(
            form.exclusions.data or '',
            tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'blockquote', 'img', 'table', 'tr', 'td', 'th', 'tbody', 'thead', 'tfoot', 'span', 'div'],
            attributes={'a': ['href', 'title'], 'img': ['src', 'alt', 'title'], 'table': ['class'], 'tr': ['class'], 'td': ['class'], 'th': ['class'], 'span': ['class'], 'div': ['class']}
        )
        sanitized_highlights = bleach.clean(
            form.highlights.data or '',
            tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'blockquote', 'img', 'table', 'tr', 'td', 'th', 'tbody', 'thead', 'tfoot', 'span', 'div'],
            attributes={'a': ['href', 'title'], 'img': ['src', 'alt', 'title'], 'table': ['class'], 'tr': ['class'], 'td': ['class'], 'th': ['class'], 'span': ['class'], 'div': ['class']}
        )
        sanitized_accommodation_details = bleach.clean(
            form.accommodation_details.data or '',
            tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'blockquote', 'img', 'table', 'tr', 'td', 'th', 'tbody', 'thead', 'tfoot', 'span', 'div'],
            attributes={'a': ['href', 'title'], 'img': ['src', 'alt', 'title'], 'table': ['class'], 'tr': ['class'], 'td': ['class'], 'th': ['class'], 'span': ['class'], 'div': ['class']}
        )
        sanitized_transportation_details = bleach.clean(
            form.transportation_details.data or '',
            tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'blockquote', 'img', 'table', 'tr', 'td', 'th', 'tbody', 'thead', 'tfoot', 'span', 'div'],
            attributes={'a': ['href', 'title'], 'img': ['src', 'alt', 'title'], 'table': ['class'], 'tr': ['class'], 'td': ['class'], 'th': ['class'], 'span': ['class'], 'div': ['class']}
        )
        sanitized_cancellation_policy = bleach.clean(
            form.cancellation_policy.data or '',
            tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'blockquote', 'img', 'table', 'tr', 'td', 'th', 'tbody', 'thead', 'tfoot', 'span', 'div'],
            attributes={'a': ['href', 'title'], 'img': ['src', 'alt', 'title'], 'table': ['class'], 'tr': ['class'], 'td': ['class'], 'th': ['class'], 'span': ['class'], 'div': ['class']}
        )
        sanitized_terms_conditions = bleach.clean(
            form.terms_conditions.data or '',
            tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'blockquote', 'img', 'table', 'tr', 'td', 'th', 'tbody', 'thead', 'tfoot', 'span', 'div'],
            attributes={'a': ['href', 'title'], 'img': ['src', 'alt', 'title'], 'table': ['class'], 'tr': ['class'], 'td': ['class'], 'th': ['class'], 'span': ['class'], 'div': ['class']}
        )
        package.title = form.title.data
        package.description = form.description.data
        package.price = form.price.data
        package.rating = form.rating.data
        package.image = form.image.data
        package.gallery_images = form.gallery_images.data
        package.duration = form.duration.data
        package.destination = form.destination.data
        package.best_time = form.best_time.data
        package.group_size = form.group_size.data
        package.overview = sanitized_overview
        package.itinerary = sanitized_itinerary
        package.itinerary_days = sanitized_itinerary_days
        package.inclusions = sanitized_inclusions
        package.exclusions = sanitized_exclusions
        package.highlights = sanitized_highlights
        package.accommodation_details = sanitized_accommodation_details
        package.transportation_details = sanitized_transportation_details
        package.cancellation_policy = sanitized_cancellation_policy
        package.terms_conditions = sanitized_terms_conditions
        package.video_url = form.video_url.data
        package.map_location = form.map_location.data
        package.version = form.version.data
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
        'gallery_images': p.gallery_images,
        'duration': p.duration,
        'destination': p.destination,
        'best_time': p.best_time,
        'group_size': p.group_size,
        'overview': p.overview,
        'itinerary': p.itinerary,
        'itinerary_days': p.itinerary_days,
        'inclusions': p.inclusions,
        'exclusions': p.exclusions,
        'highlights': p.highlights,
        'accommodation_details': p.accommodation_details,
        'transportation_details': p.transportation_details,
        'cancellation_policy': p.cancellation_policy,
        'terms_conditions': p.terms_conditions,
        'video_url': p.video_url,
        'map_location': p.map_location,
        'version': p.version
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
        gallery_images=package.gallery_images,
        duration=package.duration,
        destination=package.destination,
        best_time=package.best_time,
        group_size=package.group_size,
        overview=package.overview,
        itinerary=package.itinerary,
        itinerary_days=package.itinerary_days,
        inclusions=package.inclusions,
        exclusions=package.exclusions,
        highlights=package.highlights,
        accommodation_details=package.accommodation_details,
        transportation_details=package.transportation_details,
        cancellation_policy=package.cancellation_policy,
        terms_conditions=package.terms_conditions,
        video_url=package.video_url,
        map_location=package.map_location,
        version=package.version
    )
    db.session.add(new_package)
    db.session.commit()
    flash('Package duplicated successfully!')
    return redirect(url_for('admin.dashboard'))

# Page CRUD
@admin.route('/page/new', methods=['GET', 'POST'])
@login_required
def new_page():
    form = PageForm()
    if form.validate_on_submit():
        # Sanitize HTML content to prevent XSS
        sanitized_content = bleach.clean(
            form.content.data,
            tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'blockquote', 'img', 'table', 'tr', 'td', 'th', 'tbody', 'thead', 'tfoot', 'span', 'div'],
            attributes={'a': ['href', 'title'], 'img': ['src', 'alt', 'title'], 'table': ['class'], 'tr': ['class'], 'td': ['class'], 'th': ['class'], 'span': ['class'], 'div': ['class']}
        )
        page = Page(
            slug=form.slug.data,
            title=form.title.data,
            content=sanitized_content,
            meta_title=form.meta_title.data,
            meta_description=form.meta_description.data,
            is_active=form.is_active.data
        )
        db.session.add(page)
        db.session.commit()
        flash('Page added successfully!')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/page_form.html', form=form, title='Add Page')

@admin.route('/page/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_page(id):
    page = Page.query.get_or_404(id)
    form = PageForm(obj=page)
    if form.validate_on_submit():
        # Sanitize HTML content to prevent XSS
        sanitized_content = bleach.clean(
            form.content.data,
            tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'blockquote', 'img', 'table', 'tr', 'td', 'th', 'tbody', 'thead', 'tfoot', 'span', 'div'],
            attributes={'a': ['href', 'title'], 'img': ['src', 'alt', 'title'], 'table': ['class'], 'tr': ['class'], 'td': ['class'], 'th': ['class'], 'span': ['class'], 'div': ['class']}
        )
        form.populate_obj(page)
        page.content = sanitized_content
        db.session.commit()
        flash('Page updated successfully!')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/page_form.html', form=form, title='Edit Page')

@admin.route('/page/<int:id>/delete')
@login_required
def delete_page(id):
    page = Page.query.get_or_404(id)
    db.session.delete(page)
    db.session.commit()
    flash('Page deleted successfully!')
    return redirect(url_for('admin.dashboard'))

# Banner CRUD
@admin.route('/banner/new', methods=['GET', 'POST'])
@login_required
def new_banner():
    form = BannerForm()
    if form.validate_on_submit():
        banner = Banner(
            title=form.title.data,
            image=form.image.data,
            link=form.link.data,
            position=form.position.data,
            is_active=form.is_active.data,
            order=form.order.data
        )
        db.session.add(banner)
        db.session.commit()
        flash('Banner added successfully!')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/banner_form.html', form=form, title='Add Banner')

@admin.route('/banner/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_banner(id):
    banner = Banner.query.get_or_404(id)
    form = BannerForm(obj=banner)
    if form.validate_on_submit():
        form.populate_obj(banner)
        db.session.commit()
        flash('Banner updated successfully!')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/banner_form.html', form=form, title='Edit Banner')

@admin.route('/banner/<int:id>/delete')
@login_required
def delete_banner(id):
    banner = Banner.query.get_or_404(id)
    db.session.delete(banner)
    db.session.commit()
    flash('Banner deleted successfully!')
    return redirect(url_for('admin.dashboard'))

# FAQ CRUD
@admin.route('/faq/new', methods=['GET', 'POST'])
@login_required
def new_faq():
    form = FAQForm()
    if form.validate_on_submit():
        faq = FAQ(
            question=form.question.data,
            answer=form.answer.data,
            category=form.category.data,
            is_active=form.is_active.data,
            order=form.order.data
        )
        db.session.add(faq)
        db.session.commit()
        flash('FAQ added successfully!')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/faq_form.html', form=form, title='Add FAQ')

@admin.route('/faq/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_faq(id):
    faq = FAQ.query.get_or_404(id)
    form = FAQForm(obj=faq)
    if form.validate_on_submit():
        form.populate_obj(faq)
        db.session.commit()
        flash('FAQ updated successfully!')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/faq_form.html', form=form, title='Edit FAQ')

@admin.route('/faq/<int:id>/delete')
@login_required
def delete_faq(id):
    faq = FAQ.query.get_or_404(id)
    db.session.delete(faq)
    db.session.commit()
    flash('FAQ deleted successfully!')
    return redirect(url_for('admin.dashboard'))

# Testimonial CRUD
@admin.route('/testimonial/new', methods=['GET', 'POST'])
@login_required
def new_testimonial():
    form = TestimonialForm()
    if form.validate_on_submit():
        testimonial = Testimonial(
            name=form.name.data,
            location=form.location.data,
            rating=form.rating.data,
            message=form.message.data,
            image=form.image.data,
            is_active=form.is_active.data
        )
        db.session.add(testimonial)
        db.session.commit()
        flash('Testimonial added successfully!')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/testimonial_form.html', form=form, title='Add Testimonial')

@admin.route('/testimonial/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_testimonial(id):
    testimonial = Testimonial.query.get_or_404(id)
    form = TestimonialForm(obj=testimonial)
    if form.validate_on_submit():
        form.populate_obj(testimonial)
        db.session.commit()
        flash('Testimonial updated successfully!')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/testimonial_form.html', form=form, title='Edit Testimonial')

@admin.route('/testimonial/<int:id>/delete')
@login_required
def delete_testimonial(id):
    testimonial = Testimonial.query.get_or_404(id)
    db.session.delete(testimonial)
    db.session.commit()
    flash('Testimonial deleted successfully!')
    return redirect(url_for('admin.dashboard'))

# SEOConfig CRUD
@admin.route('/seoconfig/new', methods=['GET', 'POST'])
@login_required
def new_seoconfig():
    form = SEOConfigForm()
    if form.validate_on_submit():
        seoconfig = SEOConfig(
            key=form.key.data,
            value=form.value.data,
            description=form.description.data
        )
        db.session.add(seoconfig)
        db.session.commit()
        flash('SEO Config added successfully!')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/seoconfig_form.html', form=form, title='Add SEO Config')

@admin.route('/seoconfig/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_seoconfig(id):
    seoconfig = SEOConfig.query.get_or_404(id)
    form = SEOConfigForm(obj=seoconfig)
    if form.validate_on_submit():
        form.populate_obj(seoconfig)
        db.session.commit()
        flash('SEO Config updated successfully!')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/seoconfig_form.html', form=form, title='Edit SEO Config')

@admin.route('/seoconfig/<int:id>/delete')
@login_required
def delete_seoconfig(id):
    seoconfig = SEOConfig.query.get_or_404(id)
    db.session.delete(seoconfig)
    db.session.commit()
    flash('SEO Config deleted successfully!')
    return redirect(url_for('admin.dashboard'))

# Language CRUD
@admin.route('/language/new', methods=['GET', 'POST'])
@login_required
def new_language():
    form = LanguageForm()
    if form.validate_on_submit():
        language = Language(
            code=form.code.data,
            name=form.name.data,
            is_active=form.is_active.data,
            is_default=form.is_default.data
        )
        db.session.add(language)
        db.session.commit()
        flash('Language added successfully!')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/language_form.html', form=form, title='Add Language')

@admin.route('/language/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_language(id):
    language = Language.query.get_or_404(id)
    form = LanguageForm(obj=language)
    if form.validate_on_submit():
        form.populate_obj(language)
        db.session.commit()
        flash('Language updated successfully!')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/language_form.html', form=form, title='Edit Language')

@admin.route('/language/<int:id>/delete')
@login_required
def delete_language(id):
    language = Language.query.get_or_404(id)
    db.session.delete(language)
    db.session.commit()
    flash('Language deleted successfully!')
    return redirect(url_for('admin.dashboard'))

# Export routes for new models
@admin.route('/export/pages')
@login_required
def export_pages():
    pages = Page.query.all()
    data = [{
        'id': p.id,
        'slug': p.slug,
        'title': p.title,
        'content': p.content,
        'meta_title': p.meta_title,
        'meta_description': p.meta_description,
        'is_active': p.is_active,
        'created_at': p.created_at,
        'updated_at': p.updated_at
    } for p in pages]
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Pages')
    output.seek(0)
    return send_file(output, download_name='pages.xlsx', as_attachment=True)

@admin.route('/export/banners')
@login_required
def export_banners():
    banners = Banner.query.all()
    data = [{
        'id': b.id,
        'title': b.title,
        'image': b.image,
        'link': b.link,
        'position': b.position,
        'is_active': b.is_active,
        'order': b.order,
        'created_at': b.created_at
    } for b in banners]
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Banners')
    output.seek(0)
    return send_file(output, download_name='banners.xlsx', as_attachment=True)

@admin.route('/export/faqs')
@login_required
def export_faqs():
    faqs = FAQ.query.all()
    data = [{
        'id': f.id,
        'question': f.question,
        'answer': f.answer,
        'category': f.category,
        'is_active': f.is_active,
        'order': f.order,
        'created_at': f.created_at
    } for f in faqs]
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='FAQs')
    output.seek(0)
    return send_file(output, download_name='faqs.xlsx', as_attachment=True)

@admin.route('/export/testimonials')
@login_required
def export_testimonials():
    testimonials = Testimonial.query.all()
    data = [{
        'id': t.id,
        'name': t.name,
        'location': t.location,
        'rating': t.rating,
        'message': t.message,
        'image': t.image,
        'is_active': t.is_active,
        'created_at': t.created_at
    } for t in testimonials]
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Testimonials')
    output.seek(0)
    return send_file(output, download_name='testimonials.xlsx', as_attachment=True)

@admin.route('/export/seoconfigs')
@login_required
def export_seoconfigs():
    seoconfigs = SEOConfig.query.all()
    data = [{
        'id': s.id,
        'key': s.key,
        'value': s.value,
        'description': s.description
    } for s in seoconfigs]
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='SEOConfigs')
    output.seek(0)
    return send_file(output, download_name='seoconfigs.xlsx', as_attachment=True)

@admin.route('/export/languages')
@login_required
def export_languages():
    languages = Language.query.all()
    data = [{
        'id': l.id,
        'code': l.code,
        'name': l.name,
        'is_active': l.is_active,
        'is_default': l.is_default
    } for l in languages]
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Languages')
    output.seek(0)
    return send_file(output, download_name='languages.xlsx', as_attachment=True)
