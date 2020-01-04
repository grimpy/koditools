#!/usr/bin/env python2
import curses
import logging
import socket
import json
import sys
import os
import time
import subprocess
import importlib
from .kodiclient import KodiClient
from . import utils

cursestokodimap = {'KEY_PPAGE': 'pageup',
                   'KEY_NPAGE': 'pagedown'}


def getKodiKey(curseskey):
    return cursestokodimap.get(curseskey, curseskey[4:].lower())

curseskeymap = {getattr(curses, x):
                getKodiKey(x) for x in dir(curses) if x.startswith('KEY_')}


class Remote(object):
    MAPPING = {127: {'key': 'backspace'},  # Backspace
               10: {'key': 'enter'},  # Enter
               27: {'key': 'escape'},  # Escape
               9: {'key': 'tab'},  # Tab
               32: {'key': 'space'},  # Space
               45: {'key': 'minus'},  # Minus
               61: {'key': 'equals'},  # Equals
               92: {'key': 'backslash'},  # Backslash
               44: {'key': 'comma'},  # Comma
               46: {'key': 'period'},  # Period
               47: {'macro': [{'action': "RunScript(script.globalsearch," +
                                         "movies=true&amp;tvhows=true)"},
                              {'text': 'Search: '}]},  # /
               58: {'text': 'Enter text: '},  # :
               63: {'macro': [{'api': {'command': 'Input.ExecuteAction',
                                       'action': 'filter'}},
                              {'key': 'enter'},
                              {'text': 'Filter: '}]},  # ?
               }

    def __init__(self, host=None, port=None, eport=None, init=True):
        self.mode = 'default'
        self.scr = None
        self.host = host
        self.port = port
        self.eport = eport
        self.plugins = {}
        self.cfg = None
        if init:
            self.init()

    def init(self):
        hostname = socket.gethostname()
        self.readConfig()
        if self.host is None:
            raise ValueError("Host can not be none, " +
                             "please set in configuration or pass")
        self.remote = KodiClient('PyRemote: %s' % hostname, ip=self.host,
                                 port=self.eport)
        self.client = utils.getJSONRC(self.host, self.port)
        self.remote.connect()

    def getKeyCode(self, option):
        if isinstance(option, int) or option.isdigit():
            key = int(option)
        elif option.lower().startswith('key_'):
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

    def print_help(self):
        idx = 2
        self.scr.clear()
        self.scr.addstr(0, 0, "Key mode {}".format(self.mode))
        for key, settings in self.MAPPING.items():
            if 'macro' not in settings:
                settings = [settings]
            else:
                settings = settings['macro']
            
            helpstr = []
            for setting in settings:
                keyname = curseskeymap.get(key)
                if keyname is None:
                    keyname = chr(key)
                if 'help' in setting:
                    helpstr.append(setting['help'].format(keyname.title()))
                    #helpstr.append("{}: {}".format(keyname.title(), setting))
            if self.scr and helpstr:
                self.scr.addstr(idx, 0, " / ".join(helpstr))
                idx += 1

    def get_section(self, mode=None):
        mode = mode or self.mode
        section = 'keybindings'
        if mode != 'default':
            section = 'keybindings.{}'.format(mode)
        return section

    def readConfig(self):
        if self.cfg is None:
            self.cfg = utils.getConfigFile()
        mapping = dict()
        section = self.get_section()
        if self.cfg.has_section(section):
            for idx, option in enumerate(self.cfg.options(section)):
                key = self.getKeyCode(option)
                setting = json.loads(self.cfg.get(section, option))
                mapping[key] = setting
        self.host, self.port = utils.getHostPort(self.cfg, self.host, self.port)
        self.eport = utils.getEventPort(self.cfg, self.eport)
        self.MAPPING.update(mapping)
        for section in self.cfg.sections():
            if section.startswith('plugin.'):
                pluginname = section.split('.', 1)[1]
                classparts = self.cfg.get(section, 'class').split('.')
                classname = classparts[-1]
                modulename = '.'.join(classparts[:-1])
                module = importlib.import_module(modulename)
                args = json.loads(self.cfg.get(section, 'args'))
                self.plugins[pluginname] = getattr(module, classname)(*args)

    def getCommand(self, code):
        code = self.getKeyCode(code)
        action = self.MAPPING.get(code)
        if not action:
            if code > 255:
                key = curseskeymap[code]
            else:
                key = chr(code)
            action = {'key': key}
        return action

    def command(self, code=None, command=None):
        result = ''
        if code and not command:
            command = self.getCommand(code)
        if not command:
            return False
        for pluginname, plugin in self.plugins.items():
            if pluginname in command:
                return plugin.command(**command[pluginname])

        if 'mode' in command:
            mode = command['mode']
            if self.cfg.has_section(self.get_section(mode)):
                self.mode = command['mode']
                self.readConfig()
                self.print_help()
            else:
                self.write_error("Invallid mode {}".format(mode))
        if 'action' in command:
            self.remote.send_action(str(command['action']))
            time.sleep(0.2)
        if 'key' in command:
            self.remote.send_keyboard_button(command['key'])
            time.sleep(0.1)
            self.remote.release_button()
        if 'api' in command:
            self.client.command(**command['api'])
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
            result = self.client.command('Input.SendText', text=text,
                                         done=True)
        if 'exec' in command:
            subprocess.Popen(command['exec'].format(host=self.host, port=self.port, eport=self.eport), shell=True, stdout=open(os.devnull, 'w'))
        logging.info("%s %s", command, result)
        return result

    def write_error(self, text):
        my, mx = self.scr.getmaxyx()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        self.scr.addstr(my - 1, 0, text, curses.color_pair(1))

    def run(self, scr):
        self.scr = scr
        self.init()
        self.print_help()
        try:
            char = self.scr.getch()
            while char not in (3,):  # control + c and q
                try:
                    self.command(char)
                    my, mx = self.scr.getmaxyx()
                    self.scr.move(my - 1, 0)
                    self.scr.deleteln()
                except Exception as e:
                    self.write_error("Command failed for {}: {}".format(char, e))
                logging.info(char)
                char = self.scr.getch()
        except KeyboardInterrupt:
            sys.exit(0)
