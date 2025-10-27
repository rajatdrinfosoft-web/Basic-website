import sys
import os
sys.path.append('pilgrim-packge')

from app import create_app
from app.models import User

app = create_app()

with app.app_context():
    user = User.query.filter_by(username='admin').first()
    print('Admin user exists:', user is not None)
    if user:
        print('Username:', user.username)
        print('Password check for admin123:', user.check_password('admin123'))
    else:
        print('Creating admin user...')
        admin = User(username='admin')
        admin.set_password('admin123')
        from app import db
        db.session.add(admin)
        db.session.commit()
        print('Admin user created.')
