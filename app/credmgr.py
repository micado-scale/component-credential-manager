"""[summary]
Credential Manager module
[description]
This module interface and implements the necessary functions of the Credential manager component of the framework. 
The component relies on Flask-User which applies MIT license
"""
import os
import csv
from flask import jsonify, abort, Response
from flask_restful import request, reqparse, fields, marshal, Resource
import json
from sqlalchemy import exc
from app import app
from app import db
from app.models.db_models import User, Role
from flask_user import UserManager
from flask_user.db_manager import DBManager
from flask_user import PasswordManager
from wtforms.validators import ValidationError
import re # Regular expression
import random # to generate password
from random import randint # to generate password
import string # to generate password

#from flask_user import DBManager

##### CONSTANT VALUES
# http codes
# Success
HTTP_CODE_OK = 200
HTTP_CODE_CREATED = 201
# Clients's errors
HTTP_CODE_BAD_REQUEST = 400
HTTP_CODE_UNAUTHORIZED = 401
#HTTP_CODE_NOT_FOUND = 404
HTTP_CODE_LOCKED = 423
# Server error
HTTP_CODE_SERVER_ERR = 500
##### END - CONSTANT VALUES

##### INITIALIZATION
# import the resource of all messages
#resource_file = os.path.join(os.getcwd(), 'resource.csv')
reader = csv.DictReader(open("resource.csv", 'r'))
msg_dict = {}
for row in reader:
	msg_dict[row['Code']] = row['Message']

# Regular expression for user name
# Username may contain A-Z, a-z, 0-9, -, _, . character(s). 
# Length must be between 3 to 10
# When you change this regular expression, please remember to change item 'invalid_user_name' in resource.csv
REG_EXP_USER_NAME = "^[a-zA-Z0-9_.-]{3,10}$" 

# Regular expression for user name for password.
# For meaning of regular expression: please see Reg 1 below as. 
# When you change this regular expression,
# please remember to change item 'invalid_pasword' in resource.csv 
# and (optional) change implementation of function "generate_passwd()"
PASSWD_MIN_LEN = 3
PASSWD_MAX_LEN = 10
REG_EXP_PASSWD = "(?=^.{PASSWD_MIN_LEN,}$)(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.*\s)[0-9a-zA-Z!@#$%^&*()]*$"

# Ready-to-use regular expressions for password
# Reg 1. Strong password 
# At least 1 lowercase letter, 1 uppercase letter, and 1 digit, 
# allow for some special characters like !@#. The length should be equal or greater than 3 characters.
# The sequence of the characters is not important.
# "(?=^.{3,}$)(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.*\s)[0-9a-zA-Z!@#$%^&*()]*$"

# Reg 2. Weak password
# Allow a-z, A-Z, 0-9. Length must be between 3 and 15
# "^[a-zA-Z0-9]{3,15}$" # A-Z, a-z, 0-9

# Regular expression for email
REG_EXP_EMAIL = "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

# Validators
def password_validator(password):
	if(re.match(REG_EXP_PASSWD,password)==None):
		raise ValidationError(msg_dict['invalid_pasword'])

def username_validator(username):
	if(re.match(REG_EXP_USER_NAME,username)==None): # if name does not follow the rule (only contains a-z, A-Z, 0-9)
		raise ValidationError(msg_dict['invalid_user_name'])

def email_validator(email):
	if(re.match(REG_EXP_EMAIL,email)==None):
		raise ValidationError(msg_dict['invalid_email'])	

# Setup Flask-User
user_manager = UserManager(app, db, User)
db_manager = DBManager(app, db, User)
pwd_manager = PasswordManager(app)

##### END - INITIALIZATION

