#!/usr/bin/env python
import logging
from typing import Union

from expiringdict import ExpiringDict

from .cognito import CognitoUserPassAuth, CognitoBase, CognitoTokenAuth
from .entities import User, JWTToken, JWTPublicKeyRing
from . import __appname__

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class Authenticator(object):
    def __init__(self, cache_obj: ExpiringDict, client_id: str = '', user_salt: str = '') -> None:
        self.logger = logging.getLogger(f'{__appname__}.{self.__class__.__name__}')
        self._data = cache_obj
        self._client_id = client_id
        self._user_salt = user_salt

    def _get_from_cache(self, username: str) -> Union[None, User]:
        if not self._data:
            return None
        return self._data.get(username, None)

    def _cognito_auth(self, username: str, password: str) -> Union[None, User]:
        cauth = CognitoUserPassAuth(client_id=self._client_id)
        return cauth.authenticate(username, password, self._user_salt)

    def auth_basic(self, username: str, password: str) -> Union[None, User]:
        cached_user = self._get_from_cache(username)
        if cached_user:
            if cached_user == User(username, password, self._user_salt):
                return cached_user
        return self._cognito_auth(username, password)

    def refresh_token(self, token: str) -> Union[None, User]:
        cauth = CognitoBase(self._client_id)
        return cauth.refresh_token(token)

    def auth_token(self, token: JWTToken, pubkey_ring: JWTPublicKeyRing) -> Union[None, User]:
        cauth = CognitoTokenAuth(self._client_id, pubkey_ring)
        user = cauth.authenticate(token)
        if not user:
            return None
        cached_user = self._get_from_cache(user.username)
        return cached_user or user


