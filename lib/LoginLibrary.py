import os.path
import subprocess
import sys
import requests
import os
import json

class LoginLibrary(object):

    def __init__(self):
        #self._sut_path = os.path.join(os.path.dirname(__file__),
         #                             '..', 'sut', 'login.py')
        self._status = ''

    def print_hello(self):
        url     = 'http://127.0.0.1:5001/v1.0/'
        res = requests.get(url)
        return res

    def add_user(self, username=None, password = None, email = None):
        url     = 'http://127.0.0.1:5001/v1.1/adduser'
        payload = {'username': username, 'password': password, 'email': email}
        res = requests.post(url, data=payload)
        json_data = json.loads(res.text)
        '''file = open('test_file.txt','w')
        file.write(res.url)
        file.write('  ')
        file.write(res.content)
        file.write('  ')
        file.write(json_data['user message'])
        file.close()'''
        self._status = json_data['code']

    def verify_user(self, username=None, password=None):
        url     = 'http://127.0.0.1:5001/v1.1/verify'
        payload = {'username': username, 'password': password}
        res = requests.post(url, data=payload)
        json_data = json.loads(res.text)
        self._status = json_data['code']
        #return json_data['code']

    def status_should_be(self, expected_status):
        if expected_status != str(self._status):
            raise AssertionError("Expected status to be '%s' but was '%s'."
                                 % (expected_status, self._status))

    def reset_passwd(self, username=None):
        url     = 'http://127.0.0.1:5001/v1.1/resetpwd'
        payload = {'username': username}
        res = requests.put(url, data=payload)
        json_data = json.loads(res.text)
        self._status = json_data['code']

    def delete_user(self, username=None):
        url     = 'http://127.0.0.1:5001/v1.1/deleteuser'
        payload = {'username': username}
        res = requests.put(url, data=payload)
        json_data = json.loads(res.text)
        self._status = json_data['code']

    def change_password(self, username=None, old_passwd=None, new_passwd=None):
        url     = 'http://127.0.0.1:5001/v1.1/changepwd'
        payload = {'username': username, 'oldpasswd': old_passwd, 'newpasswd': new_passwd}
        res = requests.put(url, data=payload)
        json_data = json.loads(res.text)
        self._status = json_data['code']

    def change_user_role(self, username=None, new_role=None):
        url     = 'http://127.0.0.1:5001/v1.1/changerole'
        payload = {'username': username, 'newrole': new_role}
        res = requests.put(url, data=payload)
        json_data = json.loads(res.text)
        self._status = json_data['code']

    def get_user_role(self, username=None):
        url     = 'http://127.0.0.1:5001/v1.1/getrole'
        payload = {'username': username}
        res = requests.get(url, data=payload)
        json_data = json.loads(res.text)
        self._status = json_data['role']
