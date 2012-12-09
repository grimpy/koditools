#!/usr/bin/env python2
import tty
import sys
import termios
import logging
from .xbmcclient import XBMCClient
import time

def getch_():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

ESCAPEMAPPING = {68: 500, #left
                 65: 501, #up,
                 67: 502, #right
                 66: 503, #down
                }

def getch():
    logging.debug('Getting key')
    char = ord(getch_())
    if char == 27:
        getch_()
        char = ord(getch_())
        char = ESCAPEMAPPING.get(char, 0)
    logging.debug('Retreived key %s' % char)
    return char



class Remote(object):
    MAPPING = {127: {'key': 'backspace'}, #backspace
               13: {'key': 'enter'}, #Enter
               32: {'key': 'space'}, #space
               44: {'key': 'menu'}, #,
               45: {'key': 'volume_down'}, #-
               61: {'key': 'volume_up'}, #=
               102: {'action': 'ActivateWindow(favourites)'}, #f
               104: {'action': 'ActivateWindow(home)'}, #f
               116: {'action': 'ActivateWindow(Videos, TvShowTitles)'}, #t
               118: {'action': 'ActivateWindow(Videos, MovieTitles)'}, #v
               105: {'key': 'i'}, #i
               109: {'action': 'mute'}, #m
               111: {'action': 'OSD'}, #o
               115: {'action': 'ActivateWindow(shutdownmenu)'}, #s
               120: {'key': 'Stop' }, #x
               500: {'key': 'left'}, #left
               501: {'key': 'up'}, #up
               502: {'key': 'right'}, #right
               503: {'key': 'down'}, #Down
              }
    def __init__(self, host):
        self.client = XBMCClient('PyRemote', ip=host)
        self.client.connect()

    def command(self, code):
        command = Remote.MAPPING.get(code)
        if not command:
            return False
        if 'action' in command:
            result = self.client.send_action(command['action'])
        if 'key' in command:
            result = self.client.send_keyboard_button(command['key'])
            time.sleep(0.1)
            self.client.release_button()
        logging.info("%s %s" % (command, result))
        return result


    def run(self):
        char = getch()
        while char not in (3,113): #control + c and q
            if not self.command(char):
                if char == 58: #this is a : we are gonna enter text now
                    print 'Enter text: ',
                    text = sys.stdin.readline()
                    kwargs = {'command': 'Input.SendText', 'text': text, 'done': True}
                    result = self.client.command(**kwargs)
                    logging.info('%s %s' % (kwargs, result))
                else:
                    logging.info(char)

            char = getch()