##### RESOURCES
class User(Resource): 
	def get(self,user_name): # retrieve a user
		try:
			user = db_manager.find_user_by_username(user_name)
			if user is not None:
				data = {
					'username': user.username,
					'email':user.email,
					'first_name':user.first_name,
					'last_name':user.last_name,
					'active':user.active
				}
				user_roles = db_manager.get_user_roles(user)
				if user_roles:
					data.update({'roles' : user_roles})
				return create_response(HTTP_CODE_OK, specific_key='User', specific_value=data)
			else:
				return create_response(HTTP_CODE_BAD_REQUEST, user_message=msg_dict['uname_notexist'], developer_message=msg_dict['uname_notexist'])
		except exc.SQLAlchemyError as e:
			app.logger.error(e)
			abort(HTTP_CODE_SERVER_ERR,msg_dict['sqlalchemy_error']) # SQLAlchemyError
		except Exception as e:
			app.logger.error(e)
			abort(HTTP_CODE_SERVER_ERR,msg_dict['error_undefined'])

	def delete(self,user_name): # delete a user
		try:
			user = db_manager.find_user_by_username(user_name)
			if user is not None:
				db_manager.delete_object(user)
				db_manager.commit()
				return create_response(HTTP_CODE_OK, user_message=msg_dict['del_user_success'], developer_message=msg_dict['del_user_success'])
			else:
				return create_response(HTTP_CODE_BAD_REQUEST, user_message=msg_dict['uname_notexist'], developer_message=msg_dict['uname_notexist'])
		except exc.SQLAlchemyError as e:
			app.logger.error(e)
			abort(HTTP_CODE_SERVER_ERR,msg_dict['sqlalchemy_error']) # SQLAlchemyError
		except Exception as e:
			app.logger.error(e)
			abort(HTTP_CODE_SERVER_ERR,msg_dict['error_undefined'])

	def put(self,user_name): # update a user's firstname and/or lastname
		from app.models.db_models import User

		new_info = request.json

		firstname_flag = False
		lastname_flag = False

		# Retrieve optional data from POST request
		try:
		    first_name = new_info['firstname']
		    firstname_flag = True
		except Exception as e:
			pass

		try:
		    last_name = new_info['lastname']
		    lastname_flag = True
		except Exception as e:
			pass


		try:
			user = db_manager.find_user_by_username(user_name)
			if user is not None:		# Check if user exist
				if(firstname_flag):
					user.first_name = first_name 
				if(lastname_flag):
					user.last_name = last_name
				db_manager.commit()
				return create_response(HTTP_CODE_OK,user_message=msg_dict['user_update_success'], developer_message=msg_dict['user_update_success']) #, specific_key='User', specific_value=data)	
			else:
				return create_response(HTTP_CODE_BAD_REQUEST, user_message=msg_dict['uname_notexist'], developer_message=msg_dict['uname_notexist'])
		except exc.SQLAlchemyError as e:
			app.logger.error(e)
			abort(HTTP_CODE_SERVER_ERR,msg_dict['sqlalchemy_error']) # SQLAlchemyError
		except Exception as e:
			app.logger.error(e)
			abort(HTTP_CODE_SERVER_ERR,msg_dict['error_undefined'])
		
