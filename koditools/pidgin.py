#!/usr/bin/env python2
import dbus
import gobject
import logging
from htmllib import HTMLParser
from formatter import AbstractFormatter, DumbWriter
from cStringIO import StringIO
from dbus.mainloop.glib import DBusGMainLoop
from .kodiclient import KodiClient
from . import utils


def toText(val):
    if isinstance(val, unicode):
        val = val.encode('utf8')
    return val


def html2text(html):
    output = StringIO()
    writer = DumbWriter(output)
    p = HTMLParser(AbstractFormatter(writer))
    p.feed(toText(html))
    return toText(output.getvalue())


class Forwarder(object):
    def __init__(self, host):
        if not host:
            cfg = utils.getConfigFile()
            if not cfg.has_section('server') or \
               not cfg.has_option('server', 'host'):
                raise ValueError('Host not configured')
            host = cfg.get('server', 'host')
        self._client = KodiClient('KodiPidgin', ip=host)
        self._client.connect()
        DBusGMainLoop(set_as_default=True)
        self._bus = dbus.SessionBus()
        obj = self._bus.get_object("im.pidgin.purple.PurpleService",
                                   "/im/pidgin/purple/PurpleObject")
        self.purple = dbus.Interface(obj, "im.pidgin.purple.PurpleInterface")

    def run(self):
        self._bus.add_signal_receiver(
            self.receiveIM,
            dbus_interface="im.pidgin.purple.PurpleInterface",
            signal_name="ReceivedImMsg")

        loop = gobject.MainLoop()
        loop.run()

    def receiveIM(self, account, sender, message, conversation, flags):
        logging.info("Received msg from %s: %s account: %s, conversation: %s" %
                     (sender, message, account, conversation))
        buddyid = self.purple.PurpleFindBuddy(account, sender)
        name = self.purple.PurpleBuddyGetLocalBuddyAlias(buddyid)
        self._client.send_notification(toText('%s says' % name),
                                       html2text(message))
