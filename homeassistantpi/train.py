import appdaemon.plugins.hass.hassapi as hass
import socket
import datetime


class Train(hass.Hass):
    def initialize(self):
        self.log("Waiting for training activation")

        # Calculate a timeframe (e.g., the last 2 hours)
        start_time = self.datetime() - datetime.timedelta(hours=2)
        
        # Fetch the history
        history = self.get_history(entity_id="sensor.living_room_temperature", start_time=start_time)
        
        # Process the results
        if history:
            # history[0] contains the list of state changes for the entity
            for entry in history[0]:
                state = entry.get("state")
                last_changed = entry.get("last_changed")
                self.log(f"Time: {last_changed} | State: {state}")

    def ping_callback(self, entity, attribute, old, new, kwargs):
        self.log("Training started")
        # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        # self.log("Connecting")
        # s.connect(("192.168.1.44", 65400))
        # self.log("Sending ping")
        # s.sendall(b"ping")
        # self.log("Waiting for answer")
        # self.log(s.recv(4096).decode("utf-8"))
        