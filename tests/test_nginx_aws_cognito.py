#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `nginx_aws_cognito` package."""

import pytest

from nginx_aws_cognito.nginx_aws_cognito import User


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


class TestUser(object):
    def test_hash(self):
        password = '123456'
        salt = '7890'
        assert User.make_hash(password, salt) == \
               'b477f6f2c0aeef3e57ca5336c20c89c8b36263f664409b29676d5eb34b95c80432bddd140ef909c77a5ce0205cb9de27b2837d46a28b5a519b9761262ea03a2c'
