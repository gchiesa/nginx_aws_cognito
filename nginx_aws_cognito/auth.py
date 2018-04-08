#!/usr/bin/env python
import logging
from typing import Union

from expiringdict import ExpiringDict

from .cognito import CognitoUserPassAuth
from .entities import User

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class Authenticator(object):
    def __init__(self, cache_obj: ExpiringDict, client_id: str = '', user_salt: str = ''):
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
            self.logger.info(f'Found user: {username} in cache')
            if cached_user == User(username, password, self._user_salt):
                return cached_user
        return self._cognito_auth(username, password)
