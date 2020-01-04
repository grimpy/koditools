#!/usr/bin/env python
try:
    from urllib2 import Request, urlopen
    str = unicode  # NOQA
except ImportError:
    from urllib.request import Request, urlopen
import json
import logging


class JsonRPC(object):
    def __init__(self, url):
        self._url = url
        self._headers = {'Accept': 'application/json, text/javascript, */*; ' +
                                   'q=0.01',
                         'Content-Type': 'application/json'}

    def command(self, command, **kwargs):
        message = {'jsonrpc': '2.0', 'method': command, 'id': 1,
                   'params': kwargs}
        logging.debug('Making command %s with args %s', command, kwargs)
        data = json.dumps(message)
        if isinstance(data, str):
            data = data.encode()
        result = self._post(data)
        logging.debug('Result of command %s: %s', command, result)

        return result

    def _post(self, data):
        req = Request(self._url, data, self._headers)
        strm = urlopen(req)
        return strm.read()
