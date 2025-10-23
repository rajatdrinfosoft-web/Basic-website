import os
os.chdir('pilgrim-packge')
from app import create_app, db
app = create_app()
app.app_context().push()

from app.models import Package
p = Package.query.first()
if p:
    p.images = '["https://example.com/image1.jpg", "https://example.com/image2.jpg"]'
    p.video_url = 'https://www.youtube.com/embed/dQw4w9WgXcQ'
    p.is_featured = True
    db.session.commit()
    print('Updated package with sample photo gallery data')
else:
    print('No packages found')
