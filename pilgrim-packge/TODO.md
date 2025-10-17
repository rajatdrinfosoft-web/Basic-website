# TODO: Build Full Flask Website with Admin Panel

## 1. Database Models
- [x] Expand Package model with fields: duration, inclusions, exclusions, destination, best_time, group_size, overview, itinerary
- [x] Add Event model for upcoming events
- [x] Add User model for admin authentication

## 2. Dependencies
- [x] Install Flask-Login, Flask-WTF, WTForms

## 3. Authentication Setup
- [x] Update app/__init__.py to initialize Flask-Login
- [x] Create app/auth.py with login/logout routes

## 4. Admin Panel
- [x] Create app/admin_routes.py with CRUD for packages and events
- [x] Create admin templates (login.html, dashboard.html, package_form.html, event_form.html)

## 5. Main Routes
- [x] Update app/routes.py: home (fetch from DB), packages list with filters, package detail, about, contact

## 6. Templates
- [x] Update home.html to use DB data
- [x] Create packages.html (list with filters)
- [x] Create package_detail.html
- [x] Create about.html and contact.html
- [x] Update nav.html and footer.html if needed

## 7. Forms
- [x] Create app/forms.py with WTForms for admin data entry

## 8. Seed Database
- [x] Create seed script to populate packages and events from extra/ data

## 9. Cleanup
- [x] Delete a.html and settings.py

## 10. Configuration and Init
- [x] Update config.py for any new settings
- [x] Run DB init and seed

## 11. Testing
- [x] Test admin login and CRUD
- [x] Test public pages
- [x] Run locally and verify

## 12. Additional Updates
- [x] Add SECRET_KEY to config.py
- [x] Create Contact model and form
- [x] Replace Zoho form with custom contact form
- [x] Update admin dashboard to show contact messages
- [x] Update database schema
