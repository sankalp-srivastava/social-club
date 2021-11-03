from flaskblog import db
from flask import current_app
current_app.app_context().push()
db.create_all()