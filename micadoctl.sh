#!/bin/bash
SCRIPT=$(basename $0)

if [[ ! $1 =~ (adduser)|(verify)|(resetpwd)|(changepwd)|(getrole)|(changerole)|(deleteuser)  ]]; then
  echo "Usage: ./$SCRIPT adduser|verify|resetpwd|changepwd|getrole|changerole|deleteuser"
  exit 1
fi

if [[ $1 == 'adduser' ]]; 
then
	if [ -z "$2" ]  && [ -z "$3" ] && [ -z "$4" ]
	then
		echo "Usage: $(basename $0) adduser arg1 arg2 arg3"
		echo "arg1 (required): username"
		echo "arg2 (optional): password"
		echo "arg3 (optional): email"
		exit 0
	fi

	if [ -z "$4" ]
	then
		curl -X POST -d "username=$2&password=$3" localhost:5001/v1.1/adduser	
  	else
  		curl -X POST -d "username=$2&password=$3&email=$4" localhost:5001/v1.1/adduser
  	fi
fi

if [[ $1 == 'verify' ]]; 
then
	if [ -z "$2" ]  || [ -z "$3" ]
	then
		echo "Usage: $(basename $0) verify arg1 arg2"
		echo "arg1 (required): username"
		echo "arg2 (required): password"
		exit 0
	fi
  	curl -X POST -d "username=$2&password=$3" localhost:5001/v1.1/verify
fi

if [[ $1 == 'resetpwd' ]]; 
then
	if [ -z "$2" ]
	then
		echo "Usage: $(basename $0) resetpwd arg1"
		echo "arg1 (required): username"
		exit 0
	fi
  	curl -X PUT -d "username=$2" localhost:5001/v1.1/resetpwd
fi

if [[ $1 == 'changepwd' ]]; 
then
	if [ -z "$2" ]  || [ -z "$3" ] || [ -z "$4" ]
	then
		echo "Usage: $(basename $0) changepwd arg1 arg2 arg3"
		echo "arg1 (required): username"
		echo "arg2 (required): current password"
		echo "arg3 (required): new password"
		exit 0
	fi
	curl -X PUT -d "username=$2&oldpasswd=$3&newpasswd=$4" localhost:5001/v1.1/changepwd
fi

if [[ $1 == 'getrole' ]]; 
then
	if [ -z "$2" ]
	then
		echo "Usage: $(basename $0) getrole arg1"
		echo "arg1 (required): username"
		exit 0
	fi
	curl -X GET -d "username=$2" localhost:5001/v1.1/getrole
fi

if [[ $1 == 'changerole' ]]; 
then
	if [ -z "$2" ]  || [ -z "$3" ]
	then
		echo "Usage: $(basename $0) changerole arg1 arg2"
		echo "arg1 (required): username"
		echo "arg2 (required): new role ('user' or 'admin')"
		exit 0
	fi
  	curl -X PUT -d "username=$2&newrole=$3" localhost:5001/v1.1/changerole
fi

if [[ $1 == 'deleteuser' ]]; 
then
	if [ -z "$2" ]
	then
		echo "Usage: $(basename $0) deleteuser arg1"
		echo "arg1 (required): username"
		exit 0
	fi
  	curl -X PUT -d "username=$2" localhost:5001/v1.1/deleteuser
fi