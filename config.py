"""[summary]

[description]
This module defines configuration for the project

Variables:
	basedir {[type]} -- [description]
"""
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	"""[summary]
	
	[description]
	This class sets configuration for the project. For instance, database configuration
	
	Variables:
		SQLALCHEMY_DATABASE_URI {[type]} -- [description]
		SQLALCHEMY_TRACK_MODIFICATIONS {bool} -- [description]
	"""
	
	# Define database location
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'credential.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	# Mail configuration
	MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.googlemail.com'
	MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
	MAIL_USE_TLS = int(os.environ.get('MAIL_USE_TLS') or 1)is not None
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'your_email@gmail.com' # from address
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'your_email_password' # fill in the password here
	ADMINS = ['your_email@gmail.com'] # to address

#DATABASE_CONFIG = {
 #   'PASSWD_LEN': 'localhost'
 #}