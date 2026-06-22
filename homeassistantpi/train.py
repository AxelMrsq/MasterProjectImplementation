import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime
from collections import defaultdict

class Train(hass.Hass):

    def initialize(self):
        self.log("Requesting 30 days of history...")
        
        # 1. Fetch 30 days asynchronously to protect AppDaemon's performance
        self.get_history(
            entity_id="sensor.lixee_zlinky_tic_puissance_apparente", 
            days=30, 
            callback=self.process_history
        )

    def process_history(self, data):
        import datetime
        from collections import defaultdict

        # 1. Safely extract the raw list from AppDaemon's response payload
        history_list = []
        if isinstance(data, dict):
            for val in data.values():
                if isinstance(val, list):
                    history_list = val
                    break
        elif isinstance(data, list):
            history_list = data

        if not history_list or not history_list[0]:
            self.log("No historical entries found or history is empty.")
            return
            
        entries = history_list[0] if isinstance(history_list[0], list) else history_list

        # 2. Extract valid entries and track overall min/max timestamps
        hourly_groups = defaultdict(list)
        timestamps = []

        for entry in entries:
            state_str = entry.get("state")
            dt = entry.get("last_changed") # Native datetime object
            
            try:
                value = float(state_str)
            except (ValueError, TypeError):
                continue
                
            if dt:
                timestamps.append(dt)
                # Drop minutes/seconds to group by hour
                hour_floor = dt.replace(minute=0, second=0, microsecond=0)
                hourly_groups[hour_floor].append(value)

        if not timestamps:
            self.log("No valid numeric data found to process.")
            return

        # 3. Establish the bounds of your timeline
        start_hour = min(timestamps).replace(minute=0, second=0, microsecond=0)
        end_hour = max(timestamps).replace(minute=0, second=0, microsecond=0)

        # 4. Loop through every single hour sequentially, filling gaps with 0
        hourly_averages = {}
        current_hour = start_hour
        
        while current_hour <= end_hour:
            # Format key as a clean string for your final output dictionary
            hour_str = current_hour.strftime("%Y-%m-%d %H:00")
            
            if current_hour in hourly_groups:
                # Calculate true mean if data exists
                values = hourly_groups[current_hour]
                mean_value = sum(values) / len(values)
                hourly_averages[hour_str] = round(mean_value, 2)
            else:
                # Default to 0.0 if the hour had no state changes registered
                hourly_averages[hour_str] = 0.0
                
            # Log the output line by line
            self.log(f"Hour: {hour_str} | Mean: {hourly_averages[hour_str]}")
            
            # Move to the next hour increment
            current_hour += datetime.timedelta(hours=1)

        self.log(f"Completed processing timeline. Outputted {len(hourly_averages)} hourly slots.")
# https://appdaemon.readthedocs.io/en/latest/HASS_API_REFERENCE.html#appdaemon.plugins.hass.hassapi.Hass.get_history