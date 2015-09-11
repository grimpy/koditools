#!/usr/bin/env python2
import urllib2
import json
import logging

class JsonRPC(object):
    def __init__(self, url):
        self._url = url
        self._headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
                         'Content-Type': 'application/json'}

    def command(self, command, **kwargs):
        message = {'jsonrpc': '2.0', 'method': command, 'id': 1, 'params': kwargs}
        logging.debug('Making command %s with args %s' % (command, kwargs))
        result = self._post(json.dumps(message))
        logging.debug('Result of command %s: %s' % (command, result))

        return result

    def _post(self, data):
        req = urllib2.Request(self._url, data, self._headers)
        strm = urllib2.urlopen(req)
        return strm.read()

