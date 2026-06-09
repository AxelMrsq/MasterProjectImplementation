import appdaemon.plugins.hass.hassapi as hass
import socket


class HelloWorld(hass.Hass):
    def initialize(self):
        self.log("commonucation !")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        s.connect(("192.168.1.44", 65400))
        s.sendall(b"coucou")
        self.log(s.recv(4096))