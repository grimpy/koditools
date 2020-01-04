import requests
from urllib.parse import urlparse

class HTTP:
    def __init__(self, basepath):
        self.basepath = basepath
        self.session = requests.Session()

    def command(self, path, method="GET", data=None, json=None, **kwargs):
        parsed = urlparse(path)
        if parsed.scheme:
            url = path
        else:
            url = "{}/{}".format(self.basepath.rstrip('/'), path.strip('/'))
        return self.session.request(method, url, data=data, json=json, **kwargs)
