# -*- coding: utf-8 -*-

"""Main module."""
import hashlib
import logging
import uuid
from typing import Union

import boto3
from expiringdict import ExpiringDict
from sanic import Sanic
from sanic import response
from sanic.request import Request


class User(object):
    def __init__(self, username: str, password: str, salt: str, access_token: str = '', response_raw: dict = None):
        self.username = username
        self._salt = salt
        self.hash = self.make_hash(password, self._salt)
        self.access_token = access_token
        self._response_raw = response_raw

    @staticmethod
    def make_hash(password: str, salt: str) -> str:
        return hashlib.sha512(f'{password}${salt}'.encode('utf-8')).hexdigest()

    def __eq__(self, other):
        return (self.username == other.username) and (self.hash == other.hash)

    def __ne__(self, other):
        return not self.__eq__(other)


class CognitoUserPassAuthException(Exception):
    pass


class CognitoUserPassAuth(object):
    def __init__(self, client_id):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._client = boto3.client('cognito-idp')
        """ :type : pyboto3.cognitoidentityprovider """
        self._client_id = client_id

    def authenticate(self, username: str, password: str, user_salt: str) -> Union[User, None]:
        auth_parameters = {
            'USERNAME': username,
            'PASSWORD': password,
        }
        try:
            response = self._client.initiate_auth(AuthFlow='USER_PASSWORD_AUTH', AuthParameters=auth_parameters,
                                                  ClientId=self._client_id)
        except Exception as e:
            self.logger.error('Exception while authenticating. Type: {e}. Error: {m}'.format(e=str(type(e)), m=str(e)))
            return None

        if not response.get('AuthenticationResult', None):
            return None
        return User(username, password, salt=user_salt, access_token=response['AuthenticationResult'].get('AccessToken'),
                    response_raw=response)


class Authenticator(object):
    def __init__(self, cache_obj: ExpiringDict, client_id: str='', user_salt: str= ''):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._data = cache_obj
        self._client_id = client_id
        self._user_salt = user_salt

    def _get_from_cache(self, username: str) -> Union[None, User]:
        return self._data.get(username, None)

    def _cognito_auth(self, username: str, password: str) -> Union[None, User]:
        cauth = CognitoUserPassAuth(client_id=self._client_id)
        return cauth.authenticate(username, password, self._user_salt)

    def authenticate(self, username: str, password: str) -> Union[None, User]:
        cached_user = self._get_from_cache(username)
        if cached_user:
            self.logger.debug(f'found user: {username} in cache')
            if cached_user == User(username, password, self._user_salt):
                return cached_user
        return self._cognito_auth(username, password)


MAX_CACHE_ENTRIES = 10000
MAX_CACHE_TTL = 3600
app = Sanic()
app.nginx_data_cache = ExpiringDict(MAX_CACHE_ENTRIES, MAX_CACHE_TTL)
app.nginx_user_salt = uuid.uuid4().hex


@app.route('/userpass')
async def userpass(request: Request):
    """
    X-AWS-Cognito-Username
    X-AWS-Cognito-Password
    :param request:
    :return:
    """
    username = request.headers.get('X-AWS-Cognito-Username', None)
    password = request.headers.get('X-AWS-Cognito-Password', None)
    if not username or not password:
        return response.json({'message': 'username or password not set'},
                             status=400)
    authenticator = Authenticator(request.app.nginx_data_cache, client_id='4q80akfi6274dobq150th3aath',
                                  user_salt=app.nginx_user_salt)
    user = authenticator.authenticate(username, password)
    if not user:
        return response.json({'message': 'authentication failed'}, status=401)
    request.app.nginx_data_cache[user.username] = user
    response_headers = {
        'X-AWS-Cognito-Username': user.username,
        'X-AWS-Cognito-AccessToken': user.access_token
    }
    return response.json({'message': 'authorized'}, headers=response_headers, status=200)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9988, workers=4)
