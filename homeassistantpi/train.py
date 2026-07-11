import appdaemon.plugins.hass.hassapi as hass
import datetime
from collections import defaultdict
import pickle
import socket
import struct
import math
import threading

class Train(hass.Hass):

    def initialize(self):
        self.log("Waiting for a ping...")
        self.listen_state(self.ping_callback,"input_button.ping")

        
        # 1. Fetch 30 days asynchronously to protect AppDaemon's performance
        # self.get_history(
        #     entity_id="sensor.lixee_zlinky_tic_puissance_apparente", 
        #     days=30, 
        #     callback=self.process_history
        # )

    def ping_callback(self, entity, attribute, old, new, kwargs):
        self.log("Ping !")
        self.log("Initializing historical feature training script...")
        
        # Entity Configs
        self.consumption_entity = "sensor.lixee_zlinky_tic_puissance_apparente"
        self.weather_entity_id = "weather.forecast_home"

        # # Test current state reading
        # weather_entity = self.get_entity(self.weather_entity_id)
        # temperature = weather_entity.get_state(attribute="temperature")
        # humidity = weather_entity.get_state(attribute="humidity")
        # wind_speed = weather_entity.get_state(attribute="wind_speed")
        
        # self.log(f"Current Weather -> Temp: {temperature}°C | Humidity: {humidity}% | Wind Speed: {wind_speed} m/s")

        # Step 1: Fetch consumption history
        self.get_history(entity_id=self.consumption_entity, days=10, callback=self.process_consumption_history)

    def process_consumption_history(self, data):
        self.consumption_raw = data
        # Step 2: Fetch weather history
        self.get_history(entity_id=self.weather_entity_id, days=10, callback=self.process_weather_history)

    def extract_hourly_values(self, data_payload):
        """Helper to extract native states and group them by hour chunks"""
        history_list = []
        if isinstance(data_payload, dict):
            for val in data_payload.values():
                if isinstance(val, list):
                    history_list = val
                    break
        elif isinstance(data_payload, list):
            history_list = data_payload

        if not history_list or not history_list[0]:
            return defaultdict(list)

        entries = history_list[0] if isinstance(history_list[0], list) else history_list
        hourly_groups = defaultdict(list)
        
        for entry in entries:
            state_str = entry.get("state")
            dt_str = entry.get("last_changed")
            
            if isinstance(dt_str, str):
                dt_str = dt_str.split("+")[0]
                try:
                    dt = datetime.datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S.%f")
                except ValueError:
                    dt = datetime.datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S")
            else:
                dt = dt_str

            try:
                value = float(state_str)
            except (ValueError, TypeError):
                continue
                
            if dt:
                hour_floor = dt.replace(minute=0, second=0, microsecond=0)
                hourly_groups[hour_floor].append(value)
        return hourly_groups

    def process_weather_history(self, weather_data):
        self.log("Parsing consumption history and extracting weather attributes...")
        
        # 1. Parse Consumption standard values
        consumption_groups = self.extract_hourly_values(self.consumption_raw)

        # 2. Extract Weather attributes over time
        weather_list = []
        if isinstance(weather_data, dict):
            for val in weather_data.values():
                if isinstance(val, list): weather_list = val; break
        elif isinstance(weather_data, list):
            weather_list = weather_data

        weather_entries = weather_list[0] if (weather_list and isinstance(weather_list[0], list)) else weather_list

        temp_groups = defaultdict(list)
        humidity_groups = defaultdict(list)
        wind_groups = defaultdict(list)

        for entry in weather_entries:
            dt_str = entry.get("last_changed")
            attrs = entry.get("attributes", {})
            
            if isinstance(dt_str, str):
                dt_str = dt_str.split("+")[0]
                try:
                    dt = datetime.datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S.%f")
                except ValueError:
                    dt = datetime.datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S")
            else:
                dt = dt_str

            if dt:
                hour_floor = dt.replace(minute=0, second=0, microsecond=0)
                
                if "temperature" in attrs and attrs["temperature"] is not None:
                    temp_groups[hour_floor].append(float(attrs["temperature"]))
                if "humidity" in attrs and attrs["humidity"] is not None:
                    humidity_groups[hour_floor].append(float(attrs["humidity"]))
                if "wind_speed" in attrs and attrs["wind_speed"] is not None:
                    wind_groups[hour_floor].append(float(attrs["wind_speed"]))

        # Assemble timelines
        all_timestamps = list(consumption_groups.keys()) + list(temp_groups.keys())
        if not all_timestamps:
            self.log("No overlapping data found. Exiting.")
            return

        start_hour = min(all_timestamps).replace(minute=0, second=0, microsecond=0)
        end_hour = max(all_timestamps).replace(minute=0, second=0, microsecond=0)

        hourly_timeline = {}
        current_hour = start_hour
        
        while current_hour <= end_hour:
            cons = sum(consumption_groups[current_hour]) / len(consumption_groups[current_hour]) if current_hour in consumption_groups else 0.0

            t_ext = sum(temp_groups[current_hour]) / len(temp_groups[current_hour]) if current_hour in temp_groups else 15.0
            rh = sum(humidity_groups[current_hour]) / len(humidity_groups[current_hour]) if current_hour in humidity_groups else 60.0
            ws = sum(wind_groups[current_hour]) / len(wind_groups[current_hour]) if current_hour in wind_groups else 2.0

            try:
                e = (rh / 100.0) * 6.105 * math.exp((17.27 * t_ext) / (237.7 + t_ext))
                at = t_ext + 0.33 * e - 0.70 * ws - 4.0
            except ZeroDivisionError:
                at = t_ext

            is_weekend = 1 if current_hour.weekday() >= 5 else 0

            hourly_timeline[current_hour] = {
                "consumption": round(cons, 2),
                "apparent_temp": round(at, 2),
                "is_weekend": is_weekend,
                "hour_of_day": int(current_hour.hour),
                "weekday": int(current_hour.weekday())
            }
            current_hour += datetime.timedelta(hours=1)

        # 3. Calculate AVG4D features
        for dt, metrics in hourly_timeline.items():
            target_hour = metrics["hour_of_day"]
            target_weekend = metrics["is_weekend"]
            
            past_consumptions = []
            check_day = dt - datetime.timedelta(days=1)
            
            while len(past_consumptions) < 4 and check_day >= start_hour:
                if check_day in hourly_timeline:
                    historical_point = hourly_timeline[check_day]
                    if historical_point["is_weekend"] == target_weekend:
                        past_consumptions.append(historical_point["consumption"])
                check_day -= datetime.timedelta(days=1)

            avg4d = sum(past_consumptions) / len(past_consumptions) if past_consumptions else metrics["consumption"]
            metrics["avg4d"] = round(avg4d, 2)

        # 4. K-Means (k=2) Clustering for Apparent Temperature
        at_values = [m["apparent_temp"] for m in hourly_timeline.values()]
        if at_values:
            c0, c1 = min(at_values), max(at_values)
            if c0 == c1: c1 += 1.0

            for _ in range(10):
                cluster_0 = [v for v in at_values if abs(v - c0) < abs(v - c1)]
                cluster_1 = [v for v in at_values if abs(v - c0) >= abs(v - c1)]
                if cluster_0: c0 = sum(cluster_0) / len(cluster_0)
                if cluster_1: c1 = sum(cluster_1) / len(cluster_1)

            for dt, metrics in hourly_timeline.items():
                val = metrics["apparent_temp"]
                metrics["tempcluster"] = 0 if abs(val - c0) < abs(val - c1) else 1
        else:
            for dt, metrics in hourly_timeline.items():
                metrics["tempcluster"] = 0

        # Build message package
        final_payload = []
        for dt, metrics in hourly_timeline.items():
            final_payload.append({
                "timestamp": dt.strftime("%Y-%m-%d %H:00"),
                "hour": metrics["hour_of_day"],
                "weekday": metrics["weekday"],
                "consumption": metrics["consumption"],
                "avg4d": metrics["avg4d"],
                # "apparent_temp": metrics["apparent_temp"],
                "tempcluster": metrics["tempcluster"]
            })

        final_payload_bis = {"cmd" : "train", "data": final_payload}

        self.log(f"Successfully processed {len(final_payload_bis)} timeline samples.")
        threading.Thread(target=self.send_data, args=(final_payload_bis,), daemon=True).start()
        

    def send_data(self, payload):
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10.0)
        s.connect(("192.168.1.44", 65400))
        message = pickle.dumps(payload)
        header = struct.pack('!I', len(message))
        s.sendall(header + message)
        
        self.log("Data successfully transmitted over network socket.")
        self.log("Waiting for train answer")

        buffer = b""
        while len(buffer) < 4:
            packet = s.recv(4 - len(buffer))
            buffer += packet
        
        header = buffer
        message_length = struct.unpack('!I', header)[0]

        buffer = b""
        while len(buffer) < message_length:
            packet = s.recv(message_length - len(buffer))
            buffer += packet
        full_data = buffer

        score = pickle.loads(full_data)

        self.log(score)
        s.close()
        # self.log(payload)