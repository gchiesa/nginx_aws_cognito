#!/usr/bin/env python

import logging
from typing import Union

import boto3

from . import __appname__
from .entities import User, JWTPublicKeyRing, JWTToken

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class CognitoUserPassAuthException(Exception):
    pass


class CognitoBase(object):
    def __init__(self, client_id) -> None:
        self.logger = logging.getLogger(f'{__appname__}.{self.__class__.__name__}')
        self._client = boto3.client('cognito-idp')
        """ :type : pyboto3.cognitoidentityprovider """
        self._client_id = client_id

    def refresh_token(self, refresh_token):
        auth_parameters = {
            'REFRESH_TOKEN': refresh_token
        }
        try:
            response = self._client.initiate_auth(AuthFlow='REFRESH_TOKEN', AuthParameters=auth_parameters,
                                                  ClientId=self._client_id)
        except Exception as e:
            self.logger.error('Exception while refreshing token. Type: {e}. Error: {m}'.format(e=str(type(e)), m=str(e)))
            return None
        if not response.get('AuthenticationResult', None):
            self.logger.warning('no AuthenticationResult received. Response was: {}'.format(response))
            return None
        access_token = JWTToken(response['AuthenticationResult'].get('AccessToken'))
        refresh_token = response['AuthenticationResult'].get('RefreshToken')
        username = access_token.claims['username']
        user = User(username, access_token=access_token.token,
                    refresh_token=refresh_token, cognito_client=self._client)
        return user


class CognitoUserPassAuth(CognitoBase):
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
        user = User(username,
                    access_token=response['AuthenticationResult'].get('AccessToken'),
                    refresh_token=response['AuthenticationResult'].get('RefreshToken'),
                    password=password, salt=user_salt, cognito_client=self._client)
        return user


class CognitoTokenAuth(CognitoBase):
    def __init__(self, client_id, pubkey_ring: JWTPublicKeyRing)-> None:
        self._pubkey_ring = pubkey_ring
        super(CognitoTokenAuth, self).__init__(client_id)

    def authenticate(self, token: JWTToken) -> Union[None, User]:
        hmac_key = self._pubkey_ring.by_kid(token.kid)
        claims = token.with_hmac_key(hmac_key).claims
        if not token.claims_verified:
            return None
        if token.expired:
            return None
        user = User(claims['username'],
                    access_token=token.token,
                    refresh_token='',
                    cognito_client=self._client)
        return user
