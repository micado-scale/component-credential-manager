micado-credential-manager
------------------------------------------------------
__Version__: v1.0

__File structures:__
- my_script.py : the main script
- resource.csv : containing definition for notification messages, error messages,...
- config.py : configuring the admin's email, database filename and file location
- app :
  - _init_py : initialize log handler and database
  - routes.py : add URL rule for all rest APIs
  - dbmodels.py : implementation of all rest APIs (HTTP return codes are defined by constants in this file)
- template:
  - reset_pwd_mail.html: template mail to notify the user about password reset
- test_script.rst : the Robot framework test script that can be used for automatic acceptance tests
- lib :
  - LoginLibrary.py : the library that contains all API used in the test scripts
- API documentation : Documentation for the whole source code
- micadoctl.sh : Bash script to run in the master node (host machine). After that, inside the master node, admin can run command line to add user, verify user,...

__How to use Rest API:__

Assuming that the following command lines are called inside a docker container in the master node, and the rest APIs are provided by the credential manager, i.e. "credman" container.

- Add a new user (the user's role will be 'USER' as default):

curl -d "username=user01&password=123" credman:5001/v1.1/adduser

- Verify a user:

curl -d "username=user01&password=123" credman:5001/v1.1/verify

- Change a user's password:

curl -d "username=user01&oldpasswd=123&newpasswd=456" -X PUT credman:5001/v1.0/changepwd

- Reset a user's password:

curl -d "username=user01" credman:5001/v1.1/resetpwd

- Delete a user:

curl -d "username=user01" credman:5001/v1.1/deleteuser

- Retrieve a user's role

curl -d "username=user01" credman:5001/v1.1/getrole

- Change a user's role (There are 2 roles: user or admin)

curl -d "username=user01&newrole=user" -X PUT credman:5001/v1.1/changerole

curl -d "username=user01&newrole=admin" -X PUT credman:5001/v1.1/changerole

__How to use the test_script.rst:__

Assuming that you installed Robot framework successfully (Please follow this link if you has not installed the Robot framework yet: https://github.com/robotframework/QuickStartGuide/blob/master/QuickStart.rst#demo-application)

Change the following values defined in the section Variables with approriate information if you wish to test the feature of sending email for resetting password:
- receiverEmail@mail.com
- receverMailPassword
- senderEmail
- imap.gmail.com

You may need to change the settings in your mail account to let less secure apps access your account if the mail server requires. For instance, gmail requires that.

Run the following command line
- robot test_script.rst

__How to run command line in the master node (host machine):__

- Add a new user (the user's role will be 'USER' as default):

micadoctl.sh adduser user01 123

- Verify a user:

micadoctl.sh verify user01 123

- Change a user's password:

micadoctl.sh changepwd user01 123 456

(change the password from 123 to 456)

- Reset a user's password:

micadoctl.sh resetpwd user01

- Delete a user:

micadoctl.sh deleteuser user01

- Retrieve a user's role

micadoctl.sh getrole user01

- Change a user's role (There are 2 roles: user or admin)

micadoctl.sh changerole user01 user

(Change the role into 'user')

micadoctl.sh changerole user01 admin

(Change the role into 'admin')