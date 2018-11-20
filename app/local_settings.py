import os

# *****************************
# Environment specific settings
# *****************************

# DO NOT use "DEBUG = True" in production environments
DEBUG = True

# DO NOT use Unsecure Secrets in production environments
# Generate a safe one with:
#     python -c "import os; print repr(os.urandom(24));"
SECRET_KEY = 'This is an UNSECURE Secret. CHANGE THIS for production environments.'

# SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = 'sqlite:///../app.sqlite'
SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids a SQLAlchemy Warning

# Flask-Mail settings
# For smtp.gmail.com to work, you MUST set "Allow less secure apps" to ON in Google Accounts.
# Change it in https://myaccount.google.com/security#connectedapps (near the bottom).
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_SSL = False
MAIL_USE_TLS = True
MAIL_USERNAME = 'testcola086@gmail.com'
MAIL_PASSWORD = 'testcola4321'

# Sendgrid settings
SENDGRID_API_KEY='place-your-sendgrid-api-key-here'

# Flask-User settings (https://flask-user.readthedocs.io/en/latest/configuring_settings.html)
USER_APP_NAME = 'Credential-Manager'
USER_EMAIL_SENDER_NAME = 'Cola_Admin'
USER_EMAIL_SENDER_EMAIL = 'testcola086@gmail.com'
USER_PASSLIB_CRYPTCONTEXT_SCHEMES = ['pbkdf2_sha512','bcrypt'] # List of accepted password hashes.

ADMINS = [
    '"Admin One" <testcola086@gmail.com>',
    ]
