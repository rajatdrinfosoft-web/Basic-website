# Pilgrim Packages — Flask Web Application

## Overview
Pilgrim Packages is a dynamic web application built with Flask for managing and showcasing pilgrim tour packages in India. It features an admin panel for content management, user authentication, package listings, event displays, and a contact form. The app is designed for tourism businesses focusing on spiritual journeys like Char Dham Yatra, Amarnath Yatra, and visits to the Golden Temple.

## Features
- **User Authentication**: Admin login with Flask-Login for secure access to the admin panel.
- **Package Management**: CRUD operations for tour packages including details like itinerary, inclusions, exclusions, pricing, and ratings.
- **Event Management**: Display and manage upcoming events related to pilgrim sites.
- **Contact Form**: Collect user inquiries with name, email, phone, and message.
- **Responsive UI**: Built with Bootstrap 5.3, Jinja2 templates, and custom CSS/JS.
- **Caching & Compression**: Integrated Flask-Caching and Flask-Compress for performance.
- **Asset Bundling**: Flask-Assets for minifying and bundling CSS/JS.
- **Database**: PostgreSQL with SQLAlchemy ORM and Flask-Migrate for schema management.
- **Seeding**: Pre-seeded data for packages and events via `seed.py`.
- **Admin Dashboard**: Manage packages, events, and view contacts.

## Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/rajatdrinfosoft-web/Basic-website.git
   cd pilgrim-packge
   ```

2. **Set Up Virtual Environment** (Recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On macOS/Linux
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   Note: Ensure you have Python 3.8+ installed.

4. **Configure Database**:
   - Update `config.py` with your PostgreSQL connection string.
   - For development, the config uses Neon PostgreSQL. Change `SECRET_KEY` for production.

5. **Initialize Database**:
   ```bash
   flask db init  # If not already done
   flask db migrate
   flask db upgrade
   ```

6. **Seed Database** (Optional):
   ```bash
   python seed.py
   ```
   This adds sample packages (e.g., Char Dham Yatra) and events.

## Usage
1. **Run the Application**:
   ```bash
   python run.py
   ```
   The app will run on `http://localhost:5000` in debug mode.

2. **Access the Site**:
   - Homepage: Browse packages and events.
   - Admin Login: Go to `/admin/login` (default: username `admin`, password `admin123`).
   - Admin Dashboard: Manage packages, events, and contacts.

3. **Key Routes**:
   - `/`: Home page with featured packages and events.
   - `/packages`: List all packages.
   - `/package/<id>`: Package details.
   - `/about`, `/contact`: Static pages.
   - `/admin/dashboard`: Admin panel.

## Project Structure
```
pilgrim-packge/
├── app/
│   ├── __init__.py          # Flask app factory and extensions
│   ├── models.py            # SQLAlchemy models (User, Package, Event, Contact)
│   ├── routes.py            # Main routes (home, packages, contact)
│   ├── auth.py              # Authentication routes
│   ├── admin_routes.py      # Admin panel routes
│   ├── forms.py             # WTForms for forms
│   ├── static/              # CSS, JS, images
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   └── templates/           # Jinja2 templates
│       ├── base.html        # Base template
│       ├── home.html        # Homepage
│       ├── packages.html    # Package listings
│       ├── package_detail.html  # Package details
│       ├── about.html       # About page
│       ├── contact.html     # Contact page
│       └── admin/           # Admin templates
│           ├── dashboard.html
│           ├── login.html
│           ├── package_form.html
│           └── event_form.html
├── migrations/              # Alembic migrations
├── extra/                   # Additional static files (e.g., index.html)
├── config.py                # Configuration settings
├── run.py                   # Entry point to run the app
├── seed.py                  # Database seeding script
├── TODO.md                  # Feature roadmap and improvements
├── TODO_IMPROVEMENTS.md     # Additional tasks
└── README.md                # This file
```

## Dependencies
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-Caching
- Flask-Assets
- Flask-Migrate
- Flask-Compress
- WTForms
- Bootstrap 5.3 (via CDN)
- PostgreSQL

## Contributing
1. Fork the repository.
2. Create a feature branch: `git checkout -b feature-name`.
3. Make changes and commit: `git commit -m 'Add feature'`.
4. Push to branch: `git push origin feature-name`.
5. Open a pull request.

Refer to `TODO.md` for planned enhancements like security improvements, performance optimizations, and new features.

## License
This project is licensed under the MIT License. See LICENSE file for details.

## Contact
For questions or contributions, contact the project maintainer.

