.. default-role:: code
.. code:: robotframework

	*** Settings *** 				
	Library     lib/TestLibrary.py 			
	*** Test Cases *** 				
	Print hello 					
		print_hello
		Status should be    ${http_code_ok}

	Admin can create a user
		Create a user    ${username}    ${password}   ${email}    ${firstname}    ${lastname}
		Status should be    ${http_code_created}

	Admin can retrieve a user information
		Retrieve a user        ${username}
		Status should be    ${http_code_ok}
		Data should be    ${email}${firstname}${lastname}

	Admin can change a user information
		Update a user    ${username}    ${new_firstname}    ${new_lastname}
		Status should be    ${http_code_ok}
		Retrieve a user        ${username}
		Status should be    ${http_code_ok}
		Data should be    ${email}${new_firstname}${new_lastname}

	Admin can create roles in MiCADO
		Create role    ${rolename_admin}       ${rolelabel_admin}
		Status should be    ${http_code_ok}
		Create role    ${rolename_user}       ${rolelabel_user}
		Status should be    ${http_code_ok}
		Create role    ${rolename_developer}       ${rolelabel_developer}
		Status should be    ${http_code_ok}
	
	Admin can retrieve roles in MiCADO
		Retrieve role    ${rolename_admin}
		Status should be    ${http_code_ok}
		Data should be    ${rolelabel_admin} 

	Admin can retrieve all roles in MiCADO
		Retrieve all roles
		Status should be    ${http_code_ok}

	Admin can grant a list of roles to a user
		Grant roles to a user    ${username}    @{role_list}
		Status should be    ${http_code_ok}
		Retrieve roles from a user    ${username}
		Data list should be    ${role_list}

	Admin can retrieve list of roles of a user
		Retrieve roles from a user    ${username}
		Status should be    ${http_code_ok}

	User can verify its user name and password
		Verify user name and password    ${username}    ${password}
		Status should be    ${http_code_ok}

	User cannot be authenticated with invalid password
		Verify user name and password    ${username}   ${invalid password}
		Status Should Be    ${http_code_bad_request} 

	User cannot be authenticated with invalid user name
		Verify user name and password	 ${invalid username}		${password}
		Status should be    ${http_code_bad_request} 

	User can change its password
		Change password    ${username}    ${password}    ${new_password}
		Status should be    ${http_code_ok}
		Verify user name and password    ${username}    ${password}
		Status should be    ${http_code_bad_request}
		Verify user name and password    ${username}    ${new_password}
		Status should be    ${http_code_ok}

	Admin can reset user password
		Reset password     ${username}
		Status should be    ${http_code_ok}
		Verify user name and password    ${username}    ${new_password}
		Status should be    ${http_code_bad_request}

	Admin can revoke a role from a user
		Revoke role from a user    ${username}    ${rolename_user}
		Status should be    ${http_code_ok}
		Retrieve roles from a user    ${username}
		Data list should be    ${left_list}

	Admin can update a role label
		Update role    ${rolename_user}    ${role_newlabel_user}
		Status should be    ${http_code_ok}
		Retrieve role    ${rolename_user}
		Data should be    ${role_newlabel_user}

	Admin can delete roles
		Delete role    ${rolename_user}
		Status should be    ${http_code_ok}
		Retrieve role    ${rolename_user}
		Status should be    ${http_code_bad_request}
		Delete role    ${rolename_admin}
		Status should be    ${http_code_ok}
		Retrieve role    ${rolename_admin}
		Status should be    ${http_code_bad_request}
		Delete role    ${rolename_developer}
		Status should be    ${http_code_ok}
		Retrieve role    ${rolename_developer}
		Status should be    ${http_code_bad_request}

	Admin can delete a user
		Delete a user     ${username}
		Status should be    ${http_code_ok}


	*** Variables ***
	${http_code_ok}           200
	${http_code_bad_request}    400
	${http_code_created}    201

	${username}               user1
	${password}               1aBc
	${email}    			  user1@mail.com
	${firstname}              user1fn
	${lastname}               user1ln

	${invalid_username}       user01
	${invalid_password}       1abc


	${new_firstname}          user1fn_new
	${new_lastname}           user1ln_new
	${new_password}           1aBcnew

	${rolename_user}	      user
	${rolelabel_user}         UserRole
	${role_newlabel_user}         User

	${rolename_admin}         admin
	${rolelabel_admin}        Admin

	${rolename_developer}     dev
	${rolelabel_developer}         Developer

	@{role_list}              ${rolename_user}    ${rolename_admin}    ${rolename_developer}
	@{left_list}			  ${rolename_admin}    ${rolename_developer}

	*** Keywords ***
	.. USERS
	Create a user 
		[Arguments]    ${username}    ${password}	${email}    ${firstname}   ${lastname}			
		add_user	${username}    ${password}    ${email}    ${firstname}    ${lastname}
	Delete a user
		[Arguments]    ${username}
		delete_user	   ${username}
	Update a user
		[Arguments]    ${username}    ${new_firstname}    ${new_lastname}
		update_user	   ${username}    ${new_firstname}    ${new_lastname}
	Retrieve a user
		[Arguments]    ${username}
		retrieve_user	   ${username}

	.. PASSWORD
	Verify user name and password
		[Arguments]    ${username}    ${password}
		verify_user    ${username}    ${password}
	Change password
		[Arguments]    ${username}    ${current_password}    ${new_password}
		change_user_password    ${username}    ${current_password}    ${new_password}
	Reset password
		[Arguments]    ${username}
		reset_user_password     ${username}

	.. ROLES
	Create role
		[Arguments]    ${role_name}       ${role_label}
		create_a_role    ${role_name}      ${role_label}
	Retrieve role
		[Arguments]    ${role_name}
		retrieve_a_role    ${role_name}
	Retrieve all roles
		retrieve_existed_roles
	Delete role
		[Arguments]    ${role_name}
		delete_a_role    ${role_name}
	Update role
		[Arguments]    ${role_name}    ${new_role_label}
		update_a_role    ${role_name}    ${new_role_label}

	.. USER ROLES
	Grant roles to a user
		[Arguments]    ${username}   @{role_list}
		grant_user_roles    ${username}   ${role_list}
	Revoke role from a user
		[Arguments]    ${username}    ${role_name}
		revoke_user_role    ${username}    ${role_name}
	Retrieve roles from a user
		[Arguments]    ${username}
		get_user_roles    ${username}