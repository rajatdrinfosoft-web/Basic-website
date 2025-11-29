import os
os.chdir('pilgrim-packge')
from app import create_app, db
app = create_app()
app.app_context().push()

from app.models import Package
p = Package.query.first()
if p:
    p.images = '[]'
    p.video_url = None
    p.is_featured = False
    db.session.commit()
    print('Updated existing package with new fields')
else:
    print('No packages found')
