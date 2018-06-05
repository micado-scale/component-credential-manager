"""[summary]
Database models module
[description]
The dbmodels defines models for the databases for i.e. table User and AccessLog. Later, corresponding databases will be created from these models in the init module. 
"""
from datetime import datetime
from app import db
from app import app
from flask_restful import request
from flask import jsonify, abort, Response
import json
from werkzeug.security import generate_password_hash, check_password_hash
import os
from sqlalchemy import exc
import sqlite3
from random import *
import string
import logging
import csv
from string import Template
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import io
from datetime import datetime
from datetime import timedelta

# Constants
PASSWD_LEN = 256 # bits
PASSWD_MIN_LEN = 8 # characters
PASSWD_MAX_LEN = 16 # characters
MAX_FAILS = 5
LOCKED = False
UNLOCKED = True
LOCK_DURATION = 6 # seconds
USER_ROLE = 0
ADMIN_ROLE = 2
USER_ROLE_LIST = ['user','admin']
# http codes
# Success
HTTP_CODE_OK = 200
# HTTP_CODE_CREATED = 201
# Clients's errors
HTTP_CODE_BAD_REQUEST = 400
HTTP_CODE_UNAUTHORIZED = 401
#HTTP_CODE_NOT_FOUND = 404
HTTP_CODE_LOCKED = 423
# Server error
HTTP_CODE_SERVER_ERR = 500



FROM_ADDRESS = app.config['MAIL_USERNAME']
MAIL_PWD = app.config['MAIL_PASSWORD']
SEND_MAIL_RESET_PWD = app.config['MAIL_SEND_RESET_PWD'] # Send mail whenever password is reset



# import the resource of all messages
reader = csv.DictReader(open('resource.csv', 'r'))
msg_dict = {}
for row in reader:
	msg_dict[row['Code']] = row['Message']

class User(db.Model):
	"""[summary]
	The class User defines the model for table User.
	[description]
	This class defines all fields of the table User, for i.e. id, username, password, etc.
	Extends:
		db.Model
	
	Variables:
		id {[type: Integer]} -- [description: identity]
		username {[type: string]} -- [description: user name]
		email {[type: string]} -- [description: email]
		password_hash {[type: string]} -- [description: hash value of password]
		accesslog {[type: relationship]} -- [description: relationship between the two databases User and AccessLog]
	"""
	# Field: id. It is auto-increment by default
	id = db.Column(db.Integer, primary_key=True) 
	# Field: username
	username = db.Column(db.String(64), index=True, unique=True)
	# Field: email
	email = db.Column(db.String(120), index=True, unique=True)
	# Field: password_hash
	password_hash = db.Column(db.String(PASSWD_LEN))
	# Field: user role
	role = db.Column(db.Integer, default = USER_ROLE)
	# define relationship with database model accesslog
	accesslog = db.relationship('AccessLog', backref='author', lazy='dynamic')

	def __repr__(self):
		return '<User {}>'.format(self.username)
		
	def __init__(self, username, password, email='', role=USER_ROLE): # change TO_ADDR to ''
		"""[summary]
		Constructor
		[description]
		This constructor initalizes a user object with username and password
		Arguments:
			username {[type: string]} -- [description: user name]
			password {[type: string]} -- [description: password]
		"""
		self.username = username
		self.password_hash = password
		self.email = email
		self.role = role


class AccessLog(db.Model):
	"""[summary]
	The class AccessLog defines the model for table AccessLog.
	[description]
	This class defines all fields of the table AccessLog, for i.e. id, start_time, etc.
	Extends:
		db.Model
	
	Variables:
		id {[type: Integer]} -- [description: identity]
		user_id {[type: Integer]} -- [description: Identity of the user. This is the foreign key to the table User]
		start_time {[type: Datetime]} -- [description: Datetime of log-in]
	"""
	# Field: id
	id = db.Column(db.Integer, primary_key=True)
	# Field: user_id
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	# Field: start_time
	#start_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	# Field: lock_status
	lock_status = db.Column(db.Boolean, default = UNLOCKED)
	# Field: lock_start_time
	lock_start_time = db.Column(db.DateTime)
	# Field: no_fails as number of fails
	no_fails = db.Column(db.Integer, default = 0)

	def __repr__(self):
		return '<AccessLog {}>'.format(self.body)
	def __init__(self, uid):
		"""[summary]
		Constructor
		[description]
		This constructor initalizes a user object with username and password
		Arguments:
			username {[type: string]} -- [description: user name]
			password {[type: string]} -- [description: password]
		"""
		self.user_id = uid
		self.no_fails = 1
			
