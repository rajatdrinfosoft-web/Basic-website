import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from io import BytesIO

from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, Response, current_app
from flask_login import login_required, current_user
from sqlalchemy import func
from sqlalchemy.orm import joinedload
import bleach

from .models import (
    Package,
    Event,
    Contact,
    Page,
    Banner,
    FAQ,
    Query,
    QueryResponse,
    QueryResponseTemplate,
    Testimonial,
    SEOConfig,
    Language,
    User,
    db,
)
from .forms import (
    PackageForm,
    EventForm,
    PageForm,
    BannerForm,
    FAQForm,
    TestimonialForm,
    SEOConfigForm,
    LanguageForm,
    QueryFilterForm,
    QueryUpdateForm,
    QueryResponseForm,
    QueryTemplateForm,
    QueryEscalationForm,
)


admin = Blueprint('admin', __name__)


def send_query_email(query_obj, subject, body, attachments=None):
    """
    Placeholder email sender that logs the outbound message.
    Replace with Flask-Mail / external provider when ready.
    """
    current_app.logger.info(
        "Sending email to %s (%s) | Subject: %s | Attachments: %s",
        query_obj.customer_name,
        query_obj.customer_email,
        subject,
        attachments or [],
    )


@admin.route('/')
@login_required
def dashboard():
    packages = Package.query.all()
    events = Event.query.all()
    banners = Banner.query.all()
    testimonials = Testimonial.query.all()
    pages = Page.query.all()
    faqs = FAQ.query.all()

    # Analytics data
    total_packages = len(packages)
    total_events = len(events)
    total_banners = len(banners)
    total_testimonials = len(testimonials)

    # Package destinations count
    destination_counts = db.session.query(Package.destination, func.count(Package.id)).group_by(Package.destination).all()
    destinations = [d[0] for d in destination_counts]
    dest_counts = [d[1] for d in destination_counts]

    # Query analytics
    now = datetime.utcnow()
    query_counts = db.session.query(Query.status, func.count(Query.id)).group_by(Query.status).all()
    status_labels = [qc[0] for qc in query_counts]
    status_counts = [qc[1] for qc in query_counts]
    total_queries = sum(status_counts)
    overdue_queries = (
        Query.query.filter(
            Query.sla_deadline != None,  # noqa: E711
            Query.sla_deadline < now,
            Query.status.notin_(('Resolved', 'Closed')),
        ).count()
    )
    due_soon_queries = (
        Query.query.filter(
            Query.sla_deadline != None,  # noqa: E711
            Query.sla_deadline.between(now, now + timedelta(hours=2)),
            Query.status.notin_(('Resolved', 'Closed')),
        ).count()
    )
    unassigned_queries = Query.query.filter(Query.assigned_staff_id.is_(None)).count()
    query_type_rows = (
        db.session.query(Query.query_type, func.count(Query.id))
        .group_by(Query.query_type)
        .filter(Query.query_type != None)  # noqa: E711
        .all()
    )
    query_type_labels = [row[0] for row in query_type_rows]
    query_type_counts = [row[1] for row in query_type_rows]

    avg_first_response = (
        db.session.query(
            func.avg(
                func.extract('epoch', Query.first_response_at - Query.created_at) / 60.0
            )
        )
        .filter(Query.first_response_at != None)  # noqa: E711
        .scalar()
    )
    avg_resolution_hours = (
        db.session.query(
            func.avg(func.extract('epoch', Query.resolved_at - Query.created_at) / 3600.0)
        )
        .filter(Query.resolved_at != None)  # noqa: E711
        .scalar()
    )

    staff_performance_rows = (
        db.session.query(
            User.username,
            func.count(Query.id),
            func.avg(func.extract('epoch', Query.resolved_at - Query.created_at) / 3600.0),
        )
        .outerjoin(Query, Query.assigned_staff_id == User.id)
        .group_by(User.username)
        .all()
    )
    staff_performance = [
        {
            'name': row[0],
            'tickets': row[1],
            'avg_resolution': round(row[2], 2) if row[2] else None,
        }
        for row in staff_performance_rows
    ]

    return render_template('admin/dashboard.html', packages=packages, events=events,
                         banners=banners, testimonials=testimonials, pages=pages, faqs=faqs,
                         total_packages=total_packages, total_events=total_events,
                         total_banners=total_banners, total_testimonials=total_testimonials,
                         destinations=destinations, dest_counts=dest_counts,
                         status_labels=status_labels, status_counts=status_counts,
                         total_queries=total_queries, overdue_queries=overdue_queries,
                         due_soon_queries=due_soon_queries, unassigned_queries=unassigned_queries,
                         query_type_labels=query_type_labels, query_type_counts=query_type_counts,
                         avg_first_response=round(avg_first_response, 1) if avg_first_response else None,
                         avg_resolution_hours=round(avg_resolution_hours, 1) if avg_resolution_hours else None,
                         staff_performance=staff_performance)

