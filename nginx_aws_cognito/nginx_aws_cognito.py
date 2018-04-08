# -*- coding: utf-8 -*-

"""Main module."""
import os
import json
import uuid

from expiringdict import ExpiringDict
from sanic import Sanic
from sanic import response
from sanic.request import Request

from .auth import Authenticator
from .config import Config


def allocate_data_cache(max_entries: int, max_ttl: int) -> ExpiringDict:
    return ExpiringDict(max_entries, max_ttl)


app = Sanic()

config = Config(os.environ.get('NGINX_AWS_COGNIGO_CONFIG', None))
app.nginx_data_cache = allocate_data_cache(config.max_cache_entries, config.max_cache_ttl)
app.nginx_user_salt = uuid.uuid4().hex


@app.route('/resetcache')
async def resetcache(request: Request):
    app.nginx_data_cache = allocate_data_cache(config.max_cache_entries, config.max_cache_ttl)
    return response.json({'message': 'cache reset'}, status=200)


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
        'X-AWS-Cognito-AccessToken': user.access_token,
        'X-AWS-Cognito-AttributesJson': json.dumps(user.attributes),
    }
    return response.json({'message': 'authorized'}, headers=response_headers, status=200)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9988, workers=4)
