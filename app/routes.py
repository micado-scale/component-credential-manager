"""[summary]
This modules contains URL rules for all APIs
[description]

"""

from app import app, credmgr
from flask_restful import Api
#@app.route('/')
#@app.route('/index')

def index():
	"""[summary]
	Hello world function
	[description]
	This function is only for testing if the web service is in operating
	"""
	return "Hello, this is the Credential Manager component!"
    
app.add_url_rule('/v2.0/','index',index)

api = Api(app)

# User resource
api.add_resource(credmgr.Users,'/v2.0/users')
api.add_resource(credmgr.User,'/v2.0/user/<user_name>')

# Role resource
api.add_resource(credmgr.Roles,'/v2.0/roles')
api.add_resource(credmgr.Role,'/v2.0/role/<role_name>')

# User's role resource
api.add_resource(credmgr.UserRole,'/v2.0/user/<user_name>/role/<role_name>')
api.add_resource(credmgr.UserRoles,'/v2.0/user/<user_name>/role')

# User's password resource
api.add_resource(credmgr.UserPwd,'/v2.0/user/<user_name>/password')