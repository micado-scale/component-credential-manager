default-role:: code
.. code:: robotframework

	*** Settings *** 				
	Library     lib/test_lib.py
	Library     ImapLibrary

	*** Test Cases *** 				
	Print hello 					
		${resp}= 	print_hello
		Should Be Equal As Strings 	${resp.status_code} 	${http_code_ok}
	
	Admin can create a user
		Create user    ${username}    ${password}   ${email}    ${firstname}    ${lastname}
		Status should be    ${http_code_ok}

	Admin can create a role in MiCADO
		Create role    ${rolename_user}       ${rolelabel_user}
		Status should be    ${http_code_ok}
		Create role    ${rolename_admin}       ${rolelabel_admin}
		Status should be    ${http_code_ok}

	Admin can grant a list of roles to a user
		Grant roles to a user    ${username}    ${role_list}

	User can be authenticated with valid credential
		Verify a user    ${username}   ${password}
		Status should be    ${http_code_ok}

	User cannot be authenticated with invalid password
		Verify a user    ${username}   ${invalid password}
		Status Should Be    ${http_code_unauthorized} 

	User cannot be authenticated with invalid user name
		Login 	 ${invalid username}		${password}
		Status should be    ${http_code_unauthorized} 

	Admin cannot create account with existed user name
		Create user    ${username}    ${password}
		Status should be    ${http_code_bad_request}

	User cannot create account with empty user name
		Create user     ${null username}    ${null password}
		Status should be    ${http_code_bad_request}
	
	User can change password then log in with new password, cannot log in with old password
		Change user password    ${username}    ${password}    ${new password}
		Status should be   ${http_code_ok}
		Login     ${username}    ${new password}
		Status should be    ${http_code_ok}
		Login     ${username}    ${password}
		Status should be    ${http_code_unauthorized} 

	User can reset password and then cannot log in with the old password
		Reset password    ${username}
		Status should be    ${http_code_ok}
		Login    ${username}    ${password}
		Status should be    ${http_code_unauthorized} 

	User cannot reset password of non-existed username
		Reset password    ${invalid username}
		Status should be    ${http_code_bad_request}

	User who fails to log in continuously should be locked in fixed time
	    Delete a user    ${username}
	    Status should be    ${http_code_ok}	
	    Create user    ${username}    ${password}
	    Status should be    ${http_code_ok}	
		: FOR    ${INDEX}    IN RANGE    0    ${max_fails}
		\    Log    ${INDEX}
		\    Login    ${username}    ${invalid password}
		\    Status should be    ${http_code_unauthorized}
		Log    For loop is over
		Login    ${username}    ${invalid password}
		Status should be    ${http_code_locked}
		Sleep    ${half_lock_duration}
		Login    ${username}    ${password}
		Status should be    ${http_code_locked}
		Sleep    ${half_lock_duration}
		Login    ${username}    ${password}
		Status should be    ${http_code_ok}

	Admin can delete a user
		Delete a user     ${username}
		Status should be    ${http_code_ok}		

	Admin cannot delete a non-existing user
		Delete a user     ${username}
		Status should be    ${http_code_bad_request}

	Admin can create user with auto-generated password then delete it
		Create user with auto-generated password    ${username}
		Status should be    ${http_code_ok}
		Delete a user     ${username}
		Status should be    ${http_code_ok}		

	Email Verification
		Create user with email    ${username}    ${password}   ${receiver_email}
		Status should be    ${http_code_ok}	
		Reset password    ${username}
		Status should be    ${http_code_ok}
		Delete a user     ${username}
		Status should be    ${http_code_ok}	
		Open Mailbox    host=${mail_server}   user=${receiver_email}      password=${receiver_passwd}
		${LATEST}=    Wait For Email    sender=${sender_email}    timeout=300
		${HTML} =     Get Email body    ${LATEST}
		Should Contain    ${HTML}    ${email_reset_pwd_body}
		Close Mailbox

	User List
		Create user with auto-generated password    check_length
		${user_list} =	Get User List
		Log	${user_list}
		Should Not Be Empty	${_user_list}

	*** Variables ***
	${username}               user1
	${password}               123
	${email}    			  "user1@mail.com"
	${firstname}              "user1fn"
	${lastname}               "user1ln"

	${rolename_user}         "user"
	${rolelabel_user}         "User"

	${rolename_admin}         "admin"
	${rolelabel_admin}        "Admin"

    ${role_list}              [${rolename_user},${rolename_admin}]

	${invalid username}       Daisy
	${null password}          ''
	${null username}          ''
	${invalid password}       1234
	${new password}           123
	${http_code_ok}           200
	${http_code_bad_request}    400
	${http_code_unauthorized}    401
	${http_code_locked}        423
	${max_fails}				5
	${lock_duration}          6
	${half_lock_duration}          3
	${receiver_email}        receiverEmail@mail.com
	${receiver_passwd}      receverMailPassword
	${sender_email}         senderEmail
	${mail_server}          imap.gmail.com
	${email_reset_pwd_subject}        [MiCADO] Reset your password
	${email_reset_pwd_body}    We received a request to reset your password in the MiCADO infrastructure.
	${new_role_1}               user
	${new_role_2}               admin
	${pwd_generated_msg}      Password is auto-generated.

	*** Keywords ***
	* Users *
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

	* Password *
	Verify a user
		[Arguments]    ${username}    ${password}
		verify_user    ${username}    ${password}

	Reset user password
		[Arguments]    ${username}
		reset_password  ${username}

	Change user password
		[Arguments]    ${username}    ${current_password}    ${new_password}
		reset_password  ${username}   ${current_password}    ${new_password}


	* Roles *
	Retrieve a role
		[Arguments]    ${role_name}
		retrieve_one_role    ${role_name}

	Create role
		[Arguments]    ${role_name}       ${role_label}
		create_a_role    ${role_name}      ${role_label}

	Delete role
		[Arguments]    ${role_name}
		delete_a_role    ${role_name}

	Update role
		[Arguments]    ${role_name}    ${new_role_label}
		update_a_role    ${role_name}    ${new_role_label}

	* User Roles *
	Revoke a role
		[Arguments]    ${username}    ${role_name}
		revoke_user_role     ${username}    ${role_name}
	Retrieve a user roles
		[Arguments]    ${username}
		get_user_roles    ${username}
	Grant roles to a user
		[Arguments]    ${username}   ${role_list}
		grant_user_roles    ${username}   ${role_list}