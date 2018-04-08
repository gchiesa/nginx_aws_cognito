# !/usr/bin/env python

import hashlib

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class User(object):
    def __init__(self, username: str, password: str, salt: str, access_token: str = '', response_raw: dict = None):
        self.username = username
        self._salt = salt
        self.hash = self.make_hash(password, self._salt)
        self.access_token = access_token
        self._response_raw = response_raw
        self.attributes = None

    @staticmethod
    def make_hash(password: str, salt: str) -> str:
        return hashlib.sha512(f'{password}${salt}'.encode('utf-8')).hexdigest()

    def __eq__(self, other):
        return (self.username == other.username) and (self.hash == other.hash)

    def __ne__(self, other):
        return not self.__eq__(other)

    def set_attributes(self, attributes: dict):
        self.attributes = attributes
        return self
