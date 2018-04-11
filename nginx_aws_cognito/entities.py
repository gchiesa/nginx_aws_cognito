# !/usr/bin/env python

import hashlib
import logging
import time
from typing import Dict
from jose import jwk, jwt
from jose.utils import base64url_decode

from . import __appname__

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class JWTTokenException(Exception):
    pass


class JWTToken(object):
    def __init__(self, token_data: str) -> None:
        self.logger = logging.getLogger(f'{__appname__}.{self.__class__.__name__}')
        self._token_data = token_data
        self._hmac_key: Dict = {}
        self._key = None
        self.message = None
        self.encoded_sig = None
        self._headers = None
        self._validate()

    @property
    def kid(self)-> str:
        return self.headers['kid']

    @property
    def headers(self):
        if not self._headers:
            self._get_headers()
        return self._headers

    def _get_headers(self):
        self._headers = jwt.get_unverified_headers(self._token_data)

    def _validate(self):
        self.message, self.encoded_sig = self._token_data.rsplit('.', 1)
        if not self.message or not self.encoded_sig:
            raise JWTTokenException('Malformed token')

    def with_hmac_key(self, hmac_key: dict):
        self._hmac_key = hmac_key
        self._key = jwk.construct(hmac_key)
        return self

    @property
    def token(self):
        return self._token_data

    @property
    def claims_verified(self):
        if not self._key:
            return False
        return self._verify_sig()

    @property
    def claims(self):
        return jwt.get_unverified_claims(self._token_data)

    def _verify_sig(self):
        decoded_sig = base64url_decode(self.encoded_sig.encode('utf-8'))
        return self._key.verify(self.message.encode('utf-8'), decoded_sig)

    @property
    def expired(self):
        return time.time() > self.claims['exp']

    @property
    def audience(self):
        return self.claims['aud']


class User(object):
    def __init__(self, username: str, access_token: str = '', refresh_token: str = '', password: str='', salt: str='',
                 cognito_client=None) -> None:
        self.logger = logging.getLogger(f'{__appname__}.{self.__class__.__name__}')
        self.username = username
        self._salt = salt
        self.hash = self.make_hash(password, self._salt)
        self.access_token = access_token
        self.refresh_token = refresh_token
        self._attributes = None
        self._cognito_client = cognito_client
        """ :type : pyboto3.cognitoidentityprovider """

    @staticmethod
    def make_hash(password: str, salt: str) -> str:
        return hashlib.sha512(f'{password}${salt}'.encode('utf-8')).hexdigest()

    def with_cognito_client(self, client):
        self._cognito_client = client

    def _load_attributes(self):
        self.logger.info('Loading user attributes')
        response = self._cognito_client.get_user(AccessToken=self.access_token)
        if response and response.get('UserAttributes', None):
            self._attributes = response['UserAttributes']

    @property
    def attributes(self):
        if not self._attributes:
            self._load_attributes()
        return self._attributes

    def __eq__(self, other):
        return (self.username == other.username) and (self.hash == other.hash)

    def __ne__(self, other):
        return not self.__eq__(other)


class JWTPublicKeyRing(object):
    def __init__(self, keyring: dict) -> None:
        self._keyring_raw = keyring

    def by_kid(self, kid: str) -> dict:
        return next((key for key in self._keyring_raw['keys'] if key['kid'] == kid))
