#!/usr/bin/env python

import logging
from typing import Union

import boto3

from .entities import User

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


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
        user = User(username, password, salt=user_salt,
                    access_token=response['AuthenticationResult'].get('AccessToken'),
                    response_raw=response)
        response = self._client.get_user(AccessToken=user.access_token)
        if response and response.get('UserAttributes', None):
            user.set_attributes(response['UserAttributes'])
        return user

