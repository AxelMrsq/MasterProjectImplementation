import appdaemon.plugins.hass.hassapi as hass
import socket


class HelloWorld(hass.Hass):
    def initialize(self):
        self.log("commonucation !")
        self.listen_state(self.ping_callback,"input_button.ping")
        # https://appdaemon.readthedocs.io/en/3.0.0/APIREFERENCE.html#listen-state
        # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        # s.connect(("192.168.1.44", 65400))
        # s.sendall(b"coucou")
        # self.log(s.recv(4096))

    def ping_callback(self, entity, attribute, old, new, kwargs):
        self.log("hello")