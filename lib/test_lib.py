import os.path
import subprocess
import sys
import requests
import os
import json

HOME_URL = 'http://127.0.0.1:5001/v2.0'

class LoginLibrary(object):

    def __init__(self):
        #self._sut_path = os.path.join(os.path.dirname(__file__),
         #                             '..', 'sut', 'login.py')
        self._status = ''

    def print_hello(self):
        url     = HOME_URL + '/'
        res = requests.get(url)
        return res


    def status_should_be(self, expected_status):
        if expected_status != str(self._status):
            raise AssertionError("Expected status to be '%s' but was '%s'."
                                 % (expected_status, self._status))

    ##### USERS
    def add_user(self, username=None, password = None, email = None, firstname = None, lastname = None):
        url     = HOME_URL + '/users'
        payload = {'username': username, 'password': password, 'email': email, 'firstname': firstname, 'lastname': lastname}
        res = requests.post(url, data=payload)
        json_data = json.loads(res.text)
        self._status = json_data['code']

   def retrieve_user(self, username=None):
        url     = HOME_URL + '/user/' + username
        res = requests.get(url)
        json_data = json.loads(res.text)
        self._status = json_data['code']

   def update_user(self, username=None, new_firstname=None, new_lastname=None):
        url     = HOME_URL + '/user/' + username
        payload = {'firstname': new_firstname, 'lastname': new_lastname}
        res = requests.put(url)
        json_data = json.loads(res.text)
        self._status = json_data['code']

    def delete_user(self, username=None):
        url     = HOME_URL + '/user/' + username
        res = requests.delete(url)
        json_data = json.loads(res.text)
        self._status = json_data['code']

    def get_user_list(self):
        url     = HOME_URL + '/users'
        res = requests.get(url)
        json_data = json.loads(res.text)
        self._status = json_data['code']

    ##### PASSWORD
    def verify_user(self, username=None, password=None):
        url     = HOME_URL + '/user/' + username + "/password"
        payload = {'password': password}
        res = requests.post(url, data=payload)
        json_data = json.loads(res.text)
        self._status = json_data['code']
        #return json_data['code']

    def change_password(self, username=None, current_passwd=None, new_passwd=None):
        url    =  HOME_URL + '/user/' + username + "/password"
        payload = {'current_password': current_passwd, 'new_password': new_passwd}
        res = requests.put(url, data=payload)
        json_data = json.loads(res.text)
        self._status = json_data['code']

    def reset_password(self, username=None):
        url     = HOME_URL + '/user/' + username + "/password"
        res = requests.delete(url)
        json_data = json.loads(res.text)
        self._status = json_data['code']

    ##### USER ROLES
    def revoke_user_role(self, username=None, role_name=None):
        url     =  HOME_URL + '/user/' + username + "/role/" + role_name
        res = requests.delete(url)
        json_data = json.loads(res.text)
        self._status = json_data['code']

    def grant_user_roles(self, username=None, role_list=None):
        url     =  HOME_URL + '/user/' + username + "/role/"
        payload = {'roles': role_list}
        res = requests.post(url, data=payload)
        json_data = json.loads(res.text)
        self._status = json_data['code']

    def get_user_roles(self, username=None):
        url     = HOME_URL+ '/user/' + username + '/role'
        res = requests.get(url)
        json_data = json.loads(res.text)
        self._status = json_data['code']
    
    ##### ROLES
    def retrieve_all_roles(self):
        url     = HOME_URL+ '/roles'
        res = requests.get(url)
        json_data = json.loads(res.text)
        self._status = json_data['code']

    def retrieve_one_role(self, role_name = None):
        url     = HOME_URL+ '/role/' + role_name
        res = requests.get(url)
        json_data = json.loads(res.text)
        self._status = json_data['code']

    def create_a_role(self, role_name = None, role_label = None):
        url     = HOME_URL+ '/roles'
        payload = {'name': role_name, 'label': role_label}
        res = requests.post(url,data=payload)
        json_data = json.loads(res.text)
        self._status = json_data['code']

    def update_a_role(self, role_name = None, role_label = None):
        url     = HOME_URL+ '/role/' + role_name
        payload = {'label': role_label}
        res = requests.post(url,data=payload)
        json_data = json.loads(res.text)
        self._status = json_data['code']

    def delete_a_role(self, role_name = None):
        url     = HOME_URL+ '/role/' + role_name
        res = requests.delete(url)
        json_data = json.loads(res.text)
        self._status = json_data['code']