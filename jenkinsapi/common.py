#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import sys
import urllib

class ClientError(Exception):
    pass


class ServerError(Exception):
    pass


class AuthError(ClientError):
    pass


class ValidationError(ClientError):
    pass

def expand_url(url, params={}):
    _url = url
    if params:
        _url += '?'
    paramFormat = '{}={}&'

    for key, value in params.items():
        if isinstance(value, list):
            for value2 in value:
                _url += paramFormat.format(key, urllib.quote_plus(str(value2)))
        else:
            _url += paramFormat.format(key, urllib.quote_plus(str(value)))

    return _url

def copy_dict(dest, src):
    for k, v in src.items():
        if isinstance(v, dict):
            # Transform dict values to new attributes. For example:
            # custom_attributes: {'foo', 'bar'} =>
            #   "custom_attributes['foo']": "bar"
            for dict_k, dict_v in v.items():
                dest['%s[%s]' % (k, dict_k)] = dict_v
        else:
            dest[k] = v

