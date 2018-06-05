.. default-role:: code
.. code:: robotframework

	*** Settings *** 				
	Library     lib/LoginLibrary.py
	Library     ImapLibrary

	*** Test Cases *** 				
	Print hello 					
		${resp}= 	print_hello
		Should Be Equal As Strings 	${resp.status_code} 	${http_code_ok}
	
	Admin can create an account
		Create user    ${username}    ${password}
		Status should be    ${http_code_ok}

	Admin can change the user role
		Change role    ${username}   ${new_role_2}
		Status should be    ${http_code_ok}
		Retrieve role    ${username}
		Status should be    ${new_role_2}
		Change role    ${username}   ${new_role_1}
		Status should be    ${http_code_ok}
		Retrieve role    ${username}
		Status should be    ${new_role_1}

	User can log in with valid credential
		Login    ${username}   ${password}
		Status should be    ${http_code_ok}

	User cannot log in with bad password
		Login    ${username}   ${invalid password}
		Status Should Be    ${http_code_unauthorized} 

	User cannot log in with invalid user name
		Login 	 ${invalid username}		${password}
		Status should be    ${http_code_unauthorized} 
	
	User cannot log in with empty password
		Login    ${username}        ${null password}
		Status should be    ${http_code_unauthorized}

	User cannot create account with existed user name
		Create user    ${username}    ${password}
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

	*** Variables ***
	${username}               mai
	${password}               123£$!$"^"
	${invalid username}       Daisy
	${null password}          ''
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

	*** Keywords ***
	Create user 
		[Arguments]    ${username}    ${password}					
		add_user	${username}    ${password} 
	Create user with email
		[Arguments]    ${username}    ${password}    ${email}					
		add_user	${username}    ${password}    ${email}
	Create user with auto-generated password
		[Arguments]    ${username}
		add_user    ${username}
	Login
		[Arguments]    ${username}    ${password}
		verify_user    ${username}    ${password}
	Reset password
		[Arguments]    ${username}
		reset_passwd   ${username}
	Delete a user
		[Arguments]    ${username}
		delete_user	   ${username}
	Change user password
		[Arguments]    ${username}    ${old_passwd}    ${new_passwd}
		change_password    ${username}    ${old_passwd}    ${new_passwd}
	Change role
		[Arguments]    ${username}    ${new_role}
		change_user_role     ${username}    ${new_role}
	Retrieve role
		[Arguments]    ${username}
		get_user_role    ${username}
