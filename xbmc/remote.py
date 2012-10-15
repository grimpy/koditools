#!/usr/bin/env python2
import tty
import sys
import termios
import logging
from .restclient import JsonRPC
    
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
    MAPPING = {127: {'command': 'Input.Back'}, #backspace
               13: {'command': 'Input.Select'}, #Enter
               32: {'command': 'Player.PlayPause', 'playerid': 1}, #space
               44: {'command': 'Input.ContextMenu'}, #,
               45: {'command': 'Application.SetVolume', 'volume': 'decrement'}, #-
               61: {'command': 'Application.SetVolume', 'volume': 'increment'}, #=
               102: {'command': 'GUI.ActivateWindow', 'window': 'favourites'}, #f
               104: {'command': 'GUI.ActivateWindow', 'window': 'home'}, #f
               116: {'command': 'GUI.ActivateWindow', 'window': 'videos', 'parameters': ['TvShowTitles']}, #t
               118: {'command': 'GUI.ActivateWindow', 'window': 'videos', 'parameters': ['MovieTitles']}, #v
               105: {'command': 'Input.Info'}, #i
               109: {'command': 'Application.SetMute', 'mute': 'toggle'}, #m
               111: {'command': 'Input.ShowOSD'}, #o
               115: {'command': 'GUI.ActivateWindow', 'window': 'shutdownmenu'}, #s
               120: {'command': 'Player.Stop', 'playerid': 1}, #x 
               500: {'command': 'Input.Left'}, #left
               501: {'command': 'Input.Up'}, #up
               502: {'command': 'Input.Right'}, #right
               503: {'command': 'Input.Down'}, #Down
              }
    def __init__(self, host):
        self.client = JsonRPC('http://%s:8080/jsonrpc' % host)

    def command(self, code):
        command = Remote.MAPPING.get(code)
        if not command:
            return False
        try:
            result = self.client.command(**command)
        except Exception, e:
            logging.warning('Error happened durring %s\n%s' % (command, e))
            result = None
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
