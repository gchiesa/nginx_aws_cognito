#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `nginx_aws_cognito` package."""

import pytest
from nginx_aws_cognito.entities import User, JWTToken
from .conftest import valid_user
import copy


class TestUser(object):

    def test_hash(self, p='123456', s='7890'):
        assert User.make_hash(p, s) == 'b477f6f2c0aeef3e57ca5336c20c89c8b36263f664409b29676d5eb34b95c80432' \
                                       'bddd140ef909c77a5ce0205cb9de27b2837d46a28b5a519b9761262ea03a2c'

    def test_user_equality(self):
        a = User('usernameA', password='passwordA', salt='saltA')
        b = User('usernameA', password='passwordA', salt='saltA')
        assert a == b

    def test_user_nequality_different_password(self):
        a = User('usernameA', password='passwordA', salt='saltA')
        b = User('usernameA', password='passwordB', salt='saltA')
        assert a != b

    def test_user_nequality_different_username(self):
        a = User('usernameA', password='passwordA', salt='saltA')
        b = User('usernameB', password='passwordA', salt='saltA')
        assert a != b


class TestJWTToken(object):

    @pytest.mark.usefixtures('expired_token')
    def test_headers(self, expired_token):
        t = JWTToken(expired_token)
        assert t.headers == {'kid': '6is6+hXlytngUN7EaJ+XjVLETgTJxFciFFYR9Q3tg3Q=', 'alg': 'RS256'}

