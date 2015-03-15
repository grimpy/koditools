import ConfigParser
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
