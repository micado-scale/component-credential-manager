"""[summary]
This modules contains URL rules for all APIs
[description]

Variables:
	app.add_url_rule('/','index',index) {[type]} -- [description]
	app.add_url_rule('/v1.0/adduser','create_user_api', dbmodels.create_user_api, methods {list} -- [description]
	app.add_url_rule('/v1.0/verify','verify_user_api', dbmodels.verify_user_api, methods {list} -- [description]
	app.add_url_rule('/v1.0/resetpwd','reset_passwd_api', dbmodels.reset_passwd_api, methods {list} -- [description]
	app.add_url_rule('/v1.0/deleteuser','delete_user_api', dbmodels.delete_user_api, methods {list} -- [description]
"""

from app import app, dbmodels

#@app.route('/')
#@app.route('/index')
def index():
	"""[summary]
	Hello world function
	[description]
	This function is only for testing if the web service is in operating
	"""
	return "Hello, this is the Credential Manager component!"
    
app.add_url_rule('/v1.0/','index',index)
# app.add_url_rule('/getuser','get_user', dbmodels.get_user,methods=['GET'])
# endpoint to create new user
app.add_url_rule('/v1.1/adduser','create_user_api', dbmodels.create_user_api, methods=['POST'])
app.add_url_rule('/v1.1/verify','verify_user_api', dbmodels.verify_user_api, methods=['POST'])
app.add_url_rule('/v1.1/resetpwd','reset_passwd_api', dbmodels.reset_passwd_api, methods=['PUT'])
app.add_url_rule('/v1.1/deleteuser','delete_user_api', dbmodels.delete_user_api, methods=['PUT'])
app.add_url_rule('/v1.1/changepwd','change_password_api', dbmodels.change_password_api, methods=['PUT'])
app.add_url_rule('/v1.1/changerole','change_role_api', dbmodels.change_role_api, methods=['PUT'])
app.add_url_rule('/v1.1/getrole','retrieve_role_api', dbmodels.retrieve_role_api, methods=['GET'])
app.add_url_rule('/v1.1/listusers','list_users_api', dbmodels.list_users_api, methods=['GET'])