def hash_passwd(passwd):
	"""[summary]
	The function hashes a password.
	[description]
	This function creates a hash value with salf for an inputted password.
	Arguments:
		passwd {[type : string]} -- [description : Hashing using SHA 256 with salt of size 8 bits]
	
	Returns:
		[type : string] -- [description : hash value of size 256 bits]
	"""
	key = generate_password_hash(passwd) # default method='pbkdf2:sha256', default salt_length=8
	return key

def generate_passwd():
	"""[summary]
	The function randomly generates a password.
	[description]
	This function generates randomly a password from ascii letters and digits. The length of password is limitted from PASSWD_MIN_LEN to PASSWD_MAX_LEN
	
	Returns:
		[type: String] -- [description: a generated password]
	"""
	characters = string.ascii_letters + string.digits # + string.punctuation
	passwd =  "".join(choice(characters) for x in range(randint(PASSWD_MIN_LEN, PASSWD_MAX_LEN)))
	return passwd

def add_user(uname, passwd, email=''):
	"""[summary]
	The function adds a user in the table User.
	[description]
	This function adds a user into the table User.	
	
	Arguments:
		uname {[type: String]} -- [description: user name]
		passwd {[type: String]} -- [description: password]
	"""
	try:
		# create new user
		passwd_hash = hash_passwd(passwd)
		new_user = User(uname, passwd_hash, email)
		
		# add new user to database
		db.session.add(new_user)
		db.session.commit()
	# Catch the exception
	except exc.IntegrityError as e: # existed user
		db.session.rollback()
		raise
	except exc.SQLAlchemyError as e:
		# Roll back any change if something goes wrong
		db.session.rollback()
		raise # Raise error again so that it will be caught in create_user_api()'''
	except Exception as e:
		# Roll back any change if something goes wrong
		db.session.rollback()
		app.logger.error(e)
		raise
	finally:
		# Close the db connection
		db.session.close()
		

def create_user_api():
	"""[summary]
	
	[description]
	The function add_user() inserts a user into the database
	Input: username in URL request argument
	Output: password (inputted or randomized), or a raised error
	Body: the user's password is randomized or inputted from URL request
	
	Returns:
		[type: json] -- [description: code, message for the user, message for the developer]
	"""
	# parse parameters from http request. Use request.values instead of request.args to indicate parameters possibly come from argument or form
	uname = request.values.get("username")
	passwd = request.values.get("password")
	email = request.values.get("email")
	if(email is None):
		email=''

	msg_passwd = msg_dict['pwd_setby_user'] # Password is set by inputted value from the user
	if(passwd is None):
		# random a default password
		passwd = generate_passwd()
		msg_passwd = msg_dict['pwd_generated'] + passwd # Password is auto-generated. Its value is:  

	# create a user
	app.logger.info(msg_dict['add_user_progress']) # Trying to add a user to database
	
	try:
		add_user(uname, passwd, email)
		data = {
			'code' : HTTP_CODE_OK,
			'user message'  : msg_dict['add_user_success'],#'Add user successfully',
			'developer message' : msg_passwd
		}
		js = json.dumps(data)
		resp = Response(js, status=HTTP_CODE_OK, mimetype='application/json')
		return resp
	except exc.IntegrityError as e: # existed user
		data = {
			'code' : HTTP_CODE_BAD_REQUEST,
			'user message'  : msg_dict['add_existed_user'], #Add existed user
			'developer message' : msg_dict['add_existed_user']
		}
		js = json.dumps(data)
		resp = Response(js, status=HTTP_CODE_BAD_REQUEST, mimetype='application/json')
		return resp
	except exc.SQLAlchemyError as e:
		app.logger.error(e)
		abort(HTTP_CODE_SERVER_ERR,msg_dict['sqlalchemy_error']) # SQLAlchemyError
	except Exception as e:
		app.logger.error(e)
		abort(HTTP_CODE_BAD_REQUEST,msg_dict['error_undefined'])

