from flask_migrate import upgrade
from app import create_app, db

app = create_app()
app.app_context().push()

# Apply migrations programmatically
upgrade()
print("Database migrations have been applied successfully.")
