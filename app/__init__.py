# __init__.py is a special Python file that allows a directory to become
# a Python package so it can be accessed using the 'import' statement.

from datetime import datetime
import os

from flask import Flask
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_user import UserManager
from flask_wtf.csrf import CSRFProtect

import logging
from logging.handlers import RotatingFileHandler
from logging.handlers import SMTPHandler


# Instantiate Flask extensions
csrf_protect = CSRFProtect()
db = SQLAlchemy()
mail = Mail()


# Initialize Flask Application
def create_app():
    # Instantiate Flask
    app = Flask(__name__)

    # Load common settings
    app.config.from_object('app.settings')
    # Load environment specific settings
    app.config.from_object('app.local_settings')
    
    # Setup Flask-SQLAlchemy
    db.init_app(app)

    # Setup Flask-Mail
    mail.init_app(app)

    # Setup an error-logger to send emails to app.config.ADMINS
    set_log_handlers(app)

    # Setup Flask-User to handle user account related forms
    # from .models.db_models import User


    # # Setup Flask-User
    # user_manager = UserManager(app, db, User)

    # @app.context_processor
    # def context_processor():
    #     return dict(user_manager=user_manager)

    return app

def set_log_handlers(app):
    
    # initialize the log handler: The handler used is RotatingFileHandler which rotates the log file when the size of the file exceeds a certain limit.
    logHandler = RotatingFileHandler('info.log', maxBytes=1000, backupCount=1) 
    # set the log handler level
    logHandler.setLevel(logging.INFO)
    # create formatter and add it to the handlers: date time - name of package - file name (module name) - function name - line number - level (error, infor,...) - message 
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(module)s - %(funcName)s - %(lineno)d- %(levelname)s - %(message)s')
    logHandler.setFormatter(formatter)

    # set the app logger level:  ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'). See http://flask.pocoo.org/docs/0.12/errorhandling/
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(logHandler)

    #Setup logger to send emails on error-level messages to app.config.ADMINS.
    
    if app.debug: return  # No error emails in developing

    # Retrieve email settings from app.config
    host = app.config['MAIL_SERVER']
    port = app.config['MAIL_PORT']
    from_addr = app.config['MAIL_DEFAULT_SENDER']
    username = app.config['MAIL_USERNAME']
    password = app.config['MAIL_PASSWORD']
    secure = () if app.config.get('MAIL_USE_TLS') else None

    # Retrieve app settings from app.config
    to_addr_list = app.config['ADMINS']
    subject = app.config.get('APP_SYSTEM_ERROR_SUBJECT_LINE', 'System Error')

    mail_handler = SMTPHandler(
        mailhost=(host, port),  # Mail host and port
        fromaddr=from_addr,  # From address
        toaddrs=to_addr_list,  # To address
        subject=subject,  # Subject line
        credentials=(username, password),  # Credentials
        secure=secure,
    )
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

# instantiate app
app = create_app()

from app import routes