
from flask_user import UserMixin

from app import db


# User Model
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    # User login information 
    username = db.Column(db.String(64), index=True, nullable=False, unique=True)
    email = db.Column(db.Unicode(255), nullable=False, server_default=u'', unique=True)
    password = db.Column(db.String(255), nullable=False) # server_default=''
    

    active = db.Column(db.Boolean(), nullable=False, server_default='0')

    # User information
    first_name = db.Column(db.Unicode(50), nullable=False, server_default=u'')
    last_name = db.Column(db.Unicode(50), nullable=False, server_default=u'')

    # Relationships
    roles = db.relationship('Role', secondary='users_roles',
                            backref=db.backref('users', lazy='dynamic'))
    # accesslog = db.relationship('AccessLog', backref='author', lazy='dynamic')

# class AccessLog(db.Model):
#     """[summary]
#     The class AccessLog defines the model for table AccessLog.
#     [description]
#     This class defines all fields of the table AccessLog, for i.e. id, start_time, etc.
#     Extends:
#         db.Model
    
#     Variables:
#         id {[type: Integer]} -- [description: identity]
#         user_id {[type: Integer]} -- [description: Identity of the user. This is the foreign key to the table User]
#         start_time {[type: Datetime]} -- [description: Datetime of log-in]
#     """
#     __tablename__ = 'access_log'
#     # Field: id
#     id = db.Column(db.Integer, primary_key=True)
#     # Field: user_id
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
#     # Field: start_time
#     #start_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
#     # Field: lock_status
#     lock_status = db.Column(db.Boolean, default = True) #current_app.config['DB_DEFAULT_LOCK_STATUS_VALUE']
#     # Field: lock_start_time
#     lock_start_time = db.Column(db.DateTime)
#     # Field: no_fails as number of fails
#     no_fails = db.Column(db.Integer, default = 0)

# Role data model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False, server_default=u'', unique=True)  # for @roles_accepted()
    label = db.Column(db.Unicode(255), server_default=u'')  # for display purposes


# UserRoles association table
class UsersRoles(db.Model):
    __tablename__ = 'users_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))
