import appdaemon.plugins.hass.hassapi as hass

class Train(hass.Hass):

    def initialize(self):
        # self.log("Waiting for a ping...")
        # self.listen_state(self.ping_callback, "input_button.ping")
        self.weather_entity =  self.get_entity("weather.forecast_home")
        temperature = self.weather_entity.get_state(attribute="temperature")
        humidity = self.weather_entity.get_state(attribute="humidity")
        wind_speed = self.weather_entity.get_state(attribute="wind_speed") #m/s
        
        self.log("temperature : ")
        self.log(temperature)
        self.log("humidity : ")
        self.log(humidity)
        self.log("wind speed m/s : ")
        self.log(wind_speed)
        self.log("wind speed km/h : ")
        self.log(wind_speed*3.6)

        

    def ping_callback(self, entity, attribute, old, new, kwargs):
        # self.log("Ping received! Gathering 30 days of data...")
        pass
        
        