def reset_passwd_api():
	"""[summary]
	This function is for resetting password of a user.
	[description]
	Only administrator is allowed to call this API.
	Returns:
		[type: json] -- [description: code, message for the developer, new password if resetting successfully]
	"""
	uname = request.values.get("username")

	app.logger.info(msg_dict['reset_pwd_progress'])#Reset password of user"
	try:
		user = db.session.query(User.email).filter_by(username=uname).first()
		if(user == None):
			data = {
				'code' : HTTP_CODE_BAD_REQUEST,
				'developer message' : msg_dict['uname_notexist'], # User name does not exist
			}
			js = json.dumps(data)
			resp = Response(js, status=HTTP_CODE_BAD_REQUEST, mimetype='application/json')
		else:
			passwd =  generate_passwd()
			passwd_hash = generate_password_hash(passwd)
			db.session.query(User).filter_by(username=uname).update({User.password_hash: passwd_hash})
			db.session.commit()
			data = {
				'code' : HTTP_CODE_OK,
				'developer message' : msg_dict['reset_pwd_success'], # Reset password successfully
				'new password' : passwd
			}
			js = json.dumps(data)
			resp = Response(js, status=HTTP_CODE_OK, mimetype='application/json')
			if(SEND_MAIL_RESET_PWD == True): # NOTE: Add try...catch error from sending email
				to_addr = user[0]
				try:
					if(to_addr!=''): # send email only email address exists
						send_reset_pwd_mail(uname,passwd, FROM_ADDRESS,to_addr,'template/reset_pwd_mail.html');
				except Exception as e:
					app.logger.error(e)
		return resp
	except exc.SQLAlchemyError as e:
		db.session.rollback()
		app.logger.error(e)
		abort(HTTP_CODE_SERVER_ERR,msg_dict['sqlalchemy_error'])
	except Exception as e:
		db.session.rollback()
		app.logger.error(e)
		abort(HTTP_CODE_SERVER_ERR,msg_dict['error_undefined'])
	finally:
		db.session.close()

