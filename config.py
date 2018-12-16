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


class ConfigFU(Config):
    
    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///basic_app.sqlite'    # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids SQLAlchemy warning

    # Flask-Mail SMTP server settings
    MAIL_DEFAULT_SENDER = '"Gabor Admin" <gbcode62@gmail.com>'

    # Flask-User settings
    USER_APP_NAME = "Flask-User Basic App"      # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = True        # Enable email authentication
    USER_ENABLE_USERNAME = True    # Disable username authentication
    USER_EMAIL_SENDER_NAME = USER_APP_NAME
    USER_EMAIL_SENDER_EMAIL = '"Gabor Admin" <gbcode62@gmail.com>'
