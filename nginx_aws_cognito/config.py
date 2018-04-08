#!/usr/bin/env python

import multiprocessing
import os

import yaml

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class Defaults(object):
    DEFAULT_MAX_CACHE_ENTRIES = 10000
    DEFAULT_MAX_CACHE_TTL = 3600
    DEFAULT_HOST = '127.0.0.1'
    DEFAULT_PORT = '9988'
    DEFAULT_WORKERS = multiprocessing.cpu_count()
    DEFAULT_CLIENT_ID = ''


class ConfigException(Exception):
    pass


class Config(object):
    def __init__(self, config_yaml_file: str = None):
        self._config_file = config_yaml_file
        self._config = {}
        self.host = None
        self.port = None
        self.workers = None
        self.max_cache_entries = None
        self.max_cache_ttl = None
        self.client_id = None
        self._load()

    def _load(self):
        if self._config_file:
            if not os.path.exists(os.path.expanduser(self._config_file)):
                raise ConfigException(f'Config file: {self._config_file} does not exists')
            if not os.access(os.path.expanduser(self._config_file), os.R_OK):
                raise ConfigException(f'Config file: {self._config_file} is not readable')
            with open(os.path.expanduser(self._config_file), 'r') as fh:
                self._config = yaml.load(fh.read())
        self.host = self.config.get('host', Defaults.DEFAULT_HOST)
        self.port = int(self.config.get('port', Defaults.DEFAULT_PORT))
        self.workers = int(self.config.get('workers', Defaults.DEFAULT_WORKERS))
        self.max_cache_entries = int(self.config.get('max_cache_entries', Defaults.DEFAULT_MAX_CACHE_ENTRIES))
        self.max_cache_ttl = int(self.config.get('max_cache_ttl', Defaults.DEFAULT_MAX_CACHE_TTL))
        self.client_id = self.config.get('client_id', Defaults.DEFAULT_CLIENT_ID)
        return self

    @property
    def config(self)-> dict:
        return self._config