# API to verify a user	
def verify_user_api():
	"""[summary]
	This function is for verifying a user.
	[description]
	The function retrieves the user name and password from the request, then check if they exists in the database or not.
	Returns:
		[type: json] -- [description: code, message for the user, authentication result]
	"""
	try:
		uname = request.values.get("username")
		passwd = request.values.get("password")
		
		if(uname==None or passwd==None): # Verify parameters
			data = {
				'code' : HTTP_CODE_BAD_REQUEST,
	 			'user message'  : msg_dict['uname_pwd_wrong'],
	 			'result' : msg_dict['uname_pwd_wrong'] # User name does not exist
			}
			js = json.dumps(data)
			resp = Response(js, status=HTTP_CODE_OK, mimetype='application/json')
			return resp

		# Check password
		uid_pwd = db.session.query(User.id, User.password_hash, User.email).filter_by(username=uname).first()
		
		# If there does not exist the inputted user name 'uname'
		if(uid_pwd == None):
			data = {
				'code' : HTTP_CODE_UNAUTHORIZED,
	 			'user message'  : msg_dict['uname_pwd_wrong'],
	 			'result' : msg_dict['uname_notexist'] # User name does not exist
			}
		else: # If the user exists
			# Check lock status			
			uid = uid_pwd[0]
			latest_log = db.session.query(AccessLog.lock_status, AccessLog.no_fails, AccessLog.lock_start_time).filter_by(user_id=uid).first()		
			if(latest_log == None): # if there's no log
				lock_status = 'Not locked'
				number_fails = 0
			else:
				if (latest_log[0] == UNLOCKED): # check lock status
					lock_status = 'Not locked'
				else:
					lock_status = 'Locked'
				number_fails = latest_log[1]

			# If user is locked, check if time is over
			current_time = datetime.now()
			if(lock_status == 'Locked'):
				if((current_time - latest_log[2]).total_seconds()>LOCK_DURATION): # if time is over
					db.session.query(AccessLog).filter_by(user_id=uid).update({AccessLog.lock_status: UNLOCKED, AccessLog.no_fails: '0'}) # unlock the user and reset the number of fails to 0
					lock_status = 'Not locked'
					number_fails = 0
			
			if(lock_status == 'Locked'): # Announce that user is being locked
				lock_until = latest_log[2] + timedelta(seconds=LOCK_DURATION)
				data = {
					'code' : HTTP_CODE_LOCKED,
	 				'user message'  : msg_dict['being_locked_user'],
	 				'result' : msg_dict['being_locked_user'] + lock_until.strftime('%m/%d/%Y %H:%M:%S'), #http://strftime.org/
	 				'lock status': lock_status,
				}
			else: # verify the password
				stored_passwd = uid_pwd[1]
				result = check_password_hash(stored_passwd,passwd)
				if (result == True): # password matched
					data = {
						'code' : HTTP_CODE_OK,
		 				'user message'  : msg_dict['auth_success'],
		 				'result' : msg_dict['auth_success'],
		 				'lock status': lock_status,
		 				'role': "user" # 2. modify to other roles later
					}
					# Unlock
					if(latest_log != None):
						db.session.query(AccessLog).filter_by(user_id=uid).update({AccessLog.lock_status: UNLOCKED, AccessLog.no_fails: 0}) # unlock the user and reset the number of fails to 0	
				else: # password does not match
					number_fails = number_fails + 1
					message = msg_dict['pwd_notmatch']
					# add log of failed attempts to log-in				
					if(latest_log == None): # It has not been logged before
						new_log = AccessLog(uid)
						db.session.add(new_log)
						db.session.commit()
					else:
						lock_time = datetime.now()	
						if(number_fails > MAX_FAILS): # Locked if fails more then MAX_FAILS times
							db.session.query(AccessLog).filter_by(user_id=uid).update({AccessLog.no_fails: number_fails, AccessLog.lock_status: LOCKED, AccessLog.lock_start_time: lock_time}) # update the number of fails and lock status						
							lock_status = 'Locked'
							lock_until = lock_time + timedelta(seconds=LOCK_DURATION)
							message = message + msg_dict['lock_user_now'] + lock_until.strftime('%m/%d/%Y %H:%M:%S')
						else:	
							db.session.query(AccessLog).filter_by(user_id=uid).update({AccessLog.no_fails: number_fails}) # update the number of fails only
							lock_status = 'Not locked' # check if omitting this is possible
						db.session.commit()
					if(lock_status=='Locked'):
						http_code = HTTP_CODE_LOCKED
					else:
						http_code = HTTP_CODE_UNAUTHORIZED
					data = {
						'code' : http_code,
		 				'user message'  : msg_dict['auth_fail'],
		 				'result' : message, # password does not match
		 				'number of fails': number_fails,
		 				'lock status': lock_status
					}
		js = json.dumps(data)
		resp = Response(js, status=HTTP_CODE_OK, mimetype='application/json')
		return resp
	# Catch the exception
	except Exception as e:
		app.logger.error(e)
		abort(HTTP_CODE_SERVER_ERR,msg_dict['error_undefined'])