class Users(Resource): 
	def get(self): # Retrieve all users

		from app.models.db_models import User

		try:
			list_users = []
			for u in db.session.query(User.username):
				user = db_manager.find_user_by_username(u.username)
				if user is not None:
					user_data = {
						'username': user.username,
						'email':user.email,
						'first_name':user.first_name,
						'last_name':user.last_name,
						'active':user.active
					}
					user_roles = db_manager.get_user_roles(user)
					if user_roles:
						user_data.update({'roles' : user_roles})
					list_users.append(user_data)
			#list_users_json = json.dumps(list_users)
			return create_response(HTTP_CODE_OK, specific_key='Users', specific_value=list_users)
		except exc.SQLAlchemyError as e:
			app.logger.error(e)
			abort(HTTP_CODE_SERVER_ERR, msg_dict['sqlalchemy_error'])
			#return create_response(HTTP_CODE_SERVER_ERR, user_message= msg_dict['sqlalchemy_error'], developer_message = msg_dict['sqlalchemy_error'])


	def post(self): # add a new user
		user_info = request.json
		
		# Retrieve optional data from POST request
		try:
		    #Here are the optional json parameters inside a try
		    firstname = user_info['firstname']
		    lastname = user_info['lastname']
		except Exception as e:
			firstname = ""
			lastname = ""
		    #Here handle the exception, maybe parse some default values. 
			pass

   		# Retrieve mandatory data from POST request
		try:
		    username = user_info['username']
		    password = user_info['password']
		    email = user_info['email']
		except Exception as e:
		    app.logger.error(e)
		    return create_response(HTTP_CODE_BAD_REQUEST, user_message=msg_dict['lack_of_user_data'], developer_message=msg_dict['lack_of_user_data'])

		try: # Check if new_password satisfies password conditions defined by regular expression REG_EXP_PASSWD
			password_validator(password)
		except Exception as e:
			app.logger.error(e)
			return create_response(HTTP_CODE_BAD_REQUEST, user_message=msg_dict['invalid_pasword'], developer_message=msg_dict['invalid_pasword'])

		# compute hash value of password	
		user_hash_pwd = user_manager.hash_password(user_info['password'])
		
		try:
			username_validator(username)
		except Exception as e:
			app.logger.error(e)
			return create_response(HTTP_CODE_BAD_REQUEST, user_message=msg_dict['invalid_user_name'], developer_message=msg_dict['invalid_user_name'])

		try:
			email_validator(email)
		except Exception as e:
			app.logger.error(e)
			return create_response(HTTP_CODE_BAD_REQUEST, user_message=msg_dict['invalid_email'], developer_message=msg_dict['invalid_email'])

		try:
			newUser = db_manager.add_user(username=username, password = user_hash_pwd, email = email,  first_name = firstname, last_name = lastname)
			db_manager.commit()
			return create_response(HTTP_CODE_CREATED,msg_dict['add_user_success'],msg_dict['add_user_success'])
		except exc.IntegrityError as e: # existed user (existed username and/or email)
			app.logger.error(e)
			return create_response(HTTP_CODE_BAD_REQUEST,msg_dict['add_existed_user'],msg_dict['add_existed_user'])
		except exc.SQLAlchemyError as e:
			app.logger.error(e)
			abort(HTTP_CODE_SERVER_ERR,msg_dict['sqlalchemy_error']) # SQLAlchemyError
		except Exception as e:
			app.logger.error(e)
			abort(HTTP_CODE_SERVER_ERR,msg_dict['error_undefined'])

class Roles(Resource): 
	def get(self): # retrieve all roles
		from app.models.db_models import Role
		try:
			list_roles = []
			for role in db.session.query(Role.name, Role.label):
				role_data = {
						'name': role.name,
						'label':role.label
					}
				list_roles.append(role_data)
			return create_response(HTTP_CODE_OK, specific_key='Roles', specific_value=list_roles)
		except exc.SQLAlchemyError:
			abort(HTTP_CODE_SERVER_ERR, msg_dict['sqlalchemy_error'])
		except Exception as e:
			app.logger.error(e)
			abort(HTTP_CODE_SERVER_ERR,msg_dict['error_undefined'])
	
	def post(self): # add a new role
		role_info = request.json
		name = role_info['name']
		label = role_info['label']

		from app.models.db_models import Role

		role = Role.query.filter(Role.name == name).first()
		try:
			if not role:
				role = Role(name=name, label=label)
				db.session.add(role)
				db.session.commit()
				return create_response(HTTP_CODE_OK,msg_dict['add_role_success'],msg_dict['add_role_success'])
			else:
				return create_response(HTTP_CODE_BAD_REQUEST,msg_dict['add_role_exist'],msg_dict['add_role_exist'])
		except exc.IntegrityError as e: # existed role
			return create_response(HTTP_CODE_BAD_REQUEST,msg_dict['add_role_exist'],msg_dict['add_role_exist'])
		except exc.SQLAlchemyError as e:
			app.logger.error(e)
			abort(HTTP_CODE_SERVER_ERR,msg_dict['sqlalchemy_error']) # SQLAlchemyError
		except Exception as e:
			app.logger.error(e)
			abort(HTTP_CODE_SERVER_ERR,msg_dict['error_undefined'])

