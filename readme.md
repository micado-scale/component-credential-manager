micado-credential-manager
------------------------------------------------------
v1.0:
File structures:
- Messages are organized in the csv file: resource.csv
- All initialization (log handler, database creation)  are put in the _init_.py module: app/_init_.py
- Rest API routing is configured in: app/routes.py
- Configuration (sender's mail configuration, database filename selection) is configured in: config.py
- Main script: my_script.py
- Mail templates are in: template/
- HTTP return codes are described by constants defined in dbmodels.py

Example: 
Assuming that the following command lines are called towards the credential manager, i.e. credman component, from another component inside the master node.

- Add a new user:

curl -d "username=user01&password=123" credman:5001/v1.0/adduser

- Verify a user:

curl -d "username=user01&password=123" credman:5001/v1.0/verify

- Change a user's password:

curl -d "username=user01&oldpasswd=123&newpasswd=456" -X PUT credman:5001/v1.0/changepwd

- Reset a user's password:

curl -d "username=user01" credman:5001/v1.0/resetpwd

- Delete a user:
TBD