def delete_user_api():
	"""[summary]
	This function is for deleting a user from the table User
	[description]
	The function retrieves the user name and password from the request, then delete it if it exists in the database.
	Only administrator can call this API.
	Returns:
		[type: json] -- [description: code, message for the user, message for the developer]
	"""
	try:
		uname = request.values.get("username")
		app.logger.info("Delete a user")

		user = db.session.query(User).filter_by(username=uname).first()
		if(user == None):
			data = {
				'code' : HTTP_CODE_BAD_REQUEST,
				'user message': msg_dict['uname_notexist'],
				'developer message' : msg_dict['uname_notexist'], # User name does not exist
			}
			js = json.dumps(data)
			resp = Response(js, status=HTTP_CODE_BAD_REQUEST, mimetype='application/json')
		else:
			db.session.delete(user)
			db.session.commit()
			data = {
				'code' : HTTP_CODE_OK,
				'user message' : msg_dict['del_user_success'],
				'developer message' : msg_dict['del_user_success'],
			}
			js = json.dumps(data)
			resp = Response(js, status=HTTP_CODE_OK, mimetype='application/json')
		return resp
	except exc.SQLAlchemyError as e:
		db.session.rollback()
		app.logger.error(e)
		abort(HTTP_CODE_SERVER_ERR,msg_dict['sqlalchemy_error'])
	# Catch the exception
	except Exception as e:
		db.session.rollback()
		db.session.close()
		app.logger.error(e)
		abort(HTTP_CODE_SERVER_ERR,msg_dict['error_undefined'])

def read_template(filename):
	"""[summary]
	This function is for reading a template from a file
	[description]
	
	Arguments:
		filename {[type]} -- [description]
	
	Returns:
		[type] -- [description]
	"""
	with io.open(filename, encoding = 'utf-8') as template_file:
		content = template_file.read()
	return Template(content)


def send_reset_pwd_mail(receiver_name, new_pwd, from_addr, to_addr, template_file):
	# set up the SMTP server
	mail_server = smtplib.SMTP(host='smtp.gmail.com', port=587)
	if mail_server.starttls()[0] != 220: # start using tls
		return False # cancel if connection is not encrypted
	mail_server.login(FROM_ADDRESS, MAIL_PWD) # log in email of the admin

	message_template = read_template(template_file)

	msg = MIMEMultipart() # create a message

	# add in the actual person name to the message template
	message = message_template.substitute(PERSON_NAME=receiver_name.title(), PWD = new_pwd)

	# setup the parameters of the message
	msg['From']= from_addr
	msg['To']= to_addr
	msg['Subject']="[MiCADO] Reset your password"
	
	msg.attach(MIMEText(message, 'html'))

	mail_server.sendmail(msg['From'], msg['To'], msg.as_string())
    
	del message # delete the message

	mail_server.quit()
	return True

def change_password_api():
	"""[summary]
	This function is for changing password of a user.
	[description]
	Only current user is allowed to use this function for himself
	Returns:
		[type: json] -- [description: ]
	"""
	uname = request.values.get("username")
	old_passwd = request.values.get("oldpasswd")
	new_passwd = request.values.get("newpasswd")

	app.logger.info(msg_dict['change_pwd_progress'])#Reset password of user"
	try:
		user = db.session.query(User.password_hash).filter_by(username=uname).first()
		if(user == None):
			data = {
				'code' : HTTP_CODE_BAD_REQUEST,
				'developer message' : msg_dict['uname_notexist'], # User name does not exist
			}
			js = json.dumps(data)
			resp = Response(js, status=HTTP_CODE_BAD_REQUEST, mimetype='application/json')
		else:
			stored_passwd = user[0]
			result = check_password_hash(stored_passwd,old_passwd)
			if (result == True): # password matched
				passwd_hash = generate_password_hash(new_passwd)
				db.session.query(User).filter_by(username=uname).update({User.password_hash: passwd_hash})
				db.session.commit()
				data = {
					'code' : HTTP_CODE_OK,
					'developer message' : msg_dict['change_pwd_success'], # Reset password successfully
					# 'new password' : new_passwd
				}
				js = json.dumps(data)
				resp = Response(js, status=HTTP_CODE_OK, mimetype='application/json')
			else:
				data = {
					'code' : HTTP_CODE_BAD_REQUEST,
					'developer message' : msg_dict['change_pwd_fail'],
				}
				js = json.dumps(data)
				resp = Response(js, status=HTTP_CODE_BAD_REQUEST, mimetype='application/json')
		return resp
	except exc.SQLAlchemyError as e:
		db.session.rollback()
		app.logger.error(e)
		abort(HTTP_CODE_SERVER_ERR,msg_dict['sqlalchemy_error'])
	except Exception as e:
		db.session.rollback()
		app.logger.error(e)
		abort(HTTP_CODE_SERVER_ERR,msg_dict['error_undefined'])
	finally:
		db.session.close()