class Role(Resource):
	def delete(self,role_name): # delete a role. It also deletes this role from all users
		from app.models.db_models import Role
		try:
			role = Role.query.filter(Role.name == role_name).first()
			if role is not None:
				db_manager.delete_object(role)
				db_manager.commit()
				return create_response(HTTP_CODE_OK, user_message=msg_dict['del_role_success'], developer_message=msg_dict['del_role_success'])
			else:
				return create_response(HTTP_CODE_BAD_REQUEST, user_message=msg_dict['role_notexist'], developer_message=msg_dict['role_notexist'])
		except exc.SQLAlchemyError as e:
			app.logger.error(e)
			abort(HTTP_CODE_SERVER_ERR,msg_dict['sqlalchemy_error']) # SQLAlchemyError
		except Exception as e:
			app.logger.error(e)
			abort(HTTP_CODE_SERVER_ERR,msg_dict['error_undefined'])
	def get(self,role_name):	# retrieve a role
		try:
			from app.models.db_models import Role
			role = Role.query.filter(Role.name == role_name).first()
			if role is not None:
				data = {}
				data["name"] = role.name
				data["label"] = role.label
				#json_data = json.dumps(data)
				return create_response(HTTP_CODE_OK, specific_key='Roles',specific_value=data)
			else:
				return create_response(HTTP_CODE_BAD_REQUEST, user_message=msg_dict['role_notexist'], developer_message=msg_dict['role_notexist'])
		except exc.SQLAlchemyError as e:
			app.logger.error(e)
			abort(HTTP_CODE_SERVER_ERR,msg_dict['sqlalchemy_error']) # SQLAlchemyError
		except Exception as e:
			app.logger.error(e)
			abort(HTTP_CODE_SERVER_ERR,msg_dict['error_undefined'])	
	def put(self,role_name): # update a role
		try:
			from app.models.db_models import Role
			from sqlalchemy import update

			new_label = request.json['label']
			role = Role.query.filter(Role.name == role_name).first()
			if role is not None:
				role.label = new_label
				db.session.commit()
				return create_response(HTTP_CODE_OK,user_message=msg_dict['role_label_updated'], developer_message=msg_dict['role_label_updated'])
			else:
				return create_response(HTTP_CODE_BAD_REQUEST, user_message=msg_dict['role_notexist'], developer_message=msg_dict['role_notexist'])
		except exc.SQLAlchemyError as e:
			app.logger.error(e)
			abort(HTTP_CODE_SERVER_ERR,msg_dict['sqlalchemy_error']) # SQLAlchemyError
		except Exception as e:
			app.logger.error(e)
			abort(HTTP_CODE_SERVER_ERR,msg_dict['error_undefined'])	

class UserRole(Resource):
	def delete(self,user_name,role_name): # revoke a role of user
		from app.models.db_models import Role
		from app.models.db_models import User
		try:
			user = db_manager.find_user_by_username(user_name)
			if user is not None:		# Check if user exist
				role = Role.query.filter(Role.name == role_name).first() # check if role record exist
				if role is not None:
					user_roles = db_manager.get_user_roles(user) #.filter(Role.name == role_name).first()
					for assigned_role in user_roles:
						if assigned_role == role_name:
							user.roles.remove(role)
							db_manager.commit()
							return create_response(HTTP_CODE_OK,user_message=msg_dict['user_role_revoked'], developer_message=msg_dict['user_role_revoked'])			
					return create_response(HTTP_CODE_BAD_REQUEST, user_message=msg_dict['user_not_hold_role'], developer_message=msg_dict['user_not_hold_role'])	
				else:
					return create_response(HTTP_CODE_BAD_REQUEST, user_message=msg_dict['role_notexist'], developer_message=msg_dict['role_notexist'])	
				return create_response(HTTP_CODE_OK,user_message=msg_dict['user_role_assigned'], developer_message=msg_dict['user_role_assigned']) #, specific_key='User', specific_value=data)
			else:
				return create_response(HTTP_CODE_BAD_REQUEST, user_message=msg_dict['uname_notexist'], developer_message=msg_dict['uname_notexist'])
		except exc.SQLAlchemyError as e:
			app.logger.error(e)
			abort(HTTP_CODE_SERVER_ERR,msg_dict['sqlalchemy_error']) # SQLAlchemyError
		except Exception as e:
			app.logger.error(e)
			abort(HTTP_CODE_BAD_REQUEST,msg_dict['error_undefined'])

