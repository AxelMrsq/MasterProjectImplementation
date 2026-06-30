import appdaemon.plugins.hass.hassapi as hass

class Train(hass.Hass):

    def initialize(self):
        # self.log("Waiting for a ping...")
        # self.listen_state(self.ping_callback, "input_button.ping")
        self.weather_entity = "weather.forecast_home"
        state = self.weather_entity.get_state(attribute="all")
        self.log(state)
        

    def ping_callback(self, entity, attribute, old, new, kwargs):
        # self.log("Ping received! Gathering 30 days of data...")
        pass
        
        
        
        
