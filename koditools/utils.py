import ConfigParser
from koditools.restclient import JsonRPC
import os

def getConfigFile():
    cfgpath = os.environ.get('XDG_CONFIG_HOME', os.path.join(os.environ['HOME'], '.config'))
    cfgpath = os.path.join(cfgpath, 'koditools')
    if not os.path.exists(cfgpath):
        os.makedirs(cfgpath, 0755)
    cfgpath = os.path.join(cfgpath, 'remote.conf')
    cfg = ConfigParser.ConfigParser()
    cfg.read(cfgpath)
    return cfg

def getHostPort(cfg, host, port):
    if cfg.has_section('server'):
        if cfg.has_option('server', 'host') and host is None:
            host = cfg.get('server', 'host')
        if cfg.has_option('server', 'port') and port is None:
            port = cfg.get('server', 'port')
    return host, port

def getEventPort(cfg, port):
    if cfg.has_section('server'):
        if cfg.has_option('sever', 'event-port') and port is None:
            port = cfg.get('server', 'event-port')
    return port

def getJSONRC(host, port):
    return JsonRPC("http://%s:%s/jsonrpc" % (host, port))