class UserRoles(Resource):
	def get(self,user_name): # List all roles of user
		try:
			user = db_manager.find_user_by_username(user_name)
			if user is not None:		# Check if user exist
				user_roles = db_manager.get_user_roles(user) #.filter(Role.name == role_name).first()
				return create_response(HTTP_CODE_OK, specific_key='Roles', specific_value=user_roles)
			else:
				return create_response(HTTP_CODE_BAD_REQUEST, user_message=msg_dict['uname_notexist'], developer_message=msg_dict['uname_notexist'])
		except exc.SQLAlchemyError as e:
			app.logger.error(e)
			abort(HTTP_CODE_SERVER_ERR,msg_dict['sqlalchemy_error']) # SQLAlchemyError
		except Exception as e:
			app.logger.error(e)
			abort(HTTP_CODE_SERVER_ERR,msg_dict['error_undefined'])
	def post(self,user_name): # add role(s) to user
		from app.models.db_models import Role
		from app.models.db_models import User

		new_roles = set(request.json['roles'])
		
		try:
			user = db_manager.find_user_by_username(user_name)
			if user is not None:		# Check if user exist
				#allowed_roles = Role.query.filter(Role.name == 'admin').first()# check if role record exist

				#allowed_roles = db.session.query(Role) # retrieve all role names
				#invalid_roles = set(new_roles) - set(allowed_roles)
				#print(allowed_roles)

				list_roles = Role.query.all()
				allowed_roles = []
				for role in list_roles:
					allowed_roles.append(role.name)

				invalid_roles = new_roles - set(allowed_roles)
				if invalid_roles==set([]): # if there is no invalid role
					user_roles = db_manager.get_user_roles(user) #.filter(Role.name == role_name).first()
					# find difference between current user_roles and new_roles
					diff_roles = new_roles - set(user_roles)
					print(diff_roles)
					for role_name in diff_roles:
						#print(role_name)
						role = next(filter(lambda x: x.name == role_name, list_roles)) # get Role object from list_roles
						#print(role)
						user.roles.append(role)
					db_manager.commit()
					return create_response(HTTP_CODE_OK,user_message=msg_dict['user_role_assigned'], developer_message=msg_dict['user_role_assigned']) #, specific_key='User', specific_value=data)				
				else:
					return create_response(HTTP_CODE_BAD_REQUEST, user_message=msg_dict['role_notexist'], developer_message=msg_dict['role_notexist'])	
			else:
				return create_response(HTTP_CODE_BAD_REQUEST, user_message=msg_dict['uname_notexist'], developer_message=msg_dict['uname_notexist'])
		except exc.SQLAlchemyError as e:
			app.logger.error(e)
			abort(HTTP_CODE_SERVER_ERR,msg_dict['sqlalchemy_error']) # SQLAlchemyError
		except Exception as e:
			app.logger.error(e)
			abort(HTTP_CODE_SERVER_ERR,msg_dict['error_undefined'])

