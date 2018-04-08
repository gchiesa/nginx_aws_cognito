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
from http_basic_auth import parse_header

def allocate_data_cache(max_entries: int, max_ttl: int) -> ExpiringDict:
    return ExpiringDict(max_entries, max_ttl)


app = Sanic()

config = Config(os.environ.get('NGINX_AWS_COGNITO_CONFIG', None))
app.nginx_data_cache = allocate_data_cache(config.max_cache_entries, config.max_cache_ttl)
app.nginx_user_salt = uuid.uuid4().hex


@app.route('/resetcache')
async def resetcache(request: Request):
    app.nginx_data_cache = allocate_data_cache(config.max_cache_entries, config.max_cache_ttl)
    return response.json({'message': 'cache reset'}, status=200)


@app.route('/basicauth')
async def userpass(request: Request):
    """
    X-AWS-Cognito-Username
    X-AWS-Cognito-Password
    X-AWS-Cognito-BasicAuth
    :param request:
    :return:
    """
    username = request.headers.get('X-AWS-Cognito-Username', None)
    password = request.headers.get('X-AWS-Cognito-Password', None)

    if request.headers.get('X-AWS-Cognito-BasicAuth', None):
        username, password = parse_header(request.headers['X-AWS-Cognito-BasicAuth'])

    if not username or not password:
        return response.json({'message': 'username or password not set'},
                             status=400)
    authenticator = Authenticator(request.app.nginx_data_cache, client_id=config.client_id,
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
    app.run(host=config.host, port=config.port, workers=config.workers)