# Query inbox route with filters and search
@admin.route('/queries')
@login_required
def query_inbox():
    from sqlalchemy import or_

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 15, type=int)
    status = request.args.get('status')
    query_type = request.args.get('query_type')
    priority = request.args.get('priority')
    assigned_staff_id = request.args.get('assigned_staff')
    search = request.args.get('search')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    sla_filter = request.args.get('sla', 'all')

    now = datetime.utcnow()
    query = Query.query.options(joinedload(Query.assigned_staff))

    if status:
        query = query.filter(Query.status == status)
    if query_type:
        query = query.filter(Query.query_type.ilike(f'%{query_type}%'))
    if priority:
        query = query.filter(Query.priority == priority)
    if assigned_staff_id:
        try:
            assigned_staff_value = int(assigned_staff_id)
            query = query.filter(Query.assigned_staff_id == assigned_staff_value)
        except (TypeError, ValueError):
            flash('Invalid staff filter supplied.', 'warning')
    if from_date:
        try:
            start_dt = datetime.strptime(from_date, '%Y-%m-%d')
            query = query.filter(Query.created_at >= start_dt)
        except ValueError:
            flash('Invalid start date filter', 'warning')
    if to_date:
        try:
            end_dt = datetime.strptime(to_date, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(Query.created_at < end_dt)
        except ValueError:
            flash('Invalid end date filter', 'warning')
    if sla_filter == 'overdue':
        query = query.filter(
            Query.sla_deadline != None,  # noqa: E711
            Query.sla_deadline < now,
            Query.status.notin_(('Resolved', 'Closed')),
        )
    elif sla_filter == 'due_soon':
        query = query.filter(
            Query.sla_deadline != None,  # noqa: E711
            Query.sla_deadline.between(now, now + timedelta(hours=2)),
            Query.status.notin_(('Resolved', 'Closed')),
        )
    elif sla_filter == 'met':
        query = query.filter(
            Query.sla_deadline != None,  # noqa: E711
            Query.sla_deadline >= now,
            Query.status.in_(('Responded', 'Resolved', 'Closed')),
        )
    if search:
        query = query.filter(
            or_(
                Query.customer_name.ilike(f'%{search}%'),
                Query.customer_email.ilike(f'%{search}%'),
                Query.ticket_number.ilike(f'%{search}%'),
                Query.message.ilike(f'%{search}%'),
            )
        )

    query = query.order_by(Query.priority.desc(), Query.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    queries = pagination.items

    staff_list = User.query.order_by(User.username).all()
    query_type_rows = (
        db.session.query(Query.query_type).filter(Query.query_type != None).distinct().order_by(Query.query_type).all()  # noqa: E711
    )
    available_query_types = [row[0] for row in query_type_rows]

    status_breakdown = dict(db.session.query(Query.status, func.count(Query.id)).group_by(Query.status).all())
    priority_breakdown = dict(db.session.query(Query.priority, func.count(Query.id)).group_by(Query.priority).all())
    total_tickets = sum(status_breakdown.values()) if status_breakdown else 0
    total_priority = sum(priority_breakdown.values()) if priority_breakdown else 0
    sla_overview = {
        'overdue': Query.query.filter(
            Query.sla_deadline != None,  # noqa: E711
            Query.sla_deadline < now,
            Query.status.notin_(('Resolved', 'Closed')),
        ).count(),
        'due_soon': Query.query.filter(
            Query.sla_deadline != None,  # noqa: E711
            Query.sla_deadline.between(now, now + timedelta(hours=2)),
            Query.status.notin_(('Resolved', 'Closed')),
        ).count(),
        'met': Query.query.filter(
            Query.sla_deadline != None,  # noqa: E711
            Query.sla_deadline >= now,
            Query.status.in_(('Responded', 'Resolved', 'Closed')),
        ).count(),
    }

    return render_template(
        'admin/query_inbox.html',
        queries=queries,
        pagination=pagination,
        staff_list=staff_list,
        status=status,
        query_type=query_type,
        available_query_types=available_query_types,
        assigned_staff_id=assigned_staff_id,
        search=search,
        priority=priority,
        from_date=from_date,
        to_date=to_date,
        sla_filter=sla_filter,
        per_page=per_page,
        status_breakdown=status_breakdown,
        priority_breakdown=priority_breakdown,
        sla_overview=sla_overview,
        total_tickets=total_tickets,
        total_priority=total_priority,
    )

# Query detail route to view and update query
@admin.route('/query/<int:query_id>', methods=['GET', 'POST'])
@login_required
def query_detail(query_id):
    query_obj = (
        Query.query.options(
            joinedload(Query.responses).joinedload(QueryResponse.staff),
            joinedload(Query.assigned_staff),
        )
        .filter_by(id=query_id)
        .first_or_404()
    )
    staff_list = User.query.order_by(User.username).all()
    templates = QueryResponseTemplate.query.filter_by(is_active=True).order_by(QueryResponseTemplate.name).all()
    related_queries = (
        Query.query.filter(
            Query.customer_email == query_obj.customer_email,
            Query.id != query_obj.id,
        )
        .order_by(Query.created_at.desc())
        .limit(5)
        .all()
    )

    update_form = QueryUpdateForm(obj=query_obj)
    update_form.assigned_staff_id.choices = [(0, 'Unassigned')] + [(staff.id, staff.username) for staff in staff_list]
    update_form.assigned_staff_id.data = query_obj.assigned_staff_id or 0

    response_form = QueryResponseForm()
    response_form.template_id.choices = [(0, 'Select template')] + [(t.id, t.name) for t in templates]
    if response_form.template_id.data is None:
        response_form.template_id.data = 0
    if not response_form.subject.data:
        response_form.subject.data = f"Re: {query_obj.query_type or 'Your query'}"

    escalation_form = QueryEscalationForm()

    action = request.form.get('action')
    if request.method == 'POST' and action == 'update':
        if update_form.validate_on_submit():
            staff_id = update_form.assigned_staff_id.data or None
            query_obj.assigned_staff_id = staff_id if staff_id else None
            query_obj.status = update_form.status.data
            query_obj.priority = update_form.priority.data
            if query_obj.status in ('Responded', 'Resolved') and not query_obj.first_response_at:
                query_obj.first_response_at = datetime.utcnow()
            if query_obj.status in ('Resolved', 'Closed'):
                query_obj.resolved_at = datetime.utcnow()
            db.session.commit()
            flash('Query updated successfully.', 'success')
            return redirect(url_for('admin.query_detail', query_id=query_id))
    elif request.method == 'POST' and action == 'respond':
        if response_form.validate_on_submit():
            template_id = response_form.template_id.data or None
            if template_id == 0:
                template_id = None
            attachments = []
            if response_form.attachment_urls.data:
                attachments = [item.strip() for item in response_form.attachment_urls.data.split(',') if item.strip()]

            responding_staff_id = current_user.id if current_user.is_authenticated else query_obj.assigned_staff_id
            channel = 'internal' if response_form.log_internal_note.data else response_form.channel.data
            response_entry = QueryResponse(
                query_id=query_obj.id,
                staff_id=responding_staff_id,
                subject=response_form.subject.data,
                body=response_form.body.data,
                channel=channel,
                attachment_urls=",".join(attachments) if attachments else None,
                used_template_id=template_id,
                status_after=query_obj.status,
            )
            query_obj.responses.append(response_entry)
            query_obj.last_contact_channel = response_form.channel.data
            query_obj.last_response_summary = response_form.body.data[:500]
            if not query_obj.first_response_at:
                query_obj.first_response_at = datetime.utcnow()
            query_obj.status = 'Responded' if query_obj.status in ('Open', 'Pending', 'In Progress') else query_obj.status
            query_obj.updated_at = datetime.utcnow()
            db.session.add(response_entry)
            db.session.commit()

            if response_form.send_email.data and not response_form.log_internal_note.data:
                send_query_email(query_obj, response_entry.subject, response_entry.body, attachments)

            flash('Response recorded successfully.', 'success')
            return redirect(url_for('admin.query_detail', query_id=query_id))
    elif request.method == 'POST' and action == 'escalate':
        if escalation_form.validate_on_submit():
            query_obj.priority = escalation_form.priority.data
            query_obj.status = 'In Progress'
            query_obj.escalated_at = datetime.utcnow()
            query_obj.escalation_reason = escalation_form.reason.data
            db.session.commit()
            flash('Query escalated.', 'info')
            return redirect(url_for('admin.query_detail', query_id=query_id))

    templates_payload = [
        {'id': t.id, 'subject': t.subject, 'body': t.body, 'category': t.category} for t in templates
    ]

    return render_template(
        'admin/query_detail.html',
        query=query_obj,
        staff_list=staff_list,
        update_form=update_form,
        response_form=response_form,
        escalation_form=escalation_form,
        templates=templates,
        related_queries=related_queries,
        templates_payload=templates_payload,
    )

# Query response templates management
@admin.route('/query-templates', methods=['GET', 'POST'])
@login_required
def manage_query_templates():
    form = QueryTemplateForm()
    templates = QueryResponseTemplate.query.order_by(QueryResponseTemplate.updated_at.desc()).all()
    if form.validate_on_submit():
        template = QueryResponseTemplate(
            name=form.name.data,
            category=form.category.data,
            subject=form.subject.data,
            body=form.body.data,
            is_active=form.is_active.data,
        )
        db.session.add(template)
        db.session.commit()
        flash('Template saved successfully.', 'success')
        return redirect(url_for('admin.manage_query_templates'))
    return render_template('admin/query_templates.html', form=form, templates=templates)


@admin.route('/query-template/<int:template_id>/toggle', methods=['POST'])
@login_required
def toggle_query_template(template_id):
    template = QueryResponseTemplate.query.get_or_404(template_id)
    template.is_active = not template.is_active
    db.session.commit()
    flash(f"Template {'activated' if template.is_active else 'paused'}.", 'info')
    return redirect(url_for('admin.manage_query_templates'))


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