class UserPwd(Resource):
	def put(self, user_name): # change password
		from app.models.db_models import User
		try:
			passwords = request.json
			pwd = passwords['current_password']
			new_pwd = passwords['new_password']

			try: # Check if new_password satisfies password conditions defined by regular expression REG_EXP_PASSWD
				password_validator(new_pwd)
			except Exception as e:
				app.logger.error(e)
				return create_response(HTTP_CODE_BAD_REQUEST, user_message=msg_dict['invalid_pasword'], developer_message=msg_dict['invalid_pasword'])

			user = db_manager.find_user_by_username(user_name)
			if user is not None:		# Check if user exist
				if user_manager.verify_password(pwd,user.password) == True:

					user.password = user_manager.hash_password(new_pwd)
					db_manager.commit()
					return create_response(HTTP_CODE_OK,user_message=msg_dict['change_pwd_success'], developer_message=msg_dict['change_pwd_success'])			
				else:
					return create_response(HTTP_CODE_BAD_REQUEST, user_message=msg_dict['current_password_not_match'], developer_message=msg_dict['current_password_not_match'])	
			else:
				return create_response(HTTP_CODE_BAD_REQUEST, user_message=msg_dict['uname_notexist'], developer_message=msg_dict['uname_notexist'])
		except exc.SQLAlchemyError as e:
			app.logger.error(e)
			abort(HTTP_CODE_SERVER_ERR,msg_dict['sqlalchemy_error']) # SQLAlchemyError
		except Exception as e:
			app.logger.error(e)
			abort(HTTP_CODE_SERVER_ERR,msg_dict['error_undefined'])
	def post(self,user_name): # verify password
		from app.models.db_models import User
		try:
			pwd = request.json['password']
			user = db_manager.find_user_by_username(user_name)
			if user is not None:		# Check if user exist
				if user_manager.verify_password(pwd,user.password) == True:
					return create_response(HTTP_CODE_OK,user_message=msg_dict['auth_success'], developer_message=msg_dict['auth_success'])			
				else:
					return create_response(HTTP_CODE_BAD_REQUEST, user_message=msg_dict['uname_pwd_wrong'], developer_message=msg_dict['pwd_notmatch'])	
			else:
				return create_response(HTTP_CODE_BAD_REQUEST, user_message=msg_dict['uname_pwd_wrong'], developer_message=msg_dict['uname_notexist'])
		except exc.SQLAlchemyError as e:
			app.logger.error(e)
			abort(HTTP_CODE_SERVER_ERR,msg_dict['sqlalchemy_error']) # SQLAlchemyError
		except Exception as e:
			app.logger.error(e)
			abort(HTTP_CODE_SERVER_ERR,msg_dict['error_undefined'])
	def delete(self, user_name): # reset password
		from app.models.db_models import User
		try:
			user = db_manager.find_user_by_username(user_name)
			if user is not None:		# Check if user exist
				new_pwd = generate_passwd()
				print(new_pwd)
				user.password = user_manager.hash_password(new_pwd)
				db_manager.commit()
				return create_response(HTTP_CODE_OK,specific_key='New reset password', specific_value=new_pwd)			
			else:
				return create_response(HTTP_CODE_BAD_REQUEST, user_message=msg_dict['uname_notexist'], developer_message=msg_dict['uname_notexist'])
		except exc.SQLAlchemyError as e:
			app.logger.error(e)
			abort(HTTP_CODE_SERVER_ERR,msg_dict['sqlalchemy_error']) # SQLAlchemyError
		except Exception as e:
			app.logger.error(e)
			abort(HTTP_CODE_SERVER_ERR,msg_dict['error_undefined'])
	
def create_response(message_code,user_message=None,developer_message=None, specific_key=None, specific_value=None):
	data = {
			'code' : message_code
	}
	if user_message is not None:
		data.update({'user message'  : user_message})
	if developer_message is not None:
		data.update({'developer message' : developer_message})
	if specific_key is not None and specific_value is not None:
		data.update({specific_key:specific_value})
	js = json.dumps(data)
	resp = Response(js, status=message_code, mimetype='application/json')
	return resp

def find_or_create_role(name, label):
    """ Find existing role or create new role """
    role = Role.query.filter(Role.name == name).first()
    if not role:
        role = Role(name=name, label=label)
        db.session.add(role)
    return role

def generate_passwd():
	"""[summary]
	The function randomly generates a password.
	Returns:
		[type: String] -- [description: a generated password]
	"""
	characters = string.ascii_letters + string.digits # + string.punctuation
	passwd =  "".join(random.choice(characters) for x in range(randint(PASSWD_MIN_LEN, PASSWD_MAX_LEN)))
	return passwd