def change_role_api():
	try:
		uname = request.values.get("username")
		new_role_meaning = request.values.get("newrole")
		app.logger.info("Change the user's role")

		if(new_role_meaning not in USER_ROLE_LIST):
			data = {
				'code' : HTTP_CODE_BAD_REQUEST,
				'user message': msg_dict['role_notexist'],
				'developer message' : msg_dict['role_notexist'], # User name does not exist
			}
			js = json.dumps(data)
			resp = Response(js, status=HTTP_CODE_BAD_REQUEST, mimetype='application/json')
			return resp

		user = db.session.query(User).filter_by(username=uname).first()
		if(user == None):
			data = {
				'code' : HTTP_CODE_BAD_REQUEST,
				'user message': msg_dict['uname_notexist'],
				'developer message' : msg_dict['uname_notexist'], # User name does not exist
			}
			js = json.dumps(data)
			resp = Response(js, status=HTTP_CODE_BAD_REQUEST, mimetype='application/json')
		else:
			current_role = user.role

			if(new_role_meaning=='admin'):
				new_role = ADMIN_ROLE
			else:
				new_role = USER_ROLE

			if (current_role == new_role):
				data = {
					'code' : HTTP_CODE_OK,
					'user message' : msg_dict['same_user_role'],
					'developer message' : msg_dict['same_user_role'],
				}
			else:
				db.session.query(User).filter_by(username=uname).update({User.role: new_role})
				db.session.commit()
				data = {
					'code' : HTTP_CODE_OK,
					'user message' : msg_dict['change_user_role_success'],
					'developer message' : msg_dict['change_user_role_success'],
				}
			js = json.dumps(data)
			resp = Response(js, status=HTTP_CODE_OK, mimetype='application/json')
		return resp
	except exc.SQLAlchemyError as e:
		db.session.rollback()
		app.logger.error(e)
		abort(HTTP_CODE_SERVER_ERR,msg_dict['sqlalchemy_error'])
	# Catch the exception
	except Exception as e:
		db.session.rollback()
		db.session.close()
		app.logger.error(e)
		abort(HTTP_CODE_SERVER_ERR,msg_dict['error_undefined'])
	
def retrieve_role_api():
	try:
		uname = request.values.get("username")
		app.logger.info("Retrieve the user's role")

		user = db.session.query(User).filter_by(username=uname).first()
		if(user == None):
			data = {
				'code' : HTTP_CODE_BAD_REQUEST,
				'user message': msg_dict['uname_notexist'],
				'developer message' : msg_dict['uname_notexist'], # User name does not exist
			}
			js = json.dumps(data)
			resp = Response(js, status=HTTP_CODE_BAD_REQUEST, mimetype='application/json')
		else:
			if(user.role==USER_ROLE):
				user_role_meaning = 'user'
			if (user.role==ADMIN_ROLE):
				user_role_meaning = 'admin'
			data = {
				'code' : HTTP_CODE_OK,
				'role' : user_role_meaning,
			}
			js = json.dumps(data)
			resp = Response(js, status=HTTP_CODE_OK, mimetype='application/json')
		return resp
	except exc.SQLAlchemyError as e:
		db.session.rollback()
		app.logger.error(e)
		abort(HTTP_CODE_SERVER_ERR,msg_dict['sqlalchemy_error'])
	# Catch the exception
	except Exception as e:
		db.session.rollback()
		db.session.close()
		app.logger.error(e)
		abort(HTTP_CODE_SERVER_ERR,msg_dict['error_undefined'])