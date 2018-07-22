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
from .config import Config, LOGGING_CONFIG
from http_basic_auth import parse_header
import requests
from .entities import JWTPublicKeyRing, JWTToken
import logging.config
import logging
from . import __appname__


def allocate_data_cache(max_entries: int, max_ttl: int) -> ExpiringDict:
    return ExpiringDict(max_entries, max_ttl)


def get_jwt_public_keys(region: str, userpool: str) -> JWTPublicKeyRing:
    url = f'https://cognito-idp.{region}.amazonaws.com/{userpool}/.well-known/jwks.json'
    response = requests.get(url)
    if not response.ok:
        raise RuntimeError('Unable to fetch the userpool public key')
    jwt_keys = response.json()
    return JWTPublicKeyRing(jwt_keys)


logging.config.dictConfig(LOGGING_CONFIG)

app = Sanic()

config = Config(os.environ.get('NGINX_AWS_COGNITO_CONFIG', None))
app.nginx_user_cache = allocate_data_cache(config.max_cache_entries, config.max_cache_ttl)
app.nginx_user_salt = uuid.uuid4().hex
app.cognito_jwt_public_key_ring = get_jwt_public_keys(config.region, config.userpool_id)


def access_token(request: Request):
    logger = logging.getLogger(__appname__)
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if request.args.get('username', None):
        username = request.args.get('username', None)
    if request.args.get('password', None):
        password = request.args.get('password', None)
    if not request.args.get('grant_type', '') == 'password':
        return response.json({'message': 'grant type not supported'},
                             status=400)
    if not username or not password:
        return response.json({'message': 'username or password not set'},
                             status=400)
    logger.info(f'Processing access token for username: {username}')
    authenticator = Authenticator(request.app.nginx_user_cache,
                                  client_id=config.client_id,
                                  user_salt=app.nginx_user_salt)
    user = authenticator.auth_basic(username, password)
    if not user:
        return response.json({'message': 'authentication failed'}, status=401)
    request.app.nginx_user_cache[user.username] = user
    response_headers = {
        'X-AWS-Cognito-Username': user.username,
        'X-AWS-Cognito-AccessToken': user.access_token,
        'X-AWS-Cognito-RefreshToken': user.refresh_token,
    }
    if config.load_profile:
        response_headers['X-AWS-Cognito-AttributesJson'] = json.dumps(user.attributes)
    response_data = {
        'access_token': user.access_token,
        'refresh_token': user.refresh_token,
        'token_type': 'Bearer',
        'expires_in': 3600
    }
    return response.json(response_data, headers=response_headers, status=200)


def refresh_token(request: Request):
    logger = logging.getLogger(__appname__)
    token = request.json.get('refresh_token', None)
    # logger.info('json content: {}'.format(request.json))
    # logger.info('args: {}'.format(request.args))
    if request.args.get('refresh_token', None):
        token = request.args.get('refresh_token', None)
    if not token:
        return response.json({'message': 'refresh token not set'},
                             status=401)
    if not request.args.get('grant_type', '') == 'refresh_token':
        return response.json({'message': 'grant type not supported'},
                             status=401)
    logger.info('Processing access token')
    authenticator = Authenticator(request.app.nginx_user_cache,
                                  client_id=config.client_id,
                                  user_salt=app.nginx_user_salt)
    user = authenticator.refresh_token(token)
    if not user:
        return response.json({'message': 'authentication failed'}, status=401)
    request.app.nginx_user_cache[user.username] = user
    response_headers = {
        'X-AWS-Cognito-Username': user.username,
        'X-AWS-Cognito-AccessToken': user.access_token,
    }
    if config.load_profile:
        response_headers['X-AWS-Cognito-AttributesJson'] = json.dumps(user.attributes)
    response_data = {
        'access_token': user.access_token,
        'refresh_token': user.refresh_token,
        'token_type': 'Bearer',
        'expires_in': 3600
    }
    return response.json(response_data, headers=response_headers, status=200)


@app.route('/resetcache')
async def resetcache(request: Request):
    app.nginx_user_cache = allocate_data_cache(config.max_cache_entries, config.max_cache_ttl)
    return response.json({'message': 'cache reset'}, status=200)


@app.route('/basicauth')
async def basicauth(request: Request):
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
    authenticator = Authenticator(request.app.nginx_user_cache,
                                  client_id=config.client_id,
                                  user_salt=app.nginx_user_salt)
    user = authenticator.auth_basic(username, password)
    if not user:
        return response.json({'message': 'authentication failed'}, status=401)
    request.app.nginx_user_cache[user.username] = user
    response_headers = {
        'X-AWS-Cognito-Username': user.username,
        'X-AWS-Cognito-AccessToken': user.access_token,
        'X-AWS-Cognito-AttributesJson': json.dumps(user.attributes),
    }
    return response.json({'message': 'authorized'}, headers=response_headers, status=200)


@app.route('/oauth2/token', methods=['POST'])
async def token(request: Request):
    """
    reference https://labs.hybris.com/2012/06/18/trying-out-oauth2-via-curl/
    :param request:
    :return:
    """
    logger = logging.getLogger(f'{__appname__}.token')
    # logger.info('request: {h}, {f}, {j}'.format(h=request.headers, f=request.form, j=request.json))
    grant_types = {
        'password': access_token,
        'refresh_token': refresh_token
    }
    if request.args.get('grant_type', None) not in grant_types.keys():
        return response.json({'message': 'grant type not supported'},
                             status=400)
    return grant_types[request.args.get('grant_type')](request)


@app.route('/verify')
async def bearer(request: Request):
    access_token_bearer = request.headers.get('Authorization', None)
    if not access_token_bearer:
        return response.json({'message': 'access token not provided'},
                             status=401)
    authenticator = Authenticator(request.app.nginx_user_cache,
                                  client_id=config.client_id,
                                  user_salt=app.nginx_user_salt)
    token = access_token_bearer.replace('Bearer', '').strip()
    user = authenticator.auth_token(JWTToken(token), app.cognito_jwt_public_key_ring)
    if not user:
        return response.json({'message': 'unhauthorized'}, status=401)
    request.app.nginx_user_cache[user.username] = user
    response_headers = {
        'X-AWS-Cognito-Username': user.username,
        'X-AWS-Cognito-AccessToken': user.access_token,
    }
    if config.load_profile:
        response_headers['X-AWS-Cognito-AttributesJson'] = json.dumps(user.attributes)
    return response.json({'message': 'authorized'}, headers=response_headers, status=200)


if __name__ == '__main__':
    app.run(host=config.host, port=config.port, workers=config.workers)

