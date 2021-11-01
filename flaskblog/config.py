import os
class Config():
    SECRET_KEY = os.environ.get('APP_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('ADMIN_USER_USERNAME')
    MAIL_PASSWORD = os.environ.get('ADMIN_USER_PASSWORD')