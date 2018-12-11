import os


class Config:

    #   SECRET_KEY = '7f85eda25a67a9c3a43f8d591159fedb'
    # SQLALCHEMY_DATABASE_URI = 'mysql://flask_db_user:flask@localhost/flask_blog'
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT')

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USERNAME = os.environ.get('SMTP_EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('SMTP_EMAIL_PASS')
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False