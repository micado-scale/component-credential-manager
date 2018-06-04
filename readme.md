micado-credential-manager
------------------------------------------------------
v1.0:

** File structures: **
- my_script.py : the main script
- resource.csv : containing definition for notification messages, error messages,...
- config.py : configuring the admin's email, database filename and file location
- app :
  - _init_py : initialize log handler and database
  - routes.py : add URL rule for all rest APIs
  - dbmodels.py : implementation of all rest APIs (HTTP return codes are described by constants defined in this file)
- template:
  - reset_pwd_mail.html: template mail to notify the user about password reset

** How to use Rest API: **

Assuming that the following command lines are called inside a docker container in the master node, and the rest APIs are provided by the credential manager, i.e. credman container.

- Add a new user:

curl -d "username=user01&password=123" credman:5001/v1.0/adduser

- Verify a user:

curl -d "username=user01&password=123" credman:5001/v1.0/verify

- Change a user's password:

curl -d "username=user01&oldpasswd=123&newpasswd=456" -X PUT credman:5001/v1.0/changepwd

- Reset a user's password:

curl -d "username=user01" credman:5001/v1.0/resetpwd

- Delete a user:

curl -d "username=01" credman:5001/v1.0/deleteuser
