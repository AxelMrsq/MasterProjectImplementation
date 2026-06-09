import appdaemon.plugins.hass.hassapi as hass
import socket


class HelloWorld(hass.Hass):
    def initialize(self):
        self.log("commonication !")
        # self.listen_state(self.ping_callback,"input_button.ping")
        # https://appdaemon.readthedocs.io/en/3.0.0/APIREFERENCE.html#listen-state
        self.log(self.get_state("sensor.lixee_zlinky_tic_puissance_apparente"))
        # https://appdaemon.readthedocs.io/en/3.0.0/APIREFERENCE.html#get-state
        

    def ping_callback(self, entity, attribute, old, new, kwargs):
        self.log("Creating socket")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.log("Connecting")
        s.connect(("192.168.1.44", 65400))
        self.log("Sending ping")
        s.sendall(b"ping")
        self.log("Waiting for answer")
        self.log(s.recv(4096).decode("utf-8"))
        
        