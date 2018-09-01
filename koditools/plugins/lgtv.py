from pywebostv.connection import WebOSClient
from pywebostv.controls import MediaControl, InputControl, SystemControl, SourceControl

class TV:
    def __init__(self, ip, key=None):
        self.store = {}
        if key:
            self.store['client_key'] = key
        self.ip = ip
        self.client = WebOSClient(ip)
        self.connnected = False
        self.clients = {}

    def connect(self):
        self.client.connect()
        list(self.client.register(self.store))
        self.connnected = True

    def command(self, control, command, args=None):
        args = args or []
        if not self.connnected:
            self.connect()
        control = self.get_control(control)
        return getattr(control, command)(*args)

    def get_control(self, controltype):
        if controltype not in self.clients: 
            if controltype == 'media':
                control = MediaControl(self.client)
            elif controltype == 'input':
                control = InputControl(self.client)
                control.connect_input()
            elif controltype == 'system':
                control = SystemControl(self.client)
            elif controltype == 'source':
                control = SourceControl(self.client)
            self.clients[controltype] = control
        return self.clients[controltype]

