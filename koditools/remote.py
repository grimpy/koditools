#!/usr/bin/env python2
import curses
import logging
import socket
import json
import ConfigParser
import os
from .kodiclient import KodiClient
from .restclient import JsonRPC
import time

cursestokodimap = {'KEY_PPAGE': 'pageup',
                   'KEY_NPAGE': 'pagedown' }

def getKodiKey(curseskey):
    return cursestokodimap.get(curseskey, curseskey[4:].lower())

curseskeymap = { getattr(curses, x): getKodiKey(x) for x in dir(curses) if x.startswith('KEY_') }

class Remote(object):
    MAPPING = {127: {'key': 'backspace'}, #backspace
               10: {'key': 'enter'}, #Enter
               27: {'key': 'escape'}, #Escape
               9: {'key': 'tab'}, #tab
               32: {'key': 'space'}, #Space
               45: {'key': 'minus'}, #Minus
               61: {'key': 'equals'}, #Equals
               92: {'key': 'backslash'}, #Backslash
               44: {'key': 'comma'}, #Comma
               46: {'key': 'period'}, #Period
               #47: {'macro': [{'api': {'command': 'GUI.ActivateWindow', 'window': 'home'}},
               47: {'macro': [{'action': "RunScript(script.globalsearch,movies=true&amp;tvhows=true)"},
                              {'text': 'Search: '}]}, #/
               58: {'text': 'Enter text: '}, #:
               63: {'macro': [{'api': {'command': 'Input.ExecuteAction', 'action':'filter'}},
                              {'key': 'enter'},
                              {'text': 'Filter: '}]}, #?
              }

    def __init__(self, host):
        hostname = socket.gethostname()
        self.remote = KodiClient('PyRemote: %s' % hostname, ip=host)
        self.client = JsonRPC("http://%s:8080/jsonrpc" %host)
        self.remote.connect()
        self.readConfig()

    def getKeyCode(self, option):
        if isinstance(option, int) or option.isdigit():
            key = int(option)
        elif option.startswith('KEY_'):
            if len(option) > 1:
                option = option.upper()
            key = getattr(curses, option, None)
            if not key:
                if len(option) > 5:
                    raise ValueError("Invalid characeter %s" % option)
                key = ord(option[4:])
        else:
            key = ord(option)
        return key

    def readConfig(self):
        cfgpath = os.environ.get('XDG_CONFIG_HOME', os.path.join(os.environ['HOME'], '.config'))
        cfgpath = os.path.join(cfgpath, 'koditools')
        if not os.path.exists(cfgpath):
            os.makedirs(cfgpath, 0755)
        cfgpath = os.path.join(cfgpath, 'remote.conf')
        cfg = ConfigParser.ConfigParser()
        cfg.read(cfgpath)
        mapping = dict()
        if cfg.has_section('keybindings'):
            for option in cfg.options('keybindings'):
                key = self.getKeyCode(option)
                mapping[key] = json.loads(cfg.get('keybindings', option))
        self.MAPPING.update(mapping)


    def getCommand(self, code):
        code = self.getKeyCode(code)
        action = self.MAPPING.get(code)
        if not action:
            if code > 255:
                key = curseskeymap[code]
            else:
                key = chr(code)
            action = {'key': key }
        return action

    def command(self, code=None, command=None):
        if code and not command:
            command = self.getCommand(code)
        if not command:
            return False
        if 'action' in command:
            result = self.remote.send_action(str(command['action']))
            time.sleep(0.2)
        if 'key' in command:
            result = self.remote.send_keyboard_button(command['key'])
            time.sleep(0.1)
            self.remote.release_button()
        if 'api' in command:
            result = self.client.command(**command['api'])
            time.sleep(0.2)
        if 'macro' in command:
            result = list()
            for macro in command['macro']:
                result.append(self.command(command=macro))
        if 'text' in command:
            self.scr.addnstr(command['text'], len(command['text']))
            curses.echo()
            text = self.scr.getstr()
            curses.noecho()
            result = self.client.command('Input.SendText', text=text, done=True)


        logging.info("%s %s" % (command, result))
        return result


    def run(self, scr):
        self.scr = scr
        char = self.scr.getch()
        while char not in (3,): #control + c and q
            self.command(char)
            logging.info(char)
            char = self.scr.getch()
