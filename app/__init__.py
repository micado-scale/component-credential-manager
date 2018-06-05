"""[summary]
Init module
[description]
The init module creates Flask object, databases, and logging handler
"""
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import sqlite3
from config import Config
from flask_sqlalchemy import SQLAlchemy
import os
import csv

import logging
from logging.handlers import RotatingFileHandler
from logging.handlers import SMTPHandler

# create application object of class Flask
app = Flask(__name__)
app.config.from_object(Config) # retrieve database configuration from the class Config
db = SQLAlchemy(app)

from app import dbmodels
from app import routes

# create all databases from dbmodels
db.create_all()
db.session.commit()

#provision initial values from csv and remove file on success
if os.access(app.config['PROVISION_FILE'], os.R_OK):
    with open(app.config['PROVISION_FILE'], 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            db.session.add(dbmodels.User(username=row['Username'], password=row['Password'], email=row['Email'], role=dbmodels.ADMIN_ROLE))
        f.close()
        db.session.commit()
        os.unlink(app.config['PROVISION_FILE'])

#if not app.debug:
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

#if not app.debug:
if app.config['MAIL_SERVER']:
    auth = None
    if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
        auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
    secure = None
    if app.config['MAIL_USE_TLS']:
        secure = ()
    mail_handler = SMTPHandler(
        mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
        fromaddr='no-reply@' + app.config['MAIL_SERVER'],
        toaddrs=app.config['ADMINS'], subject='System Failure',
        credentials=auth, secure=secure)
    mail_handler.setLevel(logging.ERROR) # change to CRITICAL later
    app.logger.addHandler(mail_handler)
